from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_admin_user
from app.models.user import User
from app.repositories.ai_usage_repository import AIUsageRepository
from app.repositories.user_repository import UserRepository
from app.schemas.admin import (
    AdminGlobalUsageSummaryRead,
    AdminUserDetailRead,
    AdminUserListRead,
    AdminUserStatusUpdate,
)
from app.services.admin_service import AdminOperationError, AdminResourceNotFoundError, AdminService

router = APIRouter(prefix="/admin", tags=["admin"])


def get_admin_service(db: Session) -> AdminService:
    return AdminService(
        user_repository=UserRepository(db),
        ai_usage_repository=AIUsageRepository(db),
    )


@router.get("/users", response_model=AdminUserListRead)
def list_admin_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None),
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> AdminUserListRead:
    _ = current_admin
    return get_admin_service(db).list_users(page=page, page_size=page_size, search=search)


@router.get("/users/{user_id}", response_model=AdminUserDetailRead)
def get_admin_user_detail(
    user_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> AdminUserDetailRead:
    _ = current_admin
    try:
        return get_admin_service(db).get_user_detail(user_id=user_id)
    except AdminResourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/users/{user_id}/status", response_model=AdminUserDetailRead)
def update_admin_user_status(
    user_id: int,
    payload: AdminUserStatusUpdate,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> AdminUserDetailRead:
    try:
        return get_admin_service(db).update_user_status(
            current_admin=current_admin,
            user_id=user_id,
            status=payload.status,
        )
    except AdminResourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AdminOperationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/usage/summary", response_model=AdminGlobalUsageSummaryRead)
def get_admin_usage_summary(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> AdminGlobalUsageSummaryRead:
    _ = current_admin
    return get_admin_service(db).global_usage_summary()
