import { apiGet, apiPost } from "./client";

export interface MatchReportCreate {
  resume_profile_id: number;
  project_ids: number[];
  job_description_id?: number;
  job_analysis_id?: number;
}

export interface MatchReportRead {
  id: number;
  user_id: number;
  resume_profile_id: number;
  project_ids: number[];
  job_description_id: number;
  job_analysis_id: number;
  score: number;
  strengths: string[];
  weaknesses: string[];
  missing_keywords: string[];
  recommended_changes: string[];
  truthfulness_warnings: string[];
  model_name: string;
  created_at: string;
  updated_at: string;
}

export function createMatchReport(payload: MatchReportCreate): Promise<MatchReportRead> {
  return apiPost<MatchReportCreate, MatchReportRead>("/match-reports", payload);
}

export function listMatchReports(): Promise<MatchReportRead[]> {
  return apiGet<MatchReportRead[]>("/match-reports");
}
