from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ResumeFit"
    environment: str = "development"
    database_url: str = "sqlite:///./resumefit.db"
    ai_provider: str = "deepseek"
    ai_base_url: str = "https://api.deepseek.com"
    ai_api_key: str | None = None
    ai_model: str = "deepseek-chat"
    ai_timeout_seconds: int = 60
    cors_origins: str = "http://localhost:5173"
    jwt_secret_key: str = "change_me_for_local_dev_secret_please_replace"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    model_config = SettingsConfigDict(env_file=("../.env", ".env"), env_file_encoding="utf-8")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
