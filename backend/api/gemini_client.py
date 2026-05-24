import os
import logging
import warnings

from dotenv import load_dotenv # type: ignore

# =========================================================
# LOAD ENV
# =========================================================

load_dotenv(
    os.path.join(
        os.path.dirname(
            os.path.dirname(__file__)
        ),
        ".env"
    )
)

logger = logging.getLogger("helios")

# =========================================================
# GEMINI IMPORT
# =========================================================

genai = None
_GENAI_IMPORT_ATTEMPTED = False


def get_genai_client():

    global genai
    global _GENAI_IMPORT_ATTEMPTED

    if _GENAI_IMPORT_ATTEMPTED:
        return genai

    _GENAI_IMPORT_ATTEMPTED = True

    try:

        with warnings.catch_warnings():
            warnings.simplefilter(
                "ignore",
                FutureWarning
            )

            import google.generativeai as legacy_genai # type: ignore

        genai = legacy_genai

    except Exception as e:

        logger.error(
            f"Gemini import failed: {e}"
        )

        genai = None

    return genai


def configure_genai_client():

    client = get_genai_client()

    if not client or not GEMINI_API_KEY:
        return client

    try:

        client.configure(
            api_key=GEMINI_API_KEY
        )

        logger.info(
            "Gemini configured successfully."
        )

    except Exception as e:

        logger.error(
            f"Gemini configuration failed: {e}"
        )

    return client

# =========================================================
# API KEY
# =========================================================

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

# =========================================================
# GENERATE RESPONSE
# =========================================================

def generate_ai_response(
    prompt: str,
    model_name: str = "gemini-2.0-flash"
) -> str:

    # =====================================================
    # SDK CHECK
    # =====================================================

    client = configure_genai_client()

    if client is None:

        logger.error(
            "Gemini SDK unavailable."
        )

        return (
            "HELIOS AI systems are currently unavailable."
        )

    # =====================================================
    # API KEY CHECK
    # =====================================================

    if not GEMINI_API_KEY:

        logger.error(
            "Missing GEMINI_API_KEY."
        )

        return (
            "HELIOS inference systems are not configured."
        )

    # =====================================================
    # EMPTY PROMPT CHECK
    # =====================================================

    if not prompt or not str(prompt).strip():

        logger.warning(
            "Empty prompt received."
        )

        return (
            "No valid request received."
        )

    # =====================================================
    # GENERATION
    # =====================================================

    try:

        model = client.GenerativeModel(
            model_name
        )

        response = model.generate_content(
            prompt,
            request_options={
                "timeout": 20
            }
        )

        # =================================================
        # RESPONSE EXTRACTION
        # =================================================

        text = ""

        if hasattr(response, "text"):

            text = response.text

        else:

            try:

                text = str(response)

            except Exception:

                text = ""

        # =================================================
        # EMPTY RESPONSE
        # =================================================

        if not text or not str(text).strip():

            logger.warning(
                "Gemini returned empty response."
            )

            return (
                "HELIOS could not generate a response."
            )

        # =================================================
        # SAFE CLEAN RESPONSE
        # =================================================

        cleaned = str(text).strip()

        return cleaned

    # =====================================================
    # EXCEPTION HANDLER
    # =====================================================

    except Exception as e:

        logger.exception(
            "Gemini generation failed"
        )

        return (
            "HELIOS inference execution failed."
        )
