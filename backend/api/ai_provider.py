import os
import logging

from dotenv import load_dotenv # type: ignore

try:
    import ollama # type: ignore
except Exception:
    ollama = None

try:
    from api import gemini_client
except Exception:
    gemini_client = None

BACKEND_DIR = os.path.dirname(
    os.path.dirname(__file__)
)

load_dotenv(
    os.path.join(BACKEND_DIR, ".env")
)

logger = logging.getLogger("helios")


def _int_env(name, default):

    try:

        return int(
            os.getenv(
                name,
                str(default)
            )
        )

    except (TypeError, ValueError):

        return default


MODEL_NAME = os.getenv(
    "HELIOS_OLLAMA_MODEL",
    os.getenv(
        "OLLAMA_MODEL",
        "qwen2.5:3b"
    )
)
GEMINI_MODEL_NAME = os.getenv(
    "GEMINI_MODEL_NAME",
    "gemini-2.0-flash"
)
OLLAMA_NUM_PREDICT = _int_env(
    "HELIOS_OLLAMA_NUM_PREDICT",
    360
)

SYSTEM_PROMPT = """

You are HELIOS.

A futuristic autonomous AI operating system assistant.

You are intelligent, calm, concise, confident,
and slightly futuristic.

You help with:
- coding
- research
- automation
- system control
- productivity
- engineering

You speak naturally like a premium AI assistant.

Never say you are ChatGPT.

"""

# =========================================
# STANDARD RESPONSE
# =========================================

def _clean_provider_error(provider, error):

    logger.warning(
        "%s inference failed: %s",
        provider,
        error
    )

    return str(error).strip()


def _generate_with_gemini(prompt):

    if gemini_client is None:

        return None, "Gemini client is unavailable."

    response = gemini_client.generate_ai_response(
        str(prompt),
        model_name=GEMINI_MODEL_NAME
    )

    if response and response not in {
        "HELIOS AI systems are currently unavailable.",
        "HELIOS inference systems are not configured.",
        "HELIOS inference execution failed.",
        "HELIOS could not generate a response."
    }:

        return response, None

    return None, response or "Gemini returned an empty response."


def _generate_with_ollama(prompt):

    if ollama is None:

        return None, "Ollama package is unavailable."

    try:

        response = ollama.chat(

            model=MODEL_NAME,

            messages=[

                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },

                {
                    "role": "user",
                    "content": str(prompt)
                }

            ],
            options={
                "num_predict": OLLAMA_NUM_PREDICT
            }
        )

        message = getattr(
            response,
            "message",
            None
        )

        content = None

        if message is not None:

            content = getattr(
                message,
                "content",
                None
            )

            if content is None and isinstance(message, dict):

                content = message.get(
                    "content"
                )

        if content is None:

            content = response["message"]["content"]

        return content, None

    except Exception as e:

        return None, _clean_provider_error(
            "Ollama",
            e
        )


def generate_ai_response(prompt):

    provider_order = os.getenv(
        "HELIOS_AI_PROVIDER",
        "ollama"
    )

    errors = []

    for provider in [
        item.strip().lower()
        for item in provider_order.split(",")
        if item.strip()
    ]:

        if provider == "gemini":

            response, error = _generate_with_gemini(
                prompt
            )

        elif provider == "ollama":

            response, error = _generate_with_ollama(
                prompt
            )

        else:

            response = None
            error = f"Unknown provider: {provider}"

        if response:

            return response

        if error:

            errors.append(
                f"{provider}: {error}"
            )

    return (
        "HELIOS inference is not available right now. "
        f"Start Ollama and make sure the `{MODEL_NAME}` model is available, then try again.\n\n"
        + "\n".join(errors)
    )


def generate_response(prompt):

    return generate_ai_response(prompt)

# =========================================
# STREAM RESPONSE
# =========================================

def stream_ai_response(prompt):

    try:

        if ollama is None:

            print(
                generate_ai_response(prompt)
            )

            return

        stream = ollama.chat(

            model=MODEL_NAME,

            messages=[

                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },

                {
                    "role": "user",
                    "content": str(prompt)
                }

            ],

            stream=True
        )

        for chunk in stream:

            content = chunk["message"]["content"]

            print(content, end="", flush=True)

        print()

    except Exception as e:

        print(f"""

[HELIOS AI ERROR]

{str(e)}

""")
