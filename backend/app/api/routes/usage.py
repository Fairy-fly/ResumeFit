from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.repositories.ai_usage_repository import AIUsageRepository
from app.schemas.usage import AIUsageSummaryRead
from app.services.ai_usage_service import AIUsageService

router = APIRouter(prefix="/usage", tags=["usage"])


@router.get("/summary", response_model=AIUsageSummaryRead)
def get_usage_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AIUsageSummaryRead:
    service = AIUsageService(AIUsageRepository(db))
    return service.summary(user_id=current_user.id)
