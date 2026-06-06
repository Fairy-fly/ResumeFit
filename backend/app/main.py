from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.analyses import router as analyses_router
from app.api.routes.auth import router as auth_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.health import router as health_router
from app.api.routes.interview_questions import router as interview_questions_router
from app.api.routes.job_descriptions import router as job_descriptions_router
from app.api.routes.projects import router as projects_router
from app.api.routes.resume_profiles import router as resume_profiles_router
from app.api.routes.resume_versions import router as resume_versions_router
from app.api.routes.truth_checks import router as truth_checks_router
from app.api.routes.usage import router as usage_router
from app.core.config import settings
from app.core.database import init_db
from app.core.security import ensure_user_auth_columns


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Content-Disposition"],
    )

    @app.on_event("startup")
    def on_startup() -> None:
        init_db()
        if getattr(init_db, "__name__", "") == "init_db":
            ensure_user_auth_columns()

    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(dashboard_router)
    app.include_router(resume_profiles_router)
    app.include_router(projects_router)
    app.include_router(job_descriptions_router)
    app.include_router(analyses_router)
    app.include_router(resume_versions_router)
    app.include_router(truth_checks_router)
    app.include_router(interview_questions_router)
    app.include_router(usage_router)
    return app


app = create_app()
