"""Database model imports for metadata registration."""

from app.models.job_analysis import JobAnalysis
from app.models.job_description import JobDescription
from app.models.interview_question import InterviewQuestionResult
from app.models.ai_usage_log import AIUsageLog
from app.models.match_report import MatchReport
from app.models.project import Project
from app.models.resume_profile import ResumeProfile
from app.models.resume_version import ResumeVersion
from app.models.truth_check_result import TruthCheckResult
from app.models.user import User

__all__ = [
    "JobAnalysis",
    "JobDescription",
    "InterviewQuestionResult",
    "AIUsageLog",
    "MatchReport",
    "Project",
    "ResumeProfile",
    "ResumeVersion",
    "TruthCheckResult",
    "User",
]
