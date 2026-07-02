"""
Planner Agent node.

Generates a structured research plan from the user's topic using
LangChain ChatPromptTemplate + LangChainLLMService.
"""

from backend.graph.state import ResearchState
from backend.llm.client import LangChainLLMService
from backend.llm.config import LLMConfig
from backend.llm.prompts import PLANNER_TEMPLATE


def planner_node(state: ResearchState) -> dict:
    """
    Generate a step-by-step research plan for the given topic.
    Uses the fast model tier — planning is lightweight and latency-sensitive.
    """
    topic = state.get("topic", "")
    print(f"\n{'='*60}")
    print(f"[PLANNER] TOPIC: {topic!r}")
    print(f"{'='*60}")

    if not topic:
        print("[PLANNER] WARNING: topic is empty! Check state initialization in research.py")

    llm_service = LangChainLLMService(
        model_name=LLMConfig.get_fast_model(),
        temperature=0.2,
    )
    messages = PLANNER_TEMPLATE.format_messages(topic=topic)
    print(f"[PLANNER] Human message preview: {messages[-1].content[:120]!r}")

    response = llm_service.invoke(messages)
    plan = response.content

    print(f"[PLANNER] Plan generated ({len(plan)} chars). First line: {plan.splitlines()[0]!r}")

    return {"plan": plan}
