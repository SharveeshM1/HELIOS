import logging
import json
import time
import uuid
import asyncio

from fastapi import (
    BackgroundTasks,
    FastAPI,
    HTTPException,
    Request,
    Response,
    WebSocket,
    WebSocketDisconnect
)
from fastapi.responses import JSONResponse

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
from core.code_workflow import (
    run_general_code_repair,
    run_structured_code_repair
)
from core.source_library import (
    load_sources,
    search_sources,
    source_stats,
    upsert_source
)
from core.research_grounding import (
    build_grounded_research_artifact
)
from core.project_brain import (
    build_project_brain
)
from core.observability import (
    build_observability_report
)
from core.git_workflow import (
    commit_staged_changes,
    git_status
)
from core.autonomous_runs import (
    cancel_run,
    create_run,
    execute_run,
    get_run,
    load_runs,
    queue_run,
    reconcile_run,
    resume_run
)
from core.auth import (
    authenticate_user,
    create_user,
    has_permission,
    issue_token,
    load_users,
    public_user,
    verify_token
)
from core.runtime_config import (
    ALLOWED_MODULES,
    API_KEY,
    APP_VERSION,
    AUTH_SECRET,
    ENVIRONMENT,
    MAX_ATTACHMENT_CHARS,
    MAX_CHAT_MESSAGE_CHARS,
    RATE_LIMIT_PER_MINUTE,
    STORAGE_BACKEND
)
from core.runtime_store import (
    allow_rate_limited_request,
    list_jobs,
    storage_status
)
from core.shared_bus import (
    shared_bus
)
from core.mission_ledger import (
    advance_mission,
    agent_activity,
    create_mission,
    latest_missions,
    load_mission_events,
    mission_stats,
    record_mission_event
)
from core.mission_workflows import (
    run_mission_workflow
)
from core.tool_executor import (
    execute_agent_tool
)
from core.tool_manager import (
    execute_tool,
    list_tools
)
from memory import execution_memory

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

STARTED_AT = time.time()
REQUEST_COUNT = 0
RATE_BUCKETS = {}
PUBLIC_PATHS = {
    "/health",
    "/ready",
    "/metrics",
    "/voice/status",
    "/auth/login"
}

PERMISSION_PREFIXES = {
    "/git/commit": "commit",
    "/tools/execute": "execute",
    "/code/repair": "write",
    "/autonomy/runs": "execute",
    "/missions": "execute",
    "/sources": "write",
    "/auth/users": "admin"
}


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

CONVERSATION_MODES = {
    "balanced": "Answer clearly, balance speed with useful depth, and stay scoped.",
    "concise": "Answer directly in the smallest useful form.",
    "deep": "Analyze tradeoffs, risks, and implementation details before concluding.",
    "execute": "Prioritize actionable steps, tools, verification, and concrete outcomes."
}

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

    message: str = Field(
        min_length=1,
        max_length=MAX_CHAT_MESSAGE_CHARS
    )
    module: str = "dashboard"
    agent: str = "HELIOS"
    mode: str = "balanced"
    attachments: list[dict] = Field(
        default_factory=list
    )


class ChatResponse(BaseModel):

    response: str
    module: str
    agent: str
    mode: str
    trace: list[dict]
    plan: list[dict]
    citations: list[dict] = Field(
        default_factory=list
    )
    grounded: bool = False


class SourceRequest(BaseModel):

    name: str = Field(
        min_length=1,
        max_length=180
    )
    type: str = "FILE"
    size: str = "unknown"
    content: str = Field(
        default="",
        max_length=MAX_ATTACHMENT_CHARS
    )
    scope: str = "project"


class SourceResponse(BaseModel):

    source: dict
    stats: dict


class SourceSearchResponse(BaseModel):

    sources: list[dict]
    stats: dict
    query: str


class SourceIntelligenceResponse(BaseModel):

    query: str
    sources: list[dict]
    citations: list[dict]
    claims: list[dict]
    grounded_answer: str
    coverage: dict
    stats: dict
    graph: dict = Field(
        default_factory=dict
    )


class MissionEventsResponse(BaseModel):

    events: list[dict]
    missions: list[dict] = Field(
        default_factory=list
    )
    stats: dict
    agents: dict = Field(
        default_factory=dict
    )


