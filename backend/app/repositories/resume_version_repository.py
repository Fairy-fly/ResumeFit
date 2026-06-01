from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.resume_version import ResumeVersion


class ResumeVersionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        user_id: int,
        resume_profile_id: int,
        job_description_id: int,
        match_report_id: int,
        title: str,
        version_type: str,
        content_markdown: str,
        generation_notes: str,
        change_explanations_json: str,
        raw_ai_output_json: str,
        model_name: str,
    ) -> ResumeVersion:
        resume_version = ResumeVersion(
            user_id=user_id,
            resume_profile_id=resume_profile_id,
            job_description_id=job_description_id,
            match_report_id=match_report_id,
            title=title,
            version_type=version_type,
            content_markdown=content_markdown,
            generation_notes=generation_notes,
            change_explanations_json=change_explanations_json,
            risk_report_json=None,
            raw_ai_output_json=raw_ai_output_json,
            model_name=model_name,
        )
        self.db.add(resume_version)
        self.db.commit()
        self.db.refresh(resume_version)
        return resume_version

    def get_by_id_for_user(self, *, resume_version_id: int, user_id: int) -> ResumeVersion | None:
        statement = select(ResumeVersion).where(
            ResumeVersion.id == resume_version_id,
            ResumeVersion.user_id == user_id,
        )
        return self.db.scalar(statement)

    def list_by_user(self, *, user_id: int) -> list[ResumeVersion]:
        statement = (
            select(ResumeVersion)
            .where(ResumeVersion.user_id == user_id)
            .order_by(ResumeVersion.created_at.desc())
        )
        return list(self.db.scalars(statement).all())
