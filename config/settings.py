from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ALLOWED_LOG_LEVELS = frozenset({"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"})

class Settings(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_db: str

    database_url: str

    log_level: str = Field(default="INFO", description="Application log level.")

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    @field_validator("log_level")
    @classmethod
    def normalize_log_level(cls, value: str) -> str:
        normalized = value.upper()
        if normalized not in ALLOWED_LOG_LEVELS:
            allowed = ", ".join(sorted(ALLOWED_LOG_LEVELS))
            raise ValueError(f"log_level must be one of: {allowed}")
        return normalized


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
