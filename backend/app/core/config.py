"""
KidecoIQ — Core Configuration
Loads settings from environment variables or .env file.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # App
    APP_NAME: str = "KidecoIQ API"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql://kideco:kideco@localhost:5432/kidecoiq"

    # JWT (stub — will be refined in later phases)
    JWT_SECRET_KEY: str = "kideco-dev-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # CORS
    CORS_ORIGINS: list[str] = ["*"]


@lru_cache()
def get_settings() -> Settings:
    return Settings()
