import json

from sqlalchemy.orm import Session

from app.ai.client import AIClient
from app.ai.prompt_loader import PromptLoader
from app.models.job_analysis import JobAnalysis
from app.models.job_description import JobDescription
from app.repositories.job_analysis_repository import JobAnalysisRepository
from app.repositories.job_description_repository import JobDescriptionRepository
from app.schemas.analysis import JobAnalysisAIResult, JobAnalysisRead
from app.schemas.job_description import JobDescriptionCreate, JobDescriptionRead

JD_ANALYZER_PROMPT = "jd_analyzer_v1.md"


class JobDescriptionNotFoundError(RuntimeError):
    pass


class JobAnalysisService:
    def __init__(
        self,
        db: Session,
        *,
        ai_client: AIClient | None = None,
        prompt_loader: PromptLoader | None = None,
    ) -> None:
        self.job_description_repository = JobDescriptionRepository(db)
        self.job_analysis_repository = JobAnalysisRepository(db)
        self.ai_client = ai_client or AIClient()
        self.prompt_loader = prompt_loader or PromptLoader()

    def create_job_description(self, payload: JobDescriptionCreate, *, user_id: int) -> JobDescriptionRead:
        job_description = self.job_description_repository.create(
            user_id=user_id,
            company_name=payload.company_name,
            title=payload.job_title,
            raw_text=payload.raw_text,
        )
        return self._job_description_to_read_model(job_description)

    def list_job_descriptions(self, *, user_id: int) -> list[JobDescriptionRead]:
        return [
            self._job_description_to_read_model(job_description)
            for job_description in self.job_description_repository.list_by_user(user_id=user_id)
        ]

    def analyze_job_description(self, job_description_id: int, *, user_id: int) -> JobAnalysisRead:
        job_description = self.job_description_repository.get_by_id_for_user(
            job_description_id=job_description_id,
            user_id=user_id,
        )
        if job_description is None:
            raise JobDescriptionNotFoundError("Job description was not found.")

        raw_ai_output = self.ai_client.chat_json(
            system_prompt=self.prompt_loader.load(JD_ANALYZER_PROMPT),
            user_prompt=self._build_user_prompt(job_description),
            temperature=0.1,
        )
        parsed = JobAnalysisAIResult.model_validate(raw_ai_output)

        analysis = self.job_analysis_repository.upsert(
            job_description_id=job_description.id,
            job_title=self._analysis_title(parsed, job_description),
            job_type=parsed.job_type,
            responsibilities_json=self._to_json(parsed.responsibilities),
            required_skills_json=self._to_json(parsed.required_skills),
            preferred_skills_json=self._to_json(parsed.bonus_skills),
            keywords_json=self._to_json(parsed.keywords),
            resume_focus_suggestions_json=self._to_json(parsed.resume_focus_suggestions),
            raw_ai_output_json=self._to_json(raw_ai_output),
            model_name=self.ai_client.model_name,
        )
        self.job_description_repository.update_status(job_description=job_description, status="analyzed")
        return self._analysis_to_read_model(analysis)

    def _build_user_prompt(self, job_description: JobDescription) -> str:
        return (
            f"公司名称：{job_description.company_name or '信息不足'}\n"
            f"岗位名称：{job_description.title}\n"
            "岗位 JD 原文：\n"
            f"{job_description.raw_text}"
        )

    def _analysis_title(self, parsed: JobAnalysisAIResult, job_description: JobDescription) -> str:
        if parsed.job_title and parsed.job_title != "信息不足":
            return parsed.job_title
        return job_description.title

    def _job_description_to_read_model(self, job_description: JobDescription) -> JobDescriptionRead:
        return JobDescriptionRead(
            id=job_description.id,
            user_id=job_description.user_id,
            company_name=job_description.company_name,
            job_title=job_description.title,
            raw_text=job_description.raw_text,
            status=job_description.status,
            created_at=job_description.created_at,
            updated_at=job_description.updated_at,
        )

    def _analysis_to_read_model(self, analysis: JobAnalysis) -> JobAnalysisRead:
        return JobAnalysisRead(
            id=analysis.id,
            job_description_id=analysis.job_description_id,
            job_title=analysis.job_title,
            job_type=analysis.job_type,
            required_skills=self._from_json_list(analysis.required_skills_json),
            bonus_skills=self._from_json_list(analysis.preferred_skills_json),
            responsibilities=self._from_json_list(analysis.responsibilities_json),
            keywords=self._from_json_list(analysis.keywords_json),
            resume_focus_suggestions=self._from_json_list(analysis.resume_focus_suggestions_json),
            model_name=analysis.model_name,
            created_at=analysis.created_at,
            updated_at=analysis.updated_at,
        )

    def _to_json(self, value: object) -> str:
        return json.dumps(value, ensure_ascii=False)

    def _from_json_list(self, value: str) -> list[str]:
        parsed = json.loads(value)
        if isinstance(parsed, list):
            return [str(item) for item in parsed]
        return []