class MissionRequest(BaseModel):

    title: str = Field(
        min_length=1,
        max_length=180
    )
    module: str = "planning"
    agent: str = "Orion"
    detail: str = Field(
        default="",
        max_length=360
    )


class MissionResponse(BaseModel):

    mission: dict
    events: list[dict]
    stats: dict
    agents: dict


class MissionAdvanceRequest(BaseModel):

    stage: str = Field(
        min_length=1,
        max_length=40
    )
    detail: str = Field(
        default="",
        max_length=360
    )
    agent: str | None = None
    module: str | None = None


class MissionAdvanceResponse(BaseModel):

    mission: dict
    event: dict
    missions: list[dict]
    stats: dict
    agents: dict


class MissionRunResponse(BaseModel):

    mission: dict
    event: dict
    artifact: dict
    task: dict
    missions: list[dict]
    stats: dict
    agents: dict


class ToolExecuteRequest(BaseModel):

    tool: str = Field(
        min_length=1,
        max_length=80
    )
    args: list = Field(
        default_factory=list
    )
    kwargs: dict = Field(
        default_factory=dict
    )
    agent: str | None = None
    module: str = "dashboard"
    retries: int = Field(
        default=0,
        ge=0,
        le=2
    )


class ToolExecuteResponse(BaseModel):

    tool: str
    status: str
    result: object | None = None
    error: str | None = None
    events: list[dict]
    stats: dict


class ExecutionEventsResponse(BaseModel):

    events: list[dict]
    stats: dict


class ProjectBrainResponse(BaseModel):

    nodes: list[dict]
    links: list[dict]
    stats: dict
    summary: dict


class ObservabilityResponse(BaseModel):

    stats: dict
    window: dict
    rates: dict
    tool_counts: dict
    status_counts: dict
    slow_tools: list[dict]
    recent_failures: list[dict]
    recommendations: list[str]


class GitCommitRequest(BaseModel):

    message: str = Field(
        min_length=1,
        max_length=240
    )
    confirm: bool = False


class GitCommitResponse(BaseModel):

    status: str
    reason: str | None = None
    message: str | None = None
    stdout: str | None = None
    stderr: str | None = None
    return_code: int | None = None
    git: dict


class VoiceStatusResponse(BaseModel):

    realtime_available: bool
    openai_key_configured: bool
    model: str
    voice: str
    max_offer_bytes: int
    status: str


class AutonomousRunRequest(BaseModel):

    objective: str = Field(
        min_length=1,
        max_length=MAX_CHAT_MESSAGE_CHARS
    )


class AutonomousRunResponse(BaseModel):

    run: dict


class CodeRepairRequest(BaseModel):

    objective: str = Field(
        min_length=1,
        max_length=MAX_CHAT_MESSAGE_CHARS
    )
    edits: list[dict] = Field(
        default_factory=list
    )
    verification_commands: list[str] = Field(
        default_factory=list
    )
    verification_attempts: int = Field(
        default=2,
        ge=1,
        le=3
    )


class GeneralCodeRepairRequest(BaseModel):

    objective: str = Field(
        min_length=1,
        max_length=MAX_CHAT_MESSAGE_CHARS
    )
    target_files: list[str] = Field(
        default_factory=list
    )
    verification_commands: list[str] = Field(
        default_factory=list
    )
    repair_attempts: int = Field(
        default=2,
        ge=1,
        le=3
    )


class LoginRequest(BaseModel):

    username: str = Field(
        min_length=1,
        max_length=80
    )
    password: str = Field(
        min_length=1,
        max_length=240
    )


class UserCreateRequest(LoginRequest):

    role: str = "viewer"


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

MAX_REALTIME_OFFER_BYTES = int(
    os.getenv(
        "HELIOS_MAX_REALTIME_OFFER_BYTES",
        "120000"
    )
)


@app.middleware("http")

