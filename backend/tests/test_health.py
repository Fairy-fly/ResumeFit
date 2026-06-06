from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.ai.client import AIClient, AIResponseError
from app.core.database import Base, get_db
from app.core.config import settings
from app.core.security import create_access_token
from app.main import app
from app.models.job_description import JobDescription
from app.models.resume_version import ResumeVersion
from app.models.user import User


def _build_test_client(
    monkeypatch: pytest.MonkeyPatch,
    *,
    authenticated: bool,
) -> Generator[TestClient, None, None]:
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
        if authenticated:
            test_client.headers.update({"Authorization": f"Bearer {create_access_token(user_id=1)}"})
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch) -> Generator[TestClient, None, None]:
    yield from _build_test_client(monkeypatch, authenticated=True)


@pytest.fixture()
def anonymous_client(monkeypatch: pytest.MonkeyPatch) -> Generator[TestClient, None, None]:
    yield from _build_test_client(monkeypatch, authenticated=False)


def _register_test_user(client: TestClient, *, email: str) -> str:
    response = client.post(
        "/auth/register",
        json={"email": email, "password": "password123", "display_name": email},
    )
    assert response.status_code == 201
    return str(response.json()["access_token"])


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _request_kwargs(headers: dict[str, str] | None) -> dict[str, dict[str, str]]:
    return {"headers": headers} if headers is not None else {}


