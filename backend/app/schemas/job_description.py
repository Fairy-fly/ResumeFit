from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class JobDescriptionCreate(BaseModel):
    company_name: str = Field(..., min_length=1)
    job_title: str = Field(..., min_length=1)
    raw_text: str = Field(..., min_length=1)

    @field_validator("company_name", "job_title", "raw_text")
    @classmethod
    def required_text_must_not_be_blank(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("This field is required.")
        return normalized


class JobDescriptionRead(BaseModel):
    id: int
    user_id: int
    company_name: str | None
    job_title: str
    raw_text: str
    status: str
    created_at: datetime
    updated_at: datetime
