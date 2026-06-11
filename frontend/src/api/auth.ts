import { apiGet, apiPost } from "./client";

export interface AuthUser {
  id: number;
  email: string | null;
  display_name: string | null;
  role: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface AuthTokenResponse {
  access_token: string;
  token_type: string;
  user: AuthUser;
}

export interface RegisterPayload {
  email: string;
  password: string;
  display_name: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export function register(payload: RegisterPayload): Promise<AuthTokenResponse> {
  return apiPost<RegisterPayload, AuthTokenResponse>("/auth/register", payload);
}

export function login(payload: LoginPayload): Promise<AuthTokenResponse> {
  return apiPost<LoginPayload, AuthTokenResponse>("/auth/login", payload);
}

export function getMe(): Promise<AuthUser> {
  return apiGet<AuthUser>("/auth/me");
}
