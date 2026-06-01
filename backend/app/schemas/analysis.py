from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


class JobAnalysisAIResult(BaseModel):
    job_title: str = "信息不足"
    job_type: str = "信息不足"
    required_skills: list[str] = Field(default_factory=list)
    bonus_skills: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    resume_focus_suggestions: list[str] = Field(default_factory=list)

    @field_validator("job_title", "job_type", mode="before")
    @classmethod
    def normalize_text(cls, value: Any) -> str:
        if value is None:
            return "信息不足"
        normalized = str(value).strip()
        return normalized or "信息不足"

    @field_validator(
        "required_skills",
        "bonus_skills",
        "responsibilities",
        "keywords",
        "resume_focus_suggestions",
        mode="before",
    )
    @classmethod
    def normalize_string_list(cls, value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            normalized = value.strip()
            return [normalized] if normalized else []
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        normalized = str(value).strip()
        return [normalized] if normalized else []


class JobAnalysisRead(BaseModel):
    id: int
    job_description_id: int
    job_title: str
    job_type: str
    required_skills: list[str]
    bonus_skills: list[str]
    responsibilities: list[str]
    keywords: list[str]
    resume_focus_suggestions: list[str]
    model_name: str
    created_at: datetime
    updated_at: datetime
