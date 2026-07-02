"""
LangChain-based LLM Service for the AI Research Assistant.

This module provides a single `LangChainLLMService` class that:
  - Routes to ChatOpenAI, ChatGoogleGenerativeAI, or ChatGroq based on LLMConfig.PROVIDER
  - Preserves the SQLite-backed CacheService for prompt deduplication (live providers only)
  - Falls back to a rich deterministic mock generator for offline/testing mode
  - Exposes `.invoke(messages)` returning an AIMessage-compatible object with `.content`
  - Exposes `.get_llm()` for callers that need the raw LangChain chat model object

Both `LLMClient` and `LangChainChatWrapper` are aliased to this class for
backwards-compatibility with any remaining import sites.
"""

import json
import re
import logging
import time
from typing import List, Optional, Any

from backend.llm.config import LLMConfig

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

class _MockMessage:
    """AIMessage-compatible container returned by the mock provider."""
    type = "ai"

    def __init__(self, content: str) -> None:
        self.content = content

    def __repr__(self) -> str:  # pragma: no cover
        return f"MockMessage(content={self.content[:80]!r}...)"


def _extract_messages(messages: List[Any]) -> tuple[str, str]:
    """
    Extract (system_instruction, user_prompt) from a list of LangChain messages.
    Handles both LangChain message objects (.type/.content) and (role, content) tuples.
    """
    system_instruction = ""
    user_prompt = ""
    for msg in messages:
        if isinstance(msg, tuple):
            role, content = msg
        else:
            role = getattr(msg, "type", getattr(msg, "role", ""))
            content = getattr(msg, "content", "")

        role_lower = str(role).lower()
        if "system" in role_lower:
            system_instruction = content
        elif role_lower in ("human", "user", "humanmessage"):
            user_prompt = content
    return system_instruction, user_prompt


def _extract_topic(system_instruction: str, user_prompt: str) -> str:
    """
    Reliably extract the research topic from the combined prompt text.

    Tries multiple patterns in priority order. Designed to work with the
    canonical 'Topic: {topic}' and 'User Query: {topic}' prefixes used in
    prompts.py, and also with legacy prompt formats.

    Returns 'Unknown Topic' only as a true last resort — never silently wrong.
    """
    combined = system_instruction + "\n" + user_prompt

    # Priority 1 — explicit "Topic: ..." label (Writer, Planner templates)
    m = re.search(r'(?:^|\n)Topic:\s+([^\n]+)', combined, re.IGNORECASE | re.MULTILINE)
    if m:
        return m.group(1).strip().strip('"').strip("'")

    # Priority 2 — "User Query: ..." label (Intent Analyzer template)
    m = re.search(r'(?:^|\n)User Query:\s+([^\n]+)', combined, re.IGNORECASE | re.MULTILINE)
    if m:
        return m.group(1).strip().strip('"').strip("'")

    # Priority 3 — "query: ..." in user_prompt (any remaining format)
    m = re.search(r'(?:^|\n)(?:query|subject):\s+([^\n]+)', user_prompt, re.IGNORECASE | re.MULTILINE)
    if m:
        return m.group(1).strip().strip('"').strip("'")

    # Priority 4 — quoted string in the user prompt (last resort)
    m = re.search(r'["\']([^"\']{3,})["\']', user_prompt)
    if m:
        return m.group(1).strip()

    print("[WARN] _extract_topic: could not extract topic from prompt. Returning 'Unknown Topic'.")
    return "Unknown Topic"


# ---------------------------------------------------------------------------
# Mock provider — deterministic, topic-aware responses for offline / CI testing
# ---------------------------------------------------------------------------