def test_health_check(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_account_me_requires_login(anonymous_client: TestClient) -> None:
    get_response = anonymous_client.get("/account/me")
    patch_response = anonymous_client.patch("/account/me", json={"display_name": "New Name"})

    assert get_response.status_code == 401
    assert patch_response.status_code == 401


def test_account_me_returns_current_user_and_usage_summary(client: TestClient) -> None:
    token = _register_test_user(client, email="account-reader@example.com")

    response = client.get("/account/me", headers=_auth_headers(token))

    assert response.status_code == 200
    payload = response.json()
    assert payload["email"] == "account-reader@example.com"
    assert payload["display_name"] == "account-reader@example.com"
    assert payload["status"] == "active"
    assert payload["created_at"]
    assert payload["updated_at"]
    assert payload["usage_summary"]["monthly_used"] == 0
    assert payload["usage_summary"]["recent_calls"] == []


def test_account_me_updates_display_name_and_auth_me_reflects_it(client: TestClient) -> None:
    token = _register_test_user(client, email="account-update@example.com")
    headers = _auth_headers(token)

    update_response = client.patch("/account/me", headers=headers, json={"display_name": "  新昵称  "})
    account_response = client.get("/account/me", headers=headers)
    auth_response = client.get("/auth/me", headers=headers)

    assert update_response.status_code == 200
    assert update_response.json()["display_name"] == "新昵称"
    assert account_response.json()["display_name"] == "新昵称"
    assert auth_response.json()["display_name"] == "新昵称"


def test_account_display_name_update_is_isolated_by_user(client: TestClient) -> None:
    user_a_token = _register_test_user(client, email="account-a@example.com")
    user_b_token = _register_test_user(client, email="account-b@example.com")

    user_a_response = client.patch(
        "/account/me",
        headers=_auth_headers(user_a_token),
        json={"display_name": "User A New Name"},
    )
    user_b_response = client.get("/account/me", headers=_auth_headers(user_b_token))

    assert user_a_response.status_code == 200
    assert user_a_response.json()["display_name"] == "User A New Name"
    assert user_b_response.status_code == 200
    assert user_b_response.json()["display_name"] == "account-b@example.com"


def test_account_display_name_validation(client: TestClient) -> None:
    token = _register_test_user(client, email="account-validation@example.com")
    headers = _auth_headers(token)

    empty_response = client.patch("/account/me", headers=headers, json={"display_name": ""})
    blank_response = client.patch("/account/me", headers=headers, json={"display_name": "   "})
    long_response = client.patch("/account/me", headers=headers, json={"display_name": "a" * 51})

    assert empty_response.status_code == 422
    assert blank_response.status_code == 422
    assert long_response.status_code == 422


def test_account_update_ignores_forbidden_fields(client: TestClient) -> None:
    token = _register_test_user(client, email="account-forbidden@example.com")
    headers = _auth_headers(token)

    response = client.patch(
        "/account/me",
        headers=headers,
        json={
            "display_name": "Allowed Name",
            "email": "changed@example.com",
            "status": "disabled",
            "password_hash": "plain-text-should-not-apply",
            "role": "admin",
            "monthly_quota": 999999,
        },
    )
    auth_response = client.get("/auth/me", headers=headers)

    assert response.status_code == 200
    assert response.json()["display_name"] == "Allowed Name"
    assert response.json()["email"] == "account-forbidden@example.com"
    assert response.json()["status"] == "active"
    assert auth_response.json()["email"] == "account-forbidden@example.com"
    assert auth_response.json()["status"] == "active"


def test_dashboard_summary_starts_empty(client: TestClient) -> None:
    response = client.get("/dashboard/summary")

    assert response.status_code == 200
    assert response.json() == {
        "resume_profile_count": 0,
        "project_count": 0,
        "job_description_count": 0,
        "match_report_count": 0,
        "resume_version_count": 0,
    }


def test_resume_profiles_start_empty(client: TestClient) -> None:
    response = client.get("/resume-profiles")
    assert response.status_code == 200
    assert response.json() == []


def test_resume_profiles_require_login(anonymous_client: TestClient) -> None:
    response = anonymous_client.get("/resume-profiles")

    assert response.status_code == 401


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


def test_resume_profiles_are_isolated_by_user(client: TestClient) -> None:
    user_a_token = _register_test_user(client, email="resume-a@example.com")
    user_b_token = _register_test_user(client, email="resume-b@example.com")

    create_response = client.post(
        "/resume-profiles",
        headers=_auth_headers(user_a_token),
        json={"title": "User A Resume", "raw_markdown": "# User A"},
    )
    assert create_response.status_code == 201

    user_a_list_response = client.get("/resume-profiles", headers=_auth_headers(user_a_token))
    user_b_list_response = client.get("/resume-profiles", headers=_auth_headers(user_b_token))

    assert [resume["title"] for resume in user_a_list_response.json()] == ["User A Resume"]
    assert user_b_list_response.json() == []


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


def test_projects_are_isolated_by_user(client: TestClient) -> None:
    user_a_token = _register_test_user(client, email="project-a@example.com")
    user_b_token = _register_test_user(client, email="project-b@example.com")

    create_response = client.post(
        "/projects",
        headers=_auth_headers(user_a_token),
        json={
            "name": "User A Project",
            "project_type": "Web",
            "role": "Owner",
            "tech_stack": ["FastAPI"],
            "description": "User A project",
            "user_contribution": "Built the project",
        },
    )
    assert create_response.status_code == 201

    user_a_list_response = client.get("/projects", headers=_auth_headers(user_a_token))
    user_b_list_response = client.get("/projects", headers=_auth_headers(user_b_token))

    assert [project["name"] for project in user_a_list_response.json()] == ["User A Project"]
    assert user_b_list_response.json() == []


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


def test_job_descriptions_are_isolated_by_user(client: TestClient) -> None:
    user_a_token = _register_test_user(client, email="job-a@example.com")
    user_b_token = _register_test_user(client, email="job-b@example.com")

    create_response = client.post(
        "/job-descriptions",
        headers=_auth_headers(user_a_token),
        json={
            "company_name": "User A Company",
            "job_title": "Backend Engineer",
            "raw_text": "Build APIs with FastAPI.",
        },
    )
    assert create_response.status_code == 201

    user_a_list_response = client.get("/job-descriptions", headers=_auth_headers(user_a_token))
    user_b_list_response = client.get("/job-descriptions", headers=_auth_headers(user_b_token))

    assert [job["company_name"] for job in user_a_list_response.json()] == ["User A Company"]
    assert user_b_list_response.json() == []


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


def test_usage_summary_requires_login(anonymous_client: TestClient) -> None:
    response = anonymous_client.get("/usage/summary")

    assert response.status_code == 401


def test_usage_summary_starts_empty(client: TestClient) -> None:
    response = client.get("/usage/summary")

    assert response.status_code == 200
    payload = response.json()
    assert payload["monthly_quota"] == settings.ai_monthly_call_limit
    assert payload["monthly_used"] == 0
    assert payload["monthly_remaining"] == settings.ai_monthly_call_limit
    assert payload["total_call_count"] == 0
    assert payload["monthly_success_count"] == 0
    assert payload["monthly_failure_count"] == 0
    assert payload["feature_counts"] == []
    assert payload["recent_calls"] == []


def test_successful_ai_call_is_logged_in_usage_summary(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_chat_json(self: AIClient, **_: object) -> dict[str, object]:
        return {
            "job_title": "后端开发工程师",
            "job_type": "后端开发",
            "required_skills": ["FastAPI"],
            "bonus_skills": [],
            "responsibilities": ["负责 API 开发"],
            "keywords": ["FastAPI"],
            "resume_focus_suggestions": ["突出 API 经验"],
        }

    monkeypatch.setattr(AIClient, "chat_json", fake_chat_json)
    create_response = client.post(
        "/job-descriptions",
        json={
            "company_name": "示例公司",
            "job_title": "后端开发工程师",
            "raw_text": "负责 FastAPI 服务开发。",
        },
    )

    analyze_response = client.post(f"/job-descriptions/{create_response.json()['id']}/analyze")
    summary_response = client.get("/usage/summary")

    assert analyze_response.status_code == 200
    assert summary_response.status_code == 200
    payload = summary_response.json()
    assert payload["monthly_used"] == 1
    assert payload["total_call_count"] == 1
    assert payload["monthly_success_count"] == 1
    assert payload["monthly_failure_count"] == 0
    assert payload["feature_counts"] == [
        {"feature_type": "jd_analysis", "count": 1, "success_count": 1, "failure_count": 0}
    ]
    assert payload["recent_calls"][0]["feature_type"] == "jd_analysis"
    assert payload["recent_calls"][0]["status"] == "success"
    assert payload["recent_calls"][0]["error_message"] is None


def test_usage_summary_is_isolated_by_user(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_chat_json(self: AIClient, **_: object) -> dict[str, object]:
        return {
            "job_title": "后端开发工程师",
            "job_type": "后端开发",
            "required_skills": ["FastAPI"],
            "bonus_skills": [],
            "responsibilities": ["负责 API 开发"],
            "keywords": ["FastAPI"],
            "resume_focus_suggestions": ["突出 API 经验"],
        }

    monkeypatch.setattr(AIClient, "chat_json", fake_chat_json)
    user_a_token = _register_test_user(client, email="usage-a@example.com")
    user_b_token = _register_test_user(client, email="usage-b@example.com")
    user_a_headers = _auth_headers(user_a_token)
    user_b_headers = _auth_headers(user_b_token)

    create_response = client.post(
        "/job-descriptions",
        headers=user_a_headers,
        json={
            "company_name": "示例公司",
            "job_title": "后端开发工程师",
            "raw_text": "负责 FastAPI 服务开发。",
        },
    )
    client.post(f"/job-descriptions/{create_response.json()['id']}/analyze", headers=user_a_headers)

    user_a_summary = client.get("/usage/summary", headers=user_a_headers)
    user_b_summary = client.get("/usage/summary", headers=user_b_headers)

    assert user_a_summary.json()["monthly_used"] == 1
    assert user_b_summary.json()["monthly_used"] == 0
    assert user_b_summary.json()["recent_calls"] == []


def test_failed_ai_call_is_logged_in_usage_summary(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "ai_api_key", None)
    monkeypatch.setattr(AIClient, "chat_json", lambda self, **_: self._ensure_configured())
    create_response = client.post(
        "/job-descriptions",
        json={
            "company_name": "示例公司",
            "job_title": "后端开发工程师",
            "raw_text": "负责 FastAPI 服务开发。",
        },
    )

    analyze_response = client.post(f"/job-descriptions/{create_response.json()['id']}/analyze")
    summary_response = client.get("/usage/summary")

    assert analyze_response.status_code == 503
    payload = summary_response.json()
    assert payload["monthly_used"] == 1
    assert payload["monthly_success_count"] == 0
    assert payload["monthly_failure_count"] == 1
    assert payload["feature_counts"] == [
        {"feature_type": "jd_analysis", "count": 1, "success_count": 0, "failure_count": 1}
    ]
    assert payload["recent_calls"][0]["status"] == "failed"
    assert payload["recent_calls"][0]["error_message"] == "AI_API_KEY is not configured."


def test_monthly_ai_quota_blocks_provider_call(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "ai_monthly_call_limit", 1)

    def fake_chat_json(self: AIClient, **_: object) -> dict[str, object]:
        return {
            "job_title": "后端开发工程师",
            "job_type": "后端开发",
            "required_skills": ["FastAPI"],
            "bonus_skills": [],
            "responsibilities": ["负责 API 开发"],
            "keywords": ["FastAPI"],
            "resume_focus_suggestions": ["突出 API 经验"],
        }

    monkeypatch.setattr(AIClient, "chat_json", fake_chat_json)
    first_jd = client.post(
        "/job-descriptions",
        json={"company_name": "A", "job_title": "Backend", "raw_text": "Build APIs."},
    )
    first_response = client.post(f"/job-descriptions/{first_jd.json()['id']}/analyze")
    assert first_response.status_code == 200

    def fail_if_called(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise AssertionError("AI should not be called after quota is exhausted.")

    monkeypatch.setattr(AIClient, "chat_json", fail_if_called)
    second_jd = client.post(
        "/job-descriptions",
        json={"company_name": "B", "job_title": "Backend", "raw_text": "Build APIs."},
    )
    second_response = client.post(f"/job-descriptions/{second_jd.json()['id']}/analyze")
    summary_response = client.get("/usage/summary")

    assert second_response.status_code == 429
    assert second_response.json()["detail"] == "Monthly AI quota exceeded."
    assert summary_response.json()["monthly_used"] == 1


def test_user_cannot_analyze_another_users_job_description(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_if_called(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise AssertionError("AI should not be called for another user's JD.")

    monkeypatch.setattr(AIClient, "chat_json", fail_if_called)
    user_a_token = _register_test_user(client, email="jd-analyze-a@example.com")
    user_b_token = _register_test_user(client, email="jd-analyze-b@example.com")

    create_response = client.post(
        "/job-descriptions",
        headers=_auth_headers(user_a_token),
        json={
            "company_name": "User A Company",
            "job_title": "Backend Engineer",
            "raw_text": "Build APIs with FastAPI.",
        },
    )
    assert create_response.status_code == 201
    job_description_id = create_response.json()["id"]

    analyze_response = client.post(
        f"/job-descriptions/{job_description_id}/analyze",
        headers=_auth_headers(user_b_token),
    )
    assert analyze_response.status_code == 404
    assert analyze_response.json()["detail"] == "Job description was not found."


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


def test_create_match_report_with_mock_ai(
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
        if "Match Scorer v1" in system_prompt:
            assert "后端开发通用简历" in user_prompt
            assert "ResumeFit Demo" in user_prompt
            assert "后端开发工程师" in user_prompt
            return {
                "score": 82,
                "strengths": ["简历和项目都体现了 FastAPI 服务开发经验"],
                "weaknesses": ["缓存和云服务经验表达不足"],
                "missing_keywords": ["缓存", "云服务"],
                "recommended_changes": ["基于真实经历补充 API 设计和数据库优化描述"],
                "truthfulness_warnings": ["不要把未提供的云服务经验写成已掌握"],
            }

        return {
            "job_title": "后端开发工程师",
            "job_type": "后端开发",
            "required_skills": ["FastAPI", "SQL"],
            "bonus_skills": ["缓存", "云服务"],
            "responsibilities": ["负责后端服务开发"],
            "keywords": ["FastAPI", "SQL", "缓存", "云服务"],
            "resume_focus_suggestions": ["突出后端 API 和数据库经验"],
        }

    monkeypatch.setattr(AIClient, "chat_json", fake_chat_json)

    resume_response = client.post(
        "/resume-profiles",
        json={"title": "后端开发通用简历", "raw_markdown": "# 我的简历\n熟悉 FastAPI 和 SQL。"},
    )
    project_response = client.post(
        "/projects",
        json={
            "name": "ResumeFit Demo",
            "project_type": "Web 应用",
            "role": "独立开发",
            "tech_stack": ["FastAPI", "SQLite"],
            "description": "智能简历定制平台 Demo",
            "user_contribution": "负责后端 API 和数据库设计",
            "work_url": "https://example.com",
        },
    )
    job_response = client.post(
        "/job-descriptions",
        json={
            "company_name": "示例公司",
            "job_title": "后端开发工程师",
            "raw_text": "负责 FastAPI 服务开发，熟悉 SQL、缓存和云服务。",
        },
    )
    job_description_id = job_response.json()["id"]
    analyze_response = client.post(f"/job-descriptions/{job_description_id}/analyze")
    assert analyze_response.status_code == 200

    match_response = client.post(
        "/match-reports",
        json={
            "resume_profile_id": resume_response.json()["id"],
            "project_ids": [project_response.json()["id"]],
            "job_description_id": job_description_id,
        },
    )

    assert match_response.status_code == 201
    report = match_response.json()
    assert report["user_id"] == 1
    assert report["resume_profile_id"] == resume_response.json()["id"]
    assert report["project_ids"] == [project_response.json()["id"]]
    assert report["job_description_id"] == job_description_id
    assert report["job_analysis_id"] == analyze_response.json()["id"]
    assert report["score"] == 82
    assert report["strengths"] == ["简历和项目都体现了 FastAPI 服务开发经验"]
    assert report["weaknesses"] == ["缓存和云服务经验表达不足"]
    assert report["missing_keywords"] == ["缓存", "云服务"]
    assert report["recommended_changes"] == ["基于真实经历补充 API 设计和数据库优化描述"]
    assert report["truthfulness_warnings"] == ["不要把未提供的云服务经验写成已掌握"]
    assert report["model_name"] == "deepseek-chat"


def test_match_reports_require_login(anonymous_client: TestClient) -> None:
    response = anonymous_client.get("/match-reports")

    assert response.status_code == 401


def test_match_reports_are_isolated_by_user(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    user_a_token = _register_test_user(client, email="match-a@example.com")
    user_b_token = _register_test_user(client, email="match-b@example.com")
    user_a_headers = _auth_headers(user_a_token)
    user_b_headers = _auth_headers(user_b_token)

    ids = _resume_version_context(client, monkeypatch, headers=user_a_headers)

    user_a_response = client.get("/match-reports", headers=user_a_headers)
    user_b_response = client.get("/match-reports", headers=user_b_headers)

    assert user_a_response.status_code == 200
    assert [report["id"] for report in user_a_response.json()] == [ids["match_report_id"]]
    assert user_b_response.status_code == 200
    assert user_b_response.json() == []


def test_match_report_rejects_cross_user_inputs(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    user_a_token = _register_test_user(client, email="match-input-a@example.com")
    user_b_token = _register_test_user(client, email="match-input-b@example.com")
    user_a_headers = _auth_headers(user_a_token)
    user_b_headers = _auth_headers(user_b_token)

    user_a_ids = _resume_version_context(client, monkeypatch, headers=user_a_headers)
    user_b_ids = _resume_version_context(client, monkeypatch, headers=user_b_headers)

    resume_response = client.post(
        "/match-reports",
        headers=user_b_headers,
        json={
            "resume_profile_id": user_a_ids["resume_profile_id"],
            "project_ids": [user_b_ids["project_id"]],
            "job_description_id": user_b_ids["job_description_id"],
        },
    )
    project_response = client.post(
        "/match-reports",
        headers=user_b_headers,
        json={
            "resume_profile_id": user_b_ids["resume_profile_id"],
            "project_ids": [user_a_ids["project_id"]],
            "job_description_id": user_b_ids["job_description_id"],
        },
    )
    job_response = client.post(
        "/match-reports",
        headers=user_b_headers,
        json={
            "resume_profile_id": user_b_ids["resume_profile_id"],
            "project_ids": [user_b_ids["project_id"]],
            "job_description_id": user_a_ids["job_description_id"],
        },
    )

    assert resume_response.status_code == 404
    assert resume_response.json()["detail"] == "Resume profile was not found."
    assert project_response.status_code == 404
    assert project_response.json()["detail"] == "One or more projects were not found."
    assert job_response.status_code == 404
    assert job_response.json()["detail"] == "Job description was not found."


def test_match_report_requires_project_ids(client: TestClient) -> None:
    response = client.post(
        "/match-reports",
        json={"resume_profile_id": 1, "project_ids": [], "job_description_id": 1},
    )

    assert response.status_code == 422


def test_match_report_requires_analyzed_job_description(client: TestClient) -> None:
    resume_response = client.post(
        "/resume-profiles",
        json={"title": "后端开发通用简历", "raw_markdown": "# 我的简历"},
    )
    project_response = client.post(
        "/projects",
        json={
            "name": "ResumeFit Demo",
            "project_type": "Web 应用",
            "role": "独立开发",
            "tech_stack": ["FastAPI"],
            "description": "智能简历定制平台 Demo",
            "user_contribution": "负责后端 API",
        },
    )
    job_response = client.post(
        "/job-descriptions",
        json={
            "company_name": "示例公司",
            "job_title": "后端开发工程师",
            "raw_text": "负责 FastAPI 服务开发。",
        },
    )

    response = client.post(
        "/match-reports",
        json={
            "resume_profile_id": resume_response.json()["id"],
            "project_ids": [project_response.json()["id"]],
            "job_description_id": job_response.json()["id"],
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Job description has not been analyzed yet."


def test_match_report_returns_not_found_for_missing_inputs(client: TestClient) -> None:
    missing_resume_response = client.post(
        "/match-reports",
        json={"resume_profile_id": 999, "project_ids": [1], "job_description_id": 1},
    )
    assert missing_resume_response.status_code == 404
    assert missing_resume_response.json()["detail"] == "Resume profile was not found."

    resume_response = client.post(
        "/resume-profiles",
        json={"title": "后端开发通用简历", "raw_markdown": "# 我的简历"},
    )
    missing_project_response = client.post(
        "/match-reports",
        json={"resume_profile_id": resume_response.json()["id"], "project_ids": [999], "job_description_id": 1},
    )
    assert missing_project_response.status_code == 404
    assert missing_project_response.json()["detail"] == "One or more projects were not found."


def test_match_report_requires_api_key(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_job_analysis_chat_json(
        self: AIClient,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
    ) -> dict[str, object]:
        return {
            "job_title": "后端开发工程师",
            "job_type": "后端开发",
            "required_skills": ["FastAPI"],
            "bonus_skills": [],
            "responsibilities": ["负责后端服务开发"],
            "keywords": ["FastAPI"],
            "resume_focus_suggestions": ["突出后端 API 经验"],
        }

    monkeypatch.setattr(AIClient, "chat_json", fake_job_analysis_chat_json)
    resume_response = client.post(
        "/resume-profiles",
        json={"title": "后端开发通用简历", "raw_markdown": "# 我的简历"},
    )
    project_response = client.post(
        "/projects",
        json={
            "name": "ResumeFit Demo",
            "project_type": "Web 应用",
            "role": "独立开发",
            "tech_stack": ["FastAPI"],
            "description": "智能简历定制平台 Demo",
            "user_contribution": "负责后端 API",
        },
    )
    job_response = client.post(
        "/job-descriptions",
        json={
            "company_name": "示例公司",
            "job_title": "后端开发工程师",
            "raw_text": "负责 FastAPI 服务开发。",
        },
    )
    job_description_id = job_response.json()["id"]
    assert client.post(f"/job-descriptions/{job_description_id}/analyze").status_code == 200

    monkeypatch.setattr(settings, "ai_api_key", None)
    monkeypatch.setattr(
        AIClient,
        "chat_json",
        lambda self, **_: self._ensure_configured(),
    )
    response = client.post(
        "/match-reports",
        json={
            "resume_profile_id": resume_response.json()["id"],
            "project_ids": [project_response.json()["id"]],
            "job_description_id": job_description_id,
        },
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "AI_API_KEY is not configured."


def test_match_report_handles_invalid_ai_response(
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
        if "Match Scorer v1" in system_prompt:
            raise AIResponseError("AI response was not valid JSON.")
        return {
            "job_title": "后端开发工程师",
            "job_type": "后端开发",
            "required_skills": ["FastAPI"],
            "bonus_skills": [],
            "responsibilities": ["负责后端服务开发"],
            "keywords": ["FastAPI"],
            "resume_focus_suggestions": ["突出后端 API 经验"],
        }

    monkeypatch.setattr(AIClient, "chat_json", fake_chat_json)
    resume_response = client.post(
        "/resume-profiles",
        json={"title": "后端开发通用简历", "raw_markdown": "# 我的简历"},
    )
    project_response = client.post(
        "/projects",
        json={
            "name": "ResumeFit Demo",
            "project_type": "Web 应用",
            "role": "独立开发",
            "tech_stack": ["FastAPI"],
            "description": "智能简历定制平台 Demo",
            "user_contribution": "负责后端 API",
        },
    )
    job_response = client.post(
        "/job-descriptions",
        json={
            "company_name": "示例公司",
            "job_title": "后端开发工程师",
            "raw_text": "负责 FastAPI 服务开发。",
        },
    )
    job_description_id = job_response.json()["id"]
    assert client.post(f"/job-descriptions/{job_description_id}/analyze").status_code == 200

    response = client.post(
        "/match-reports",
        json={
            "resume_profile_id": resume_response.json()["id"],
            "project_ids": [project_response.json()["id"]],
            "job_description_id": job_description_id,
        },
    )

    assert response.status_code == 502
    assert response.json()["detail"] == "AI response was not valid JSON."


def _resume_version_context(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    *,
    headers: dict[str, str] | None = None,
) -> dict[str, int]:
    def fake_chat_json(
        self: AIClient,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
    ) -> dict[str, object]:
        if "Resume Writer v1" in system_prompt:
            assert "Backend General Resume" in user_prompt
            assert "ResumeFit Demo" in user_prompt
            assert "Backend Developer" in user_prompt
            assert temperature == 0.2
            return {
                "markdown": "# Backend Developer\n\n## Projects\n- ResumeFit Demo: Built FastAPI APIs and SQLite persistence.",
                "change_explanations": [
                    {
                        "section": "Projects",
                        "reason": "Highlighted the selected project because it directly supports the JD requirements.",
                        "source": "ResumeFit Demo project and match report",
                        "uncertain": False,
                    }
                ],
            }

        if "Match Scorer v1" in system_prompt:
            return {
                "score": 86,
                "strengths": ["FastAPI and SQL experience are supported by the provided resume and project."],
                "weaknesses": ["Cloud service experience is not clearly supported by the provided materials."],
                "missing_keywords": ["Cloud services"],
                "recommended_changes": ["Emphasize backend API and database work without adding new facts."],
                "truthfulness_warnings": ["Do not claim cloud service ownership unless the user provides evidence."],
            }

        return {
            "job_title": "Backend Developer",
            "job_type": "Backend",
            "required_skills": ["FastAPI", "SQL"],
            "bonus_skills": ["Cloud services"],
            "responsibilities": ["Build backend services."],
            "keywords": ["FastAPI", "SQL", "Cloud services"],
            "resume_focus_suggestions": ["Emphasize API and database experience."],
        }

    monkeypatch.setattr(AIClient, "chat_json", fake_chat_json)

    resume_response = client.post(
        "/resume-profiles",
        **_request_kwargs(headers),
        json={
            "title": "Backend General Resume",
            "raw_markdown": "# Resume\nExperienced with FastAPI and SQL.",
        },
    )
    project_response = client.post(
        "/projects",
        **_request_kwargs(headers),
        json={
            "name": "ResumeFit Demo",
            "project_type": "Web app",
            "role": "Solo developer",
            "tech_stack": ["FastAPI", "SQLite"],
            "description": "A demo platform for resume tailoring.",
            "user_contribution": "Built backend APIs and database persistence.",
            "work_url": "https://example.com",
        },
    )
    job_response = client.post(
        "/job-descriptions",
        **_request_kwargs(headers),
        json={
            "company_name": "Example Co",
            "job_title": "Backend Developer",
            "raw_text": "Build FastAPI services, use SQL, and understand cloud services.",
        },
    )
    job_description_id = job_response.json()["id"]
    analysis_response = client.post(
        f"/job-descriptions/{job_description_id}/analyze",
        **_request_kwargs(headers),
    )
    assert analysis_response.status_code == 200

    match_response = client.post(
        "/match-reports",
        **_request_kwargs(headers),
        json={
            "resume_profile_id": resume_response.json()["id"],
            "project_ids": [project_response.json()["id"]],
            "job_description_id": job_description_id,
        },
    )
    assert match_response.status_code == 201

    return {
        "resume_profile_id": resume_response.json()["id"],
        "project_id": project_response.json()["id"],
        "job_description_id": job_description_id,
        "job_analysis_id": analysis_response.json()["id"],
        "match_report_id": match_response.json()["id"],
    }


def test_resume_versions_require_login(anonymous_client: TestClient) -> None:
    response = anonymous_client.get("/resume-versions")

    assert response.status_code == 401


def test_generate_resume_version_with_mock_ai(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ids = _resume_version_context(client, monkeypatch)
    list_match_reports_response = client.get("/match-reports")
    assert list_match_reports_response.status_code == 200
    assert list_match_reports_response.json()[0]["id"] == ids["match_report_id"]

    response = client.post(
        "/resume-versions/generate",
        json={
            "resume_profile_id": ids["resume_profile_id"],
            "project_ids": [ids["project_id"]],
            "job_description_id": ids["job_description_id"],
            "match_report_id": ids["match_report_id"],
        },
    )

    assert response.status_code == 201
    resume_version = response.json()
    assert resume_version["user_id"] == 1
    assert resume_version["resume_profile_id"] == ids["resume_profile_id"]
    assert resume_version["job_description_id"] == ids["job_description_id"]
    assert resume_version["match_report_id"] == ids["match_report_id"]
    assert resume_version["version_type"] == "tailored"
    assert "ResumeFit Demo" in resume_version["content_markdown"]
    assert resume_version["change_explanations"] == [
        {
            "section": "Projects",
            "reason": "Highlighted the selected project because it directly supports the JD requirements.",
            "source": "ResumeFit Demo project and match report",
            "uncertain": False,
        }
    ]
    assert resume_version["model_name"] == "deepseek-chat"


def test_resume_versions_are_isolated_by_user(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    user_a_token = _register_test_user(client, email="version-a@example.com")
    user_b_token = _register_test_user(client, email="version-b@example.com")
    user_a_headers = _auth_headers(user_a_token)
    user_b_headers = _auth_headers(user_b_token)

    ids = _resume_version_context(client, monkeypatch, headers=user_a_headers)
    resume_version_id = _create_generated_resume_version(client, ids, headers=user_a_headers)

    user_a_response = client.get("/resume-versions", headers=user_a_headers)
    user_b_response = client.get("/resume-versions", headers=user_b_headers)

    assert user_a_response.status_code == 200
    assert [version["id"] for version in user_a_response.json()] == [resume_version_id]
    assert user_b_response.status_code == 200
    assert user_b_response.json() == []


def test_resume_version_rejects_another_users_match_report(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user_a_token = _register_test_user(client, email="version-match-a@example.com")
    user_b_token = _register_test_user(client, email="version-match-b@example.com")
    user_a_headers = _auth_headers(user_a_token)
    user_b_headers = _auth_headers(user_b_token)

    user_a_ids = _resume_version_context(client, monkeypatch, headers=user_a_headers)
    user_b_ids = _resume_version_context(client, monkeypatch, headers=user_b_headers)

    response = client.post(
        "/resume-versions/generate",
        headers=user_b_headers,
        json={
            "resume_profile_id": user_b_ids["resume_profile_id"],
            "project_ids": [user_b_ids["project_id"]],
            "job_description_id": user_b_ids["job_description_id"],
            "match_report_id": user_a_ids["match_report_id"],
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Match report was not found."


def test_resume_version_rejects_mismatched_match_report(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ids = _resume_version_context(client, monkeypatch)
    other_resume_response = client.post(
        "/resume-profiles",
        json={"title": "Other Resume", "raw_markdown": "# Other Resume"},
    )

    response = client.post(
        "/resume-versions/generate",
        json={
            "resume_profile_id": other_resume_response.json()["id"],
            "project_ids": [ids["project_id"]],
            "job_description_id": ids["job_description_id"],
            "match_report_id": ids["match_report_id"],
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Match report does not belong to the selected resume profile."


def test_resume_version_requires_api_key(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ids = _resume_version_context(client, monkeypatch)
    monkeypatch.setattr(settings, "ai_api_key", None)
    monkeypatch.setattr(AIClient, "chat_json", lambda self, **_: self._ensure_configured())

    response = client.post(
        "/resume-versions/generate",
        json={
            "resume_profile_id": ids["resume_profile_id"],
            "project_ids": [ids["project_id"]],
            "job_description_id": ids["job_description_id"],
            "match_report_id": ids["match_report_id"],
        },
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "AI_API_KEY is not configured."


def test_resume_version_handles_invalid_ai_response(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ids = _resume_version_context(client, monkeypatch)

    def fake_resume_writer_error(self: AIClient, **_: object) -> dict[str, object]:
        raise AIResponseError("AI response was not valid JSON.")

    monkeypatch.setattr(AIClient, "chat_json", fake_resume_writer_error)

    response = client.post(
        "/resume-versions/generate",
        json={
            "resume_profile_id": ids["resume_profile_id"],
            "project_ids": [ids["project_id"]],
            "job_description_id": ids["job_description_id"],
            "match_report_id": ids["match_report_id"],
        },
    )

    assert response.status_code == 502
    assert response.json()["detail"] == "AI response was not valid JSON."


def test_resume_version_requires_project_ids(client: TestClient) -> None:
    response = client.post(
        "/resume-versions/generate",
        json={
            "resume_profile_id": 1,
            "project_ids": [],
            "job_description_id": 1,
            "match_report_id": 1,
        },
    )

    assert response.status_code == 422


def test_export_resume_version_markdown(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ids = _resume_version_context(client, monkeypatch)
    resume_version_id = _create_generated_resume_version(client, ids)
    monkeypatch.setattr(
        AIClient,
        "chat_json",
        lambda self, **_: (_ for _ in ()).throw(AssertionError("Export must not call AI.")),
    )

    response = client.get(f"/resume-versions/{resume_version_id}/export/markdown")

    assert response.status_code == 200
    assert response.text == "# Backend Developer\n\n## Projects\n- ResumeFit Demo: Built FastAPI APIs and SQLite persistence."
    assert "text/markdown" in response.headers["content-type"]
    content_disposition = response.headers["content-disposition"]
    assert "attachment" in content_disposition
    assert "ResumeFit_Backend_Developer_" in content_disposition
    assert ".md" in content_disposition


def test_export_resume_version_markdown_isolated_by_user(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user_a_token = _register_test_user(client, email="export-a@example.com")
    user_b_token = _register_test_user(client, email="export-b@example.com")
    user_a_headers = _auth_headers(user_a_token)
    user_b_headers = _auth_headers(user_b_token)

    ids = _resume_version_context(client, monkeypatch, headers=user_a_headers)
    resume_version_id = _create_generated_resume_version(client, ids, headers=user_a_headers)
    monkeypatch.setattr(
        AIClient,
        "chat_json",
        lambda self, **_: (_ for _ in ()).throw(AssertionError("Export must not call AI.")),
    )

    user_b_response = client.get(
        f"/resume-versions/{resume_version_id}/export/markdown",
        headers=user_b_headers,
    )
    user_a_response = client.get(
        f"/resume-versions/{resume_version_id}/export/markdown",
        headers=user_a_headers,
    )

    assert user_b_response.status_code == 404
    assert user_b_response.json()["detail"] == "Resume version was not found."
    assert user_a_response.status_code == 200
    assert "ResumeFit Demo" in user_a_response.text


def test_export_resume_version_markdown_sanitizes_filename(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ids = _resume_version_context(client, monkeypatch)
    resume_version_id = _create_generated_resume_version(client, ids)

    db_generator = app.dependency_overrides[get_db]()
    db = next(db_generator)
    try:
        job_description = db.get(JobDescription, ids["job_description_id"])
        assert job_description is not None
        job_description.title = 'Backend: Dev / API*?'
        db.commit()
    finally:
        db.close()
        db_generator.close()

    response = client.get(f"/resume-versions/{resume_version_id}/export/markdown")

    assert response.status_code == 200
    content_disposition = response.headers["content-disposition"]
    assert "ResumeFit_Backend_Dev_API_" in content_disposition
    assert "Backend: Dev / API*?" not in content_disposition


def test_export_resume_version_markdown_returns_not_found(client: TestClient) -> None:
    response = client.get("/resume-versions/999/export/markdown")

    assert response.status_code == 404
    assert response.json()["detail"] == "Resume version was not found."


def _create_generated_resume_version(
    client: TestClient,
    ids: dict[str, int],
    *,
    headers: dict[str, str] | None = None,
) -> int:
    response = client.post(
        "/resume-versions/generate",
        **_request_kwargs(headers),
        json={
            "resume_profile_id": ids["resume_profile_id"],
            "project_ids": [ids["project_id"]],
            "job_description_id": ids["job_description_id"],
            "match_report_id": ids["match_report_id"],
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_dashboard_summary_counts_demo_resources(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ids = _resume_version_context(client, monkeypatch)
    _create_generated_resume_version(client, ids)

    response = client.get("/dashboard/summary")

    assert response.status_code == 200
    assert response.json() == {
        "resume_profile_count": 1,
        "project_count": 1,
        "job_description_count": 1,
        "match_report_count": 1,
        "resume_version_count": 1,
    }


def test_create_truth_check_result_with_mock_ai(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ids = _resume_version_context(client, monkeypatch)
    resume_version_id = _create_generated_resume_version(client, ids)

    def fake_truth_chat_json(
        self: AIClient,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
    ) -> dict[str, object]:
        assert "Truth Checker v1" in system_prompt
        assert "ResumeFit Demo" in user_prompt
        assert "content_markdown" in user_prompt
        assert temperature == 0.1
        return {
            "overall_risk_level": "medium",
            "risky_statements": [
                {
                    "statement": "Built FastAPI APIs and SQLite persistence.",
                    "risk_level": "medium",
                    "risk_type": "unsupported_claim",
                    "reason": "The project supports backend API work, but persistence scope should stay specific.",
                    "evidence_status": "partially_supported",
                    "safer_rewrite": "Built FastAPI API endpoints and SQLite-backed demo persistence.",
                }
            ],
            "safer_rewrites": ["Keep the project description tied to the provided demo scope."],
            "missing_evidence": ["Evidence for production usage or scale was not provided."],
            "interview_risk_points": ["Be ready to explain which API endpoints and tables were implemented."],
            "summary": "The resume is mostly grounded but should keep scope conservative.",
        }

    monkeypatch.setattr(AIClient, "chat_json", fake_truth_chat_json)

    create_response = client.post("/truth-check-results", json={"resume_version_id": resume_version_id})

    assert create_response.status_code == 201
    result = create_response.json()
    assert result["user_id"] == 1
    assert result["resume_version_id"] == resume_version_id
    assert result["overall_risk_level"] == "medium"
    assert result["risky_statements"][0]["risk_type"] == "unsupported_claim"
    assert result["risky_statements"][0]["evidence_status"] == "partially_supported"
    assert result["safer_rewrites"] == ["Keep the project description tied to the provided demo scope."]
    assert result["missing_evidence"] == ["Evidence for production usage or scale was not provided."]
    assert result["interview_risk_points"] == ["Be ready to explain which API endpoints and tables were implemented."]
    assert result["summary"] == "The resume is mostly grounded but should keep scope conservative."
    assert result["model_name"] == "deepseek-chat"

    list_versions_response = client.get("/resume-versions")
    assert list_versions_response.status_code == 200
    assert list_versions_response.json()[0]["id"] == resume_version_id

    list_truth_checks_response = client.get(f"/truth-check-results?resume_version_id={resume_version_id}")
    assert list_truth_checks_response.status_code == 200
    assert list_truth_checks_response.json()[0]["id"] == result["id"]


def test_truth_checks_require_login(anonymous_client: TestClient) -> None:
    create_response = anonymous_client.post("/truth-check-results", json={"resume_version_id": 1})
    list_response = anonymous_client.get("/truth-check-results?resume_version_id=1")

    assert create_response.status_code == 401
    assert list_response.status_code == 401


def test_truth_checks_are_isolated_by_user(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    user_a_token = _register_test_user(client, email="truth-a@example.com")
    user_b_token = _register_test_user(client, email="truth-b@example.com")
    user_a_headers = _auth_headers(user_a_token)
    user_b_headers = _auth_headers(user_b_token)

    ids = _resume_version_context(client, monkeypatch, headers=user_a_headers)
    resume_version_id = _create_generated_resume_version(client, ids, headers=user_a_headers)

    def fake_truth_chat_json(self: AIClient, **_: object) -> dict[str, object]:
        return {
            "overall_risk_level": "low",
            "risky_statements": [],
            "safer_rewrites": ["Keep wording grounded in the provided project."],
            "missing_evidence": [],
            "interview_risk_points": ["Explain the demo scope clearly."],
            "summary": "User A truth check summary.",
        }

    monkeypatch.setattr(AIClient, "chat_json", fake_truth_chat_json)
    user_a_create_response = client.post(
        "/truth-check-results",
        headers=user_a_headers,
        json={"resume_version_id": resume_version_id},
    )
    user_b_create_response = client.post(
        "/truth-check-results",
        headers=user_b_headers,
        json={"resume_version_id": resume_version_id},
    )
    user_a_list_response = client.get(
        f"/truth-check-results?resume_version_id={resume_version_id}",
        headers=user_a_headers,
    )
    user_b_list_response = client.get(
        f"/truth-check-results?resume_version_id={resume_version_id}",
        headers=user_b_headers,
    )

    assert user_a_create_response.status_code == 201
    assert user_a_create_response.json()["summary"] == "User A truth check summary."
    assert user_b_create_response.status_code == 404
    assert user_b_create_response.json()["detail"] == "Resume version was not found."
    assert user_a_list_response.status_code == 200
    assert [result["id"] for result in user_a_list_response.json()] == [user_a_create_response.json()["id"]]
    assert user_b_list_response.status_code == 404
    assert user_b_list_response.json()["detail"] == "Resume version was not found."


def test_truth_check_returns_not_found_for_missing_resume_version(client: TestClient) -> None:
    create_response = client.post("/truth-check-results", json={"resume_version_id": 999})
    list_response = client.get("/truth-check-results?resume_version_id=999")

    assert create_response.status_code == 404
    assert create_response.json()["detail"] == "Resume version was not found."
    assert list_response.status_code == 404
    assert list_response.json()["detail"] == "Resume version was not found."


def test_truth_check_requires_match_report_context(client: TestClient) -> None:
    db_generator = app.dependency_overrides[get_db]()
    db = next(db_generator)
    try:
        resume_version = ResumeVersion(
            user_id=1,
            resume_profile_id=1,
            job_description_id=None,
            match_report_id=None,
            title="Manual Resume",
            version_type="manual",
            content_markdown="# Manual Resume",
            generation_notes=None,
            change_explanations_json="[]",
            risk_report_json=None,
            raw_ai_output_json="{}",
            model_name="test-model",
        )
        db.add(resume_version)
        db.commit()
        db.refresh(resume_version)
        resume_version_id = resume_version.id
    finally:
        db.close()
        db_generator.close()

    response = client.post("/truth-check-results", json={"resume_version_id": resume_version_id})

    assert response.status_code == 400
    assert response.json()["detail"] == "Resume version does not have a match report context."


def test_truth_check_requires_api_key(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ids = _resume_version_context(client, monkeypatch)
    resume_version_id = _create_generated_resume_version(client, ids)
    monkeypatch.setattr(settings, "ai_api_key", None)
    monkeypatch.setattr(AIClient, "chat_json", lambda self, **_: self._ensure_configured())

    response = client.post("/truth-check-results", json={"resume_version_id": resume_version_id})

    assert response.status_code == 503
    assert response.json()["detail"] == "AI_API_KEY is not configured."


def test_truth_check_handles_invalid_ai_response(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ids = _resume_version_context(client, monkeypatch)
    resume_version_id = _create_generated_resume_version(client, ids)

    def fake_truth_error(self: AIClient, **_: object) -> dict[str, object]:
        raise AIResponseError("AI response was not valid JSON.")

    monkeypatch.setattr(AIClient, "chat_json", fake_truth_error)

    response = client.post("/truth-check-results", json={"resume_version_id": resume_version_id})

    assert response.status_code == 502
    assert response.json()["detail"] == "AI response was not valid JSON."


def test_create_interview_question_result_with_mock_ai(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ids = _resume_version_context(client, monkeypatch)
    resume_version_id = _create_generated_resume_version(client, ids)

    def fake_truth_chat_json(self: AIClient, **_: object) -> dict[str, object]:
        return {
            "overall_risk_level": "medium",
            "risky_statements": [
                {
                    "statement": "Built FastAPI APIs and SQLite persistence.",
                    "risk_level": "medium",
                    "risk_type": "unsupported_claim",
                    "reason": "The scope should stay tied to the demo evidence.",
                    "evidence_status": "partially_supported",
                    "safer_rewrite": "Built FastAPI API endpoints and SQLite-backed demo persistence.",
                }
            ],
            "safer_rewrites": ["Keep answers tied to the provided demo scope."],
            "missing_evidence": ["No production usage evidence was provided."],
            "interview_risk_points": ["Be ready to explain which API endpoints and tables were implemented."],
            "summary": "Use conservative wording in interview answers.",
        }

    monkeypatch.setattr(AIClient, "chat_json", fake_truth_chat_json)
    truth_response = client.post("/truth-check-results", json={"resume_version_id": resume_version_id})
    assert truth_response.status_code == 201

    def fake_interview_chat_json(
        self: AIClient,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
    ) -> dict[str, object]:
        assert "Interview Question Predictor v1" in system_prompt
        assert "ResumeFit Demo" in user_prompt
        assert "truth_check_result" in user_prompt
        assert "Be ready to explain which API endpoints and tables were implemented." in user_prompt
        assert temperature == 0.2
        return {
            "questions": [
                {
                    "question": "Can you walk me through the FastAPI endpoints you built?",
                    "reason": "The tailored resume emphasizes FastAPI API work and the JD asks for backend service development.",
                    "related_resume_section": "ResumeFit Demo project",
                    "difficulty": "medium",
                    "suggested_answer": "I can describe the demo API endpoints I implemented and how they connect to SQLite persistence.",
                    "answer_strategy": "Start with the project context, explain personal contribution, then keep scope limited to the demo.",
                    "risk_reminder": "Do not imply production scale or cloud ownership unless more evidence is provided.",
                }
            ],
            "summary": "Focus interview preparation on backend API details and conservative project scope.",
        }

    monkeypatch.setattr(AIClient, "chat_json", fake_interview_chat_json)

    create_response = client.post("/interview-question-results", json={"resume_version_id": resume_version_id})

    assert create_response.status_code == 201
    result = create_response.json()
    assert result["user_id"] == 1
    assert result["resume_version_id"] == resume_version_id
    assert result["questions"][0]["difficulty"] == "medium"
    assert result["questions"][0]["related_resume_section"] == "ResumeFit Demo project"
    assert result["questions"][0]["risk_reminder"] == (
        "Do not imply production scale or cloud ownership unless more evidence is provided."
    )
    assert result["summary"] == "Focus interview preparation on backend API details and conservative project scope."
    assert result["model_name"] == "deepseek-chat"

    list_response = client.get(f"/interview-question-results?resume_version_id={resume_version_id}")
    assert list_response.status_code == 200
    assert list_response.json()[0]["id"] == result["id"]


def test_interview_questions_require_login(anonymous_client: TestClient) -> None:
    create_response = anonymous_client.post("/interview-question-results", json={"resume_version_id": 1})
    list_response = anonymous_client.get("/interview-question-results?resume_version_id=1")

    assert create_response.status_code == 401
    assert list_response.status_code == 401


def test_interview_questions_are_isolated_by_user(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    user_a_token = _register_test_user(client, email="interview-a@example.com")
    user_b_token = _register_test_user(client, email="interview-b@example.com")
    user_a_headers = _auth_headers(user_a_token)
    user_b_headers = _auth_headers(user_b_token)

    ids = _resume_version_context(client, monkeypatch, headers=user_a_headers)
    resume_version_id = _create_generated_resume_version(client, ids, headers=user_a_headers)

    def fake_truth_chat_json(self: AIClient, **_: object) -> dict[str, object]:
        return {
            "overall_risk_level": "medium",
            "risky_statements": [],
            "safer_rewrites": ["Use conservative wording for the demo project."],
            "missing_evidence": [],
            "interview_risk_points": ["User A should explain the demo scope."],
            "summary": "User A truth check summary.",
        }

    monkeypatch.setattr(AIClient, "chat_json", fake_truth_chat_json)
    truth_response = client.post(
        "/truth-check-results",
        headers=user_a_headers,
        json={"resume_version_id": resume_version_id},
    )
    assert truth_response.status_code == 201

    def fake_interview_chat_json(
        self: AIClient,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
    ) -> dict[str, object]:
        assert "Interview Question Predictor v1" in system_prompt
        assert "User A truth check summary." in user_prompt
        assert "User A should explain the demo scope." in user_prompt
        assert temperature == 0.2
        return {
            "questions": [
                {
                    "question": "How did you implement the ResumeFit demo APIs?",
                    "reason": "The resume emphasizes backend API work.",
                    "related_resume_section": "ResumeFit Demo project",
                    "difficulty": "medium",
                    "suggested_answer": "Describe the demo API endpoints and SQLite persistence honestly.",
                    "answer_strategy": "Keep the answer tied to provided evidence.",
                    "risk_reminder": "Do not imply production scale.",
                }
            ],
            "summary": "User A interview question summary.",
        }

    monkeypatch.setattr(AIClient, "chat_json", fake_interview_chat_json)
    user_a_create_response = client.post(
        "/interview-question-results",
        headers=user_a_headers,
        json={"resume_version_id": resume_version_id},
    )
    user_b_create_response = client.post(
        "/interview-question-results",
        headers=user_b_headers,
        json={"resume_version_id": resume_version_id},
    )
    user_a_list_response = client.get(
        f"/interview-question-results?resume_version_id={resume_version_id}",
        headers=user_a_headers,
    )
    user_b_list_response = client.get(
        f"/interview-question-results?resume_version_id={resume_version_id}",
        headers=user_b_headers,
    )

    assert user_a_create_response.status_code == 201
    assert user_a_create_response.json()["summary"] == "User A interview question summary."
    assert user_b_create_response.status_code == 404
    assert user_b_create_response.json()["detail"] == "Resume version was not found."
    assert user_a_list_response.status_code == 200
    assert [result["id"] for result in user_a_list_response.json()] == [user_a_create_response.json()["id"]]
    assert user_b_list_response.status_code == 404
    assert user_b_list_response.json()["detail"] == "Resume version was not found."


def test_interview_question_returns_not_found_for_missing_resume_version(client: TestClient) -> None:
    create_response = client.post("/interview-question-results", json={"resume_version_id": 999})
    list_response = client.get("/interview-question-results?resume_version_id=999")

    assert create_response.status_code == 404
    assert create_response.json()["detail"] == "Resume version was not found."
    assert list_response.status_code == 404
    assert list_response.json()["detail"] == "Resume version was not found."


def test_interview_question_requires_match_report_context(client: TestClient) -> None:
    db_generator = app.dependency_overrides[get_db]()
    db = next(db_generator)
    try:
        resume_version = ResumeVersion(
            user_id=1,
            resume_profile_id=1,
            job_description_id=None,
            match_report_id=None,
            title="Manual Resume",
            version_type="manual",
            content_markdown="# Manual Resume",
            generation_notes=None,
            change_explanations_json="[]",
            risk_report_json=None,
            raw_ai_output_json="{}",
            model_name="test-model",
        )
        db.add(resume_version)
        db.commit()
        db.refresh(resume_version)
        resume_version_id = resume_version.id
    finally:
        db.close()
        db_generator.close()

    response = client.post("/interview-question-results", json={"resume_version_id": resume_version_id})

    assert response.status_code == 400
    assert response.json()["detail"] == "Resume version does not have a match report context."


def test_interview_question_requires_api_key(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ids = _resume_version_context(client, monkeypatch)
    resume_version_id = _create_generated_resume_version(client, ids)
    monkeypatch.setattr(settings, "ai_api_key", None)
    monkeypatch.setattr(AIClient, "chat_json", lambda self, **_: self._ensure_configured())

    response = client.post("/interview-question-results", json={"resume_version_id": resume_version_id})

    assert response.status_code == 503
    assert response.json()["detail"] == "AI_API_KEY is not configured."


def test_interview_question_handles_invalid_ai_response(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ids = _resume_version_context(client, monkeypatch)
    resume_version_id = _create_generated_resume_version(client, ids)

    def fake_interview_error(self: AIClient, **_: object) -> dict[str, object]:
        raise AIResponseError("AI response was not valid JSON.")

    monkeypatch.setattr(AIClient, "chat_json", fake_interview_error)

    response = client.post("/interview-question-results", json={"resume_version_id": resume_version_id})

    assert response.status_code == 502
    assert response.json()["detail"] == "AI response was not valid JSON."
