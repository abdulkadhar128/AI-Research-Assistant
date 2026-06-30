import time
from backend.graph.state import ResearchState
from backend.llm.client import LLMClient
from backend.llm.config import LLMConfig
from backend.llm.prompts import MERGED_RESEARCHER_PROMPT

def researcher_node(state: ResearchState) -> dict:
    """
    Researcher node that gathers and fact-checks information in a single LLM pass.
    """
    plan = state.get("plan", "")
    search_results = state.get("search_results", "")
    
    # Use fast model tier for quick summarization and verification
    client = LLMClient(model_name=LLMConfig.get_fast_model())
    prompt = MERGED_RESEARCHER_PROMPT.format(plan=plan, search_results=search_results)
    
    research = client.generate(prompt=prompt, system_instruction="Findings generation and verification constraint")
    
    return {
        "research": research,
        "fact_checked_research": research,  # populate for backwards compatibility
        "researcher_finish_time": time.time()
    }
