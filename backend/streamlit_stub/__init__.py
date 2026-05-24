"""
Lightweight stub of `streamlit` for backend use (renamed).
This package mirrors the previous backend/streamlit stub but is
renamed to avoid shadowing the real `streamlit` installation when
running `streamlit run ...`.
"""
import logging

logger = logging.getLogger("helios.streamlit_stub")

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

# Expose components package (imported as streamlit.components.v1 in the stub)
from . import components  # noqa: E402, F401
