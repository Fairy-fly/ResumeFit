from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    pass


connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from app import models
    from app.models.user import User

    _ = models
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        default_user = db.get(User, 1)
        if default_user is None:
            db.add(User(id=1, display_name="Demo User", role="user", status="active"))
            db.commit()
