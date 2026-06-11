from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, *, email: str, password_hash: str, display_name: str) -> User:
        user = User(
            email=email,
            password_hash=password_hash,
            display_name=display_name,
            status="active",
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_email(self, *, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        return self.db.scalar(statement)

    def get_by_id(self, *, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def update_display_name(self, *, user: User, display_name: str) -> User:
        user.display_name = display_name
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def count(self, *, search: str | None = None) -> int:
        statement = select(func.count()).select_from(User)
        if search:
            statement = statement.where(self._search_filter(search))
        return int(self.db.scalar(statement) or 0)

    def list_paginated(self, *, page: int, page_size: int, search: str | None = None) -> list[User]:
        statement = select(User).order_by(User.created_at.desc(), User.id.desc())
        if search:
            statement = statement.where(self._search_filter(search))
        statement = statement.offset((page - 1) * page_size).limit(page_size)
        return list(self.db.scalars(statement).all())

    def update_status(self, *, user: User, status: str) -> User:
        user.status = status
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def _search_filter(self, search: str):
        pattern = f"%{search.strip()}%"
        return or_(User.email.ilike(pattern), User.display_name.ilike(pattern))
