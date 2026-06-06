from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.resume_profile import ResumeProfileCreate, ResumeProfileRead
from app.services.resume_profile_service import ResumeProfileService

router = APIRouter(prefix="/resume-profiles", tags=["resume profiles"])


@router.post("", response_model=ResumeProfileRead, status_code=status.HTTP_201_CREATED)
def create_resume_profile(
    payload: ResumeProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResumeProfileRead:
    service = ResumeProfileService(db)
    return service.create_resume_profile(payload, user_id=current_user.id)


@router.get("", response_model=list[ResumeProfileRead])
def list_resume_profiles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ResumeProfileRead]:
    service = ResumeProfileService(db)
    return service.list_resume_profiles(user_id=current_user.id)
