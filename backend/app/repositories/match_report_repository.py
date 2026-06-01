from sqlalchemy.orm import Session

from app.models.match_report import MatchReport


class MatchReportRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        user_id: int,
        resume_profile_id: int,
        project_ids_json: str,
        job_description_id: int,
        job_analysis_id: int,
        overall_score: int,
        strengths_json: str,
        gaps_json: str,
        missing_keywords_json: str,
        suggestions_json: str,
        truthfulness_warnings_json: str,
        raw_ai_output_json: str,
        model_name: str,
    ) -> MatchReport:
        match_report = MatchReport(
            user_id=user_id,
            resume_profile_id=resume_profile_id,
            project_ids_json=project_ids_json,
            job_description_id=job_description_id,
            job_analysis_id=job_analysis_id,
            overall_score=overall_score,
            strengths_json=strengths_json,
            gaps_json=gaps_json,
            missing_keywords_json=missing_keywords_json,
            suggestions_json=suggestions_json,
            truthfulness_warnings_json=truthfulness_warnings_json,
            raw_ai_output_json=raw_ai_output_json,
            model_name=model_name,
        )
        self.db.add(match_report)
        self.db.commit()
        self.db.refresh(match_report)
        return match_report
