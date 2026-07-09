from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, TypeDecorator, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database.connection import Base

class UTCDateTime(TypeDecorator):
    """
    SQLAlchemy TypeDecorator to ensure datetime objects are always stored and
    retrieved as timezone-aware UTC datetime objects.
    """
    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            if value.tzinfo is None:
                value = value.replace(tzinfo=timezone.utc)
            else:
                value = value.astimezone(timezone.utc)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            if value.tzinfo is None:
                value = value.replace(tzinfo=timezone.utc)
            else:
                value = value.astimezone(timezone.utc)
        return value

class User(Base):
    """
    SQLAlchemy model representing an application User.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(UTCDateTime, default=lambda: datetime.now(timezone.utc), server_default=func.now())

    reports = relationship("Report", back_populates="user", cascade="all, delete-orphan")

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
    generation_time = Column(Float, nullable=True)
    created_at = Column(UTCDateTime, default=lambda: datetime.now(timezone.utc), server_default=func.now())

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="reports")

