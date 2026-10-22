"""Application settings loaded from the environment."""

from functools import lru_cache

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the API."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: PostgresDsn = Field(..., description="PostgreSQL SQLAlchemy connection URL.")
    secret_key: str = Field(..., min_length=32, description="JWT signing secret.")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(default=30, gt=0)
    cors_origins: str = "http://localhost:5500,http://127.0.0.1:5500"

    @property
    def cors_origin_list(self) -> list[str]:
        """Return normalized, configured development frontend origins."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings object for the current process."""
    return Settings()
