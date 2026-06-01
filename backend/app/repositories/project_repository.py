from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import Project


class ProjectRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        user_id: int,
        name: str,
        project_type: str,
        role: str,
        tech_stack_json: str,
        description: str,
        user_contribution: str,
        evidence_links_json: str,
    ) -> Project:
        project = Project(
            user_id=user_id,
            name=name,
            project_type=project_type,
            role=role,
            tech_stack_json=tech_stack_json,
            description=description,
            user_contribution=user_contribution,
            evidence_links_json=evidence_links_json,
        )
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def list_by_user(self, *, user_id: int) -> list[Project]:
        statement = (
            select(Project)
            .where(Project.user_id == user_id)
            .order_by(Project.created_at.desc())
        )
        return list(self.db.scalars(statement).all())

    def list_by_ids_for_user(self, *, project_ids: list[int], user_id: int) -> list[Project]:
        statement = select(Project).where(
            Project.user_id == user_id,
            Project.id.in_(project_ids),
        )
        return list(self.db.scalars(statement).all())
