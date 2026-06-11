from datetime import datetime

from app.models.ai_usage_log import AIUsageLog
from app.models.user import User
from app.repositories.ai_usage_repository import AIUsageRepository
from app.repositories.user_repository import UserRepository
from app.schemas.admin import (
    AdminGlobalUsageSummaryRead,
    AdminUserDetailRead,
    AdminUserListItemRead,
    AdminUserListRead,
    AdminUserUsageOverviewRead,
)
from app.schemas.usage import AIUsageFeatureCountRead, AIUsageLogRead
from app.services.ai_usage_service import AIUsageService


class AdminResourceNotFoundError(ValueError):
    pass


class AdminOperationError(ValueError):
    pass


class AdminService:
    def __init__(self, *, user_repository: UserRepository, ai_usage_repository: AIUsageRepository) -> None:
        self.user_repository = user_repository
        self.ai_usage_repository = ai_usage_repository
        self.ai_usage_service = AIUsageService(ai_usage_repository)

    def list_users(self, *, page: int, page_size: int, search: str | None = None) -> AdminUserListRead:
        normalized_search = search.strip() if search else None
        total = self.user_repository.count(search=normalized_search)
        users = self.user_repository.list_paginated(page=page, page_size=page_size, search=normalized_search)
        return AdminUserListRead(
            items=[self._to_user_list_item(user) for user in users],
            total=total,
            page=page,
            page_size=page_size,
        )

    def get_user_detail(self, *, user_id: int) -> AdminUserDetailRead:
        user = self.user_repository.get_by_id(user_id=user_id)
        if user is None:
            raise AdminResourceNotFoundError("User was not found.")

        return AdminUserDetailRead(
            id=user.id,
            email=user.email,
            display_name=user.display_name,
            role=user.role,
            status=user.status,
            created_at=user.created_at,
            updated_at=user.updated_at,
            usage_summary=self.ai_usage_service.summary(user_id=user.id),
        )

    def update_user_status(self, *, current_admin: User, user_id: int, status: str) -> AdminUserDetailRead:
        user = self.user_repository.get_by_id(user_id=user_id)
        if user is None:
            raise AdminResourceNotFoundError("User was not found.")

        if user.id == current_admin.id and status == "disabled":
            raise AdminOperationError("Admin cannot disable own account.")

        updated_user = self.user_repository.update_status(user=user, status=status)
        return self.get_user_detail(user_id=updated_user.id)

    def global_usage_summary(self) -> AdminGlobalUsageSummaryRead:
        month_start = self._month_start_utc()
        return AdminGlobalUsageSummaryRead(
            total_call_count=self.ai_usage_repository.count_all(),
            monthly_call_count=self.ai_usage_repository.count_all_since(since=month_start),
            monthly_success_count=self.ai_usage_repository.count_all_by_status_since(
                status="success",
                since=month_start,
            ),
            monthly_failure_count=self.ai_usage_repository.count_all_by_status_since(
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
                for feature_type, count, success_count, failure_count in self.ai_usage_repository.feature_counts_all_since(
                    since=month_start,
                )
            ],
            recent_calls=[self._to_log_read_model(usage_log) for usage_log in self.ai_usage_repository.recent_all()],
        )

    def _to_user_list_item(self, user: User) -> AdminUserListItemRead:
        summary = self.ai_usage_service.summary(user_id=user.id)
        return AdminUserListItemRead(
            id=user.id,
            email=user.email,
            display_name=user.display_name,
            role=user.role,
            status=user.status,
            created_at=user.created_at,
            updated_at=user.updated_at,
            usage=AdminUserUsageOverviewRead(
                monthly_used=summary.monthly_used,
                monthly_quota=summary.monthly_quota,
                monthly_remaining=summary.monthly_remaining,
                total_call_count=summary.total_call_count,
            ),
        )

    def _to_log_read_model(self, usage_log: AIUsageLog) -> AIUsageLogRead:
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
