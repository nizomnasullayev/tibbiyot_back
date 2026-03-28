from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# ── Progress ─────────────────────────────────────────────────

class LearnEntryRequest(BaseModel):
    entry_uid: str

class UserProgressResponse(BaseModel):
    uid: str
    topic_uid: str
    learned_entries: list[str]
    progress: float
    topic_test_passed: bool

    class Config:
        from_attributes = True


# ── Test Questions ────────────────────────────────────────────

class TestQuestion(BaseModel):
    id: str
    prompt: str
    correct_answer: str
    options: list[str]


# ── Test Submission ───────────────────────────────────────────

class TestAnswer(BaseModel):
    question_id: str
    answer: str

class TopicTestSubmit(BaseModel):
    topic_uid: str
    answers: list[TestAnswer]

class FinalTestSubmit(BaseModel):
    answers: list[TestAnswer]

class TestResultResponse(BaseModel):
    score: int
    total: int
    passed: bool
    accuracy: float
    message: str


# ── Certificate ───────────────────────────────────────────────

class CertificateResponse(BaseModel):
    uid: str
    certificate_number: int
    accuracy: float
    certificate_url: Optional[str]
    issued_at: datetime

    class Config:
        from_attributes = True