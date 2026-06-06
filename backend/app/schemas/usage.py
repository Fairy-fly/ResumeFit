from datetime import datetime

from pydantic import BaseModel


class AIUsageFeatureCountRead(BaseModel):
    feature_type: str
    count: int
    success_count: int
    failure_count: int


class AIUsageLogRead(BaseModel):
    id: int
    feature_type: str
    model_name: str
    status: str
    error_message: str | None
    input_tokens: int | None
    output_tokens: int | None
    total_tokens: int | None
    estimated_cost: float | None
    created_at: datetime


class AIUsageSummaryRead(BaseModel):
    monthly_quota: int
    monthly_used: int
    monthly_remaining: int
    total_call_count: int
    monthly_success_count: int
    monthly_failure_count: int
    feature_counts: list[AIUsageFeatureCountRead]
    recent_calls: list[AIUsageLogRead]
