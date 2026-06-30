from backend.graph.state import ResearchState
from backend.llm.client import LLMClient
from backend.llm.prompts import PLANNER_PROMPT

def planner_node(state: ResearchState) -> dict:
    """
    Planner node that outlines the research plan based on the user query.

    Args:
        state (ResearchState): The current state of the research workflow.

    Returns:
        dict: A dictionary containing the updated 'plan' key.
    """
    query = state.get("query", "")
    client = LLMClient()
    prompt = PLANNER_PROMPT.format(query=query)
    plan = client.generate(prompt=prompt, system_instruction="Plan generation constraint")
    return {"plan": plan}