async def request_observability(
    request: Request,
    call_next
):

    global REQUEST_COUNT

    REQUEST_COUNT += 1
    client_host = (
        request.client.host
        if request.client
        else "unknown"
    )
    request_id = request.headers.get(
        "x-request-id",
        str(
            uuid.uuid4()
        )
    )
    started = time.perf_counter()
    auth_header = request.headers.get(
        "authorization",
        ""
    )
    token = (
        auth_header[7:].strip()
        if auth_header.lower().startswith(
            "bearer "
        )
        else ""
    )
    user = verify_token(
        token
    ) if token else None
    request.state.helios_user = user

    if (
        (
            API_KEY
            or AUTH_SECRET
        )
        and
        request.url.path not in PUBLIC_PATHS
        and
        (
            not API_KEY
            or request.headers.get(
                "x-helios-api-key",
                ""
            )
            != API_KEY
        )
        and user is None
    ):

        return JSONResponse(
            status_code=401,
            content={
                "detail": "Missing or invalid HELIOS API key."
            }
        )

    required_permission = next(
        (
            permission
            for prefix, permission in PERMISSION_PREFIXES.items()
            if request.url.path.startswith(
                prefix
            )
            and request.method not in {
                "GET",
                "HEAD",
                "OPTIONS"
            }
        ),
        None
    )
    if request.url.path.startswith(
        "/auth/users"
    ):
        required_permission = "admin"
    if (
        required_permission
        and user is not None
        and not has_permission(
            user,
            required_permission
        )
    ):
        return JSONResponse(
            status_code=403,
            content={
                "detail": f"Role does not allow '{required_permission}'."
            }
        )

    rate_allowed = True
    if STORAGE_BACKEND in {
        "sqlite",
        "postgres"
    }:
        rate_allowed = allow_rate_limited_request(
            client_host,
            RATE_LIMIT_PER_MINUTE
        )
    else:
        now = time.time()
        bucket = RATE_BUCKETS.setdefault(
            client_host,
            []
        )
        RATE_BUCKETS[
            client_host
        ] = [
            timestamp
            for timestamp in bucket
            if now - timestamp < 60
        ]
        rate_allowed = len(
            RATE_BUCKETS[
                client_host
            ]
        ) < RATE_LIMIT_PER_MINUTE
        if rate_allowed:
            RATE_BUCKETS[
                client_host
            ].append(
                now
            )

    if not rate_allowed:

        return JSONResponse(
            status_code=429,
            content={
                "detail": "HELIOS rate limit exceeded."
            }
        )

    response = await call_next(
        request
    )

    duration_ms = round(
        (
            time.perf_counter()
            - started
        ) * 1000,
        2
    )

    response.headers["x-request-id"] = request_id
    response.headers["x-helios-duration-ms"] = str(
        duration_ms
    )
    response.headers["x-content-type-options"] = "nosniff"
    response.headers["x-frame-options"] = "DENY"
    response.headers["referrer-policy"] = "no-referrer"
    response.headers["x-helios-storage"] = STORAGE_BACKEND

    return response

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
    mode="balanced",
    attachments=None
):

    attachments = attachments or []

    saved_attachments = []
    safe_attachments = []

    for item in attachments:

        clean_item = {
            **item,
            "content": str(
                item.get(
                    "content",
                    ""
                )
            )[:MAX_ATTACHMENT_CHARS]
        }

        safe_attachments.append(
            clean_item
        )

        if clean_item.get("content"):

            saved_attachments.append(
                upsert_source(
                    clean_item.get("name", "source"),
                    clean_item.get("type", "FILE"),
                    clean_item.get("size", "unknown"),
                    clean_item.get("content", ""),
                    clean_item.get("scope", "chat")
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
        for item in safe_attachments
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

Conversation Mode:
{mode}

Mode Directive:
{CONVERSATION_MODES.get(mode, CONVERSATION_MODES["balanced"])}

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

        "version":
        APP_VERSION,

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

        "version":
        APP_VERSION,

        "environment":
        ENVIRONMENT,

        "uptime_seconds":
        round(
            time.time()
            - STARTED_AT,
            2
        ),

        "request_count":
        REQUEST_COUNT,

        "ai":
        ai_status,

        "cognitive_engine":
        cognitive_engine.status(),

        "missions":
        {
            **mission_stats(),
            "agents": agent_activity()
        },

        "sources":
        source_stats(),

        "execution":
        execution_memory.execution_stats(),

        "storage":
        storage_status(),

        "security":
        {
            "api_key_required": bool(
                API_KEY
            ),
            "token_auth_enabled": bool(
                os.getenv(
                    "HELIOS_AUTH_SECRET",
                    ""
                ).strip()
            ),
            "rate_limit_per_minute": RATE_LIMIT_PER_MINUTE
        }
    }


@app.get("/ready")

async def readiness():

    checks = {
        "durable_storage": STORAGE_BACKEND in {
            "sqlite",
            "postgres"
        },
        "multi_worker_storage": STORAGE_BACKEND == "postgres",
        "auth_secret": bool(
            AUTH_SECRET
        ),
        "admin_password": bool(
            os.getenv(
                "HELIOS_ADMIN_PASSWORD",
                ""
            ).strip()
        ),
        "cors_restricted": "*" not in parse_csv_env(
            "HELIOS_CORS_ORIGINS",
            "http://localhost:3000"
        ),
        "voice_provider": bool(
            os.getenv(
                "OPENAI_API_KEY",
                ""
            ).strip()
        )
    }
    required_checks = {
        key: value
        for key, value in checks.items()
        if key != "voice_provider"
    }
    ready = all(
        required_checks.values()
    )
    payload = {
        "ready": ready,
        "environment": ENVIRONMENT,
        "checks": checks,
        "optional": {
            "voice_provider": checks["voice_provider"]
        }
    }
    if not ready:
        return JSONResponse(
            status_code=503,
            content=payload
        )
    return payload


@app.post("/auth/login")

async def login(
    request: LoginRequest
):

    user = await run_in_threadpool(
        authenticate_user,
        request.username,
        request.password
    )
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password."
        )
    try:
        token = issue_token(
            user
        )
    except ValueError as error:
        raise HTTPException(
            status_code=503,
            detail=str(
                error
            )
        ) from error
    return {
        "token": token,
        "user": user
    }


