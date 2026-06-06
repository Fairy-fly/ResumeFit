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
from app.models.truth_check_result import TruthCheckResult
from app.repositories.job_analysis_repository import JobAnalysisRepository
from app.repositories.job_description_repository import JobDescriptionRepository
from app.repositories.match_report_repository import MatchReportRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.resume_profile_repository import ResumeProfileRepository
from app.repositories.resume_version_repository import ResumeVersionRepository
from app.repositories.truth_check_repository import TruthCheckRepository
from app.schemas.truth_check import TruthCheckAIResult, TruthCheckCreate, TruthCheckResultRead

TRUTH_CHECKER_PROMPT = "truth_checker_v1.md"


class TruthCheckNotFoundError(RuntimeError):
    pass


class TruthCheckValidationError(RuntimeError):
    pass


class TruthCheckService:
    def __init__(
        self,
        db: Session,
        *,
        ai_client: AIClient | None = None,
        prompt_loader: PromptLoader | None = None,
    ) -> None:
        self.resume_version_repository = ResumeVersionRepository(db)
        self.resume_profile_repository = ResumeProfileRepository(db)
        self.project_repository = ProjectRepository(db)
        self.job_description_repository = JobDescriptionRepository(db)
        self.job_analysis_repository = JobAnalysisRepository(db)
        self.match_report_repository = MatchReportRepository(db)
        self.truth_check_repository = TruthCheckRepository(db)
        self.ai_client = ai_client or AIClient()
        self.prompt_loader = prompt_loader or PromptLoader()

    def create_truth_check_result(self, payload: TruthCheckCreate, *, user_id: int) -> TruthCheckResultRead:
        context = self._load_context(payload.resume_version_id, user_id=user_id)
        raw_ai_output = self.ai_client.chat_json(
            system_prompt=self.prompt_loader.load(TRUTH_CHECKER_PROMPT),
            user_prompt=self._build_user_prompt(**context),
            temperature=0.1,
        )

        try:
            parsed = TruthCheckAIResult.model_validate(raw_ai_output)
        except ValidationError as exc:
            raise AIResponseError("AI response JSON did not match the truth check schema.") from exc

        truth_check_result = self.truth_check_repository.create(
            user_id=user_id,
            resume_version_id=context["resume_version"].id,
            overall_risk_level=parsed.overall_risk_level,
            risky_statements_json=self._to_json([item.model_dump() for item in parsed.risky_statements]),
            safer_rewrites_json=self._to_json(parsed.safer_rewrites),
            missing_evidence_json=self._to_json(parsed.missing_evidence),
            interview_risk_points_json=self._to_json(parsed.interview_risk_points),
            summary=parsed.summary,
            raw_ai_output_json=self._to_json(raw_ai_output),
            model_name=self.ai_client.model_name,
        )
        return self._to_read_model(truth_check_result)

    def list_truth_check_results(self, *, resume_version_id: int, user_id: int) -> list[TruthCheckResultRead]:
        resume_version = self.resume_version_repository.get_by_id_for_user(
            resume_version_id=resume_version_id,
            user_id=user_id,
        )
        if resume_version is None:
            raise TruthCheckNotFoundError("Resume version was not found.")

        return [
            self._to_read_model(truth_check_result)
            for truth_check_result in self.truth_check_repository.list_by_resume_version_for_user(
                resume_version_id=resume_version_id,
                user_id=user_id,
            )
        ]

    def _load_context(self, resume_version_id: int, *, user_id: int) -> dict[str, object]:
        resume_version = self.resume_version_repository.get_by_id_for_user(
            resume_version_id=resume_version_id,
            user_id=user_id,
        )
        if resume_version is None:
            raise TruthCheckNotFoundError("Resume version was not found.")
        if resume_version.match_report_id is None:
            raise TruthCheckValidationError("Resume version does not have a match report context.")

        match_report = self.match_report_repository.get_by_id_for_user(
            match_report_id=resume_version.match_report_id,
            user_id=user_id,
        )
        if match_report is None:
            raise TruthCheckNotFoundError("Match report was not found.")
        self._validate_resume_version_context(resume_version=resume_version, match_report=match_report)

        resume_profile = self.resume_profile_repository.get_by_id_for_user(
            resume_profile_id=resume_version.resume_profile_id,
            user_id=user_id,
        )
        if resume_profile is None:
            raise TruthCheckNotFoundError("Resume profile was not found.")

        job_description = self.job_description_repository.get_by_id_for_user(
            job_description_id=match_report.job_description_id,
            user_id=user_id,
        )
        if job_description is None:
            raise TruthCheckNotFoundError("Job description was not found.")

        job_analysis = self.job_analysis_repository.get_by_id(job_analysis_id=match_report.job_analysis_id)
        if job_analysis is None or job_analysis.job_description_id != job_description.id:
            raise TruthCheckNotFoundError("Job analysis was not found.")

        project_ids = self._from_json_int_list(match_report.project_ids_json)
        if not project_ids:
            raise TruthCheckValidationError("Match report does not include selected project IDs.")
        projects = self.project_repository.list_by_ids_for_user(project_ids=project_ids, user_id=user_id)
        found_project_ids = {project.id for project in projects}
        if any(project_id not in found_project_ids for project_id in project_ids):
            raise TruthCheckNotFoundError("One or more projects were not found.")

        return {
            "resume_version": resume_version,
            "resume_profile": resume_profile,
            "projects": sorted(projects, key=lambda project: project_ids.index(project.id)),
            "job_description": job_description,
            "job_analysis": job_analysis,
            "match_report": match_report,
        }

    def _validate_resume_version_context(
        self,
        *,
        resume_version: ResumeVersion,
        match_report: MatchReport,
    ) -> None:
        if resume_version.resume_profile_id != match_report.resume_profile_id:
            raise TruthCheckValidationError("Resume version does not match the linked match report resume.")
        if resume_version.job_description_id != match_report.job_description_id:
            raise TruthCheckValidationError("Resume version does not match the linked match report job description.")

    def _build_user_prompt(
        self,
        *,
        resume_version: ResumeVersion,
        resume_profile: ResumeProfile,
        projects: list[Project],
        job_description: JobDescription,
        job_analysis: JobAnalysis,
        match_report: MatchReport,
    ) -> str:
        payload = {
            "resume_version": {
                "id": resume_version.id,
                "title": resume_version.title,
                "content_markdown": resume_version.content_markdown,
                "generation_notes": resume_version.generation_notes,
                "change_explanations": self._from_json_list_of_objects(resume_version.change_explanations_json),
            },
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

    def _to_read_model(self, truth_check_result: TruthCheckResult) -> TruthCheckResultRead:
        return TruthCheckResultRead(
            id=truth_check_result.id,
            user_id=truth_check_result.user_id,
            resume_version_id=truth_check_result.resume_version_id,
            overall_risk_level=truth_check_result.overall_risk_level,
            risky_statements=self._from_json_list_of_objects(truth_check_result.risky_statements_json),
            safer_rewrites=self._from_json_list(truth_check_result.safer_rewrites_json),
            missing_evidence=self._from_json_list(truth_check_result.missing_evidence_json),
            interview_risk_points=self._from_json_list(truth_check_result.interview_risk_points_json),
            summary=truth_check_result.summary,
            model_name=truth_check_result.model_name,
            created_at=truth_check_result.created_at,
        )

    def _to_json(self, value: object) -> str:
        return json.dumps(value, ensure_ascii=False)

    def _from_json_list(self, value: str | None) -> list[str]:
        if value is None:
            return []
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return []
        if isinstance(parsed, list):
            return [str(item) for item in parsed]
        return []

    def _from_json_int_list(self, value: str | None) -> list[int]:
        if value is None:
            return []
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return []
        if isinstance(parsed, list):
            try:
                return [int(item) for item in parsed]
            except (TypeError, ValueError):
                return []
        return []

    def _from_json_list_of_objects(self, value: str | None) -> list[dict[str, object]]:
        if value is None:
            return []
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return []
        if isinstance(parsed, list):
            return [item for item in parsed if isinstance(item, dict)]
        return []
