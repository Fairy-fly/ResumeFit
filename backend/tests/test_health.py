from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.ai.client import AIClient, AIResponseError
from app.core.database import Base, get_db
from app.core.config import settings
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


def test_job_descriptions_start_empty(client: TestClient) -> None:
    response = client.get("/job-descriptions")
    assert response.status_code == 200
    assert response.json() == []


def test_create_and_list_job_description(client: TestClient) -> None:
    payload = {
        "company_name": "示例公司",
        "job_title": "后端开发工程师",
        "raw_text": "负责 FastAPI 服务开发，熟悉 SQL、缓存和云服务。",
    }

    create_response = client.post("/job-descriptions", json=payload)

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["id"]
    assert created["user_id"] == 1
    assert created["company_name"] == payload["company_name"]
    assert created["job_title"] == payload["job_title"]
    assert created["raw_text"] == payload["raw_text"]
    assert created["status"] == "draft"
    assert created["created_at"]
    assert created["updated_at"]

    list_response = client.get("/job-descriptions")

    assert list_response.status_code == 200
    job_descriptions = list_response.json()
    assert len(job_descriptions) == 1
    assert job_descriptions[0]["id"] == created["id"]


def test_job_description_requires_text_fields(client: TestClient) -> None:
    valid_payload = {
        "company_name": "示例公司",
        "job_title": "后端开发工程师",
        "raw_text": "负责 FastAPI 服务开发。",
    }

    for field_name in ["company_name", "job_title", "raw_text"]:
        response = client.post("/job-descriptions", json={**valid_payload, field_name: "   "})
        assert response.status_code == 422


def test_analyze_job_description_with_mock_ai(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_chat_json(
        self: AIClient,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
    ) -> dict[str, object]:
        assert "不要编造" in system_prompt
        assert "负责 FastAPI 服务开发" in user_prompt
        assert temperature == 0.1
        return {
            "job_title": "后端开发工程师",
            "job_type": "后端开发",
            "required_skills": ["FastAPI", "SQL", "缓存"],
            "bonus_skills": ["云服务"],
            "responsibilities": ["负责后端服务开发"],
            "keywords": ["FastAPI", "SQLite", "API"],
            "resume_focus_suggestions": ["突出 API 设计与数据库经验"],
        }

    monkeypatch.setattr(AIClient, "chat_json", fake_chat_json)

    create_response = client.post(
        "/job-descriptions",
        json={
            "company_name": "示例公司",
            "job_title": "后端开发工程师",
            "raw_text": "负责 FastAPI 服务开发，熟悉 SQL、缓存和云服务。",
        },
    )
    job_description_id = create_response.json()["id"]

    analyze_response = client.post(f"/job-descriptions/{job_description_id}/analyze")

    assert analyze_response.status_code == 200
    analysis = analyze_response.json()
    assert analysis["job_description_id"] == job_description_id
    assert analysis["job_title"] == "后端开发工程师"
    assert analysis["job_type"] == "后端开发"
    assert analysis["required_skills"] == ["FastAPI", "SQL", "缓存"]
    assert analysis["bonus_skills"] == ["云服务"]
    assert analysis["responsibilities"] == ["负责后端服务开发"]
    assert analysis["keywords"] == ["FastAPI", "SQLite", "API"]
    assert analysis["resume_focus_suggestions"] == ["突出 API 设计与数据库经验"]
    assert analysis["model_name"] == "deepseek-chat"

    list_response = client.get("/job-descriptions")
    assert list_response.json()[0]["status"] == "analyzed"


def test_analyze_job_description_requires_api_key(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "ai_api_key", None)
    create_response = client.post(
        "/job-descriptions",
        json={
            "company_name": "示例公司",
            "job_title": "后端开发工程师",
            "raw_text": "负责 FastAPI 服务开发。",
        },
    )
    job_description_id = create_response.json()["id"]

    response = client.post(f"/job-descriptions/{job_description_id}/analyze")

    assert response.status_code == 503
    assert response.json()["detail"] == "AI_API_KEY is not configured."


def test_analyze_job_description_handles_invalid_ai_response(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_chat_json(
        self: AIClient,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
    ) -> dict[str, object]:
        raise AIResponseError("AI response was not valid JSON.")

    monkeypatch.setattr(AIClient, "chat_json", fake_chat_json)
    create_response = client.post(
        "/job-descriptions",
        json={
            "company_name": "示例公司",
            "job_title": "后端开发工程师",
            "raw_text": "负责 FastAPI 服务开发。",
        },
    )
    job_description_id = create_response.json()["id"]

    response = client.post(f"/job-descriptions/{job_description_id}/analyze")

    assert response.status_code == 502
    assert response.json()["detail"] == "AI response was not valid JSON."
