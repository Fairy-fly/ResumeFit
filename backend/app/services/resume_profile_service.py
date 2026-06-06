from sqlalchemy.orm import Session

from app.models.resume_profile import ResumeProfile
from app.repositories.resume_profile_repository import ResumeProfileRepository
from app.schemas.resume_profile import ResumeProfileCreate


class ResumeProfileService:
    def __init__(self, db: Session) -> None:
        self.repository = ResumeProfileRepository(db)

    def create_resume_profile(self, payload: ResumeProfileCreate, *, user_id: int) -> ResumeProfile:
        return self.repository.create(user_id=user_id, payload=payload)

    def list_resume_profiles(self, *, user_id: int) -> list[ResumeProfile]:
        return self.repository.list_by_user(user_id=user_id)
