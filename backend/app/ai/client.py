from dataclasses import dataclass

from app.core.config import settings


@dataclass(frozen=True)
class AIClientConfig:
    base_url: str
    model: str
    timeout_seconds: int


def get_ai_client_config() -> AIClientConfig:
    return AIClientConfig(
        base_url=settings.ai_base_url,
        model=settings.ai_model,
        timeout_seconds=settings.ai_timeout_seconds,
    )