@app.get("/auth/users")

async def users():

    return {
        "users": [
            public_user(
                user
            )
            for user in load_users()
        ]
    }


@app.post("/auth/users")

async def add_user(
    request: UserCreateRequest
):

    try:
        user = await run_in_threadpool(
            create_user,
            request.username,
            request.password,
            request.role
        )
    except ValueError as error:
        raise HTTPException(
            status_code=409,
            detail=str(
                error
            )
        ) from error
    return {
        "user": user
    }


@app.get("/missions/events", response_model=MissionEventsResponse)

async def mission_events(
    limit: int = 25
):

    safe_limit = max(
        1,
        min(
            limit,
            100
        )
    )

    return MissionEventsResponse(
        events=load_mission_events()[-safe_limit:],
        missions=latest_missions(),
        stats=mission_stats(),
        agents=agent_activity()
    )


@app.get("/autonomy/runs")

async def autonomous_runs(
    limit: int = 20
):

    safe_limit = max(
        1,
        min(
            limit,
            100
        )
    )

    return {
        "runs": [
            reconcile_run(
                run["id"]
            )
            or run
            for run in load_runs()[
                -safe_limit:
            ]
        ]
    }


@app.post("/autonomy/runs", response_model=AutonomousRunResponse)

async def create_autonomous_run(
    request: AutonomousRunRequest
):

    run = await run_in_threadpool(
        create_run,
        request.objective
    )
    run = await run_in_threadpool(
        queue_run,
        run["id"]
    )

    return AutonomousRunResponse(
        run=run
    )


@app.get("/autonomy/runs/{run_id}", response_model=AutonomousRunResponse)

async def autonomous_run(
    run_id: str
):

    run = await run_in_threadpool(
        reconcile_run,
        run_id
    )

    if not run:
        raise HTTPException(
            status_code=404,
            detail="Autonomous run not found."
        )

    return AutonomousRunResponse(
        run=run
    )


@app.post("/autonomy/runs/{run_id}/cancel", response_model=AutonomousRunResponse)

async def cancel_autonomous_run(
    run_id: str
):

    try:
        run = await run_in_threadpool(
            cancel_run,
            run_id
        )
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(
                error
            )
        ) from error

    return AutonomousRunResponse(
        run=run
    )


@app.post("/autonomy/runs/{run_id}/resume", response_model=AutonomousRunResponse)

async def resume_autonomous_run(
    run_id: str
):

    run = await run_in_threadpool(
        get_run,
        run_id
    )

    if not run:
        raise HTTPException(
            status_code=404,
            detail="Autonomous run not found."
        )

    run = await run_in_threadpool(
        queue_run,
        run_id
    )

    return AutonomousRunResponse(
        run=run
    )


@app.get("/autonomy/jobs")

async def autonomous_jobs(
    limit: int = 50
):

    return {
        "jobs": await run_in_threadpool(
            list_jobs,
            limit
        )
    }


@app.get("/tools")

