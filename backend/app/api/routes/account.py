from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.account import AccountRead, AccountUpdate
from app.services.account_service import AccountService

router = APIRouter(prefix="/account", tags=["account"])


@router.get("/me", response_model=AccountRead)
def get_account_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AccountRead:
    return AccountService(db).get_account(user=current_user)


@router.patch("/me", response_model=AccountRead)
def update_account_me(
    payload: AccountUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AccountRead:
    return AccountService(db).update_account(user=current_user, payload=payload)
