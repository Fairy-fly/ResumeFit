from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.interview_question import InterviewQuestionResult


class InterviewQuestionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        user_id: int,
        resume_version_id: int,
        questions_json: str,
        summary: str,
        raw_ai_output_json: str,
        model_name: str,
    ) -> InterviewQuestionResult:
        interview_question_result = InterviewQuestionResult(
            user_id=user_id,
            resume_version_id=resume_version_id,
            questions_json=questions_json,
            summary=summary,
            raw_ai_output_json=raw_ai_output_json,
            model_name=model_name,
        )
        self.db.add(interview_question_result)
        self.db.commit()
        self.db.refresh(interview_question_result)
        return interview_question_result

    def list_by_resume_version_for_user(
        self,
        *,
        resume_version_id: int,
        user_id: int,
    ) -> list[InterviewQuestionResult]:
        statement = (
            select(InterviewQuestionResult)
            .where(
                InterviewQuestionResult.resume_version_id == resume_version_id,
                InterviewQuestionResult.user_id == user_id,
            )
            .order_by(InterviewQuestionResult.created_at.desc())
        )
        return list(self.db.scalars(statement).all())
