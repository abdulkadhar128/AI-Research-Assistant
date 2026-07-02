from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


# =========================
# Report Schemas
# =========================

class ReportBase(BaseModel):
    query: str
    report: str
    quality_score: float
    review_feedback: str
    citations: Optional[str] = ""
    generation_time: Optional[float] = None
    accuracy_score: Optional[float] = None
    coverage_score: Optional[float] = None
    clarity_score: Optional[float] = None
    citations_score: Optional[float] = None


class ReportCreate(ReportBase):
    pass


class Report(ReportBase):
    id: int
    created_at: datetime
    generation_time: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)