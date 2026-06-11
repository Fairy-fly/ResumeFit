from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.usage import AIUsageSummaryRead


class AccountUpdate(BaseModel):
    display_name: str = Field(..., min_length=1, max_length=50)

    @field_validator("display_name")
    @classmethod
    def display_name_must_not_be_blank(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Display name is required.")
        return normalized


class AccountRead(BaseModel):
    id: int
    email: str | None
    display_name: str | None
    role: str
    status: str
    created_at: datetime
    updated_at: datetime
    usage_summary: AIUsageSummaryRead

    model_config = ConfigDict(from_attributes=True)
