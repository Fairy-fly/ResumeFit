import { apiGet } from "./client";

export interface AIUsageFeatureCount {
  feature_type: string;
  count: number;
  success_count: number;
  failure_count: number;
}

export interface AIUsageLog {
  id: number;
  feature_type: string;
  model_name: string;
  status: "success" | "failed";
  error_message: string | null;
  input_tokens: number | null;
  output_tokens: number | null;
  total_tokens: number | null;
  estimated_cost: number | null;
  created_at: string;
}

export interface AIUsageSummary {
  monthly_quota: number;
  monthly_used: number;
  monthly_remaining: number;
  total_call_count: number;
  monthly_success_count: number;
  monthly_failure_count: number;
  feature_counts: AIUsageFeatureCount[];
  recent_calls: AIUsageLog[];
}

export function getUsageSummary(): Promise<AIUsageSummary> {
  return apiGet<AIUsageSummary>("/usage/summary");
}
