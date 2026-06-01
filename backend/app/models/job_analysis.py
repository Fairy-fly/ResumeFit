from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class JobAnalysis(Base):
    __tablename__ = "job_analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    job_description_id: Mapped[int] = mapped_column(
        ForeignKey("job_descriptions.id"),
        index=True,
        unique=True,
        nullable=False,
    )
    job_title: Mapped[str] = mapped_column(String, nullable=False)
    job_type: Mapped[str] = mapped_column(String, nullable=False)
    role_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    responsibilities_json: Mapped[str] = mapped_column(Text, nullable=False)
    required_skills_json: Mapped[str] = mapped_column(Text, nullable=False)
    preferred_skills_json: Mapped[str] = mapped_column(Text, nullable=False)
    keywords_json: Mapped[str] = mapped_column(Text, nullable=False)
    seniority_level: Mapped[str | None] = mapped_column(String, nullable=True)
    domain: Mapped[str | None] = mapped_column(String, nullable=True)
    resume_focus_suggestions_json: Mapped[str] = mapped_column(Text, nullable=False)
    raw_ai_output_json: Mapped[str] = mapped_column(Text, nullable=False)
    model_name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    job_description = relationship("JobDescription", back_populates="analysis")
