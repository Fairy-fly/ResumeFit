from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.job_description import JobDescription
from app.models.match_report import MatchReport
from app.models.project import Project
from app.models.resume_profile import ResumeProfile
from app.models.resume_version import ResumeVersion


class DashboardRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def count_resume_profiles(self, *, user_id: int) -> int:
        return self._count_by_user(ResumeProfile, ResumeProfile.user_id, user_id=user_id)

    def count_projects(self, *, user_id: int) -> int:
        return self._count_by_user(Project, Project.user_id, user_id=user_id)

    def count_job_descriptions(self, *, user_id: int) -> int:
        return self._count_by_user(JobDescription, JobDescription.user_id, user_id=user_id)

    def count_match_reports(self, *, user_id: int) -> int:
        return self._count_by_user(MatchReport, MatchReport.user_id, user_id=user_id)

    def count_resume_versions(self, *, user_id: int) -> int:
        return self._count_by_user(ResumeVersion, ResumeVersion.user_id, user_id=user_id)

    def _count_by_user(self, model: type[Any], user_id_column: Any, *, user_id: int) -> int:
        statement = select(func.count()).select_from(model).where(user_id_column == user_id)
        return int(self.db.scalar(statement) or 0)
