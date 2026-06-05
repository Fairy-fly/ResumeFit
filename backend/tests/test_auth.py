from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.main import app
from app.models.user import User
from app.core.database import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


@pytest.fixture()
def auth_client(monkeypatch: pytest.MonkeyPatch) -> Generator[tuple[TestClient, sessionmaker[Session]], None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db() -> Generator[Session, None, None]:
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    monkeypatch.setattr("app.main.init_db", lambda: None)
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client, testing_session_local

    app.dependency_overrides.clear()


def register_user(client: TestClient, *, email: str = "user@example.com", password: str = "password123") -> dict:
    response = client.post(
        "/auth/register",
        json={"email": email, "password": password, "display_name": "Test User"},
    )
    assert response.status_code == 201
    return response.json()


def test_register_user_success(auth_client: tuple[TestClient, sessionmaker[Session]]) -> None:
    client, testing_session_local = auth_client

    response = client.post(
        "/auth/register",
        json={"email": "new@example.com", "password": "password123", "display_name": "New User"},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["access_token"]
    assert payload["token_type"] == "bearer"
    assert payload["user"]["email"] == "new@example.com"
    assert payload["user"]["display_name"] == "New User"
    assert "password" not in payload["user"]
    assert "password_hash" not in payload["user"]

    with testing_session_local() as db:
        user = db.scalar(select(User).where(User.email == "new@example.com"))
        assert user is not None
        assert user.password_hash
        assert user.password_hash != "password123"


def test_register_rejects_duplicate_email(auth_client: tuple[TestClient, sessionmaker[Session]]) -> None:
    client, _ = auth_client
    register_user(client, email="duplicate@example.com")

    response = client.post(
        "/auth/register",
        json={"email": "duplicate@example.com", "password": "password123", "display_name": "Duplicate User"},
    )

    assert response.status_code == 400


def test_login_success(auth_client: tuple[TestClient, sessionmaker[Session]]) -> None:
    client, _ = auth_client
    register_user(client, email="login@example.com", password="password123")

    response = client.post("/auth/login", json={"email": "login@example.com", "password": "password123"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["access_token"]
    assert payload["token_type"] == "bearer"
    assert payload["user"]["email"] == "login@example.com"


def test_login_rejects_wrong_password(auth_client: tuple[TestClient, sessionmaker[Session]]) -> None:
    client, _ = auth_client
    register_user(client, email="wrong-password@example.com", password="password123")

    response = client.post(
        "/auth/login",
        json={"email": "wrong-password@example.com", "password": "wrongpassword"},
    )

    assert response.status_code == 401


def test_login_rejects_missing_user(auth_client: tuple[TestClient, sessionmaker[Session]]) -> None:
    client, _ = auth_client

    response = client.post("/auth/login", json={"email": "missing@example.com", "password": "password123"})

    assert response.status_code == 401


def test_me_requires_token(auth_client: tuple[TestClient, sessionmaker[Session]]) -> None:
    client, _ = auth_client

    response = client.get("/auth/me")

    assert response.status_code == 401


def test_me_rejects_invalid_token(auth_client: tuple[TestClient, sessionmaker[Session]]) -> None:
    client, _ = auth_client

    response = client.get("/auth/me", headers={"Authorization": "Bearer not-a-valid-token"})

    assert response.status_code == 401


def test_me_returns_current_user_with_valid_token(auth_client: tuple[TestClient, sessionmaker[Session]]) -> None:
    client, _ = auth_client
    registered = register_user(client, email="me@example.com")

    response = client.get("/auth/me", headers={"Authorization": f"Bearer {registered['access_token']}"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["email"] == "me@example.com"
    assert payload["display_name"] == "Test User"
    assert "password_hash" not in payload


def test_disabled_user_cannot_login_or_access_me(auth_client: tuple[TestClient, sessionmaker[Session]]) -> None:
    client, testing_session_local = auth_client
    registered = register_user(client, email="disabled@example.com")

    with testing_session_local() as db:
        user = db.scalar(select(User).where(User.email == "disabled@example.com"))
        assert user is not None
        user.status = "disabled"
        db.commit()

    login_response = client.post(
        "/auth/login",
        json={"email": "disabled@example.com", "password": "password123"},
    )
    me_response = client.get("/auth/me", headers={"Authorization": f"Bearer {registered['access_token']}"})

    assert login_response.status_code == 401
    assert me_response.status_code == 401
