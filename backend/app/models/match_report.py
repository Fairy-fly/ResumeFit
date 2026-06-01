from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class MatchReport(Base):
    __tablename__ = "match_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    resume_profile_id: Mapped[int] = mapped_column(ForeignKey("resume_profiles.id"), index=True, nullable=False)
    job_description_id: Mapped[int] = mapped_column(ForeignKey("job_descriptions.id"), index=True, nullable=False)
    job_analysis_id: Mapped[int] = mapped_column(ForeignKey("job_analyses.id"), index=True, nullable=False)
    project_ids_json: Mapped[str] = mapped_column(Text, nullable=False)
    overall_score: Mapped[int] = mapped_column(Integer, nullable=False)
    skill_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    project_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    domain_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    expression_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    strengths_json: Mapped[str] = mapped_column(Text, nullable=False)
    gaps_json: Mapped[str] = mapped_column(Text, nullable=False)
    missing_keywords_json: Mapped[str] = mapped_column(Text, nullable=False)
    suggestions_json: Mapped[str] = mapped_column(Text, nullable=False)
    truthfulness_warnings_json: Mapped[str] = mapped_column(Text, nullable=False)
    raw_ai_output_json: Mapped[str] = mapped_column(Text, nullable=False)
    model_name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    resume_profile = relationship("ResumeProfile")
    job_description = relationship("JobDescription")
    job_analysis = relationship("JobAnalysis")
