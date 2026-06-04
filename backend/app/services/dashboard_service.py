from sqlalchemy.orm import Session

from app.repositories.dashboard_repository import DashboardRepository
from app.schemas.dashboard import DashboardSummaryRead

DEFAULT_DEMO_USER_ID = 1


class DashboardService:
    def __init__(self, db: Session) -> None:
        self.dashboard_repository = DashboardRepository(db)

    def get_summary(self) -> DashboardSummaryRead:
        user_id = DEFAULT_DEMO_USER_ID
        return DashboardSummaryRead(
            resume_profile_count=self.dashboard_repository.count_resume_profiles(user_id=user_id),
            project_count=self.dashboard_repository.count_projects(user_id=user_id),
            job_description_count=self.dashboard_repository.count_job_descriptions(user_id=user_id),
            match_report_count=self.dashboard_repository.count_match_reports(user_id=user_id),
            resume_version_count=self.dashboard_repository.count_resume_versions(user_id=user_id),
        )
