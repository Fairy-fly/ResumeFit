from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ResumeProfileCreate(BaseModel):
    title: str = Field(..., min_length=1)
    raw_markdown: str = Field(..., min_length=1)

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value: str) -> str:
        title = value.strip()
        if not title:
            raise ValueError("Resume title is required.")
        return title

    @field_validator("raw_markdown")
    @classmethod
    def raw_markdown_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Resume body is required.")
        return value


class ResumeProfileRead(BaseModel):
    id: int
    user_id: int
    title: str
    raw_markdown: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
