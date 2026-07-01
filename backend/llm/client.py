import re
import logging
import time
import httpx
from typing import Optional
from backend.llm.config import LLMConfig

logger = logging.getLogger(__name__)

class LLMClient:
    """
    Unified LLM Client providing a single abstraction layer for OpenAI, Gemini, and Groq.
    Supports retry logic, timeout protection, and falls back to mock logic if configured.
    """
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name

    def generate(self, prompt: str, system_instruction: str = "") -> str:
        """
        Generates content from the configured LLM provider.

        Args:
            prompt: The formatted user prompt.
            system_instruction: The system prompt constraint instruction.

        Returns:
            The generated text content.
        """
        model = self.model_name or ""
        # Check cache first
        from backend.services.cache_service import CacheService
        cache_key = f"{prompt}|||{system_instruction}|||{model}"
        cached_res = CacheService.get("llm", cache_key)
        if cached_res:
            return cached_res

        provider = LLMConfig.PROVIDER.lower()
        if provider == "mock":
            res = self._generate_mock(prompt, system_instruction)
            CacheService.set("llm", cache_key, res)
            return res

        last_error = None
        for attempt in range(1, LLMConfig.MAX_RETRIES + 1):
            try:
                if provider == "openai":
                    res = self._call_openai(prompt, system_instruction)
                elif provider == "gemini":
                    res = self._call_gemini(prompt, system_instruction)
                elif provider == "groq":
                    res = self._call_groq(prompt, system_instruction)
                else:
                    raise ValueError(f"Unsupported LLM provider: {provider}")
                
                # Cache successful response
                CacheService.set("llm", cache_key, res)
                return res
            except Exception as e:
                logger.warning(
                    f"LLM API call failed on provider '{provider}' (attempt {attempt}/{LLMConfig.MAX_RETRIES}): {str(e)}"
                )
                last_error = e
                if attempt < LLMConfig.MAX_RETRIES:
                    # Exponential backoff: sleep 2, 4, 8...
                    time.sleep(2 ** attempt)

        raise RuntimeError(
            f"LLM generation failed for provider '{provider}' after {LLMConfig.MAX_RETRIES} attempts. "
            f"Last error: {str(last_error)}"
        )

    def _call_openai(self, prompt: str, system_instruction: str) -> str:
        if not LLMConfig.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is not configured.")

        headers = {
            "Authorization": f"Bearer {LLMConfig.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model_name or LLMConfig.OPENAI_MODEL,
            "messages": messages,
            "temperature": 0.2
        }

        # Handle JSON mode if prompt requests JSON output
        if "json" in prompt.lower() or "json" in system_instruction.lower():
            payload["response_format"] = {"type": "json_object"}

        response = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=LLMConfig.TIMEOUT_SECONDS
        )
        if response.status_code != 200:
            print("OPENAI STATUS:", response.status_code)
            print("OPENAI RESPONSE:", response.text)
            response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    def _call_groq(self, prompt: str, system_instruction: str) -> str:
        if not LLMConfig.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY environment variable is not configured.")

        headers = {
            "Authorization": f"Bearer {LLMConfig.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model_name or LLMConfig.GROQ_MODEL,
            "messages": messages,
            "temperature": 0.2
        }

        if "json" in prompt.lower() or "json" in system_instruction.lower():
            payload["response_format"] = {"type": "json_object"}

        response = httpx.post(
            "https://api.groq.com/openai/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=LLMConfig.TIMEOUT_SECONDS
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    def _call_gemini(self, prompt: str, system_instruction: str) -> str:
        if not LLMConfig.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable is not configured.")

        model = self.model_name or LLMConfig.GEMINI_MODEL

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent?key={LLMConfig.GEMINI_API_KEY}"
        )

        print("\n" + "=" * 80)
        print("GEMINI DEBUG")
        print("Provider:", LLMConfig.PROVIDER)
        print("Model:", model)
        print("Prompt Length:", len(prompt))
        print("System Length:", len(system_instruction))
        print("=" * 80)

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 2048
            }
        }

        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [
                    {
                        "text": system_instruction
                    }
                ]
            }

        headers = {
            "Content-Type": "application/json"
        }

        timeout = httpx.Timeout(
            connect=30.0,
            read=120.0,
            write=30.0,
            pool=30.0
        )

        response = httpx.post(
            url,
            json=payload,
            headers=headers,
            timeout=timeout
        )

        print("\nGEMINI STATUS:", response.status_code)
        print("\nGEMINI RESPONSE:")
        print(response.text[:3000])

        if response.status_code == 429:
            raise RuntimeError(
                "Gemini rate limit reached. Too many requests sent to Gemini."
            )

        response.raise_for_status()

        data = response.json()

        if "candidates" not in data:
            raise RuntimeError(
                f"Gemini response missing candidates field: {data}"
            )

        return data["candidates"][0]["content"]["parts"][0]["text"]
    def _generate_mock(self, prompt: str, system_instruction: str) -> str:
        """
        Simulates generation of text using the mock provider archetype matches.
        """
        logger.info("Generating content using mock provider...")

        # Simple extraction of query if present
        query_match = re.search(r"User Query:\s*(.*)", prompt, re.IGNORECASE)
        query = query_match.group(1).strip() if query_match else "Selected Topic"

        if "Planner" in prompt or "Research Planner" in prompt or "Plan" in system_instruction:
            return (
                f"1. Define and clarify the core concepts of '{query}'.\n"
                f"2. Gather key historical details, architectures, and state-of-the-art developments for '{query}'.\n"
                f"3. Critically analyze limitations, benefits, and future trends of '{query}'."
            )
        elif "Researcher" in prompt or "Findings" in system_instruction:
            search_match = re.search(r"Search Results:\s*(.*?)(?=\n\n|\n[A-Z]|$)", prompt, re.DOTALL | re.IGNORECASE)
            search_data = search_match.group(1).strip() if search_match else "No search results provided"

            return (
                f"- Definition: Gathered comprehensive documentation regarding '{query}' based on findings: [{search_data}].\n"
                f"- Architecture & Execution: Analyzed standard setups, technical workflows, and popular implementation stacks.\n"
                f"- Core findings: Identified major players, standard models, and operational patterns for '{query}'."
            )
        elif "Fact Checker" in prompt or "Fact-Checking" in system_instruction:
            research_match = re.search(r"Research Findings:\s*(.*?)(?=\n\n|\n[A-Z]|$|Search Results:)", prompt, re.DOTALL | re.IGNORECASE)
            research_data = research_match.group(1).strip() if research_match else f"General facts gathered about {query}"
            return (
                f"[Fact-Checked Findings for '{query}']:\n"
                f"1. Verified: {research_data}\n"
                f"2. Consistency Check: All claims matched against search results successfully.\n"
                f"3. Exclusions: Removed 0 unsupported claims."
            )
        elif "Analyst" in prompt or "Analysis" in system_instruction:
            return (
                f"- Advantages: High efficiency, modularity, and integration potential for '{query}'.\n"
                f"- Drawbacks & Challenges: Requires careful tuning, suffers from edge-case failure modes, and needs continuous evaluation.\n"
                f"- Emerging Paradigm: Shift towards automated debugging, advanced agent routing, and orchestration layers."
            )
        elif "Writer" in prompt or "Report" in system_instruction:
            plan_match = re.search(r"Research Plan:\s*(.*?)(?=\n\n|\n[A-Z]|$|Search Results:)", prompt, re.DOTALL | re.IGNORECASE)
            search_match = re.search(r"Search Results:\s*(.*?)(?=\n\n|\n[A-Z]|$|Research Findings:)", prompt, re.DOTALL | re.IGNORECASE)
            research_match = re.search(r"Research Findings:\s*(.*?)(?=\n\n|\n[A-Z]|$|Fact Checked Findings:)", prompt, re.DOTALL | re.IGNORECASE)
            fact_checked_match = re.search(r"Fact Checked Findings:\s*(.*?)(?=\n\n|\n[A-Z]|$|Critical Analysis:)", prompt, re.DOTALL | re.IGNORECASE)
            analysis_match = re.search(r"Critical Analysis:\s*(.*?)(?=\n\n|\n[A-Z]|$|Citations:)", prompt, re.DOTALL | re.IGNORECASE)
            citations_match = re.search(r"Citations:\s*(.*?)(?=\n\n|\n[A-Z]|$)", prompt, re.DOTALL | re.IGNORECASE)

            plan = plan_match.group(1).strip() if plan_match else f"Investigation outline for {query}"
            search_results = search_match.group(1).strip() if search_match else f"Search data for {query}"
            research = research_match.group(1).strip() if research_match else f"General facts gathered about {query}"
            fact_checked = fact_checked_match.group(1).strip() if fact_checked_match else f"Fact-checked facts gathered about {query}"
            analysis = analysis_match.group(1).strip() if analysis_match else f"Synthesized SWOT analysis of {query}"
            citations = citations_match.group(1).strip() if citations_match else f"[1] Example Source\nhttp://example.com"

            return (
                f"# Research Report: {query}\n\n"
                f"## 1. Executive Summary\n"
                f"This document provides a production-ready, compiled analysis of '{query}'. The report was synthesized via a multi-agent workflow consisting of Planning, Search Retrieval, Research, Fact Checking, Critical Analysis, and professional Technical Writing.\n\n"
                f"## 2. Research Plan\n"
                f"{plan}\n\n"
                f"## 3. Search Results\n"
                f"{search_results}\n\n"
                f"## 4. Key Findings\n"
                f"{research}\n\n"
                f"## 5. Fact Checked Findings\n"
                f"{fact_checked}\n\n"
                f"## 6. Synthesized Analysis\n"
                f"{analysis}\n\n"
                f"## 7. Conclusion\n"
                f"The analysis indicates that '{query}' represents a significant technology paradigm. Organizations utilizing it stand to benefit from reduced overhead and increased technical capability, provided typical failure modes are appropriately handled.\n\n"
                f"## 8. References\n"
                f"{citations}"
            )
        elif "Reviewer" in prompt or "Review" in system_instruction:
            # Detect JSON format requests and return structured data
            if "json" in prompt.lower() or "json" in system_instruction.lower():
                return (
                    f'{{\n'
                    f'  "review_feedback": "Review Feedback for \'{query}\' Report:\\n- Structure: Excellent.\\n- Clarity: High.\\n- Completeness: Detailed.",\n'
                    f'  "quality_score": 9.2\n'
                    f'}}'
                )

            return (
                f"Review Feedback for '{query}' Report:\n"
                f"- Structure: Excellent. Clear hierarchy and headers.\n"
                f"- Clarity: High. Very readable and concise.\n"
                f"- Completeness: Detailed coverage of all plan items.\n"
                f"- Research depth: Adequate details and source referencing.\n"
                f"- Conclusion quality: Strong organizational summary.\n\n"
                f"Score: 9.2"
            )

        return "Default Mock Response: No matching prompt archetype identified."