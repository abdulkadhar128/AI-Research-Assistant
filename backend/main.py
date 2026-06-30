import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.research import router as research_router

from backend.graph.workflow import research_graph
from backend.database.connection import init_db

# Import your ResearchState type if it exists
try:
    from backend.graph.state import ResearchState
except ImportError:
    ResearchState = dict

# Initialize database tables
init_db()

# Create FastAPI app
app = FastAPI(
    title="AI Research Assistant API",
    description="A multi-agent research assistant built using LangGraph, FastAPI, and Python.",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(research_router)


@app.get("/")
def read_root():
    return {
        "message": "Welcome to the AI Research Assistant API. Use POST /research to execute tasks."
    }


if __name__ == "__main__":
    query = "What is Retrieval-Augmented Generation?"

    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])

    print("\n--- Running AI Research Assistant CLI ---")
    print(f"Query: {query}")
    print("-" * 60)

    try:
        initial_state = {
            "query": query,
            "plan": "",
            "search_results": "",
            "research": "",
            "fact_checked_research": "",
            "analysis": "",
            "citations": "",
            "report": "",
            "review_feedback": "",
            "quality_score": 0.0,
        }

        result = research_graph.invoke(initial_state)

        report = result.get("report", "")
        review_feedback = result.get("review_feedback", "")
        quality_score = result.get("quality_score", 0.0)

        print("\nGenerated Report:\n")
        print(report)

        print("\n" + "-" * 60)
        print("Review Feedback:")
        print(review_feedback)
        print(f"\nQuality Score: {quality_score}/10")
        print("-" * 60)

        # Save report to database
        try:
            from backend.database.connection import SessionLocal
            from backend.database import crud, schemas

            db = SessionLocal()

            report_in = schemas.ReportCreate(
                query=query,
                report=report,
                quality_score=quality_score,
                review_feedback=review_feedback,
            )

            db_report = crud.create_report(db, report=report_in)

            print(
                f"\nReport saved successfully with ID: {db_report.id}"
            )

        finally:
            db.close()

    except Exception as e:
        print(f"\nExecution failed: {e}", file=sys.stderr)
        sys.exit(1)