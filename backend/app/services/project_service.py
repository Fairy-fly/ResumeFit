import json

from sqlalchemy.orm import Session

from app.models.project import Project
from app.repositories.project_repository import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectRead

DEFAULT_USER_ID = 1


class ProjectService:
    def __init__(self, db: Session) -> None:
        self.repository = ProjectRepository(db)

    def create_project(self, payload: ProjectCreate) -> ProjectRead:
        evidence_links = [payload.work_url] if payload.work_url else []
        project = self.repository.create(
            user_id=DEFAULT_USER_ID,
            name=payload.name,
            project_type=payload.project_type,
            role=payload.role,
            tech_stack_json=json.dumps(payload.tech_stack, ensure_ascii=False),
            description=payload.description,
            user_contribution=payload.user_contribution,
            evidence_links_json=json.dumps(evidence_links, ensure_ascii=False),
        )
        return self._to_read_model(project)

    def list_projects(self) -> list[ProjectRead]:
        return [self._to_read_model(project) for project in self.repository.list_by_user(user_id=DEFAULT_USER_ID)]

    def _to_read_model(self, project: Project) -> ProjectRead:
        return ProjectRead(
            id=project.id,
            user_id=project.user_id,
            name=project.name,
            project_type=project.project_type,
            role=project.role,
            tech_stack=self._parse_tech_stack(project.tech_stack_json),
            description=project.description,
            user_contribution=project.user_contribution,
            work_url=self._first_evidence_link(project.evidence_links_json),
            created_at=project.created_at,
            updated_at=project.updated_at,
        )

    def _parse_tech_stack(self, value: str) -> list[str]:
        parsed = json.loads(value)
        if isinstance(parsed, list):
            return [str(item) for item in parsed]
        return []

    def _first_evidence_link(self, value: str) -> str | None:
        parsed = json.loads(value)
        if isinstance(parsed, list) and parsed:
            return str(parsed[0])
        return None
