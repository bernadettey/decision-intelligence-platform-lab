from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Decision Intelligence Platform Lab"
    database_url: str = "postgresql+psycopg://fpa_user:fpa_password@localhost:5432/decision_intelligence"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    semantic_metrics_path: str = "semantic_layer/metrics.yaml"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
