from backend.graph.state import ResearchState
from backend.llm.client import LLMClient
from backend.llm.prompts import RESEARCHER_PROMPT

def researcher_node(state: ResearchState) -> dict:
    """
    Researcher node that gathers facts and info based on the research plan.

    Args:
        state (ResearchState): The current state of the research workflow.

    Returns:
        dict: A dictionary containing the updated 'research' key.
    """
    plan = state.get("plan", "")
    client = LLMClient()
    prompt = RESEARCHER_PROMPT.format(plan=plan)
    research = client.generate(prompt=prompt, system_instruction="Findings generation constraint")
    return {"research": research}
