import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class LLMClient:
    """
    Mock client representing a connection to an LLM provider.
    Implements dynamic placeholder logic to avoid external network/API dependencies.
    """
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        self.model_name = model_name

    def generate(self, prompt: str, system_instruction: str = "") -> str:
        """
        Simulates generation of text using the LLM based on prompt archetypes.

        Args:
            prompt: The input user prompt.
            system_instruction: The system prompt or instruction constraint.

        Returns:
            A string response simulating LLM output.
        """
        logger.info(f"Generating content using model {self.model_name}...")
        
        # Simple extraction of query if present
        query_match = re.search(r"User Query:\s*(.*)", prompt, re.IGNORECASE)
        query = query_match.group(1).strip() if query_match else "Selected Topic"
        
        # Determine archetype from keywords in prompts or system instructions
        if "Planner" in prompt or "Research Planner" in prompt or "Plan" in system_instruction:
            return (
                f"1. Define and clarify the core concepts of '{query}'.\n"
                f"2. Gather key historical details, architectures, and state-of-the-art developments for '{query}'.\n"
                f"3. Critically analyze limitations, benefits, and future trends of '{query}'."
            )
        elif "Researcher" in prompt or "Findings" in system_instruction:
            return (
                f"- Definition: Gathered comprehensive documentation regarding '{query}'.\n"
                f"- Architecture & Execution: Analyzed standard setups, technical workflows, and popular implementation stacks.\n"
                f"- Core findings: Identified major players, standard models, and operational patterns for '{query}'."
            )
        elif "Analyst" in prompt or "Analysis" in system_instruction:
            return (
                f"- Advantages: High efficiency, modularity, and integration potential for '{query}'.\n"
                f"- Drawbacks & Challenges: Requires careful tuning, suffers from edge-case failure modes, and needs continuous evaluation.\n"
                f"- Emerging Paradigm: Shift towards automated debugging, advanced agent routing, and orchestration layers."
            )
        elif "Writer" in prompt or "Report" in system_instruction:
            plan_match = re.search(r"Research Plan:\s*(.*?)(?=\n\n|\n[A-Z]|$)", prompt, re.DOTALL | re.IGNORECASE)
            research_match = re.search(r"Research Findings:\s*(.*?)(?=\n\n|\n[A-Z]|$)", prompt, re.DOTALL | re.IGNORECASE)
            analysis_match = re.search(r"Critical Analysis:\s*(.*?)(?=\n\n|\n[A-Z]|$)", prompt, re.DOTALL | re.IGNORECASE)
            
            plan = plan_match.group(1).strip() if plan_match else f"Investigation outline for {query}"
            research = research_match.group(1).strip() if research_match else f"General facts gathered about {query}"
            analysis = analysis_match.group(1).strip() if analysis_match else f"Synthesized SWOT analysis of {query}"
            
            return (
                f"# Research Report: {query}\n\n"
                f"## 1. Executive Summary\n"
                f"This document provides a production-ready, compiled analysis of '{query}'. The report was synthesized via a multi-agent workflow consisting of Planning, Research, Critical Analysis, and professional Technical Writing.\n\n"
                f"## 2. Research Plan\n"
                f"{plan}\n\n"
                f"## 3. Key Findings\n"
                f"{research}\n\n"
                f"## 4. Synthesized Analysis\n"
                f"{analysis}\n\n"
                f"## 5. Conclusion\n"
                f"The analysis indicates that '{query}' represents a significant technology paradigm. Organizations utilizing it stand to benefit from reduced overhead and increased technical capability, provided typical failure modes are appropriately handled."
            )
        
        return "Default Mock Response: No matching prompt archetype identified."
