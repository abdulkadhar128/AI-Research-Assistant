import os
os.environ["LLM_PROVIDER"] = "mock"

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
        "search_results": "",
        "research": "",
        "fact_checked_research": "",
        "analysis": "",
        "citations": "",
        "report": "",
        "review_feedback": "",
        "quality_score": 0.0
    }
    result = research_graph.invoke(initial_state)

    # Validate output keys
    assert "query" in result
    assert "plan" in result
    assert "search_results" in result
    assert "research" in result
    assert "fact_checked_research" in result
    assert "analysis" in result
    assert "report" in result
    assert "review_feedback" in result
    assert "citations" in result
    assert "quality_score" in result

    # Validate dynamic mock propagation
    assert "Test query about generative AI" in result["plan"]
    assert "Test query about generative AI" in result["search_results"]
    assert "Test query about generative AI" in result["research"]
    assert "Test query about generative AI" in result["fact_checked_research"]
    assert "Test query about generative AI" in result["report"]
    assert "Test query about generative AI" in result["review_feedback"]
    assert "Test query about generative AI" in result["citations"]
    assert result["quality_score"] == 9.2

def test_research_api_endpoint() -> None:
    """
    Tests that the FastAPI '/research' POST endpoint returns
    the generated report_id, report content, and quality score.
    """
    payload = {"query": "What is Retrieval-Augmented Generation?"}
    response = client.post("/research", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "report_id" in data
    assert "report" in data
    assert "quality_score" in data
    assert data["quality_score"] == 9.2

    # Assert content properties are verified
    assert "# Research Report: What is Retrieval-Augmented Generation?" in data["report"]
    assert "## 3. Search Results" in data["report"]
    assert "Source 1: Technical overview" in data["report"]
    assert "## 5. Fact Checked Findings" in data["report"]

def test_research_api_empty_query() -> None:
    """
    Tests that passing an empty query triggers a 400 Bad Request error.
    """
    payload = {"query": "   "}
    response = client.post("/research", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Query cannot be empty."

def test_get_reports_endpoint() -> None:
    """
    Tests retrieving all generated reports from database.
    """
    # Generate one report to ensure data exists
    client.post("/research", json={"query": "Test query for listing"})

    response = client.get("/reports")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "id" in data[0]
    assert "query" in data[0]
    assert "report" in data[0]
    assert "citations" in data[0]
    assert "quality_score" in data[0]

def test_get_report_by_id_endpoint() -> None:
    """
    Tests retrieving a specific report from database.
    """
    res = client.post("/research", json={"query": "Test query for single retrieval"})
    report_id = res.json()["report_id"]

    response = client.get(f"/reports/{report_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == report_id
    assert "Test query for single retrieval" in data["query"]

def test_delete_report_endpoint() -> None:
    """
    Tests deleting a report from database.
    """
    res = client.post("/research", json={"query": "Test query for deletion"})
    report_id = res.json()["report_id"]

    # Delete
    del_res = client.delete(f"/reports/{report_id}")
    assert del_res.status_code == 200
    assert del_res.json()["message"] == f"Report {report_id} successfully deleted"

    # Confirm it's gone
    get_res = client.get(f"/reports/{report_id}")
    assert get_res.status_code == 404

def test_get_report_not_found() -> None:
    """
    Tests that GET 404 is returned for non-existent report IDs.
    """
    response = client.get("/reports/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Report not found"

def test_delete_report_not_found() -> None:
    """
    Tests that DELETE 404 is returned for non-existent report IDs.
    """
    response = client.delete("/reports/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Report not found"

def test_export_report_pdf_endpoint() -> None:
    """
    Tests downloading a report as a PDF.
    """
    res = client.post("/research", json={"query": "Test query for PDF export"})
    report_id = res.json()["report_id"]

    response = client.get(f"/reports/{report_id}/pdf")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert f"attachment; filename=research_report_{report_id}.pdf" in response.headers["content-disposition"]
    # Check binary content is returned (PDF signature starts with %PDF)
    assert response.content.startswith(b"%PDF")

def test_export_report_pdf_not_found() -> None:
    """
    Tests downloading a non-existent report returns 404.
    """
    response = client.get("/reports/999999/pdf")
    assert response.status_code == 404
    assert response.json()["detail"] == "Report not found"
