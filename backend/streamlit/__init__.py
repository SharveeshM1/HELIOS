"""
Lightweight stub of `streamlit` for backend use.
This package provides minimal no-op implementations of commonly
used `streamlit` APIs so backend code can run without the real
Streamlit dependency (Streamlit is intended for frontend only).
"""
import logging

logger = logging.getLogger("helios.streamlit")

# Session-like storage used by backend modules
session_state = {}

def set_page_config(*args, **kwargs):
    return None

def markdown(*args, **kwargs):
    return None

def title(*args, **kwargs):
    return None

def warning(msg):
    logger.warning(msg)

def success(msg):
    logger.info(msg)

def chat_input(prompt=""):
    return None

def error(msg):
    logger.error(msg)

# Expose components package (imported as streamlit.components.v1)
from . import components  # noqa: E402, F401
