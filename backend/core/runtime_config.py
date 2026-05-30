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
