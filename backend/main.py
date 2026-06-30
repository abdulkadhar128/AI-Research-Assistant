import sys
from fastapi import FastAPI
from backend.api.research import router as research_router
from backend.graph.workflow import research_graph

# Initialize the FastAPI app
app = FastAPI(
    title="AI Research Assistant API",
    description="A multi-agent research assistant built using LangGraph, FastAPI, and Python.",
    version="1.0.0"
)

# Include the research router (directly mounts POST /research)
app.include_router(research_router)

@app.get("/")
def read_root() -> dict:
    return {"message": "Welcome to the AI Research Assistant API. Use POST /research to execute tasks."}

if __name__ == "__main__":
    # Check if a custom query is passed via command-line arguments, otherwise default to RAG query
    query = "What is Retrieval-Augmented Generation?"
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])

    print(f"--- Running AI Research Assistant CLI ---")
    print(f"Query: {query}")
    print(f"Initializing LangGraph execution...")
    print("-" * 50)

    try:
        initial_state = {
            "query": query,
            "plan": "",
            "research": "",
            "analysis": "",
            "report": ""
        }
        result = research_graph.invoke(initial_state)
        report = result.get("report", "")

        print("\nGenerated Report:\n")
        print(report)
        print("\n" + "-" * 50)
        print("Workflow execution completed successfully.")
    except Exception as e:
        print(f"Execution failed: {str(e)}", file=sys.stderr)
        sys.exit(1)
