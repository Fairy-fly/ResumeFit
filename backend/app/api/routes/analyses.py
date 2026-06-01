from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.ai.client import AIConfigurationError, AIResponseError
from app.core.database import get_db
from app.schemas.match_report import MatchReportCreate, MatchReportRead
from app.services.match_service import JobAnalysisRequiredError, MatchReportNotFoundError, MatchReportService

router = APIRouter(prefix="/match-reports", tags=["match reports"])


@router.post("", response_model=MatchReportRead, status_code=status.HTTP_201_CREATED)
def create_match_report(
    payload: MatchReportCreate,
    db: Session = Depends(get_db),
) -> MatchReportRead:
    service = MatchReportService(db)

    try:
        return service.create_match_report(payload)
    except JobAnalysisRequiredError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except MatchReportNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AIConfigurationError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except AIResponseError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
