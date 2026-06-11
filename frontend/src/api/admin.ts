import { apiGet, apiPatch } from "./client";
import type { AIUsageFeatureCount, AIUsageLog, AIUsageSummary } from "./usage";

export interface AdminUserUsageOverview {
  monthly_used: number;
  monthly_quota: number;
  monthly_remaining: number;
  total_call_count: number;
}

export interface AdminUserListItem {
  id: number;
  email: string | null;
  display_name: string | null;
  role: string;
  status: string;
  created_at: string;
  updated_at: string;
  usage: AdminUserUsageOverview;
}

export interface AdminUserListResponse {
  items: AdminUserListItem[];
  total: number;
  page: number;
  page_size: number;
}

export interface AdminUserDetail {
  id: number;
  email: string | null;
  display_name: string | null;
  role: string;
  status: string;
  created_at: string;
  updated_at: string;
  usage_summary: AIUsageSummary;
}

export interface AdminGlobalUsageSummary {
  total_call_count: number;
  monthly_call_count: number;
  monthly_success_count: number;
  monthly_failure_count: number;
  feature_counts: AIUsageFeatureCount[];
  recent_calls: AIUsageLog[];
}

export function listAdminUsers(params: {
  page: number;
  page_size: number;
  search?: string;
}): Promise<AdminUserListResponse> {
  const query = new URLSearchParams({
    page: String(params.page),
    page_size: String(params.page_size)
  });

  if (params.search && params.search.trim().length > 0) {
    query.set("search", params.search.trim());
  }

  return apiGet<AdminUserListResponse>(`/admin/users?${query.toString()}`);
}

export function getAdminUserDetail(userId: number): Promise<AdminUserDetail> {
  return apiGet<AdminUserDetail>(`/admin/users/${userId}`);
}

export function updateAdminUserStatus(userId: number, status: "active" | "disabled"): Promise<AdminUserDetail> {
  return apiPatch<{ status: "active" | "disabled" }, AdminUserDetail>(`/admin/users/${userId}/status`, { status });
}

export function getAdminUsageSummary(): Promise<AdminGlobalUsageSummary> {
  return apiGet<AdminGlobalUsageSummary>("/admin/usage/summary");
}
