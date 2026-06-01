import { apiGet, apiPost } from "./client";

export type RiskLevel = "low" | "medium" | "high";
export type RiskType =
  | "fabricated_experience"
  | "exaggerated_skill"
  | "unsupported_metric"
  | "unsupported_claim"
  | "role_exaggeration"
  | "project_scope_exaggeration"
  | "uncertain_statement"
  | "interview_risk";
export type EvidenceStatus = "supported" | "partially_supported" | "unsupported" | "uncertain";

export interface RiskyStatement {
  statement: string;
  risk_level: RiskLevel;
  risk_type: RiskType;
  reason: string;
  evidence_status: EvidenceStatus;
  safer_rewrite: string;
}

export interface TruthCheckCreate {
  resume_version_id: number;
}

export interface TruthCheckResultRead {
  id: number;
  user_id: number;
  resume_version_id: number;
  overall_risk_level: RiskLevel;
  risky_statements: RiskyStatement[];
  safer_rewrites: string[];
  missing_evidence: string[];
  interview_risk_points: string[];
  summary: string;
  model_name: string;
  created_at: string;
}

export function createTruthCheckResult(payload: TruthCheckCreate): Promise<TruthCheckResultRead> {
  return apiPost<TruthCheckCreate, TruthCheckResultRead>("/truth-check-results", payload);
}

export function listTruthCheckResults(resumeVersionId: number): Promise<TruthCheckResultRead[]> {
  return apiGet<TruthCheckResultRead[]>(`/truth-check-results?resume_version_id=${resumeVersionId}`);
}
