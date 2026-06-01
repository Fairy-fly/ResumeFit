import { apiGet, apiPost } from "./client";

export interface ResumeProfileCreate {
  title: string;
  raw_markdown: string;
}

export interface ResumeProfileRead {
  id: number;
  user_id: number;
  title: string;
  raw_markdown: string;
  created_at: string;
  updated_at: string;
}

export function createResumeProfile(payload: ResumeProfileCreate): Promise<ResumeProfileRead> {
  return apiPost<ResumeProfileCreate, ResumeProfileRead>("/resume-profiles", payload);
}

export function listResumeProfiles(): Promise<ResumeProfileRead[]> {
  return apiGet<ResumeProfileRead[]>("/resume-profiles");
}
