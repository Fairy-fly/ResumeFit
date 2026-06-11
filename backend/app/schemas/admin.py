from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.usage import AIUsageFeatureCountRead, AIUsageLogRead, AIUsageSummaryRead


class AdminUserUsageOverviewRead(BaseModel):
    monthly_used: int
    monthly_quota: int
    monthly_remaining: int
    total_call_count: int


class AdminUserListItemRead(BaseModel):
    id: int
    email: str | None
    display_name: str | None
    role: str
    status: str
    created_at: datetime
    updated_at: datetime
    usage: AdminUserUsageOverviewRead


class AdminUserListRead(BaseModel):
    items: list[AdminUserListItemRead]
    total: int
    page: int
    page_size: int


class AdminUserDetailRead(BaseModel):
    id: int
    email: str | None
    display_name: str | None
    role: str
    status: str
    created_at: datetime
    updated_at: datetime
    usage_summary: AIUsageSummaryRead


class AdminUserStatusUpdate(BaseModel):
    status: Literal["active", "disabled"] = Field(...)


class AdminGlobalUsageSummaryRead(BaseModel):
    total_call_count: int
    monthly_call_count: int
    monthly_success_count: int
    monthly_failure_count: int
    feature_counts: list[AIUsageFeatureCountRead]
    recent_calls: list[AIUsageLogRead]
