from sqlalchemy import select
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
