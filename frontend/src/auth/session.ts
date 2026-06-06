import { reactive } from "vue";

import { getMe, type AuthTokenResponse, type AuthUser } from "../api/auth";
import { ApiRequestError } from "../utils/errors";

const ACCESS_TOKEN_STORAGE_KEY = "resumefit_access_token";

interface AuthSessionState {
  token: string | null;
  user: AuthUser | null;
  initialized: boolean;
  loading: boolean;
}

export const authSession = reactive<AuthSessionState>({
  token: getStoredAccessToken(),
  user: null,
  initialized: false,
  loading: false
});

export function getStoredAccessToken(): string | null {
  return window.localStorage.getItem(ACCESS_TOKEN_STORAGE_KEY);
}

export function hasAccessToken(): boolean {
  return getStoredAccessToken() !== null;
}

export function saveSession(response: AuthTokenResponse): void {
  window.localStorage.setItem(ACCESS_TOKEN_STORAGE_KEY, response.access_token);
  authSession.token = response.access_token;
  authSession.user = response.user;
  authSession.initialized = true;
}

export function setCurrentUser(user: AuthUser): void {
  authSession.user = user;
  authSession.initialized = true;
}

export function clearSession(): void {
  window.localStorage.removeItem(ACCESS_TOKEN_STORAGE_KEY);
  authSession.token = null;
  authSession.user = null;
  authSession.initialized = true;
  authSession.loading = false;
}

export async function loadCurrentUser(): Promise<AuthUser | null> {
  const token = getStoredAccessToken();
  authSession.token = token;

  if (!token) {
    clearSession();
    return null;
  }

  authSession.loading = true;
  try {
    const user = await getMe();
    authSession.user = user;
    authSession.initialized = true;
    return user;
  } catch (error) {
    if (error instanceof ApiRequestError && error.status === 401) {
      clearSession();
      return null;
    }

    authSession.initialized = true;
    throw error;
  } finally {
    authSession.loading = false;
  }
}
