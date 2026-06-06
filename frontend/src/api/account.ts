import { apiGet, apiPatch } from "./client";
import type { AuthUser } from "./auth";
import type { AIUsageSummary } from "./usage";

export interface AccountRead extends AuthUser {
  usage_summary: AIUsageSummary;
}

export interface AccountUpdatePayload {
  display_name: string;
}

export function getAccountMe(): Promise<AccountRead> {
  return apiGet<AccountRead>("/account/me");
}

export function updateAccountMe(payload: AccountUpdatePayload): Promise<AccountRead> {
  return apiPatch<AccountUpdatePayload, AccountRead>("/account/me", payload);
}
