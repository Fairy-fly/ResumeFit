import { apiGet, apiPost } from "./client";

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

export function generateResumeVersion(payload: ResumeVersionGenerate): Promise<ResumeVersionRead> {
  return apiPost<ResumeVersionGenerate, ResumeVersionRead>("/resume-versions/generate", payload);
}

export function listResumeVersions(): Promise<ResumeVersionRead[]> {
  return apiGet<ResumeVersionRead[]>("/resume-versions");
}
