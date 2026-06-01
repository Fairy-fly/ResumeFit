import { apiGet, apiPost } from "./client";

export interface JobDescriptionCreate {
  company_name: string;
  job_title: string;
  raw_text: string;
}

export interface JobDescriptionRead {
  id: number;
  user_id: number;
  company_name: string | null;
  job_title: string;
  raw_text: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface JobAnalysisRead {
  id: number;
  job_description_id: number;
  job_title: string;
  job_type: string;
  required_skills: string[];
  bonus_skills: string[];
  responsibilities: string[];
  keywords: string[];
  resume_focus_suggestions: string[];
  model_name: string;
  created_at: string;
  updated_at: string;
}

export function createJobDescription(payload: JobDescriptionCreate): Promise<JobDescriptionRead> {
  return apiPost<JobDescriptionCreate, JobDescriptionRead>("/job-descriptions", payload);
}

export function listJobDescriptions(): Promise<JobDescriptionRead[]> {
  return apiGet<JobDescriptionRead[]>("/job-descriptions");
}

export function analyzeJobDescription(jobDescriptionId: number): Promise<JobAnalysisRead> {
  return apiPost<Record<string, never>, JobAnalysisRead>(`/job-descriptions/${jobDescriptionId}/analyze`, {});
}
