from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.resume_profile import ResumeProfile
from app.schemas.resume_profile import ResumeProfileCreate


class ResumeProfileRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, *, user_id: int, payload: ResumeProfileCreate) -> ResumeProfile:
        resume_profile = ResumeProfile(
            user_id=user_id,
            title=payload.title,
            raw_markdown=payload.raw_markdown,
        )
        self.db.add(resume_profile)
        self.db.commit()
        self.db.refresh(resume_profile)
        return resume_profile

    def list_by_user(self, *, user_id: int) -> list[ResumeProfile]:
        statement = (
            select(ResumeProfile)
            .where(ResumeProfile.user_id == user_id)
            .order_by(ResumeProfile.created_at.desc())
        )
        return list(self.db.scalars(statement).all())
