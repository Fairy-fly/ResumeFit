import { apiGet, apiPost, buildAuthHeaders } from "./client";
import { ApiRequestError } from "../utils/errors";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export interface ChangeExplanation {
  section: string;
  reason: string;
  source: string;
  uncertain: boolean;
}

export interface ResumeVersionGenerate {
  resume_profile_id: number;
  project_ids: number[];
  match_report_id: number;
  job_description_id?: number;
  job_analysis_id?: number;
}

export interface ResumeVersionRead {
  id: number;
  user_id: number;
  resume_profile_id: number;
  job_description_id: number | null;
  match_report_id: number | null;
  title: string;
  version_type: string;
  content_markdown: string;
  generation_notes: string | null;
  change_explanations: ChangeExplanation[];
  model_name: string;
  created_at: string;
  updated_at: string;
}

export interface ResumeVersionMarkdownDownload {
  blob: Blob;
  filename: string;
}

export function generateResumeVersion(payload: ResumeVersionGenerate): Promise<ResumeVersionRead> {
  return apiPost<ResumeVersionGenerate, ResumeVersionRead>("/resume-versions/generate", payload);
}

export function listResumeVersions(): Promise<ResumeVersionRead[]> {
  return apiGet<ResumeVersionRead[]>("/resume-versions");
}

export async function downloadResumeVersionMarkdown(
  resumeVersionId: number
): Promise<ResumeVersionMarkdownDownload> {
  const response = await fetch(`${API_BASE_URL}/resume-versions/${resumeVersionId}/export/markdown`, {
    headers: buildAuthHeaders()
  });

  if (!response.ok) {
    throw await buildDownloadError(response);
  }

  const blob = await response.blob();
  return {
    blob,
    filename: parseContentDispositionFilename(response.headers.get("Content-Disposition")) ?? fallbackFilename()
  };
}

async function buildDownloadError(response: Response): Promise<Error> {
  let detail: unknown;

  try {
    const payload = (await response.json()) as { detail?: unknown };
    detail = payload.detail;
    if (typeof payload.detail === "string" && payload.detail.trim().length > 0) {
      return new ApiRequestError(payload.detail, { status: response.status, detail });
    }
  } catch {
    // Fall through to the status-only message.
  }

  return new ApiRequestError(`Request failed with status ${response.status}`, {
    status: response.status,
    detail
  });
}

function parseContentDispositionFilename(contentDisposition: string | null): string | null {
  if (!contentDisposition) {
    return null;
  }

  const encodedMatch = contentDisposition.match(/filename\*=UTF-8''([^;]+)/i);
  if (encodedMatch?.[1]) {
    try {
      return decodeURIComponent(encodedMatch[1]);
    } catch {
      return encodedMatch[1];
    }
  }

  const fallbackMatch = contentDisposition.match(/filename="([^"]+)"/i);
  return fallbackMatch?.[1] ?? null;
}

function fallbackFilename(): string {
  return `ResumeFit_${new Date().toISOString().slice(0, 10).replace(/-/g, "")}.md`;
}
