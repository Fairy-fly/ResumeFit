from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.ai.client import AIConfigurationError, AIResponseError
from app.core.database import get_db
from app.schemas.resume_version import ResumeVersionGenerate, ResumeVersionRead
from app.services.resume_generation_service import (
    JobAnalysisRequiredError,
    ResumeGenerationNotFoundError,
    ResumeGenerationService,
    ResumeGenerationValidationError,
)

router = APIRouter(prefix="/resume-versions", tags=["resume versions"])


@router.get("", response_model=list[ResumeVersionRead])
def list_resume_versions(db: Session = Depends(get_db)) -> list[ResumeVersionRead]:
    service = ResumeGenerationService(db)
    return service.list_resume_versions()


@router.post("/generate", response_model=ResumeVersionRead, status_code=status.HTTP_201_CREATED)
def generate_resume_version(
    payload: ResumeVersionGenerate,
    db: Session = Depends(get_db),
) -> ResumeVersionRead:
    service = ResumeGenerationService(db)

    try:
        return service.generate_resume_version(payload)
    except JobAnalysisRequiredError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ResumeGenerationValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ResumeGenerationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AIConfigurationError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except AIResponseError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.get("/{resume_version_id}/export/markdown")
def export_resume_version_markdown(
    resume_version_id: int,
    db: Session = Depends(get_db),
) -> Response:
    service = ResumeGenerationService(db)

    try:
        export = service.export_resume_version_markdown(resume_version_id=resume_version_id)
    except ResumeGenerationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return Response(
        content=export.content,
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": export.content_disposition},
    )