async def tools_endpoint():

    return {
        "tools": [
            {
                "name": tool_name,
                "status": "available"
            }
            for tool_name in list_tools()
        ],
        "stats": execution_memory.execution_stats()
    }


@app.post("/code/repair")

async def code_repair(
    request: CodeRepairRequest
):

    return await run_in_threadpool(
        run_structured_code_repair,
        request.objective,
        request.edits,
        request.verification_commands,
        request.verification_attempts
    )


@app.post("/code/repair/auto")

async def automatic_code_repair(
    request: GeneralCodeRepairRequest
):

    return await run_in_threadpool(
        run_general_code_repair,
        request.objective,
        request.target_files,
        request.verification_commands,
        request.repair_attempts
    )


@app.get("/git/status")

async def git_status_endpoint():

    return await run_in_threadpool(
        git_status
    )


@app.post("/git/commit", response_model=GitCommitResponse)

async def git_commit_endpoint(
    request: GitCommitRequest
):

    return GitCommitResponse(
        **await run_in_threadpool(
            commit_staged_changes,
            request.message,
            request.confirm
        )
    )


@app.get("/project/brain", response_model=ProjectBrainResponse)

async def project_brain(
    limit: int = 8
):

    safe_limit = max(
        1,
        min(
            limit,
            25
        )
    )

    return ProjectBrainResponse(
        **build_project_brain(
            safe_limit
        )
    )


@app.get("/observability", response_model=ObservabilityResponse)

async def observability(
    limit: int = 100
):

    safe_limit = max(
        1,
        min(
            limit,
            500
        )
    )

    return ObservabilityResponse(
        **build_observability_report(
            safe_limit
        )
    )


@app.get("/metrics")

async def metrics():

    report = build_observability_report()
    rates = report.get(
        "rates",
        {}
    )
    stats = report.get(
        "stats",
        {}
    )
    lines = [
        "# HELP helios_requests_total Total HTTP requests handled.",
        "# TYPE helios_requests_total counter",
        f"helios_requests_total {REQUEST_COUNT}",
        "# HELP helios_tool_events_total Total recorded tool events.",
        "# TYPE helios_tool_events_total gauge",
        f"helios_tool_events_total {stats.get('tool_events', 0)}",
        "# HELP helios_tool_failure_rate Tool failure rate in the active window.",
        "# TYPE helios_tool_failure_rate gauge",
        f"helios_tool_failure_rate {rates.get('failure_rate', 0)}",
    ]
    return Response(
        content="\n".join(
            lines
        )
        + "\n",
        media_type="text/plain; version=0.0.4"
    )


@app.get("/execution/events", response_model=ExecutionEventsResponse)

async def execution_events(
    limit: int = 25,
    status: str | None = None,
    event_type: str | None = None
):

    return ExecutionEventsResponse(
        events=execution_memory.get_execution_events(
            limit=limit,
            status=status,
            event_type=event_type
        ),
        stats=execution_memory.execution_stats()
    )


@app.post("/tools/execute", response_model=ToolExecuteResponse)

async def execute_tool_endpoint(
    request: ToolExecuteRequest
):

    module = request.module.strip().lower()

    if module not in ALLOWED_MODULES:

        raise HTTPException(
            status_code=400,
            detail=f"Unsupported HELIOS module: {module}"
        )

    before_count = len(
        execution_memory.load_execution_memory()
    )

    try:

        if request.agent:

            result = await run_in_threadpool(
                execute_agent_tool,
                request.agent.strip().lower(),
                request.tool,
                *request.args,
                retries=request.retries,
                **request.kwargs
            )

        else:

            result = await run_in_threadpool(
                execute_tool,
                request.tool,
                *request.args,
                actor="HELIOS Dashboard",
                module=module,
                retries=request.retries,
                metadata={
                    "source": "api"
                },
                **request.kwargs
            )

        events = execution_memory.load_execution_memory()[
            before_count:
        ]

        status = "success"

        for event in reversed(
            events
        ):
            if event.get(
                "tool"
            ) == request.tool and event.get(
                "status"
            ) in {
                "success",
                "failed",
                "blocked"
            }:
                status = event.get(
                    "status",
                    status
                )
                break

        return ToolExecuteResponse(
            tool=request.tool,
            status=status,
            result=result,
            events=events,
            stats=execution_memory.execution_stats()
        )

    except Exception as error:

        events = execution_memory.load_execution_memory()[
            before_count:
        ]

        return ToolExecuteResponse(
            tool=request.tool,
            status="failed",
            error=str(
                error
            ),
            events=events,
            stats=execution_memory.execution_stats()
        )


