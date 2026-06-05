import { ApiRequestError } from "../utils/errors";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
const ACCESS_TOKEN_STORAGE_KEY = "resumefit_access_token";

async function parseJson<T>(response: Response): Promise<T> {
  return response.json() as Promise<T>;
}

async function buildError(response: Response): Promise<Error> {
  let detail: unknown;

  try {
    const payload = (await response.json()) as { detail?: unknown };
    detail = payload.detail;
    if (typeof payload.detail === "string" && payload.detail.trim().length > 0) {
      return new ApiRequestError(payload.detail, { status: response.status, detail });
    }
  } catch {
    // Fall through to the status-only message.
  }

  return new ApiRequestError(`Request failed with status ${response.status}`, {
    status: response.status,
    detail
  });
}

export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: buildAuthHeaders()
  });

  if (!response.ok) {
    throw await buildError(response);
  }

  return parseJson<T>(response);
}

export async function apiPost<TRequest, TResponse>(path: string, payload: TRequest): Promise<TResponse> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...buildAuthHeaders()
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    throw await buildError(response);
  }

  return parseJson<TResponse>(response);
}

export function buildAuthHeaders(): Record<string, string> {
  const token = window.localStorage.getItem(ACCESS_TOKEN_STORAGE_KEY);
  return token ? { Authorization: `Bearer ${token}` } : {};
}
