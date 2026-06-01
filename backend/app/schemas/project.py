from datetime import datetime
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1)
    project_type: str = Field(..., min_length=1)
    role: str = Field(..., min_length=1)
    tech_stack: list[str] = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    user_contribution: str = Field(..., min_length=1)
    work_url: str | None = None

    @field_validator("name", "project_type", "role", "description", "user_contribution")
    @classmethod
    def required_text_must_not_be_blank(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("This field is required.")
        return normalized

    @field_validator("tech_stack")
    @classmethod
    def tech_stack_must_not_be_empty(cls, value: list[str]) -> list[str]:
        normalized = [item.strip() for item in value]
        if not normalized or any(not item for item in normalized):
            raise ValueError("Tech stack must contain non-empty items.")
        return normalized

    @field_validator("work_url")
    @classmethod
    def work_url_must_be_url(cls, value: str | None) -> str | None:
        if value is None:
            return None

        normalized = value.strip()
        if not normalized:
            return None

        parsed = urlparse(normalized)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("Work URL must be a valid HTTP or HTTPS URL.")
        return normalized


class ProjectRead(BaseModel):
    id: int
    user_id: int
    name: str
    project_type: str
    role: str
    tech_stack: list[str]
    description: str
    user_contribution: str
    work_url: str | None
    created_at: datetime
    updated_at: datetime
