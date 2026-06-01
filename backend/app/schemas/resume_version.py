from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


class ChangeExplanation(BaseModel):
    section: str = Field(..., min_length=1)
    reason: str = Field(..., min_length=1)
    source: str = Field(..., min_length=1)
    uncertain: bool = False

    @field_validator("section", "reason", "source")
    @classmethod
    def text_must_not_be_blank(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("This field is required.")
        return normalized


class ResumeVersionGenerate(BaseModel):
    resume_profile_id: int
    project_ids: list[int] = Field(..., min_length=1)
    match_report_id: int
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
    def exactly_one_job_reference(self) -> "ResumeVersionGenerate":
        has_job_description = self.job_description_id is not None
        has_job_analysis = self.job_analysis_id is not None
        if has_job_description == has_job_analysis:
            raise ValueError("Provide exactly one of job_description_id or job_analysis_id.")
        return self


class ResumeWriterAIResult(BaseModel):
    markdown: str = Field(..., min_length=1)
    change_explanations: list[ChangeExplanation] = Field(default_factory=list)

    @field_validator("markdown")
    @classmethod
    def markdown_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Markdown content is required.")
        return value

    @field_validator("change_explanations", mode="before")
    @classmethod
    def normalize_change_explanations(cls, value: Any) -> Any:
        if value is None:
            return []
        return value


class ResumeVersionRead(BaseModel):
    id: int
    user_id: int
    resume_profile_id: int
    job_description_id: int | None
    match_report_id: int | None
    title: str
    version_type: str
    content_markdown: str
    generation_notes: str | None
    change_explanations: list[ChangeExplanation]
    model_name: str
    created_at: datetime
    updated_at: datetime
