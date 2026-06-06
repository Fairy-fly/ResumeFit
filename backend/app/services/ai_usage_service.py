from collections.abc import Callable
from datetime import datetime
from typing import Any, TypeVar

from app.ai.client import AIClient
from app.core.config import settings
from app.repositories.ai_usage_repository import AIUsageRepository
from app.schemas.usage import AIUsageFeatureCountRead, AIUsageLogRead, AIUsageSummaryRead

T = TypeVar("T")

MAX_ERROR_MESSAGE_LENGTH = 1000


class AIQuotaExceededError(RuntimeError):
    pass


class AIUsageService:
    def __init__(self, repository: AIUsageRepository) -> None:
        self.repository = repository

    def run_with_logging(
        self,
        *,
        user_id: int,
        feature_type: str,
        ai_client: AIClient,
        call: Callable[[], T],
    ) -> T:
        self.ensure_quota_available(user_id=user_id)

        try:
            result = call()
        except Exception as exc:
            self.record_failure(
                user_id=user_id,
                feature_type=feature_type,
                model_name=ai_client.model_name,
                error_message=str(exc),
            )
            raise

        self.record_success(
            user_id=user_id,
            feature_type=feature_type,
            model_name=ai_client.model_name,
        )
        return result

    def ensure_quota_available(self, *, user_id: int) -> None:
        quota = settings.ai_monthly_call_limit
        if quota <= 0:
            return

        monthly_used = self.repository.count_by_user_since(user_id=user_id, since=self._month_start_utc())
        if monthly_used >= quota:
            raise AIQuotaExceededError("Monthly AI quota exceeded.")

    def record_success(
        self,
        *,
        user_id: int,
        feature_type: str,
        model_name: str,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
        total_tokens: int | None = None,
    ) -> None:
        self.repository.create(
            user_id=user_id,
            feature_type=feature_type,
            model_name=model_name,
            status="success",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            estimated_cost=self._estimate_cost(input_tokens=input_tokens, output_tokens=output_tokens),
        )

    def record_failure(
        self,
        *,
        user_id: int,
        feature_type: str,
        model_name: str,
        error_message: str,
    ) -> None:
        self.repository.create(
            user_id=user_id,
            feature_type=feature_type,
            model_name=model_name,
            status="failed",
            error_message=error_message[:MAX_ERROR_MESSAGE_LENGTH],
        )

    def summary(self, *, user_id: int) -> AIUsageSummaryRead:
        month_start = self._month_start_utc()
        monthly_quota = settings.ai_monthly_call_limit
        monthly_used = self.repository.count_by_user_since(user_id=user_id, since=month_start)
        monthly_remaining = max(monthly_quota - monthly_used, 0) if monthly_quota > 0 else 0
        return AIUsageSummaryRead(
            monthly_quota=monthly_quota,
            monthly_used=monthly_used,
            monthly_remaining=monthly_remaining,
            total_call_count=self.repository.count_by_user(user_id=user_id),
            monthly_success_count=self.repository.count_by_status_since(
                user_id=user_id,
                status="success",
                since=month_start,
            ),
            monthly_failure_count=self.repository.count_by_status_since(
                user_id=user_id,
                status="failed",
                since=month_start,
            ),
            feature_counts=[
                AIUsageFeatureCountRead(
                    feature_type=feature_type,
                    count=count,
                    success_count=success_count,
                    failure_count=failure_count,
                )
                for feature_type, count, success_count, failure_count in self.repository.feature_counts_since(
                    user_id=user_id,
                    since=month_start,
                )
            ],
            recent_calls=[self._to_log_read_model(usage_log) for usage_log in self.repository.recent_by_user(user_id=user_id)],
        )

    def _estimate_cost(self, *, input_tokens: int | None, output_tokens: int | None) -> float | None:
        if input_tokens is None or output_tokens is None:
            return None
        input_cost = (input_tokens / 1000) * settings.ai_input_token_price_per_1k
        output_cost = (output_tokens / 1000) * settings.ai_output_token_price_per_1k
        return input_cost + output_cost

    def _to_log_read_model(self, usage_log: Any) -> AIUsageLogRead:
        return AIUsageLogRead(
            id=usage_log.id,
            feature_type=usage_log.feature_type,
            model_name=usage_log.model_name,
            status=usage_log.status,
            error_message=usage_log.error_message,
            input_tokens=usage_log.input_tokens,
            output_tokens=usage_log.output_tokens,
            total_tokens=usage_log.total_tokens,
            estimated_cost=usage_log.estimated_cost,
            created_at=usage_log.created_at,
        )

    def _month_start_utc(self) -> datetime:
        now = datetime.utcnow()
        return datetime(year=now.year, month=now.month, day=1)
