from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.ai.client import AIConfigurationError, AIResponseError
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.analysis import JobAnalysisRead
from app.schemas.job_description import JobDescriptionCreate, JobDescriptionRead
from app.services.job_analysis_service import JobAnalysisService, JobDescriptionNotFoundError

router = APIRouter(prefix="/job-descriptions", tags=["job descriptions"])


@router.post("", response_model=JobDescriptionRead, status_code=status.HTTP_201_CREATED)
def create_job_description(
    payload: JobDescriptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JobDescriptionRead:
    service = JobAnalysisService(db)
    return service.create_job_description(payload, user_id=current_user.id)


@router.get("", response_model=list[JobDescriptionRead])
def list_job_descriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[JobDescriptionRead]:
    service = JobAnalysisService(db)
    return service.list_job_descriptions(user_id=current_user.id)


@router.post("/{job_description_id}/analyze", response_model=JobAnalysisRead)
def analyze_job_description(
    job_description_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JobAnalysisRead:
    service = JobAnalysisService(db)

    try:
        return service.analyze_job_description(job_description_id, user_id=current_user.id)
    except JobDescriptionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AIConfigurationError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except AIResponseError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