@app.post("/missions", response_model=MissionResponse)

async def create_mission_endpoint(
    request: MissionRequest
):

    request.module = request.module.strip().lower()
    request.agent = request.agent.strip() or "Orion"

    if request.module not in ALLOWED_MODULES:

        raise HTTPException(
            status_code=400,
            detail=f"Unsupported HELIOS module: {request.module}"
        )

    result = await run_in_threadpool(
        create_mission,
        request.title,
        agent=request.agent,
        module=request.module,
        detail=request.detail
    )

    return MissionResponse(
        mission=result["mission"],
        events=result["events"],
        stats=mission_stats(),
        agents=agent_activity()
    )


@app.post("/missions/{mission_id}/advance", response_model=MissionAdvanceResponse)

async def advance_mission_endpoint(
    mission_id: str,
    request: MissionAdvanceRequest
):

    module = (
        request.module.strip().lower()
        if request.module
        else None
    )

    if module and module not in ALLOWED_MODULES:

        raise HTTPException(
            status_code=400,
            detail=f"Unsupported HELIOS module: {module}"
        )

    try:

        result = await run_in_threadpool(
            advance_mission,
            mission_id,
            request.stage,
            agent=request.agent,
            module=module,
            detail=request.detail
        )

    except ValueError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error)
        ) from error

    return MissionAdvanceResponse(
        mission=result["mission"],
        event=result["event"],
        missions=latest_missions(),
        stats=mission_stats(),
        agents=agent_activity()
    )


@app.post("/missions/{mission_id}/run", response_model=MissionRunResponse)

async def run_mission_endpoint(
    mission_id: str
):

    mission = None

    for item in latest_missions(
        limit=100
    ):

        if item.get("id") == mission_id:

            mission = item
            break

    if mission is None:

        raise HTTPException(
            status_code=404,
            detail="Mission not found."
        )

    workflow = await run_in_threadpool(
        run_mission_workflow,
        mission
    )

    result = await run_in_threadpool(
        advance_mission,
        mission_id,
        "Executed",
        detail=workflow["artifact"].get(
            "summary",
            "Mission workflow executed."
        ),
        artifact=workflow["artifact"]
    )

    return MissionRunResponse(
        mission=result["mission"],
        event=result["event"],
        artifact=workflow["artifact"],
        task=workflow["task"],
        missions=latest_missions(),
        stats=mission_stats(),
        agents=agent_activity()
    )


@app.get("/sources")

async def sources():

    return {
        "sources": load_sources(),
        "stats": source_stats()
    }


@app.get("/sources/search", response_model=SourceSearchResponse)

async def source_search(
    q: str = "",
    limit: int = 5,
    scope: str | None = None
):

    safe_limit = max(
        1,
        min(
            limit,
            25
        )
    )

    return SourceSearchResponse(
        sources=search_sources(
            q,
            limit=safe_limit,
            scope=scope
        ),
        stats=source_stats(),
        query=q
    )


@app.get("/sources/intelligence", response_model=SourceIntelligenceResponse)

async def source_intelligence(
    q: str = "",
    limit: int = 8,
    scope: str | None = None
):

    safe_limit = max(
        1,
        min(
            limit,
            25
        )
    )
    sources = search_sources(
        q,
        limit=safe_limit,
        scope=scope
    )
    stats = source_stats()
    grounding = build_grounded_research_artifact(
        q,
        sources,
        stats
    )

    return SourceIntelligenceResponse(
        query=q,
        sources=sources,
        citations=grounding["citations"],
        claims=grounding["claims"],
        grounded_answer=grounding["grounded_answer"],
        coverage=grounding["coverage"],
        stats=stats,
        graph=grounding["graph"]
    )


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

    await run_in_threadpool(
        record_mission_event,
        "Archived",
        f"Indexed source: {source_name}",
        agent="Nova",
        module="knowledge",
        status="archived" if source_content else "pending",
        detail=f"{request.scope} source saved for retrieval."
    )

    return SourceResponse(
        source=source,
        stats=source_stats()
    )


@app.post("/chat", response_model=ChatResponse)

