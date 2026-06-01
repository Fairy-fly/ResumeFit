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
from app.models.resume_version import ResumeVersion
from app.repositories.job_analysis_repository import JobAnalysisRepository
from app.repositories.job_description_repository import JobDescriptionRepository
from app.repositories.match_report_repository import MatchReportRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.resume_profile_repository import ResumeProfileRepository
from app.repositories.resume_version_repository import ResumeVersionRepository
from app.schemas.resume_version import ResumeVersionGenerate, ResumeVersionRead, ResumeWriterAIResult

DEFAULT_USER_ID = 1
RESUME_WRITER_PROMPT = "resume_writer_v1.md"


class ResumeGenerationNotFoundError(RuntimeError):
    pass


class ResumeGenerationValidationError(RuntimeError):
    pass


class JobAnalysisRequiredError(RuntimeError):
    pass


class ResumeGenerationService:
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
        self.resume_version_repository = ResumeVersionRepository(db)
        self.ai_client = ai_client or AIClient()
        self.prompt_loader = prompt_loader or PromptLoader()

    def generate_resume_version(self, payload: ResumeVersionGenerate) -> ResumeVersionRead:
        resume_profile = self._get_resume_profile(payload.resume_profile_id)
        projects = self._get_projects(payload.project_ids)
        job_description, job_analysis = self._get_job_context(payload)
        match_report = self._get_match_report(payload.match_report_id)
        self._validate_match_report(
            match_report=match_report,
            resume_profile=resume_profile,
            project_ids=payload.project_ids,
            job_description=job_description,
            job_analysis=job_analysis,
        )

        raw_ai_output = self.ai_client.chat_json(
            system_prompt=self.prompt_loader.load(RESUME_WRITER_PROMPT),
            user_prompt=self._build_user_prompt(
                resume_profile=resume_profile,
                projects=projects,
                job_description=job_description,
                job_analysis=job_analysis,
                match_report=match_report,
            ),
            temperature=0.2,
        )
        try:
            parsed = ResumeWriterAIResult.model_validate(raw_ai_output)
        except ValidationError as exc:
            raise AIResponseError("AI response JSON did not match the resume writer schema.") from exc

        resume_version = self.resume_version_repository.create(
            user_id=DEFAULT_USER_ID,
            resume_profile_id=resume_profile.id,
            job_description_id=job_description.id,
            match_report_id=match_report.id,
            title=f"{job_description.title} 定制简历",
            version_type="tailored",
            content_markdown=parsed.markdown,
            generation_notes="基于用户选择的简历、项目、JD 分析和匹配报告生成。",
            change_explanations_json=self._to_json([item.model_dump() for item in parsed.change_explanations]),
            raw_ai_output_json=self._to_json(raw_ai_output),
            model_name=self.ai_client.model_name,
        )
        return self._to_read_model(resume_version)

    def _get_resume_profile(self, resume_profile_id: int) -> ResumeProfile:
        resume_profile = self.resume_profile_repository.get_by_id_for_user(
            resume_profile_id=resume_profile_id,
            user_id=DEFAULT_USER_ID,
        )
        if resume_profile is None:
            raise ResumeGenerationNotFoundError("Resume profile was not found.")
        return resume_profile

    def _get_projects(self, project_ids: list[int]) -> list[Project]:
        projects = self.project_repository.list_by_ids_for_user(project_ids=project_ids, user_id=DEFAULT_USER_ID)
        found_project_ids = {project.id for project in projects}
        missing_project_ids = [project_id for project_id in project_ids if project_id not in found_project_ids]
        if missing_project_ids:
            raise ResumeGenerationNotFoundError("One or more projects were not found.")
        return sorted(projects, key=lambda project: project_ids.index(project.id))

    def _get_job_context(self, payload: ResumeVersionGenerate) -> tuple[JobDescription, JobAnalysis]:
        if payload.job_analysis_id is not None:
            job_analysis = self.job_analysis_repository.get_by_id(job_analysis_id=payload.job_analysis_id)
            if job_analysis is None:
                raise ResumeGenerationNotFoundError("Job analysis was not found.")
            job_description = self.job_description_repository.get_by_id_for_user(
                job_description_id=job_analysis.job_description_id,
                user_id=DEFAULT_USER_ID,
            )
            if job_description is None:
                raise ResumeGenerationNotFoundError("Job description was not found.")
            return job_description, job_analysis

        if payload.job_description_id is None:
            raise ResumeGenerationNotFoundError("Job description was not found.")

        job_description = self.job_description_repository.get_by_id_for_user(
            job_description_id=payload.job_description_id,
            user_id=DEFAULT_USER_ID,
        )
        if job_description is None:
            raise ResumeGenerationNotFoundError("Job description was not found.")

        job_analysis = self.job_analysis_repository.get_by_job_description_id(job_description_id=job_description.id)
        if job_analysis is None:
            raise JobAnalysisRequiredError("Job description has not been analyzed yet.")
        return job_description, job_analysis

    def _get_match_report(self, match_report_id: int) -> MatchReport:
        match_report = self.match_report_repository.get_by_id_for_user(
            match_report_id=match_report_id,
            user_id=DEFAULT_USER_ID,
        )
        if match_report is None:
            raise ResumeGenerationNotFoundError("Match report was not found.")
        return match_report

    def _validate_match_report(
        self,
        *,
        match_report: MatchReport,
        resume_profile: ResumeProfile,
        project_ids: list[int],
        job_description: JobDescription,
        job_analysis: JobAnalysis,
    ) -> None:
        if match_report.resume_profile_id != resume_profile.id:
            raise ResumeGenerationValidationError("Match report does not belong to the selected resume profile.")
        if match_report.job_description_id != job_description.id:
            raise ResumeGenerationValidationError("Match report does not belong to the selected job description.")
        if match_report.job_analysis_id != job_analysis.id:
            raise ResumeGenerationValidationError("Match report does not belong to the selected job analysis.")
        if sorted(self._from_json_int_list(match_report.project_ids_json)) != sorted(project_ids):
            raise ResumeGenerationValidationError("Match report does not belong to the selected projects.")

    def _build_user_prompt(
        self,
        *,
        resume_profile: ResumeProfile,
        projects: list[Project],
        job_description: JobDescription,
        job_analysis: JobAnalysis,
        match_report: MatchReport,
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
            "match_report": {
                "id": match_report.id,
                "score": match_report.overall_score,
                "strengths": self._from_json_list(match_report.strengths_json),
                "weaknesses": self._from_json_list(match_report.gaps_json),
                "missing_keywords": self._from_json_list(match_report.missing_keywords_json),
                "recommended_changes": self._from_json_list(match_report.suggestions_json),
                "truthfulness_warnings": self._from_json_list(match_report.truthfulness_warnings_json),
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

    def _to_read_model(self, resume_version: ResumeVersion) -> ResumeVersionRead:
        return ResumeVersionRead(
            id=resume_version.id,
            user_id=resume_version.user_id,
            resume_profile_id=resume_version.resume_profile_id,
            job_description_id=resume_version.job_description_id,
            match_report_id=resume_version.match_report_id,
            title=resume_version.title,
            version_type=resume_version.version_type,
            content_markdown=resume_version.content_markdown,
            generation_notes=resume_version.generation_notes,
            change_explanations=[
                item if isinstance(item, dict) else {}
                for item in self._from_json_list_of_objects(resume_version.change_explanations_json)
            ],
            model_name=resume_version.model_name,
            created_at=resume_version.created_at,
            updated_at=resume_version.updated_at,
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

    def _from_json_list_of_objects(self, value: str) -> list[dict[str, object]]:
        parsed = json.loads(value)
        if isinstance(parsed, list):
            return [item for item in parsed if isinstance(item, dict)]
        return []
