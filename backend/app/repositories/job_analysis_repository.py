from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.job_analysis import JobAnalysis


class JobAnalysisRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert(
        self,
        *,
        job_description_id: int,
        job_title: str,
        job_type: str,
        responsibilities_json: str,
        required_skills_json: str,
        preferred_skills_json: str,
        keywords_json: str,
        resume_focus_suggestions_json: str,
        raw_ai_output_json: str,
        model_name: str,
    ) -> JobAnalysis:
        analysis = self.get_by_job_description_id(job_description_id=job_description_id)

        if analysis is None:
            analysis = JobAnalysis(job_description_id=job_description_id)

        analysis.job_title = job_title
        analysis.job_type = job_type
        analysis.responsibilities_json = responsibilities_json
        analysis.required_skills_json = required_skills_json
        analysis.preferred_skills_json = preferred_skills_json
        analysis.keywords_json = keywords_json
        analysis.resume_focus_suggestions_json = resume_focus_suggestions_json
        analysis.raw_ai_output_json = raw_ai_output_json
        analysis.model_name = model_name

        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)
        return analysis

    def get_by_job_description_id(self, *, job_description_id: int) -> JobAnalysis | None:
        statement = select(JobAnalysis).where(JobAnalysis.job_description_id == job_description_id)
        return self.db.scalar(statement)
