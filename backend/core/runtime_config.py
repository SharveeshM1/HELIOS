import os

from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = BACKEND_DIR.parent
MEMORY_DIR = BACKEND_DIR / "memory"
UPLOADS_DIR = BACKEND_DIR / "uploads"

APP_VERSION = os.getenv(
    "HELIOS_APP_VERSION",
    "2.1.0"
)

ENVIRONMENT = os.getenv(
    "HELIOS_ENV",
    "local"
)

API_KEY = os.getenv(
    "HELIOS_API_KEY",
    ""
).strip()

AUTH_SECRET = os.getenv(
    "HELIOS_AUTH_SECRET",
    API_KEY
).strip()

ADMIN_USERNAME = os.getenv(
    "HELIOS_ADMIN_USERNAME",
    "admin"
).strip()

ADMIN_PASSWORD = os.getenv(
    "HELIOS_ADMIN_PASSWORD",
    ""
).strip()

TOKEN_TTL_MINUTES = int(
    os.getenv(
        "HELIOS_TOKEN_TTL_MINUTES",
        "480"
    )
)

RATE_LIMIT_PER_MINUTE = int(
    os.getenv(
        "HELIOS_RATE_LIMIT_PER_MINUTE",
        "120"
    )
)

STORAGE_BACKEND = os.getenv(
    "HELIOS_STORAGE_BACKEND",
    "json"
).strip().lower()

DATABASE_URL = os.getenv(
    "HELIOS_DATABASE_URL",
    ""
).strip()

WORKER_LEASE_SECONDS = int(
    os.getenv(
        "HELIOS_WORKER_LEASE_SECONDS",
        "90"
    )
)

MAX_CHAT_MESSAGE_CHARS = int(
    os.getenv(
        "HELIOS_MAX_CHAT_MESSAGE_CHARS",
        "12000"
    )
)

MAX_ATTACHMENT_CHARS = int(
    os.getenv(
        "HELIOS_MAX_ATTACHMENT_CHARS",
        "12000"
    )
)

ALLOWED_MODULES = {
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


def ensure_runtime_dirs() -> None:

    for directory in (
        MEMORY_DIR,
        UPLOADS_DIR
    ):

        directory.mkdir(
            exist_ok=True
        )
