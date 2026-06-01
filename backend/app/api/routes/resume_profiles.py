from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.resume_profile import ResumeProfileCreate, ResumeProfileRead
from app.services.resume_profile_service import ResumeProfileService

router = APIRouter(prefix="/resume-profiles", tags=["resume profiles"])


@router.post("", response_model=ResumeProfileRead, status_code=status.HTTP_201_CREATED)
def create_resume_profile(
    payload: ResumeProfileCreate,
    db: Session = Depends(get_db),
) -> ResumeProfileRead:
    service = ResumeProfileService(db)
    return service.create_resume_profile(payload)


@router.get("", response_model=list[ResumeProfileRead])
def list_resume_profiles(db: Session = Depends(get_db)) -> list[ResumeProfileRead]:
    service = ResumeProfileService(db)
    return service.list_resume_profiles()
