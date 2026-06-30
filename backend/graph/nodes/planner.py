from backend.graph.state import ResearchState
from backend.llm.client import LLMClient
from backend.llm.config import LLMConfig
from backend.llm.prompts import PLANNER_PROMPT

def planner_node(state: ResearchState) -> dict:
    """
    Planner node that outlines the research plan based on the user query.
    """
    import time
    query = state.get("query", "")
    # Route to fast model tier for quick outline generation
    client = LLMClient(model_name=LLMConfig.get_fast_model())
    prompt = PLANNER_PROMPT.format(query=query)
    plan = client.generate(prompt=prompt, system_instruction="Plan generation constraint")
    return {
        "plan": plan,
        "planner_finish_time": time.time()
    }
