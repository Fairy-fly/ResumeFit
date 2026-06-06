from datetime import datetime

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models.ai_usage_log import AIUsageLog


class AIUsageRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        user_id: int,
        feature_type: str,
        model_name: str,
        status: str,
        error_message: str | None = None,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
        total_tokens: int | None = None,
        estimated_cost: float | None = None,
    ) -> AIUsageLog:
        usage_log = AIUsageLog(
            user_id=user_id,
            feature_type=feature_type,
            model_name=model_name,
            status=status,
            error_message=error_message,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            estimated_cost=estimated_cost,
        )
        self.db.add(usage_log)
        self.db.commit()
        self.db.refresh(usage_log)
        return usage_log

    def count_by_user(self, *, user_id: int) -> int:
        statement = select(func.count()).select_from(AIUsageLog).where(AIUsageLog.user_id == user_id)
        return int(self.db.scalar(statement) or 0)

    def count_by_user_since(self, *, user_id: int, since: datetime) -> int:
        statement = (
            select(func.count())
            .select_from(AIUsageLog)
            .where(AIUsageLog.user_id == user_id, AIUsageLog.created_at >= since)
        )
        return int(self.db.scalar(statement) or 0)

    def count_by_status_since(self, *, user_id: int, status: str, since: datetime) -> int:
        statement = (
            select(func.count())
            .select_from(AIUsageLog)
            .where(AIUsageLog.user_id == user_id, AIUsageLog.status == status, AIUsageLog.created_at >= since)
        )
        return int(self.db.scalar(statement) or 0)

    def feature_counts_since(self, *, user_id: int, since: datetime) -> list[tuple[str, int, int, int]]:
        statement = (
            select(
                AIUsageLog.feature_type,
                func.count().label("count"),
                func.sum(case((AIUsageLog.status == "success", 1), else_=0)).label("success_count"),
                func.sum(case((AIUsageLog.status == "failed", 1), else_=0)).label("failure_count"),
            )
            .where(AIUsageLog.user_id == user_id, AIUsageLog.created_at >= since)
            .group_by(AIUsageLog.feature_type)
            .order_by(AIUsageLog.feature_type.asc())
        )
        return [
            (str(feature_type), int(count or 0), int(success_count or 0), int(failure_count or 0))
            for feature_type, count, success_count, failure_count in self.db.execute(statement).all()
        ]

    def recent_by_user(self, *, user_id: int, limit: int = 10) -> list[AIUsageLog]:
        statement = (
            select(AIUsageLog)
            .where(AIUsageLog.user_id == user_id)
            .order_by(AIUsageLog.created_at.desc())
            .limit(limit)
        )
        return list(self.db.scalars(statement).all())
