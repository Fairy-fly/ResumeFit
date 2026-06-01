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


def _resume_version_context(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> dict[str, int]:
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
        json={
            "title": "Backend General Resume",
            "raw_markdown": "# Resume\nExperienced with FastAPI and SQL.",
        },
    )
    project_response = client.post(
        "/projects",
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
        json={
            "company_name": "Example Co",
            "job_title": "Backend Developer",
            "raw_text": "Build FastAPI services, use SQL, and understand cloud services.",
        },
    )
    job_description_id = job_response.json()["id"]
    analysis_response = client.post(f"/job-descriptions/{job_description_id}/analyze")
    assert analysis_response.status_code == 200

    match_response = client.post(
        "/match-reports",
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
