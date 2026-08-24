from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class GeneratorSettings(BaseSettings):
    """Configuration for synthetic simulation runs."""

    model_config = SettingsConfigDict(env_prefix="GENERATOR_", env_file=".env", extra="ignore")

    generator_version: str = Field(default="m1.3-phase1")
    simulation_id: int = Field(default=1, ge=1)


def get_generator_settings() -> GeneratorSettings:
    return GeneratorSettings()
