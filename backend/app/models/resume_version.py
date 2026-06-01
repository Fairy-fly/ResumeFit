from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ResumeVersion(Base):
    __tablename__ = "resume_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    resume_profile_id: Mapped[int] = mapped_column(ForeignKey("resume_profiles.id"), index=True, nullable=False)
    job_description_id: Mapped[int | None] = mapped_column(ForeignKey("job_descriptions.id"), index=True, nullable=True)
    match_report_id: Mapped[int | None] = mapped_column(ForeignKey("match_reports.id"), index=True, nullable=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    version_type: Mapped[str] = mapped_column(String, nullable=False)
    content_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    generation_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    change_explanations_json: Mapped[str] = mapped_column(Text, nullable=False)
    risk_report_json: Mapped[str | None] = mapped_column(Text, nullable=True)
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
    match_report = relationship("MatchReport")
