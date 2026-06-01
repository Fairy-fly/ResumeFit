from sqlalchemy.orm import Session

from app.models.resume_profile import ResumeProfile
from app.repositories.resume_profile_repository import ResumeProfileRepository
from app.schemas.resume_profile import ResumeProfileCreate

DEFAULT_USER_ID = 1


class ResumeProfileService:
    def __init__(self, db: Session) -> None:
        self.repository = ResumeProfileRepository(db)

    def create_resume_profile(self, payload: ResumeProfileCreate) -> ResumeProfile:
        return self.repository.create(user_id=DEFAULT_USER_ID, payload=payload)

    def list_resume_profiles(self) -> list[ResumeProfile]:
        return self.repository.list_by_user(user_id=DEFAULT_USER_ID)
