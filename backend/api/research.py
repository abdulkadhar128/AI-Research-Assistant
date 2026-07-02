from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import time

from backend.graph.workflow import research_graph
from backend.database.connection import get_db
from backend.database import crud, schemas, models
from backend.services.pdf_service import PDFService

router = APIRouter()


class ResearchRequest(BaseModel):
    query: str

    class Config:
        json_schema_extra = {
            "example": {
                "query": "Explain About Machine Learning"
            }
        }


class ResearchResponse(BaseModel):
    report_id: Optional[int]           = None
    report: Optional[str]              = None
    quality_score: Optional[float]     = None
    generation_time: Optional[float]   = None
    clarification_needed: bool         = False
    clarification_prompt: Optional[str] = None
    interpretations: Optional[List[str]] = None


@router.post("/research")
async def run_research(request: ResearchRequest, db: Session = Depends(get_db)):
    """
    POST /research — invoke the LangGraph multi-agent research workflow.
    Streams progress updates using Server-Sent Events (SSE).
    """
    topic = request.query.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    async def event_generator():
        t0 = time.time()
        initial_state = {
            "topic": topic,
            "confidence":            1.0,
            "clarification_needed":  False,
            "clarification_prompt":  "",
            "interpretations":       [],
            "plan":             "",
            "sources":          [],
            "verified_sources": [],
            "report":           "",
            "score":            0.0,
            "feedback":         "",
            "accuracy_score":   0.0,
            "coverage_score":   0.0,
            "clarity_score":    0.0,
            "citations_score":  0.0,
            "citations":        "",
            "generation_time":  0.0,
            "revision_count":   0,
        }

        yield f"data: {json.dumps({'status': 'Analyzing Intent...'})}\n\n"
        import asyncio
        await asyncio.sleep(0) # Force flush

        final_state = initial_state.copy()
        try:
            node_status_map = {
                "intent_analyzer": "Planning & Searching...", 
                "planner": "Searching...", # Planner and Search are parallel
                "search": "Verifying Sources...",
                "verify": "Writing...",
                "writer": "Reviewing...",
                "reviewer": "Finalizing..."
            }
            
            seen_nodes = set()
            
            async for event in research_graph.astream(initial_state):
                for node_name, node_state in event.items():
                    # Update final state with the latest changes from the node
                    final_state.update(node_state)
                    seen_nodes.add(node_name)
                    
                    if node_name == "intent_analyzer" and final_state.get("clarification_needed"):
                        # Stop early
                        break
                    
                    # Compute dynamic status for parallel nodes
                    if node_name in ["planner", "search"]:
                        if "planner" in seen_nodes and "search" in seen_nodes:
                            yield f"data: {json.dumps({'status': 'Verifying Sources...'})}\n\n"
                            await asyncio.sleep(0)
                    elif node_name in node_status_map:
                        yield f"data: {json.dumps({'status': node_status_map[node_name]})}\n\n"
                        await asyncio.sleep(0)
                        
            generation_time = round(time.time() - t0, 2)

            if final_state.get("clarification_needed", False):
                yield f"data: {json.dumps({'status': 'complete', 'data': {'clarification_needed': True, 'clarification_prompt': final_state.get('clarification_prompt'), 'interpretations': final_state.get('interpretations')}})}\n\n"
                return

            report          = final_state.get("report", "")
            quality_score   = final_state.get("score", 0.0)
            review_feedback = final_state.get("feedback", "")
            citations       = final_state.get("citations", "")
            
            if not report:
                yield f"data: {json.dumps({'status': 'error', 'detail': 'No report generated'})}\n\n"
                return

            # Save to DB (Needs to run in a thread since it's synchronous)
            def save_to_db():
                report_in = schemas.ReportCreate(
                    query=topic,
                    report=report,
                    quality_score=quality_score,
                    review_feedback=review_feedback,
                    citations=citations,
                    generation_time=generation_time,
                    accuracy_score=final_state.get("accuracy_score", 0.0),
                    coverage_score=final_state.get("coverage_score", 0.0),
                    clarity_score=final_state.get("clarity_score", 0.0),
                    citations_score=final_state.get("citations_score", 0.0),
                )
                return crud.create_report(db, report=report_in)
                
            db_report = await asyncio.to_thread(save_to_db)

            yield f"data: {json.dumps({'status': 'complete', 'data': {'report_id': db_report.id, 'report': db_report.report, 'quality_score': db_report.quality_score, 'generation_time': generation_time}})}\n\n"

        except Exception as e:
            print(f"[API] WORKFLOW ERROR: {e}")
            yield f"data: {json.dumps({'status': 'error', 'detail': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/reports", response_model=List[schemas.Report])
def get_reports(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Return a paginated list of all research reports."""
    return crud.get_reports(db, skip=skip, limit=limit)


@router.get("/reports/{report_id}", response_model=schemas.Report)
def get_report(report_id: int, db: Session = Depends(get_db)):
    """Return details of a single research report by ID."""
    db_report = crud.get_report(db, report_id=report_id)
    if not db_report:
        raise HTTPException(status_code=404, detail="Report not found")
    return db_report


@router.delete("/reports/{report_id}")
def delete_report(report_id: int, db: Session = Depends(get_db)):
    """Delete a research report by ID."""
    success = crud.delete_report(db, report_id=report_id)
    if not success:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"message": f"Report {report_id} successfully deleted"}


@router.get("/reports/{report_id}/pdf")
def export_report_pdf(report_id: int, db: Session = Depends(get_db)):
    """Return a downloadable PDF for the specified report."""
    db_report = crud.get_report(db, report_id=report_id)
    if not db_report:
        raise HTTPException(status_code=404, detail="Report not found")

    try:
        pdf_buffer = PDFService.generate_report_pdf(db_report)
        filename   = f"research_report_{report_id}.pdf"
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate PDF for report {report_id}: {str(e)}"
        )