def _generate_mock(system_instruction: str, user_prompt: str) -> str:
    """
    Returns deterministic mock LLM output keyed by the agent archetype.
    The topic is extracted using _extract_topic() which reliably finds
    'Topic:' or 'User Query:' labels in the prompt.
    """
    topic = _extract_topic(system_instruction, user_prompt)
    combined = system_instruction + "\n" + user_prompt

    print(f"[MOCK LLM] Generating response for topic: '{topic}'")

    # --- Intent Analyzer ---
    if "Intent Analysis" in system_instruction or "User Query:" in user_prompt:
        print(f"[MOCK LLM] Archetype: Intent Analyzer | Topic: '{topic}'")
        return json.dumps({
            "confidence": 0.92,
            "interpretations": [
                f"Research and explanation of {topic}",
                f"Technical deep-dive into {topic}",
            ],
            "clarification_prompt": "",
        })

    # --- Planner ---
    if "Research Planner" in system_instruction or (
        "Topic:" in user_prompt and "research plan" in user_prompt.lower()
    ):
        print(f"[MOCK LLM] Archetype: Planner | Topic: '{topic}'")
        return (
            f"1. Define the core concepts and scope of '{topic}'.\n"
            f"2. Investigate the historical development and key milestones of '{topic}'.\n"
            f"3. Identify current state-of-the-art techniques and leading approaches in '{topic}'.\n"
            f"4. Examine real-world applications and industry adoption of '{topic}'.\n"
            f"5. Analyse limitations, challenges, and open research problems in '{topic}'.\n"
            f"6. Explore emerging trends and future directions for '{topic}'."
        )

    # --- Writer ---
    if "technical writer" in system_instruction.lower() and "Topic:" in user_prompt:
        print(f"[MOCK LLM] Archetype: Writer | Topic: '{topic}'")
        # Extract sub-sections from the writer prompt for richer mock output
        plan_m = re.search(r'Research Plan:\n(.*?)(?=\n\nVerified Sources:)', user_prompt, re.DOTALL)
        src_m  = re.search(r'Verified Sources:\n(.*?)(?=\n\nCitations bibliography:)', user_prompt, re.DOTALL)
        cit_m  = re.search(r'Citations bibliography:\n(.*?)$', user_prompt, re.DOTALL)

        plan     = plan_m.group(1).strip() if plan_m else f"Research objectives for {topic}"
        sources  = src_m.group(1).strip()  if src_m  else f"Source data for {topic}"
        citations = cit_m.group(1).strip() if cit_m  else "[1] Wikipedia — https://en.wikipedia.org"

        return (
            f"# {topic}\n\n"
            f"## Introduction\n"
            f"This report examines '{topic}' through a structured research methodology combining "
            f"web search, verification, and analytical synthesis.\n\n"
            f"## Background\n"
            f"Research objectives:\n{plan}\n\n"
            f"## Key Findings\n"
            f"The following sources were consulted:\n{sources}\n\n"
            f"## Analysis\n"
            f"'{topic}' demonstrates significant practical value across multiple domains. "
            f"Industry adoption has accelerated due to improved tooling and lower barriers "
            f"to entry [1].\n\n"
            f"## Future Trends\n"
            f"Continued research into '{topic}' is expected to yield advances in "
            f"interpretability, efficiency, and real-world deployment [2].\n\n"
            f"## Conclusion\n"
            f"'{topic}' represents a foundational area of study with growing relevance "
            f"across technology, science, and business applications.\n\n"
            f"## References\n"
            f"{citations}"
        )

    # --- Reviewer ---
    if "editorial reviewer" in system_instruction.lower():
        print(f"[MOCK LLM] Archetype: Reviewer")
        return json.dumps({
            "accuracy":  8.5,
            "coverage":  8.0,
            "clarity":   8.3,
            "citations": 7.8,
            "overall":   8.15,
            "feedback": (
                "The report covers the core aspects well. To improve: (1) add more inline "
                "citations in the Analysis section; (2) expand the Future Trends section with "
                "concrete timelines; (3) ensure every claim in Key Findings has a [N] reference."
            ),
        })

    # Fallback — should never be reached with well-formed prompts
    print(f"[WARN MOCK LLM] No archetype matched. system='{system_instruction[:60]}...'")
    return f"Research overview of: {topic}"


# ---------------------------------------------------------------------------
# LangChainLLMService — primary public interface
# ---------------------------------------------------------------------------

