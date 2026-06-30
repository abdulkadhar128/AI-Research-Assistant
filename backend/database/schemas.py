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


class ReportCreate(ReportBase):
    pass


class Report(ReportBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)