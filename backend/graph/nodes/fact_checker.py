from typing import Optional
from backend.graph.state import ResearchState
from backend.llm.client import LLMClient
from backend.llm.prompts import FACT_CHECKER_PROMPT

def fact_checker_node(state: ResearchState) -> dict:
    """
    Fact Checker node that verifies research findings against search results.

    Args:
        state (ResearchState): The current state of the research workflow.

    Returns:
        dict: A dictionary containing the updated 'fact_checked_research' key.
    """
    query = state.get("query", "")
    research = state.get("research", "")
    search_results = state.get("search_results", "")

    checker = FactChecker()
    fact_checked_research = checker.verify(
        query=query,
        research=research,
        search_results=search_results
    )

    return {"fact_checked_research": fact_checked_research}

class FactChecker:
    """
    FactChecker component responsible for validating research facts.
    Can be replaced or extended with a real LLM verification service.
    """
    def __init__(self, client: Optional[LLMClient] = None):
        self.client = client or LLMClient()

    def verify(self, query: str, research: str, search_results: str) -> str:
        """
        Verify findings against search results and the query.
        Currently uses placeholder logic via the mock LLM client.

        Args:
            query: The user query.
            research: The raw research findings.
            search_results: The retrieved search results.

        Returns:
            str: Fact-checked, verified findings.
        """
        prompt = FACT_CHECKER_PROMPT.format(
            query=query,
            research=research,
            search_results=search_results
        )
        return self.client.generate(
            prompt=prompt,
            system_instruction="Fact-Checking constraint"
        )
