from backend.graph.state import ResearchState
from backend.llm.client import LLMClient
from backend.llm.prompts import WRITER_PROMPT

def writer_node(state: ResearchState) -> dict:
    """
    Writer node that compiles the analysis and findings into a final markdown report.

    Args:
        state (ResearchState): The current state of the research workflow.

    Returns:
        dict: A dictionary containing the updated 'report' key.
    """
    query = state.get("query", "")
    plan = state.get("plan", "")
    research = state.get("research", "")
    analysis = state.get("analysis", "")

    client = LLMClient()
    prompt = WRITER_PROMPT.format(
        query=query,
        plan=plan,
        research=research,
        analysis=analysis
    )
    report = client.generate(prompt=prompt, system_instruction="Report writing constraint")
    return {"report": report}
