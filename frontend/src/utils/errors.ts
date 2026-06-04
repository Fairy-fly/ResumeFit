export class ApiRequestError extends Error {
  readonly status?: number;
  readonly detail?: unknown;

  constructor(message: string, options: { status?: number; detail?: unknown } = {}) {
    super(message);
    this.name = "ApiRequestError";
    this.status = options.status;
    this.detail = options.detail;
  }
}

export function getFriendlyErrorMessage(error: unknown): string {
  if (isBackendConnectionError(error)) {
    return "无法连接后端服务，请确认 FastAPI 已启动在 http://localhost:8000";
  }

  const status = error instanceof ApiRequestError ? error.status : undefined;
  const detailText = error instanceof ApiRequestError ? detailToText(error.detail) : null;
  const rawMessage = error instanceof Error ? error.message : "";
  const sourceText = [detailText, rawMessage].filter(Boolean).join(" ");
  const normalized = sourceText.toLowerCase();

  if (normalized.includes("ai_api_key is not configured")) {
    return "AI Key 未配置，请在 backend/.env 中配置 AI_API_KEY 后重启后端";
  }

  if (isAIResponseFormatError(normalized)) {
    return "AI 返回格式异常，可稍后重试；如果持续出现，请检查 Prompt 或模型配置";
  }

  if (isAIServiceUnavailableError(normalized)) {
    return "AI 服务暂时不可用，请检查网络或稍后重试";
  }

  if (status === 404 && normalized.includes("resume version")) {
    return "该简历版本不存在或已被删除";
  }

  if ((status === 400 || status === 404) && detailText) {
    return detailText;
  }

  if (rawMessage.trim().length > 0) {
    return rawMessage;
  }

  return "请求失败，请稍后重试。";
}

function isBackendConnectionError(error: unknown): boolean {
  if (error instanceof TypeError) {
    return true;
  }

  if (!(error instanceof Error)) {
    return false;
  }

  const message = error.message.toLowerCase();
  return (
    message.includes("failed to fetch") ||
    message.includes("networkerror") ||
    message.includes("load failed")
  );
}

function isAIResponseFormatError(normalizedMessage: string): boolean {
  return (
    normalizedMessage.includes("invalid json") ||
    normalizedMessage.includes("not valid json") ||
    normalizedMessage.includes("json did not match") ||
    normalizedMessage.includes("schema mismatch") ||
    normalizedMessage.includes("response json must be an object") ||
    normalizedMessage.includes("response format was unexpected") ||
    normalizedMessage.includes("returned empty content")
  );
}

function isAIServiceUnavailableError(normalizedMessage: string): boolean {
  return (
    normalizedMessage.includes("ai provider request timed out") ||
    normalizedMessage.includes("ai provider request failed") ||
    normalizedMessage.includes("ai provider returned http") ||
    normalizedMessage.includes("temporarily unavailable") ||
    normalizedMessage.includes("timed out")
  );
}

function detailToText(detail: unknown): string | null {
  if (typeof detail === "string") {
    const trimmed = detail.trim();
    return trimmed.length > 0 ? trimmed : null;
  }

  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => {
        if (typeof item === "string") {
          return item;
        }

        if (isRecord(item) && typeof item.msg === "string") {
          return item.msg;
        }

        return null;
      })
      .filter((item): item is string => item !== null && item.trim().length > 0);

    if (messages.length > 0) {
      return messages.join("；");
    }
  }

  if (detail !== undefined && detail !== null) {
    try {
      return JSON.stringify(detail);
    } catch {
      return String(detail);
    }
  }

  return null;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}
