from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


class MatchReportCreate(BaseModel):
    resume_profile_id: int
    project_ids: list[int] = Field(..., min_length=1)
    job_description_id: int | None = None
    job_analysis_id: int | None = None

    @field_validator("project_ids")
    @classmethod
    def project_ids_must_be_unique(cls, value: list[int]) -> list[int]:
        if any(project_id <= 0 for project_id in value):
            raise ValueError("Project IDs must be positive integers.")
        if len(set(value)) != len(value):
            raise ValueError("Project IDs must be unique.")
        return value

    @model_validator(mode="after")
    def exactly_one_job_reference(self) -> "MatchReportCreate":
        has_job_description = self.job_description_id is not None
        has_job_analysis = self.job_analysis_id is not None
        if has_job_description == has_job_analysis:
            raise ValueError("Provide exactly one of job_description_id or job_analysis_id.")
        return self


class MatchReportAIResult(BaseModel):
    score: int = Field(..., ge=0, le=100)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    recommended_changes: list[str] = Field(default_factory=list)
    truthfulness_warnings: list[str] = Field(default_factory=list)

    @field_validator(
        "strengths",
        "weaknesses",
        "missing_keywords",
        "recommended_changes",
        "truthfulness_warnings",
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


class MatchReportRead(BaseModel):
    id: int
    user_id: int
    resume_profile_id: int
    project_ids: list[int]
    job_description_id: int
    job_analysis_id: int
    score: int
    strengths: list[str]
    weaknesses: list[str]
    missing_keywords: list[str]
    recommended_changes: list[str]
    truthfulness_warnings: list[str]
    model_name: str
    created_at: datetime
    updated_at: datetime