async def chat(
    request: ChatRequest
):

    request.module = request.module.strip().lower()
    request.agent = request.agent.strip() or "HELIOS"
    request.mode = request.mode.strip().lower()

    if request.module not in ALLOWED_MODULES:

        raise HTTPException(
            status_code=400,
            detail=f"Unsupported HELIOS module: {request.module}"
        )

    if request.mode not in CONVERSATION_MODES:

        raise HTTPException(
            status_code=400,
            detail=f"Unsupported conversation mode: {request.mode}"
        )

    if request.module == "research":
        evidence = await run_in_threadpool(
            search_sources,
            request.message,
            8
        )
        grounding = build_grounded_research_artifact(
            request.message,
            evidence,
            source_stats()
        )
        return ChatResponse(
            response=grounding["grounded_answer"],
            module=request.module,
            agent=request.agent,
            mode=request.mode,
            trace=[
                {
                    "stage": "grounding",
                    "actor": "Nova",
                    "payload": grounding["coverage"]
                }
            ],
            plan=[
                {
                    "agent": "research",
                    "objective": "Answer only from indexed evidence."
                }
            ],
            citations=grounding["citations"],
            grounded=grounding["coverage"]["grounded"]
        )

    if (
        request.module == "dashboard"
        and
        not request.attachments
    ):

        await run_in_threadpool(
            record_mission_event,
            "Created",
            request.message,
            agent=request.agent,
            module=request.module,
            status="active",
            detail="Direct dashboard request received."
        )

        response = await run_in_threadpool(
            generate_response,
            request.message
        )

        await run_in_threadpool(
            record_mission_event,
            "Reviewed",
            request.message,
            agent=request.agent,
            module=request.module,
            status="reviewed",
            detail="Fast chat response completed."
        )

        return ChatResponse(
            response=clean_response(response),
            module=request.module,
            agent=request.agent,
            mode=request.mode,
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
        request.mode,
        request.attachments
    )

    await run_in_threadpool(
        record_mission_event,
        "Executed",
        request.message,
        agent=request.agent,
        module=request.module,
        status="executed",
        detail="Cognitive engine completed a module-scoped run."
    )

    status = cognitive_engine.status()

    return ChatResponse(
        response=clean_response(response),
        module=request.module,
        agent=request.agent,
        mode=request.mode,
        trace=status.get("trace", []),
        plan=status.get("plan", [])
    )


@app.get("/voice/status", response_model=VoiceStatusResponse)

async def voice_status():

    key_configured = bool(
        os.getenv(
            "OPENAI_API_KEY",
            ""
        ).strip()
    )

    return VoiceStatusResponse(
        realtime_available=key_configured,
        openai_key_configured=key_configured,
        model=OPENAI_REALTIME_MODEL,
        voice=OPENAI_REALTIME_VOICE,
        max_offer_bytes=MAX_REALTIME_OFFER_BYTES,
        status="ready"
        if key_configured
        else "missing_openai_key"
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

    if len(
        offer_sdp
    ) > MAX_REALTIME_OFFER_BYTES:

        raise HTTPException(
            status_code=413,
            detail="Realtime offer SDP is too large."
        )

    offer_text = offer_sdp.decode(
        "utf-8",
        errors="ignore"
    )

    if "v=0" not in offer_text:

        raise HTTPException(
            status_code=400,
            detail="Invalid WebRTC offer SDP."
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
                        offer_text
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


@app.websocket("/events")

async def event_stream(
    websocket: WebSocket
):

    await websocket.accept()

    last_event_id = None

    try:

        await websocket.send_json(
            {
                "id": str(
                    uuid.uuid4()
                ),
                "label": "Run ledger connected",
                "actor": "HELIOS Backend",
                "module": "system",
                "status": "live",
                "detail": "Realtime event stream is online.",
                "timestamp": time.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            }
        )

        while True:

            latest = shared_bus.latest_message()

            if latest and latest.get("id") != last_event_id:

                last_event_id = latest.get("id")

                await websocket.send_json(
                    {
                        "id": latest.get("id"),
                        "label": "Agent bus event",
                        "actor": latest.get("sender"),
                        "module": latest.get("receiver"),
                        "status": latest.get("status"),
                        "detail": latest.get("content"),
                        "timestamp": latest.get("timestamp")
                    }
                )

            await asyncio.sleep(
                1.5
            )

    except WebSocketDisconnect:

        logger.info(
            "Event stream disconnected."
        )

    except Exception:

        logger.exception(
            "Event stream failure."
        )
