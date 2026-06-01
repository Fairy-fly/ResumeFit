from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models.user import User


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    with testing_session_local() as db:
        db.add(User(id=1, display_name="Demo User", status="active"))
        db.commit()

    def override_get_db() -> Generator[Session, None, None]:
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    monkeypatch.setattr("app.main.init_db", lambda: None)
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_health_check(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_resume_profiles_start_empty(client: TestClient) -> None:
    response = client.get("/resume-profiles")
    assert response.status_code == 200
    assert response.json() == []


def test_create_and_list_resume_profile(client: TestClient) -> None:
    payload = {
        "title": "后端开发通用简历",
        "raw_markdown": "# 我的简历",
    }

    create_response = client.post("/resume-profiles", json=payload)

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["id"]
    assert created["user_id"] == 1
    assert created["title"] == payload["title"]
    assert created["raw_markdown"] == payload["raw_markdown"]
    assert created["created_at"]
    assert created["updated_at"]

    list_response = client.get("/resume-profiles")

    assert list_response.status_code == 200
    resumes = list_response.json()
    assert len(resumes) == 1
    assert resumes[0]["id"] == created["id"]


def test_resume_profile_requires_title_and_body(client: TestClient) -> None:
    empty_title_response = client.post(
        "/resume-profiles",
        json={"title": "", "raw_markdown": "# 我的简历"},
    )
    empty_body_response = client.post(
        "/resume-profiles",
        json={"title": "后端开发通用简历", "raw_markdown": ""},
    )

    assert empty_title_response.status_code == 422
    assert empty_body_response.status_code == 422


def test_resume_profile_rejects_whitespace_only_title_and_body(client: TestClient) -> None:
    whitespace_title_response = client.post(
        "/resume-profiles",
        json={"title": "   ", "raw_markdown": "# 我的简历"},
    )
    whitespace_body_response = client.post(
        "/resume-profiles",
        json={"title": "后端开发通用简历", "raw_markdown": "   \n\t"},
    )

    assert whitespace_title_response.status_code == 422
    assert whitespace_body_response.status_code == 422


def test_projects_start_empty(client: TestClient) -> None:
    response = client.get("/projects")
    assert response.status_code == 200
    assert response.json() == []


def test_create_and_list_project(client: TestClient) -> None:
    payload = {
        "name": "ResumeFit Demo",
        "project_type": "Web 应用",
        "role": "独立开发",
        "tech_stack": ["Vue 3", "FastAPI", "SQLite"],
        "description": "智能简历定制平台 Demo",
        "user_contribution": "负责项目库模块设计与实现",
        "work_url": "https://example.com",
    }

    create_response = client.post("/projects", json=payload)

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["id"]
    assert created["user_id"] == 1
    assert created["name"] == payload["name"]
    assert created["project_type"] == payload["project_type"]
    assert created["role"] == payload["role"]
    assert created["tech_stack"] == payload["tech_stack"]
    assert created["description"] == payload["description"]
    assert created["user_contribution"] == payload["user_contribution"]
    assert created["work_url"] == payload["work_url"]
    assert created["created_at"]
    assert created["updated_at"]

    list_response = client.get("/projects")

    assert list_response.status_code == 200
    projects = list_response.json()
    assert len(projects) == 1
    assert projects[0]["id"] == created["id"]


def test_project_requires_text_fields_and_tech_stack(client: TestClient) -> None:
    valid_payload = {
        "name": "ResumeFit Demo",
        "project_type": "Web 应用",
        "role": "独立开发",
        "tech_stack": ["Vue 3"],
        "description": "智能简历定制平台 Demo",
        "user_contribution": "负责项目库模块设计与实现",
    }

    for field_name in ["name", "project_type", "role", "description", "user_contribution"]:
        payload = {**valid_payload, field_name: "   "}
        response = client.post("/projects", json=payload)
        assert response.status_code == 422

    empty_stack_response = client.post(
        "/projects",
        json={**valid_payload, "tech_stack": []},
    )
    blank_stack_response = client.post(
        "/projects",
        json={**valid_payload, "tech_stack": ["   "]},
    )

    assert empty_stack_response.status_code == 422
    assert blank_stack_response.status_code == 422


def test_project_rejects_invalid_work_url(client: TestClient) -> None:
    response = client.post(
        "/projects",
        json={
            "name": "ResumeFit Demo",
            "project_type": "Web 应用",
            "role": "独立开发",
            "tech_stack": ["Vue 3"],
            "description": "智能简历定制平台 Demo",
            "user_contribution": "负责项目库模块设计与实现",
            "work_url": "not-a-url",
        },
    )

    assert response.status_code == 422
