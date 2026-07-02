from langgraph.graph import StateGraph, START, END
from backend.graph.state import ResearchState
from backend.graph.nodes.intent_analyzer import intent_analyzer_node
from backend.graph.nodes.planner import planner_node
from backend.graph.nodes.search import search_node
from backend.graph.nodes.verify import verify_node
from backend.graph.nodes.writer import writer_node
from backend.graph.nodes.reviewer import reviewer_node

def should_proceed_to_research(state: ResearchState) -> str:
    """Conditional edge from intent_analyzer"""
    if state.get("clarification_needed", False):
        return "clarify"
    return "research"

def should_rewrite(state: ResearchState) -> str:
    """Conditional edge from reviewer"""
    # If score < 8.0 and we haven't revised 3 times, go back to writer
    score = state.get("score", 10.0)
    revs = state.get("revision_count", 0)
    if score < 8.0 and revs < 3:
        return "rewrite"
    return "done"

workflow = StateGraph(ResearchState)

workflow.add_node("intent_analyzer", intent_analyzer_node)
workflow.add_node("planner", planner_node)
workflow.add_node("search", search_node)
workflow.add_node("verify", verify_node)
workflow.add_node("writer", writer_node)
workflow.add_node("reviewer", reviewer_node)

# Entry point
workflow.add_edge(START, "intent_analyzer")

# Conditional routing after intent analysis
workflow.add_conditional_edges(
    "intent_analyzer",
    should_proceed_to_research,
    {
        "clarify": END, # Stop early if clarification needed
        "research": "planner" # Route to planner first
    }
)

# Planner to search
workflow.add_edge("planner", "search")

# Search to verify
workflow.add_edge("search", "verify")

# verification to writer
workflow.add_edge("verify", "writer")

# writer to reviewer
workflow.add_edge("writer", "reviewer")

# Conditional loop from reviewer
workflow.add_conditional_edges(
    "reviewer",
    should_rewrite,
    {
        "rewrite": "writer",
        "done": END
    }
)

research_graph = workflow.compile()
