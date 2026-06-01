from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.job_description import JobDescription


class JobDescriptionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        user_id: int,
        company_name: str,
        title: str,
        raw_text: str,
    ) -> JobDescription:
        job_description = JobDescription(
            user_id=user_id,
            company_name=company_name,
            title=title,
            raw_text=raw_text,
            status="draft",
        )
        self.db.add(job_description)
        self.db.commit()
        self.db.refresh(job_description)
        return job_description

    def get_by_id_for_user(self, *, job_description_id: int, user_id: int) -> JobDescription | None:
        statement = select(JobDescription).where(
            JobDescription.id == job_description_id,
            JobDescription.user_id == user_id,
        )
        return self.db.scalar(statement)

    def list_by_user(self, *, user_id: int) -> list[JobDescription]:
        statement = (
            select(JobDescription)
            .where(JobDescription.user_id == user_id)
            .order_by(JobDescription.created_at.desc())
        )
        return list(self.db.scalars(statement).all())

    def update_status(self, *, job_description: JobDescription, status: str) -> JobDescription:
        job_description.status = status
        self.db.add(job_description)
        self.db.commit()
        self.db.refresh(job_description)
        return job_description
