from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.ai.client import AIConfigurationError, AIResponseError
from app.core.database import get_db
from app.schemas.truth_check import TruthCheckCreate, TruthCheckResultRead
from app.services.truth_check_service import TruthCheckNotFoundError, TruthCheckService, TruthCheckValidationError

router = APIRouter(prefix="/truth-check-results", tags=["truth checks"])


@router.post("", response_model=TruthCheckResultRead, status_code=status.HTTP_201_CREATED)
def create_truth_check_result(
    payload: TruthCheckCreate,
    db: Session = Depends(get_db),
) -> TruthCheckResultRead:
    service = TruthCheckService(db)

    try:
        return service.create_truth_check_result(payload)
    except TruthCheckValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except TruthCheckNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AIConfigurationError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except AIResponseError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.get("", response_model=list[TruthCheckResultRead])
def list_truth_check_results(
    resume_version_id: int = Query(..., gt=0),
    db: Session = Depends(get_db),
) -> list[TruthCheckResultRead]:
    service = TruthCheckService(db)

    try:
        return service.list_truth_check_results(resume_version_id=resume_version_id)
    except TruthCheckNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
