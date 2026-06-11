import re
from dataclasses import dataclass
from io import BytesIO
from urllib.parse import quote

from docx import Document
from docx.shared import Pt
from sqlalchemy.orm import Session

from app.models.resume_version import ResumeVersion
from app.repositories.job_description_repository import JobDescriptionRepository
from app.repositories.resume_version_repository import ResumeVersionRepository

DOCX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
MAX_EXPORT_FILENAME_STEM_LENGTH = 80
WINDOWS_RESERVED_FILENAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    "COM1",
    "COM2",
    "COM3",
    "COM4",
    "COM5",
    "COM6",
    "COM7",
    "COM8",
    "COM9",
    "LPT1",
    "LPT2",
    "LPT3",
    "LPT4",
    "LPT5",
    "LPT6",
    "LPT7",
    "LPT8",
    "LPT9",
}


@dataclass(frozen=True)
class BinaryExport:
    content: bytes
    filename: str
    content_disposition: str


class ExportNotFoundError(RuntimeError):
    pass


class ResumeExportService:
    def __init__(self, db: Session) -> None:
        self.resume_version_repository = ResumeVersionRepository(db)
        self.job_description_repository = JobDescriptionRepository(db)

    def export_resume_version_docx(self, *, resume_version_id: int, user_id: int) -> BinaryExport:
        resume_version = self.resume_version_repository.get_by_id_for_user(
            resume_version_id=resume_version_id,
            user_id=user_id,
        )
        if resume_version is None:
            raise ExportNotFoundError("Resume version was not found.")

        filename = self._build_export_filename(
            title_source=self._get_export_title_source(resume_version, user_id=user_id),
            resume_version=resume_version,
            extension="docx",
        )
        content = self._build_docx_content(resume_version.content_markdown)
        return BinaryExport(
            content=content,
            filename=filename,
            content_disposition=self._build_content_disposition(filename),
        )

    def _build_docx_content(self, markdown: str) -> bytes:
        document = Document()
        self._apply_standard_styles(document)

        for line in markdown.splitlines():
            stripped = line.strip()
            if not stripped:
                document.add_paragraph()
                continue

            if stripped.startswith("### "):
                document.add_heading(stripped.removeprefix("### ").strip(), level=3)
                continue
            if stripped.startswith("## "):
                document.add_heading(stripped.removeprefix("## ").strip(), level=2)
                continue
            if stripped.startswith("# "):
                document.add_heading(stripped.removeprefix("# ").strip(), level=1)
                continue

            bullet_match = re.match(r"^[-*]\s+(.+)$", stripped)
            if bullet_match:
                document.add_paragraph(bullet_match.group(1).strip(), style="List Bullet")
                continue

            document.add_paragraph(stripped)

        output = BytesIO()
        document.save(output)
        return output.getvalue()

    def _apply_standard_styles(self, document: Document) -> None:
        styles = document.styles
        normal_style = styles["Normal"]
        normal_style.font.name = "Arial"
        normal_style.font.size = Pt(10.5)

        for style_name, size in (("Heading 1", 18), ("Heading 2", 14), ("Heading 3", 12)):
            style = styles[style_name]
            style.font.name = "Arial"
            style.font.size = Pt(size)
            style.font.bold = True

    def _get_export_title_source(self, resume_version: ResumeVersion, *, user_id: int) -> str:
        if resume_version.job_description_id is None:
            return resume_version.title

        job_description = self.job_description_repository.get_by_id_for_user(
            job_description_id=resume_version.job_description_id,
            user_id=user_id,
        )
        if job_description is None:
            return resume_version.title
        return job_description.title

    def _build_export_filename(self, *, title_source: str, resume_version: ResumeVersion, extension: str) -> str:
        date_text = resume_version.created_at.strftime("%Y%m%d")
        safe_title = self._sanitize_filename_part(title_source)
        if not safe_title:
            safe_title = f"ResumeVersion_{resume_version.id}"
        return f"ResumeFit_{safe_title}_{date_text}.{extension}"

    def _sanitize_filename_part(self, value: str) -> str:
        sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", value)
        sanitized = re.sub(r"\s+", "_", sanitized)
        sanitized = re.sub(r"_+", "_", sanitized).strip(" ._")
        if not sanitized:
            return ""
        if sanitized.upper() in WINDOWS_RESERVED_FILENAMES:
            sanitized = f"{sanitized}_"
        return sanitized[:MAX_EXPORT_FILENAME_STEM_LENGTH].rstrip(" ._")

    def _build_content_disposition(self, filename: str) -> str:
        stem, _, extension = filename.rpartition(".")
        ascii_fallback = stem.encode("ascii", "ignore").decode("ascii")
        ascii_fallback = self._sanitize_filename_part(ascii_fallback) or "ResumeFit"
        quoted_filename = quote(filename)
        return f'attachment; filename="{ascii_fallback}.{extension}"; filename*=UTF-8\'\'{quoted_filename}'
