from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

QuestionDifficulty = Literal["easy", "medium", "hard"]


class InterviewQuestionCreate(BaseModel):
    resume_version_id: int = Field(..., gt=0)


class InterviewQuestionItem(BaseModel):
    question: str = Field(..., min_length=1)
    reason: str = Field(..., min_length=1)
    related_resume_section: str = Field(..., min_length=1)
    difficulty: QuestionDifficulty
    suggested_answer: str = Field(..., min_length=1)
    answer_strategy: str = Field(..., min_length=1)
    risk_reminder: str = Field(..., min_length=1)

    @field_validator(
        "question",
        "reason",
        "related_resume_section",
        "suggested_answer",
        "answer_strategy",
        "risk_reminder",
    )
    @classmethod
    def text_must_not_be_blank(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("This field is required.")
        return normalized


class InterviewQuestionAIResult(BaseModel):
    questions: list[InterviewQuestionItem] = Field(default_factory=list)
    summary: str = Field(..., min_length=1)

    @field_validator("questions", mode="before")
    @classmethod
    def normalize_questions(cls, value: Any) -> Any:
        if value is None:
            return []
        return value

    @field_validator("summary")
    @classmethod
    def summary_must_not_be_blank(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Summary is required.")
        return normalized


class InterviewQuestionResultRead(BaseModel):
    id: int
    user_id: int
    resume_version_id: int
    questions: list[InterviewQuestionItem]
    summary: str
    model_name: str
    created_at: datetime
