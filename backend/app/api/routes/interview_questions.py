from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.ai.client import AIConfigurationError, AIResponseError
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.interview_question import InterviewQuestionCreate, InterviewQuestionResultRead
from app.services.interview_question_service import (
    InterviewQuestionNotFoundError,
    InterviewQuestionService,
    InterviewQuestionValidationError,
)

router = APIRouter(prefix="/interview-question-results", tags=["interview question results"])


@router.post("", response_model=InterviewQuestionResultRead, status_code=status.HTTP_201_CREATED)
def create_interview_question_result(
    payload: InterviewQuestionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InterviewQuestionResultRead:
    service = InterviewQuestionService(db)

    try:
        return service.create_interview_question_result(payload, user_id=current_user.id)
    except InterviewQuestionValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except InterviewQuestionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AIConfigurationError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except AIResponseError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.get("", response_model=list[InterviewQuestionResultRead])
def list_interview_question_results(
    resume_version_id: int = Query(..., gt=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[InterviewQuestionResultRead]:
    service = InterviewQuestionService(db)

    try:
        return service.list_interview_question_results(resume_version_id=resume_version_id, user_id=current_user.id)
    except InterviewQuestionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
