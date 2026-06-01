from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TruthCheckResult(Base):
    __tablename__ = "truth_check_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    resume_version_id: Mapped[int] = mapped_column(ForeignKey("resume_versions.id"), index=True, nullable=False)
    overall_risk_level: Mapped[str] = mapped_column(String, nullable=False)
    risky_statements_json: Mapped[str] = mapped_column(Text, nullable=False)
    safer_rewrites_json: Mapped[str] = mapped_column(Text, nullable=False)
    missing_evidence_json: Mapped[str] = mapped_column(Text, nullable=False)
    interview_risk_points_json: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    raw_ai_output_json: Mapped[str] = mapped_column(Text, nullable=False)
    model_name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    resume_version = relationship("ResumeVersion")
