import logging
import json

from fastapi import (
    FastAPI,
    HTTPException,
    Request,
    Response,
    WebSocket,
    WebSocketDisconnect
)

from fastapi.middleware.cors import (
    CORSMiddleware
)

from fastapi.concurrency import (
    run_in_threadpool
)

from pydantic import BaseModel
from pydantic import Field

from dotenv import load_dotenv
import os
import httpx

from api.ai_provider import (
    GEMINI_MODEL_NAME,
    MODEL_NAME,
    generate_ai_response
)

try:
    import ollama # type: ignore
except Exception:
    ollama = None

from core.cognitive_engine import (
    CognitiveEngine
)
from core.source_library import (
    load_sources,
    search_sources,
    source_stats,
    upsert_source
)

# =========================================
# LOAD ENV
# =========================================

load_dotenv(
    os.path.join(
        os.path.dirname(
            os.path.dirname(__file__)
        ),
        ".env"
    )
)

# =========================================
# LOGGER
# =========================================

logging.basicConfig(
    level=logging.INFO
)

logger = logging.getLogger(
    "helios-backend"
)


def parse_csv_env(name, fallback):

    raw_value = os.getenv(
        name,
        fallback
    )

    values = [
        item.strip()
        for item in raw_value.split(",")
        if item.strip()
    ]

    return values or [
        item.strip()
        for item in fallback.split(",")
        if item.strip()
    ]

# =========================================
# SYSTEM PROMPT
# =========================================

SYSTEM_PROMPT = """

You are HELIOS.

An advanced realtime conversational AI system.

========================================
PERSONALITY
========================================

You are:
- futuristic
- intelligent
- emotionally aware
- calm
- conversational
- premium
- modern

You NEVER:
- ramble
- sound robotic
- overexplain
- sound corporate
- generate essays
- repeat yourself

========================================
VOICE STYLE
========================================

- Speak naturally
- Keep replies SHORT
- Use smooth pacing
- Sound alive and modern
- Avoid markdown
- Avoid giant responses
- Prefer conversational language

========================================
RESPONSE RULES
========================================

- Prefer 1–3 sentences
- Stay concise
- Prioritize clarity
- Respond fluidly
- Avoid filler completely

"""

# =========================================
# FASTAPI APP
# =========================================

app = FastAPI(

    title="HELIOS Backend",

    version="2.0.0"
)

# =========================================
# CORS
# =========================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=parse_csv_env(
        "HELIOS_CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000"
    ),

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)

cognitive_engine = CognitiveEngine()


class ChatRequest(BaseModel):

    message: str
    module: str = "dashboard"
    agent: str = "HELIOS"
    attachments: list[dict] = Field(
        default_factory=list
    )


class ChatResponse(BaseModel):

    response: str
    module: str
    agent: str
    trace: list[dict]
    plan: list[dict]


class SourceRequest(BaseModel):

    name: str
    type: str = "FILE"
    size: str = "unknown"
    content: str = ""
    scope: str = "project"


class SourceResponse(BaseModel):

    source: dict
    stats: dict


MAX_SOURCE_CONTENT_CHARS = int(
    os.getenv(
        "HELIOS_MAX_SOURCE_CONTENT_CHARS",
        "12000"
    )
)

OPENAI_REALTIME_MODEL = os.getenv(
    "OPENAI_REALTIME_MODEL",
    "gpt-realtime"
)

OPENAI_REALTIME_VOICE = os.getenv(
    "OPENAI_REALTIME_VOICE",
    "marin"
)

# =========================================
# CLEAN RESPONSE
# =========================================

def clean_response(text):

    if not text:

        return (
            "HELIOS could not "
            "generate a response."
        )

    text = str(text).strip()

    while "\n\n\n" in text:

        text = text.replace(
            "\n\n\n",
            "\n\n"
        )

    return text.strip()

# =========================================
# GENERATE RESPONSE
# =========================================

def generate_response(

    user_message

):

    safe_message = str(
        user_message
    ).strip()

    if not safe_message:

        return (
            "Please provide a valid message."
        )

    combined_prompt = f"""

{SYSTEM_PROMPT}

========================================
USER MESSAGE
========================================

{safe_message}

"""

    try:

        result = generate_ai_response(
            combined_prompt
        )

        if not result:

            return (
                "HELIOS inference returned "
                "an empty response."
            )

        return clean_response(
            result
        )

    except Exception:

        logger.exception(
            "Inference failure."
        )

        return (
            "HELIOS inference execution failed."
        )


