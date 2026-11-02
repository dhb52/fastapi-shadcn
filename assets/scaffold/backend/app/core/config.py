from pathlib import Path
from typing import Literal

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "FastAPI + shadcn"
    environment: Literal["development", "staging", "production"] = "development"
    api_v1_prefix: str = "/api/v1"
    secret_key: str = "dev-only-change-me"
    database_url: str = "sqlite+aiosqlite:///./app.db"
    sql_echo: bool = False
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    captcha_enabled: bool = False
    captcha_ttl_seconds: int = 300
    rate_limit_enabled: bool = True
    rate_limit_storage_uri: str = "memory://"
    redis_url: str = "redis://localhost:6379/0"

    @field_validator("database_url")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+asyncpg://", 1)
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+asyncpg://", 1)
        return value

    @model_validator(mode="after")
    def reject_default_secret_outside_development(self) -> "Settings":
        if self.environment != "development" and self.secret_key == "dev-only-change-me":
            raise ValueError("Set SECRET_KEY to a non-default value outside development")
        return self


settings = Settings()
