import json

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.ai.client import AIClient, AIResponseError
from app.ai.prompt_loader import PromptLoader
from app.models.job_analysis import JobAnalysis
from app.models.job_description import JobDescription
from app.models.match_report import MatchReport
from app.models.project import Project
from app.models.resume_profile import ResumeProfile
from app.repositories.job_analysis_repository import JobAnalysisRepository
from app.repositories.job_description_repository import JobDescriptionRepository
from app.repositories.match_report_repository import MatchReportRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.resume_profile_repository import ResumeProfileRepository
from app.schemas.match_report import MatchReportAIResult, MatchReportCreate, MatchReportRead

DEFAULT_USER_ID = 1
MATCH_SCORER_PROMPT = "match_scorer_v1.md"


class MatchReportNotFoundError(RuntimeError):
    pass


class JobAnalysisRequiredError(RuntimeError):
    pass


class MatchReportService:
    def __init__(
        self,
        db: Session,
        *,
        ai_client: AIClient | None = None,
        prompt_loader: PromptLoader | None = None,
    ) -> None:
        self.resume_profile_repository = ResumeProfileRepository(db)
        self.project_repository = ProjectRepository(db)
        self.job_description_repository = JobDescriptionRepository(db)
        self.job_analysis_repository = JobAnalysisRepository(db)
        self.match_report_repository = MatchReportRepository(db)
        self.ai_client = ai_client or AIClient()
        self.prompt_loader = prompt_loader or PromptLoader()

    def create_match_report(self, payload: MatchReportCreate) -> MatchReportRead:
        resume_profile = self._get_resume_profile(payload.resume_profile_id)
        projects = self._get_projects(payload.project_ids)
        job_description, job_analysis = self._get_job_context(payload)

        raw_ai_output = self.ai_client.chat_json(
            system_prompt=self.prompt_loader.load(MATCH_SCORER_PROMPT),
            user_prompt=self._build_user_prompt(
                resume_profile=resume_profile,
                projects=projects,
                job_description=job_description,
                job_analysis=job_analysis,
            ),
            temperature=0.1,
        )
        try:
            parsed = MatchReportAIResult.model_validate(raw_ai_output)
        except ValidationError as exc:
            raise AIResponseError("AI response JSON did not match the match report schema.") from exc

        match_report = self.match_report_repository.create(
            user_id=DEFAULT_USER_ID,
            resume_profile_id=resume_profile.id,
            project_ids_json=self._to_json(payload.project_ids),
            job_description_id=job_description.id,
            job_analysis_id=job_analysis.id,
            overall_score=parsed.score,
            strengths_json=self._to_json(parsed.strengths),
            gaps_json=self._to_json(parsed.weaknesses),
            missing_keywords_json=self._to_json(parsed.missing_keywords),
            suggestions_json=self._to_json(parsed.recommended_changes),
            truthfulness_warnings_json=self._to_json(parsed.truthfulness_warnings),
            raw_ai_output_json=self._to_json(raw_ai_output),
            model_name=self.ai_client.model_name,
        )
        return self._to_read_model(match_report)

    def list_match_reports(self) -> list[MatchReportRead]:
        return [
            self._to_read_model(match_report)
            for match_report in self.match_report_repository.list_by_user(user_id=DEFAULT_USER_ID)
        ]

    def _get_resume_profile(self, resume_profile_id: int) -> ResumeProfile:
        resume_profile = self.resume_profile_repository.get_by_id_for_user(
            resume_profile_id=resume_profile_id,
            user_id=DEFAULT_USER_ID,
        )
        if resume_profile is None:
            raise MatchReportNotFoundError("Resume profile was not found.")
        return resume_profile

    def _get_projects(self, project_ids: list[int]) -> list[Project]:
        projects = self.project_repository.list_by_ids_for_user(project_ids=project_ids, user_id=DEFAULT_USER_ID)
        found_project_ids = {project.id for project in projects}
        missing_project_ids = [project_id for project_id in project_ids if project_id not in found_project_ids]
        if missing_project_ids:
            raise MatchReportNotFoundError("One or more projects were not found.")
        return sorted(projects, key=lambda project: project_ids.index(project.id))

    def _get_job_context(self, payload: MatchReportCreate) -> tuple[JobDescription, JobAnalysis]:
        if payload.job_analysis_id is not None:
            job_analysis = self.job_analysis_repository.get_by_id(job_analysis_id=payload.job_analysis_id)
            if job_analysis is None:
                raise MatchReportNotFoundError("Job analysis was not found.")
            job_description = self.job_description_repository.get_by_id_for_user(
                job_description_id=job_analysis.job_description_id,
                user_id=DEFAULT_USER_ID,
            )
            if job_description is None:
                raise MatchReportNotFoundError("Job description was not found.")
            return job_description, job_analysis

        if payload.job_description_id is None:
            raise MatchReportNotFoundError("Job description was not found.")

        job_description = self.job_description_repository.get_by_id_for_user(
            job_description_id=payload.job_description_id,
            user_id=DEFAULT_USER_ID,
        )
        if job_description is None:
            raise MatchReportNotFoundError("Job description was not found.")

        job_analysis = self.job_analysis_repository.get_by_job_description_id(job_description_id=job_description.id)
        if job_analysis is None:
            raise JobAnalysisRequiredError("Job description has not been analyzed yet.")
        return job_description, job_analysis

    def _build_user_prompt(
        self,
        *,
        resume_profile: ResumeProfile,
        projects: list[Project],
        job_description: JobDescription,
        job_analysis: JobAnalysis,
    ) -> str:
        payload = {
            "resume_profile": {
                "id": resume_profile.id,
                "title": resume_profile.title,
                "raw_markdown": resume_profile.raw_markdown,
            },
            "projects": [self._project_to_prompt(project) for project in projects],
            "job_description": {
                "id": job_description.id,
                "company_name": job_description.company_name,
                "job_title": job_description.title,
                "raw_text": job_description.raw_text,
            },
            "job_analysis": {
                "id": job_analysis.id,
                "job_title": job_analysis.job_title,
                "job_type": job_analysis.job_type,
                "responsibilities": self._from_json_list(job_analysis.responsibilities_json),
                "required_skills": self._from_json_list(job_analysis.required_skills_json),
                "bonus_skills": self._from_json_list(job_analysis.preferred_skills_json),
                "keywords": self._from_json_list(job_analysis.keywords_json),
                "resume_focus_suggestions": self._from_json_list(job_analysis.resume_focus_suggestions_json),
            },
        }
        return json.dumps(payload, ensure_ascii=False, indent=2)

    def _project_to_prompt(self, project: Project) -> dict[str, object]:
        return {
            "id": project.id,
            "name": project.name,
            "project_type": project.project_type,
            "role": project.role,
            "tech_stack": self._from_json_list(project.tech_stack_json),
            "description": project.description,
            "user_contribution": project.user_contribution,
            "evidence_links": self._from_json_list(project.evidence_links_json),
            "resume_description": project.resume_description,
        }

    def _to_read_model(self, match_report: MatchReport) -> MatchReportRead:
        return MatchReportRead(
            id=match_report.id,
            user_id=match_report.user_id,
            resume_profile_id=match_report.resume_profile_id,
            project_ids=self._from_json_int_list(match_report.project_ids_json),
            job_description_id=match_report.job_description_id,
            job_analysis_id=match_report.job_analysis_id,
            score=match_report.overall_score,
            strengths=self._from_json_list(match_report.strengths_json),
            weaknesses=self._from_json_list(match_report.gaps_json),
            missing_keywords=self._from_json_list(match_report.missing_keywords_json),
            recommended_changes=self._from_json_list(match_report.suggestions_json),
            truthfulness_warnings=self._from_json_list(match_report.truthfulness_warnings_json),
            model_name=match_report.model_name,
            created_at=match_report.created_at,
            updated_at=match_report.updated_at,
        )

    def _to_json(self, value: object) -> str:
        return json.dumps(value, ensure_ascii=False)

    def _from_json_list(self, value: str | None) -> list[str]:
        if value is None:
            return []
        parsed = json.loads(value)
        if isinstance(parsed, list):
            return [str(item) for item in parsed]
        return []

    def _from_json_int_list(self, value: str) -> list[int]:
        parsed = json.loads(value)
        if isinstance(parsed, list):
            return [int(item) for item in parsed]
        return []
