import os
from pathlib import Path
from typing import Set

from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = BACKEND_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="HELIOS_",
        env_file=str(BACKEND_DIR / ".env"),
        extra="ignore"
    )

    APP_VERSION: str = "2.1.0"
    ENV: str = "local"
    API_KEY: str = ""
    AUTH_SECRET: str = ""
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = ""
    TOKEN_TTL_MINUTES: int = 480
    RATE_LIMIT_PER_MINUTE: int = 120
    STORAGE_BACKEND: str = "json"
    DATABASE_URL: str = ""
    WORKER_LEASE_SECONDS: int = 90
    MAX_CHAT_MESSAGE_CHARS: int = 12000
    MAX_ATTACHMENT_CHARS: int = 12000
    VECTOR_BACKEND: str = "local"
    VECTOR_DATABASE_URL: str = ""
    VECTOR_PERSIST_DIR: Path = BACKEND_DIR / "memory" / "chroma"
    API_KEY_ROLE: str = "admin"
    AUTH_COOKIE_SECURE: bool = False

    MEMORY_DIR: Path = BACKEND_DIR / "memory"
    UPLOADS_DIR: Path = BACKEND_DIR / "uploads"

    ALLOWED_MODULES: Set[str] = {
        "dashboard",
        "research",
        "code",
        "analytics",
        "voice",
        "collab",
        "swarm",
        "loop",
        "planning",
        "reasoning",
        "workflow",
        "knowledge"
    }

    @property
    def EFFECTIVE_AUTH_SECRET(self) -> str:
        return self.AUTH_SECRET or self.API_KEY


settings = Settings()

# Export for backward compatibility with existing imports
APP_VERSION = settings.APP_VERSION
ENVIRONMENT = settings.ENV
API_KEY = settings.API_KEY
AUTH_SECRET = settings.EFFECTIVE_AUTH_SECRET
ADMIN_USERNAME = settings.ADMIN_USERNAME
ADMIN_PASSWORD = settings.ADMIN_PASSWORD
TOKEN_TTL_MINUTES = settings.TOKEN_TTL_MINUTES
RATE_LIMIT_PER_MINUTE = settings.RATE_LIMIT_PER_MINUTE
STORAGE_BACKEND = settings.STORAGE_BACKEND.lower()
DATABASE_URL = settings.DATABASE_URL
WORKER_LEASE_SECONDS = settings.WORKER_LEASE_SECONDS
MAX_CHAT_MESSAGE_CHARS = settings.MAX_CHAT_MESSAGE_CHARS
MAX_ATTACHMENT_CHARS = settings.MAX_ATTACHMENT_CHARS
VECTOR_BACKEND = settings.VECTOR_BACKEND.lower()
VECTOR_DATABASE_URL = settings.VECTOR_DATABASE_URL
VECTOR_PERSIST_DIR = settings.VECTOR_PERSIST_DIR
API_KEY_ROLE = settings.API_KEY_ROLE.lower()
AUTH_COOKIE_SECURE = settings.AUTH_COOKIE_SECURE
MEMORY_DIR = settings.MEMORY_DIR
UPLOADS_DIR = settings.UPLOADS_DIR
ALLOWED_MODULES = settings.ALLOWED_MODULES


def ensure_runtime_dirs() -> None:
    for directory in (
        MEMORY_DIR,
        UPLOADS_DIR,
        VECTOR_PERSIST_DIR
    ):
        directory.mkdir(
            parents=True,
            exist_ok=True
        )
