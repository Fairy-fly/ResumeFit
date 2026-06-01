import json
from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import settings

PLACEHOLDER_API_KEYS = {"your_api_key_here", "your_deepseek_api_key_here"}


@dataclass(frozen=True)
class AIClientConfig:
    provider: str
    base_url: str
    api_key: str | None
    model: str
    timeout_seconds: int


def get_ai_client_config() -> AIClientConfig:
    return AIClientConfig(
        provider=settings.ai_provider,
        base_url=settings.ai_base_url,
        api_key=settings.ai_api_key,
        model=settings.ai_model,
        timeout_seconds=settings.ai_timeout_seconds,
    )


class AIConfigurationError(RuntimeError):
    pass


class AIResponseError(RuntimeError):
    pass


class AIClient:
    def __init__(self, config: AIClientConfig | None = None) -> None:
        self.config = config or get_ai_client_config()

    @property
    def model_name(self) -> str:
        return self.config.model

    def chat_json(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
    ) -> dict[str, Any]:
        content = self._chat_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
        )

        try:
            parsed = json.loads(self._strip_json_fence(content))
        except json.JSONDecodeError as exc:
            raise AIResponseError("AI response was not valid JSON.") from exc

        if not isinstance(parsed, dict):
            raise AIResponseError("AI response JSON must be an object.")
        return parsed

    def _chat_completion(self, *, system_prompt: str, user_prompt: str, temperature: float) -> str:
        self._ensure_configured()

        payload = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "response_format": {"type": "json_object"},
        }

        try:
            with httpx.Client(timeout=self.config.timeout_seconds) as client:
                response = client.post(
                    self._chat_completions_url(),
                    headers={"Authorization": f"Bearer {self.config.api_key}"},
                    json=payload,
                )
                response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise AIResponseError("AI provider request timed out.") from exc
        except httpx.HTTPStatusError as exc:
            raise AIResponseError(f"AI provider returned HTTP {exc.response.status_code}.") from exc
        except httpx.HTTPError as exc:
            raise AIResponseError("AI provider request failed.") from exc

        try:
            data = response.json()
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise AIResponseError("AI provider response format was unexpected.") from exc

        if not isinstance(content, str) or not content.strip():
            raise AIResponseError("AI provider returned empty content.")
        return content

    def _ensure_configured(self) -> None:
        api_key = (self.config.api_key or "").strip()
        if not api_key or api_key in PLACEHOLDER_API_KEYS:
            raise AIConfigurationError("AI_API_KEY is not configured.")

    def _chat_completions_url(self) -> str:
        return f"{self.config.base_url.rstrip('/')}/chat/completions"

    def _strip_json_fence(self, content: str) -> str:
        stripped = content.strip()
        if stripped.startswith("```json"):
            return stripped.removeprefix("```json").removesuffix("```").strip()
        if stripped.startswith("```"):
            return stripped.removeprefix("```").removesuffix("```").strip()
        return stripped
