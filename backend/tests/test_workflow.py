from fastapi.testclient import TestClient
from backend.main import app
from backend.graph.workflow import research_graph

client = TestClient(app)

def test_workflow_graph() -> None:
    """
    Tests direct invocation of the compiled LangGraph workflow
    to ensure state transitions and placeholder replacements occur properly.
    """
    initial_state = {
        "query": "Test query about generative AI",
        "plan": "",
        "research": "",
        "analysis": "",
        "report": ""
    }
    result = research_graph.invoke(initial_state)

    # Validate output keys
    assert "query" in result
    assert "plan" in result
    assert "research" in result
    assert "analysis" in result
    assert "report" in result

    # Validate dynamic mock propagation
    assert "Test query about generative AI" in result["plan"]
    assert "Test query about generative AI" in result["research"]
    assert "Test query about generative AI" in result["report"]

def test_research_api_endpoint() -> None:
    """
    Tests that the FastAPI '/research' POST endpoint returns
    the generated report with status 200 OK.
    """
    payload = {"query": "What is Retrieval-Augmented Generation?"}
    response = client.post("/research", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "report" in data
    assert "# Research Report: What is Retrieval-Augmented Generation?" in data["report"]

def test_research_api_empty_query() -> None:
    """
    Tests that passing an empty query triggers a 400 Bad Request error.
    """
    payload = {"query": "   "}
    response = client.post("/research", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Query cannot be empty."
