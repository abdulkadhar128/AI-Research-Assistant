from langgraph.graph import StateGraph, START, END
from backend.graph.state import ResearchState
from backend.graph.nodes.planner import planner_node
from backend.graph.nodes.search import search_node
from backend.graph.nodes.researcher import researcher_node
from backend.graph.nodes.writer import writer_node

# Initialize the workflow StateGraph with our ResearchState schema
workflow = StateGraph(ResearchState)

# Register nodes in the graph
workflow.add_node("planner", planner_node)
workflow.add_node("search", search_node)
workflow.add_node("researcher", researcher_node)
workflow.add_node("writer", writer_node)

# Add edges to direct the parallel and merged workflow
workflow.add_edge(START, "planner")
workflow.add_edge(START, "search")

workflow.add_edge("planner", "researcher")
workflow.add_edge("search", "researcher")

workflow.add_edge("researcher", "writer")
workflow.add_edge("writer", END)

# Compile the graph
research_graph = workflow.compile()
