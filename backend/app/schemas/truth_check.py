from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

RiskLevel = Literal["low", "medium", "high"]
RiskType = Literal[
    "fabricated_experience",
    "exaggerated_skill",
    "unsupported_metric",
    "unsupported_claim",
    "role_exaggeration",
    "project_scope_exaggeration",
    "uncertain_statement",
    "interview_risk",
]
EvidenceStatus = Literal["supported", "partially_supported", "unsupported", "uncertain"]


class TruthCheckCreate(BaseModel):
    resume_version_id: int = Field(..., gt=0)


class RiskyStatement(BaseModel):
    statement: str = Field(..., min_length=1)
    risk_level: RiskLevel
    risk_type: RiskType
    reason: str = Field(..., min_length=1)
    evidence_status: EvidenceStatus
    safer_rewrite: str = Field(..., min_length=1)

    @field_validator("statement", "reason", "safer_rewrite")
    @classmethod
    def text_must_not_be_blank(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("This field is required.")
        return normalized


class TruthCheckAIResult(BaseModel):
    overall_risk_level: RiskLevel
    risky_statements: list[RiskyStatement] = Field(default_factory=list)
    safer_rewrites: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    interview_risk_points: list[str] = Field(default_factory=list)
    summary: str = Field(..., min_length=1)

    @field_validator("safer_rewrites", "missing_evidence", "interview_risk_points", mode="before")
    @classmethod
    def normalize_string_list(cls, value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            normalized = value.strip()
            return [normalized] if normalized else []
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        normalized = str(value).strip()
        return [normalized] if normalized else []

    @field_validator("summary")
    @classmethod
    def summary_must_not_be_blank(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Summary is required.")
        return normalized


class TruthCheckResultRead(BaseModel):
    id: int
    user_id: int
    resume_version_id: int
    overall_risk_level: RiskLevel
    risky_statements: list[RiskyStatement]
    safer_rewrites: list[str]
    missing_evidence: list[str]
    interview_risk_points: list[str]
    summary: str
    model_name: str
    created_at: datetime
