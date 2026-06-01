from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.truth_check_result import TruthCheckResult


class TruthCheckRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        user_id: int,
        resume_version_id: int,
        overall_risk_level: str,
        risky_statements_json: str,
        safer_rewrites_json: str,
        missing_evidence_json: str,
        interview_risk_points_json: str,
        summary: str,
        raw_ai_output_json: str,
        model_name: str,
    ) -> TruthCheckResult:
        truth_check_result = TruthCheckResult(
            user_id=user_id,
            resume_version_id=resume_version_id,
            overall_risk_level=overall_risk_level,
            risky_statements_json=risky_statements_json,
            safer_rewrites_json=safer_rewrites_json,
            missing_evidence_json=missing_evidence_json,
            interview_risk_points_json=interview_risk_points_json,
            summary=summary,
            raw_ai_output_json=raw_ai_output_json,
            model_name=model_name,
        )
        self.db.add(truth_check_result)
        self.db.commit()
        self.db.refresh(truth_check_result)
        return truth_check_result

    def list_by_resume_version_for_user(self, *, resume_version_id: int, user_id: int) -> list[TruthCheckResult]:
        statement = (
            select(TruthCheckResult)
            .where(
                TruthCheckResult.resume_version_id == resume_version_id,
                TruthCheckResult.user_id == user_id,
            )
            .order_by(TruthCheckResult.created_at.desc())
        )
        return list(self.db.scalars(statement).all())
