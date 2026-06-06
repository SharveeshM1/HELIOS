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
    ""
).strip()

API_KEY_ROLE = os.getenv(
    "HELIOS_API_KEY_ROLE",
    "operator"
).strip().lower()

AUTH_COOKIE_SECURE = os.getenv(
    "HELIOS_AUTH_COOKIE_SECURE",
    "true"
    if ENVIRONMENT == "production"
    else "false"
).strip().lower() in {
    "1",
    "true",
    "yes",
    "on"
}

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

VECTOR_BACKEND = os.getenv(
    "HELIOS_VECTOR_BACKEND",
    "local"
).strip().lower()

VECTOR_DATABASE_URL = os.getenv(
    "HELIOS_VECTOR_DATABASE_URL",
    ""
).strip()

VECTOR_PERSIST_DIR = os.getenv(
    "HELIOS_VECTOR_PERSIST_DIR",
    str(
        MEMORY_DIR / "chroma"
    )
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

def validate_config():
    if not AUTH_SECRET and ENVIRONMENT == 'production':
        raise RuntimeError('HELIOS_AUTH_SECRET must be set in production environment')
    if STORAGE_BACKEND == 'postgres' and not DATABASE_URL:
        raise RuntimeError('HELIOS_DATABASE_URL must be set for postgres backend')

ensure_runtime_dirs()
validate_config()