def generate_cognitive_response(
    user_message,
    module="dashboard",
    agent="HELIOS",
    attachments=None
):

    attachments = attachments or []

    saved_attachments = []

    for item in attachments:

        if item.get("content"):

            saved_attachments.append(
                upsert_source(
                    item.get("name", "source"),
                    item.get("type", "FILE"),
                    item.get("size", "unknown"),
                    item.get("content", ""),
                    item.get("scope", "chat")
                )
            )

    source_matches = search_sources(
        user_message,
        limit=5
    )

    attachment_context = "\n".join(
        f"""
- {item.get('name', 'source')} ({item.get('type', 'file')}, {item.get('size', 'unknown size')})
{item.get('content', '')}
"""
        for item in attachments
    )

    source_context = "\n".join(
        f"""
- {item.get('name', 'source')} ({item.get('type', 'file')}, {item.get('scope', 'project')})
{str(item.get('content', ''))[:3000]}
"""
        for item in source_matches
    )

    enhanced_message = f"""
Active Module:
{module}

Selected Agent:
{agent}

Attachments:
{attachment_context or "None"}

Saved Knowledge Sources:
{source_context or "None"}

User Message:
{user_message}
"""

    return cognitive_engine.execute(
        enhanced_message
    )


def get_ai_status():

    providers = {
        "gemini": {
            "status": "unknown",
            "model": GEMINI_MODEL_NAME,
            "model_available": False
        },
        "ollama": {
            "status": "unknown",
            "model": MODEL_NAME,
            "model_available": False,
            "available_models": []
        }
    }

    try:

        from api import gemini_client

        gemini_ready = bool(
            gemini_client.genai
            and
            gemini_client.GEMINI_API_KEY
        )

        providers["gemini"].update(
            {
                "status": "active" if gemini_ready else "not_configured",
                "model_available": gemini_ready
            }
        )

    except Exception as error:

        providers["gemini"].update(
            {
                "status": "offline",
                "error": str(error)
            }
        )

    try:

        if ollama is None:

            raise RuntimeError(
                "Ollama package is unavailable."
            )

        models = ollama.list()
        available_models = []

        for model in models.get("models", []):

            if isinstance(model, dict):

                available_models.append(
                    model.get("name") or model.get("model") or ""
                )

            else:

                available_models.append(
                    str(getattr(model, "model", ""))
                )

        model_available = MODEL_NAME in available_models

        providers["ollama"].update(
            {
                "status": "active" if model_available else "model_missing",
                "model_available": model_available,
                "available_models": [
                item
                for item in available_models
                if item
                ]
            }
        )

    except Exception as error:

        providers["ollama"].update(
            {
                "status": "offline",
                "error": str(error)
            }
        )

    provider_order = [
        item.strip().lower()
        for item in os.getenv(
            "HELIOS_AI_PROVIDER",
            "ollama,gemini"
        ).split(",")
        if item.strip()
    ]

    active_provider = next(
        (
            provider
            for provider in provider_order
            if providers.get(provider, {}).get("model_available")
        ),
        None
    )

    if active_provider:

        active = providers[active_provider]

        return {
            "status": "active",
            "provider": active_provider,
            "model": active["model"],
            "model_available": True,
            "providers": providers
        }

    return {
        "status": "offline",
        "provider": None,
        "model": MODEL_NAME,
        "model_available": False,
        "providers": providers
    }

# =========================================
# ROOT ENDPOINT
# =========================================

@app.get("/")

async def root():

    return {

        "name":
        "HELIOS Backend",

        "status":
        "online",

        "websocket":
        "/ws"
    }

# =========================================
# HEALTH ENDPOINT
# =========================================

@app.get("/health")

async def health():

    ai_status = get_ai_status()

    return {

        "backend":
        "online",

        "ai":
        ai_status,

        "cognitive_engine":
        cognitive_engine.status(),

        "sources":
        source_stats()
    }


@app.get("/sources")

async def sources():

    return {
        "sources": load_sources(),
        "stats": source_stats()
    }


@app.post("/sources", response_model=SourceResponse)

