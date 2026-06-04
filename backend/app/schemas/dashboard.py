from pydantic import BaseModel


class DashboardSummaryRead(BaseModel):
    resume_profile_count: int
    project_count: int
    job_description_count: int
    match_report_count: int
    resume_version_count: int
