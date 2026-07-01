from sqlalchemy.orm import Session
from backend.database import models, schemas

# --- Report CRUD ---
def create_report(db: Session, report: schemas.ReportCreate):
    db_report = models.Report(
        query=report.query,
        report=report.report,
        quality_score=report.quality_score,
        review_feedback=report.review_feedback,
        citations=report.citations,
        generation_time=report.generation_time
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report

def get_reports(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Report).offset(skip).limit(limit).all()

def get_report(db: Session, report_id: int):
    """
    Retrieve a single report by its primary key ID.
    """
    return db.query(models.Report).filter(models.Report.id == report_id).first()

def delete_report(db: Session, report_id: int):
    db_report = get_report(db, report_id)
    if db_report:
        db.delete(db_report)
        db.commit()
        return True
    return False