async def save_source(
    request: SourceRequest
):

    source_name = request.name.strip()
    source_content = request.content[:MAX_SOURCE_CONTENT_CHARS]

    if not source_name:

        raise HTTPException(
            status_code=400,
            detail="Source name is required."
        )

    source = await run_in_threadpool(
        upsert_source,
        source_name,
        request.type,
        request.size,
        source_content,
        request.scope
    )

    return SourceResponse(
        source=source,
        stats=source_stats()
    )


@app.post("/chat", response_model=ChatResponse)

async def chat(
    request: ChatRequest
):

    if (
        request.module == "dashboard"
        and
        not request.attachments
    ):

        response = await run_in_threadpool(
            generate_response,
            request.message
        )

        return ChatResponse(
            response=clean_response(response),
            module=request.module,
            agent=request.agent,
            trace=[
                {
                    "stage": "response",
                    "actor": request.agent,
                    "payload": {
                        "mode": "fast_chat"
                    }
                }
            ],
            plan=[
                {
                    "agent": request.agent,
                    "objective": "Direct response"
                }
            ]
        )

    response = await run_in_threadpool(
        generate_cognitive_response,
        request.message,
        request.module,
        request.agent,
        request.attachments
    )

    status = cognitive_engine.status()

    return ChatResponse(
        response=clean_response(response),
        module=request.module,
        agent=request.agent,
        trace=status.get("trace", []),
        plan=status.get("plan", [])
    )


@app.post("/realtime/session")

async def create_realtime_session(
    request: Request
):

    api_key = os.getenv(
        "OPENAI_API_KEY",
        ""
    ).strip()

    if not api_key:

        raise HTTPException(
            status_code=501,
            detail="OPENAI_API_KEY is required for HELIOS realtime voice."
        )

    offer_sdp = await request.body()

    if not offer_sdp:

        raise HTTPException(
            status_code=400,
            detail="Missing WebRTC offer SDP."
        )

    session_config = {
        "type": "realtime",
        "model": OPENAI_REALTIME_MODEL,
        "audio": {
            "output": {
                "voice": OPENAI_REALTIME_VOICE
            }
        },
        "instructions": (
            "You are HELIOS, a warm, emotionally aware realtime voice assistant. "
            "Speak naturally and briefly. Listen like a human collaborator. "
            "Do not give long lectures unless asked. If interrupted, stop and adapt."
        )
    }

    try:

        async with httpx.AsyncClient(
            timeout=30
        ) as client:

            response = await client.post(
                "https://api.openai.com/v1/realtime/calls",
                headers={
                    "Authorization": f"Bearer {api_key}"
                },
                files={
                    "sdp": (
                        None,
                        offer_sdp.decode(
                            "utf-8",
                            errors="ignore"
                        )
                    ),
                    "session": (
                        None,
                        json.dumps(session_config)
                    )
                }
            )

        if response.status_code >= 400:

            raise HTTPException(
                status_code=response.status_code,
                detail=response.text[:1200]
            )

        return Response(
            content=response.text,
            media_type="application/sdp"
        )

    except HTTPException:

        raise

    except Exception as error:

        logger.exception(
            "Realtime session creation failed."
        )

        raise HTTPException(
            status_code=502,
            detail=str(error)
        )

# =========================================
# WEBSOCKET ENDPOINT
# =========================================

@app.websocket("/ws")

async def websocket_endpoint(

    websocket: WebSocket

):

    await websocket.accept()

    logger.info(
        "Client connected."
    )

    try:

        while True:

            # =================================
            # RECEIVE MESSAGE
            # =================================

            user_message = await (
                websocket.receive_text()
            )

            logger.info(
                f"Incoming message: "
                f"{user_message[:120]}"
            )

            # =================================
            # GENERATE RESPONSE
            # =================================

            ai_response = await run_in_threadpool(
                generate_cognitive_response,
                user_message
            )

            # =================================
            # SEND RESPONSE
            # =================================

            await websocket.send_text(
                ai_response
            )

    # =====================================
    # CLIENT DISCONNECT
    # =====================================

    except WebSocketDisconnect:

        logger.info(
            "Client disconnected."
        )

    # =====================================
    # SERVER ERROR
    # =====================================

    except Exception:

        logger.exception(
            "WebSocket failure."
        )

        try:

            await websocket.send_text(
                "HELIOS websocket connection failed."
            )

        except Exception:

            logger.error(
                "Failed to send websocket error."
            )

    finally:

        try:

            await websocket.close()

        except Exception:

            pass
