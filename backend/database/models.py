from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.sql import func
from backend.database.connection import Base

class Report(Base):
    """
    SQLAlchemy model representing a saved research report.
    """
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(String, index=True)
    report = Column(Text)
    quality_score = Column(Float)
    review_feedback = Column(Text)
    citations = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
