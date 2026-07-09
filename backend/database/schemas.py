from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from typing import Optional, List


# =========================
# User & Auth Schemas
# =========================

class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


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
    user_id: Optional[int] = None


class Report(ReportBase):
    id: int
    user_id: int
    created_at: datetime
    generation_time: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)