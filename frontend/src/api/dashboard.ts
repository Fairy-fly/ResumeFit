import { apiGet } from "./client";

export interface DashboardSummary {
  resume_profile_count: number;
  project_count: number;
  job_description_count: number;
  match_report_count: number;
  resume_version_count: number;
}

export function getDashboardSummary(): Promise<DashboardSummary> {
  return apiGet<DashboardSummary>("/dashboard/summary");
}
