from backend.graph.state import ResearchState
from backend.llm.client import LLMClient
from backend.llm.prompts import ANALYST_PROMPT

def analyst_node(state: ResearchState) -> dict:
    """
    Analyst node that processes research findings and synthesizes key insights.

    Args:
        state (ResearchState): The current state of the research workflow.

    Returns:
        dict: A dictionary containing the updated 'analysis' key.
    """
    research = state.get("research", "")
    client = LLMClient()
    prompt = ANALYST_PROMPT.format(research=research)
    analysis = client.generate(prompt=prompt, system_instruction="Analysis generation constraint")
    return {"analysis": analysis}
