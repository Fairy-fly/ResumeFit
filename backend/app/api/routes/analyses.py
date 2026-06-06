from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.ai.client import AIConfigurationError, AIResponseError
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.match_report import MatchReportCreate, MatchReportRead
from app.services.ai_usage_service import AIQuotaExceededError
from app.services.match_service import JobAnalysisRequiredError, MatchReportNotFoundError, MatchReportService

router = APIRouter(prefix="/match-reports", tags=["match reports"])


@router.post("", response_model=MatchReportRead, status_code=status.HTTP_201_CREATED)
def create_match_report(
    payload: MatchReportCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MatchReportRead:
    service = MatchReportService(db)

    try:
        return service.create_match_report(payload, user_id=current_user.id)
    except JobAnalysisRequiredError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except MatchReportNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AIQuotaExceededError as exc:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(exc)) from exc
    except AIConfigurationError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except AIResponseError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.get("", response_model=list[MatchReportRead])
def list_match_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[MatchReportRead]:
    service = MatchReportService(db)
    return service.list_match_reports(user_id=current_user.id)