class LangChainLLMService:
    """
    Production-ready LangChain LLM service for the AI Research Assistant.

    Supports OpenAI (ChatOpenAI), Google Gemini (ChatGoogleGenerativeAI),
    Groq (ChatGroq), and an offline Mock provider.

    Usage
    -----
    ```python
    from backend.llm.client import LangChainLLMService
    from backend.llm.config import LLMConfig
    from backend.llm.prompts import PLANNER_TEMPLATE

    service  = LangChainLLMService(model_name=LLMConfig.get_fast_model())
    messages = PLANNER_TEMPLATE.format_messages(topic="Machine Learning")
    response = service.invoke(messages)   # → AIMessage with .content str
    print(response.content)
    ```
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        temperature: float = 0.2,
        json_mode: bool = False,
    ) -> None:
        self.model_name   = model_name
        self.temperature  = temperature
        self.json_mode    = json_mode
        self._llm: Optional[Any] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_llm(self) -> Any:
        """
        Return the underlying LangChain chat model (lazy-initialised).
        Useful when callers want to build chains with the `|` operator.
        """
        if self._llm is None:
            self._llm = self._build_llm()
        return self._llm

    def invoke(self, messages: List[Any]) -> Any:
        """
        Invoke the LLM with the supplied LangChain message list.

        Parameters
        ----------
        messages : list
            LangChain message objects or (role, content) tuples produced by
            ChatPromptTemplate.format_messages().

        Returns
        -------
        Object with a `.content: str` attribute (AIMessage or _MockMessage).
        """
        provider = LLMConfig.PROVIDER.lower()
        system_instruction, user_prompt = _extract_messages(messages)

        # ---------- Mock provider — no caching, always fresh ----------
        if provider == "mock":
            content = _generate_mock(system_instruction, user_prompt)
            return _MockMessage(content)

        # ---------- Cache check (live providers only) ----------
        from backend.services.cache_service import CacheService
        cache_key = f"{provider}|||{self.model_name}|||{system_instruction[:200]}|||{user_prompt[:400]}"
        cached = CacheService.get("llm_lc", cache_key)
        if cached:
            logger.info("LangChainLLMService: cache HIT for provider=%s", provider)
            return _MockMessage(cached)

        # ---------- Live providers with exponential-backoff retry ----------
        last_error: Optional[Exception] = None
        for attempt in range(1, LLMConfig.MAX_RETRIES + 1):
            try:
                llm = self.get_llm()
                response = llm.invoke(messages)
                # Cache successful response
                CacheService.set("llm_lc", cache_key, response.content)
                return response
            except Exception as exc:
                last_error = exc
                logger.warning(
                    "LangChainLLMService: provider=%s attempt=%d/%d error=%s",
                    provider, attempt, LLMConfig.MAX_RETRIES, exc,
                )
                if attempt < LLMConfig.MAX_RETRIES:
                    time.sleep(2 ** attempt)   # 2 s, 4 s, 8 s …

        raise RuntimeError(
            f"LLM generation failed for provider='{provider}' after "
            f"{LLMConfig.MAX_RETRIES} attempts. Last error: {last_error}"
        )

    # ------------------------------------------------------------------
    # Private — model construction
    # ------------------------------------------------------------------

    def _build_llm(self) -> Any:
        """Instantiate and return the appropriate LangChain chat model."""
        provider = LLMConfig.PROVIDER.lower()

        if provider == "openai":
            from langchain_openai import ChatOpenAI
            if not LLMConfig.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY is not set in the environment.")
            kwargs: dict = dict(
                model=self.model_name or LLMConfig.OPENAI_MODEL,
                api_key=LLMConfig.OPENAI_API_KEY,
                temperature=self.temperature,
                timeout=LLMConfig.TIMEOUT_SECONDS,
                max_retries=0,   # retries handled by our own loop
            )
            if self.json_mode:
                kwargs["model_kwargs"] = {"response_format": {"type": "json_object"}}
            return ChatOpenAI(**kwargs)

        elif provider == "gemini":
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
            except ImportError:
                raise ImportError(
                    "Install langchain-google-genai to use the Gemini provider:\n"
                    "  pip install langchain-google-genai"
                )
            if not LLMConfig.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY is not set in the environment.")
            return ChatGoogleGenerativeAI(
                model=self.model_name or LLMConfig.GEMINI_MODEL,
                google_api_key=LLMConfig.GEMINI_API_KEY,
                temperature=self.temperature,
                timeout=LLMConfig.TIMEOUT_SECONDS,
                max_retries=0,
            )

        elif provider == "groq":
            try:
                from langchain_groq import ChatGroq
            except ImportError:
                raise ImportError(
                    "Install langchain-groq to use the Groq provider:\n"
                    "  pip install langchain-groq"
                )
            if not LLMConfig.GROQ_API_KEY:
                raise ValueError("GROQ_API_KEY is not set in the environment.")
            return ChatGroq(
                model=self.model_name or LLMConfig.GROQ_MODEL,
                api_key=LLMConfig.GROQ_API_KEY,
                temperature=self.temperature,
                timeout=LLMConfig.TIMEOUT_SECONDS,
                max_retries=0,
            )

        raise ValueError(
            f"Unsupported LLM provider: '{provider}'. "
            "Set LLM_PROVIDER to 'openai', 'gemini', 'groq', or 'mock'."
        )


# ---------------------------------------------------------------------------
# Backwards-compatibility aliases
# ---------------------------------------------------------------------------

# Old `LLMClient` (raw httpx) is superseded — alias transparently.
LLMClient = LangChainLLMService

# Old `LangChainChatWrapper` added in a prior session — alias transparently.
LangChainChatWrapper = LangChainLLMService