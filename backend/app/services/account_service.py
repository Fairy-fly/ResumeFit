from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.ai_usage_repository import AIUsageRepository
from app.repositories.user_repository import UserRepository
from app.schemas.account import AccountRead, AccountUpdate
from app.services.ai_usage_service import AIUsageService


class AccountService:
    def __init__(self, db: Session) -> None:
        self.user_repository = UserRepository(db)
        self.ai_usage_service = AIUsageService(AIUsageRepository(db))

    def get_account(self, *, user: User) -> AccountRead:
        return self._to_read_model(user)

    def update_account(self, *, user: User, payload: AccountUpdate) -> AccountRead:
        updated_user = self.user_repository.update_display_name(
            user=user,
            display_name=payload.display_name.strip(),
        )
        return self._to_read_model(updated_user)

    def _to_read_model(self, user: User) -> AccountRead:
        return AccountRead(
            id=user.id,
            email=user.email,
            display_name=user.display_name,
            role=user.role,
            status=user.status,
            created_at=user.created_at,
            updated_at=user.updated_at,
            usage_summary=self.ai_usage_service.summary(user_id=user.id),
        )
