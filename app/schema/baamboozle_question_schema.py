from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field
from pydantic import field_validator

ALLOWED_CATEGORIES = {50, 100, 150, 200, 250, 300, 350, 400, 450, 500}


class BaamboozleQuestionBase(BaseModel):
    category: int
    question: str = Field(min_length=1)
    answer: str = Field(min_length=1)

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: int) -> int:
        if value not in ALLOWED_CATEGORIES:
            raise ValueError("category must be one of: 50,100,150,...,500")
        return value


class BaamboozleQuestionCreate(BaamboozleQuestionBase):
    pass


class BaamboozleQuestionUpdate(BaseModel):
    category: int | None = None
    question: str | None = Field(default=None, min_length=1)
    answer: str | None = Field(default=None, min_length=1)

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: int | None) -> int | None:
        if value is not None and value not in ALLOWED_CATEGORIES:
            raise ValueError("category must be one of: 50,100,150,...,500")
        return value


class BaamboozleQuestionOut(BaamboozleQuestionBase):
    id: UUID
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BaamboozleAIGenerateRequest(BaseModel):
    subject: str = Field(min_length=1, max_length=200)
    topic_description: str = Field(
        min_length=10,
        description="What students were taught and what questions should be about.",
    )
    number_of_questions: int = Field(default=10, ge=1, le=30)
    categories: list[int] | None = Field(
        default=None,
        description="Optional list of point categories to assign (50..500).",
    )
    difficulty_notes: str | None = Field(
        default=None,
        max_length=1000,
        description="Optional instructions like easy/medium/hard balance.",
    )
    language: str = Field(
        default="uz",
        description="Output language for generated questions, e.g. uz or en.",
    )

    @field_validator("categories")
    @classmethod
    def validate_categories(cls, value: list[int] | None) -> list[int] | None:
        if value is None:
            return value
        if not value:
            raise ValueError("categories cannot be empty")
        invalid = [category for category in value if category not in ALLOWED_CATEGORIES]
        if invalid:
            raise ValueError("categories must only include: 50,100,150,...,500")
        return value

    @field_validator("language")
    @classmethod
    def validate_language(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in {"uz", "en"}:
            raise ValueError("language must be 'uz' or 'en'")
        return normalized


class BaamboozleAIGenerateResponse(BaseModel):
    created_questions: list[BaamboozleQuestionOut]
