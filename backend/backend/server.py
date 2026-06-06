import logging
import json
import time
import uuid
import asyncio

from contextlib import asynccontextmanager

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
from core import memory as chat_memory
from core.logging_config import (
    configure_logging
)
from core.code_workflow import (
    run_general_code_repair,
    run_structured_code_repair
)
from core.source_library import (
    delete_source,
    load_sources,
    reindex_source,
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
    create_branch,
    git_diff,
    git_status,
    push_branch,
    rollback_commit,
    stage_files
)
from core.audit_log import (
    load_audit_events,
    record_audit_event,
    verify_audit_chain
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
from core.swarm_runs import (
    create_swarm_run,
    get_swarm_run,
    load_swarm_runs,
    reconcile_swarm_run
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
    API_KEY_ROLE,
    APP_VERSION,
    AUTH_COOKIE_SECURE,
    AUTH_SECRET,
    ENVIRONMENT,
    MAX_ATTACHMENT_CHARS,
    MAX_CHAT_MESSAGE_CHARS,
    MEMORY_DIR,
    RATE_LIMIT_PER_MINUTE,
    STORAGE_BACKEND,
    TOKEN_TTL_MINUTES
)
from core.runtime_store import (
    allow_rate_limited_request,
    create_approval_request,
    get_approval_request,
    list_jobs,
    list_approval_requests,
    storage_status
)
from core.runtime_store import (
    update_approval_request
)
from core.plugin_loader import (
    list_plugin_catalog,
    load_plugins,
    plugin_directory,
    save_plugin_code,
    uninstall_plugin
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
    record_mission_event,
    recover_mission
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
from core.voice_transcripts import (
    load_voice_transcripts,
    save_voice_turn
)
from memory.vector_memory import vector_status
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

configure_logging()

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
    "/git": "commit",
    "/tools/execute": "execute",
    "/code/repair": "write",
    "/autonomy/runs": "execute",
    "/swarm/runs": "execute",
    "/missions": "execute",
    "/sources": "write",
    "/auth/users": "admin",
    "/audit": "admin",
    "/approvals": "admin",
    "/plugins": "admin"
}

APPROVAL_REQUIRED_TOOLS = {
    "append_file",
    "create_file",
    "deploy_project",
    "execute_python"
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

CONVERSATION_MODE_CONFIG = {
    "balanced": {
        "label": "Balanced",
        "description": "Useful depth without slowing down routine work.",
        "response_length": "medium",
        "reasoning_depth": "adaptive",
        "tool_posture": "when useful"
    },
    "concise": {
        "label": "Concise",
        "description": "Small, direct answers for quick decisions.",
        "response_length": "short",
        "reasoning_depth": "light",
        "tool_posture": "only when needed"
    },
    "deep": {
        "label": "Deep Analysis",
        "description": "Tradeoffs, risks, evidence, and implementation detail.",
        "response_length": "long",
        "reasoning_depth": "high",
        "tool_posture": "evidence seeking"
    },
    "execute": {
        "label": "Execution",
        "description": "Action-oriented responses with verification and concrete outcomes.",
        "response_length": "task dependent",
        "reasoning_depth": "operational",
        "tool_posture": "proactive"
    }
}

# =========================================
# LOAD PLUGINS
# =========================================

load_plugins()

from core.mission_scheduler import (
    start_mission_scheduler
)

# =========================================
# FASTAPI APP
# =========================================


@asynccontextmanager
async def lifespan(
    application: FastAPI
):
    del application
    scheduler_task = asyncio.create_task(
        start_mission_scheduler()
    )
    try:
        yield
    finally:
        scheduler_task.cancel()
        try:
            await scheduler_task
        except asyncio.CancelledError:
            pass


app = FastAPI(

    title="HELIOS Backend",

    version="2.0.0",

    lifespan=lifespan
)

class ScheduledMissionRequest(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=180
    )
    agent: str = Field(
        default="Orion",
        min_length=1,
        max_length=80
    )
    module: str = Field(
        default="planning",
        min_length=1,
        max_length=80
    )
    scheduled_at: float = Field(
        gt=0
    )
    detail: str = Field(
        default="",
        max_length=360
    )

@app.post("/missions/schedule")
async def schedule_mission_endpoint(request: ScheduledMissionRequest):
    from core.runtime_store import schedule_mission
    module = request.module.strip().lower()
    if module not in ALLOWED_MODULES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported HELIOS module: {module}"
        )
    mission = await run_in_threadpool(
        schedule_mission,
        request.title.strip(),
        request.agent.strip(),
        module,
        request.scheduled_at,
        request.detail
    )
    return {"mission": mission}

@app.get("/missions/scheduled")
async def list_scheduled_missions_endpoint(status: str = "pending"):
    from core.runtime_store import list_scheduled_missions
    missions = await run_in_threadpool(
        list_scheduled_missions,
        status
    )
    return {"missions": missions}

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
    require_grounding: bool = False


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
    enforcement: dict = Field(
        default_factory=dict
    )


class SourceRequest(BaseModel):

    name: str = Field(
        min_length=1,
        max_length=180
    )
    type: str = "FILE"
    size: str = "unknown"
    content: str = Field(
        default="",
        max_length=MAX_ATTACHMENT_CHARS * 512
    )
    scope: str = "project"


class SourceResponse(BaseModel):

    source: dict
    stats: dict


class AISettingsRequest(BaseModel):

    provider: str = "ollama"
    model: str = ""


class AISettingsResponse(BaseModel):

    provider: str
    model: str
    saved: bool


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
    enforcement: dict = Field(
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
    confirm: bool = False
    approval_id: str | None = None


class ApprovalDecisionRequest(BaseModel):
    status: str = Field(
        pattern="^(approved|denied)$"
    )


class ToolExecuteResponse(BaseModel):

    tool: str
    status: str
    result: object | None = None
    error: str | None = None
    events: list[dict]
    stats: dict
    trace_id: str | None = None
    approval: dict = Field(
        default_factory=dict
    )
    retry_policy: dict = Field(
        default_factory=dict
    )


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
    latency_percentiles: dict = Field(
        default_factory=dict
    )
    traces: list[dict] = Field(
        default_factory=list
    )
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


class GitStageRequest(BaseModel):

    paths: list[str] = Field(
        default_factory=list
    )
    confirm: bool = False


class GitBranchRequest(BaseModel):

    name: str = Field(
        min_length=1,
        max_length=120
    )
    confirm: bool = False


class GitPushRequest(BaseModel):

    branch: str = Field(
        min_length=1,
        max_length=120
    )
    remote: str = Field(
        default="origin",
        min_length=1,
        max_length=80
    )
    confirm: bool = False


class GitRollbackRequest(BaseModel):

    commit: str = Field(
        min_length=7,
        max_length=40
    )
    confirm: bool = False


class VoiceStatusResponse(BaseModel):

    realtime_available: bool
    openai_key_configured: bool
    model: str
    voice: str
    max_offer_bytes: int
    status: str


class VoiceTurnRequest(BaseModel):

    role: str = Field(
        min_length=1,
        max_length=40
    )
    text: str = Field(
        min_length=1,
        max_length=MAX_CHAT_MESSAGE_CHARS
    )
    session_id: str = Field(
        default="",
        max_length=120
    )


class VoiceFallbackRequest(BaseModel):

    text: str = Field(
        min_length=1,
        max_length=MAX_CHAT_MESSAGE_CHARS
    )
    mode: str = Field(
        default="concise",
        max_length=40
    )
    session_id: str = Field(
        default="frontend-fallback",
        max_length=120
    )


class AutonomousRunRequest(BaseModel):

    objective: str = Field(
        min_length=1,
        max_length=MAX_CHAT_MESSAGE_CHARS
    )
    max_rounds: int = Field(
        default=3,
        ge=1,
        le=6
    )


class AutonomousRunResponse(BaseModel):

    run: dict


class SwarmRunRequest(BaseModel):

    objective: str = Field(
        min_length=1,
        max_length=MAX_CHAT_MESSAGE_CHARS
    )
    conversation_context: str = Field(
        default="",
        max_length=MAX_ATTACHMENT_CHARS
    )


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

    password: str = Field(
        min_length=8,
        max_length=240
    )
    role: str = "viewer"


class PluginUploadRequest(BaseModel):

    name: str = Field(
        min_length=1,
        max_length=80
    )
    code: str = Field(
        min_length=1,
        max_length=250000
    )
    version: str = Field(
        default="1.0.0",
        max_length=40
    )
    description: str = Field(
        default="",
        max_length=500
    )
    dependencies: list[str] = Field(
        default_factory=list
    )


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
    if request.method == "OPTIONS":
        return await call_next(
            request
        )
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
    if not token:
        token = request.cookies.get(
            "helios_session",
            ""
        )
    user = verify_token(
        token
    ) if token else None
    api_key_authenticated = bool(
        API_KEY
        and request.headers.get(
            "x-helios-api-key",
            ""
        )
        == API_KEY
    )
    if user is None and api_key_authenticated:
        user = {
            "sub": "api-key",
            "username": "api-key",
            "role": API_KEY_ROLE,
            "active": True
        }
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
            not api_key_authenticated
        )
        and user is None
    ):

        await run_in_threadpool(
            record_audit_event,
            "authentication_denied",
            actor=client_host,
            resource=request.url.path,
            status="401",
            detail="Missing or invalid HELIOS credentials.",
            metadata={
                "request_id": request_id
            }
        )
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
    if request.url.path.startswith(
        "/audit"
    ):
        required_permission = "admin"
    if request.url.path.startswith(
        "/plugins"
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
        await run_in_threadpool(
            record_audit_event,
            "permission_denied",
            actor=user.get(
                "username",
                "token-user"
            ),
            resource=request.url.path,
            status="403",
            detail=f"Role does not allow '{required_permission}'.",
            metadata={
                "request_id": request_id,
                "required_permission": required_permission
            }
        )
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

        await run_in_threadpool(
            record_audit_event,
            "rate_limit_denied",
            actor=client_host,
            resource=request.url.path,
            status="429",
            detail="HELIOS rate limit exceeded.",
            metadata={
                "request_id": request_id
            }
        )
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
    response.headers["permissions-policy"] = "camera=(), geolocation=(), microphone=(self)"
    response.headers["content-security-policy"] = "default-src 'none'; frame-ancestors 'none'"
    response.headers["x-helios-storage"] = STORAGE_BACKEND

    if request.method not in {
        "GET",
        "HEAD",
        "OPTIONS"
    }:
        await run_in_threadpool(
            record_audit_event,
            f"{request.method} {request.url.path}",
            actor=(
                user.get(
                    "username",
                    "token-user"
                )
                if user
                else "api-key"
                if api_key_authenticated
                else client_host
            ),
            resource=request.url.path,
            status=str(
                response.status_code
            ),
            metadata={
                "request_id": request_id,
                "client": client_host,
                "duration_ms": duration_ms
            }
        )

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

    user_message,
    mode="balanced"

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
CONVERSATION MODE
========================================

{mode}

{CONVERSATION_MODES.get(mode, CONVERSATION_MODES["balanced"])}

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


AI_SETTINGS_FILE = MEMORY_DIR / "settings.json"


def load_ai_settings() -> dict:

    try:
        if AI_SETTINGS_FILE.exists():
            return json.loads(AI_SETTINGS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}

    return {}


def save_ai_settings(provider: str, model: str = "") -> dict:

    payload = {
        "provider": str(provider or "ollama").strip().lower() or "ollama",
        "model": str(model or "").strip()
    }
    AI_SETTINGS_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def get_ai_status():

    provider_preference = load_ai_settings().get("provider", "")

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
        for item in [provider_preference, *[
            item.strip().lower()
            for item in os.getenv(
                "HELIOS_AI_PROVIDER",
                "ollama,gemini"
            ).split(",")
            if item.strip()
        ]]
        if item.strip()
    ]
    provider_order = list(dict.fromkeys(provider_order))

    available_provider = next(
        (
            provider
            for provider in provider_order
            if providers.get(provider, {}).get("model_available")
        ),
        None
    )
    preferred_provider = provider_preference or available_provider or provider_order[0]
    selected_provider = available_provider or preferred_provider

    if selected_provider and providers.get(selected_provider):
        selected = providers[selected_provider]
        preferred_model = load_ai_settings().get("model", "") or selected.get("model") or MODEL_NAME

        return {
            "status": "active" if selected.get("model_available") else "degraded",
            "provider": selected_provider,
            "model": preferred_model,
            "model_available": bool(selected.get("model_available")),
            "available_models": list(selected.get("available_models", []) or []),
            "providers": providers
        }

    return {
        "status": "offline",
        "provider": preferred_provider,
        "model": load_ai_settings().get("model", "") or MODEL_NAME,
        "model_available": False,
        "available_models": [],
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

@app.get("/settings/ai", response_model=AISettingsResponse)

async def get_ai_settings():

    settings = load_ai_settings()

    return AISettingsResponse(
        provider=str(settings.get("provider", "ollama") or "ollama").strip().lower(),
        model=str(settings.get("model", "") or "").strip(),
        saved=True
    )


@app.post("/settings/ai", response_model=AISettingsResponse)

async def update_ai_settings(request: AISettingsRequest):

    settings = save_ai_settings(request.provider, request.model)

    return AISettingsResponse(
        provider=settings["provider"],
        model=settings["model"],
        saved=True
    )


@app.get("/memory")

async def list_memory():

    items = chat_memory.load_memory()

    return {
        "items": items,
        "total": len(items)
    }


@app.delete("/memory/{index:int}")

async def delete_memory(index: int):

    items = chat_memory.load_memory()

    if index < 0 or index >= len(items):
        raise HTTPException(status_code=404, detail="Memory item not found")

    deleted_item = dict(items[index])
    updated_items = chat_memory.delete_memory_item(items, index)

    return {
        "deleted": True,
        "item": deleted_item,
        "total": len(updated_items)
    }


@app.get("/memory/export")

async def export_memory():

    items = chat_memory.load_memory()

    return JSONResponse(
        content=items,
        media_type="application/json",
        headers={
            "Content-Disposition": "attachment; filename=helios-memory.json"
        }
    )


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

        "vector":
        vector_status(),

        "security":
        {
            "api_key_required": bool(
                API_KEY
            ),
            "api_key_role": API_KEY_ROLE
            if API_KEY
            else None,
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
        "auth_secret_distinct_from_api_key": bool(
            AUTH_SECRET
        )
        and (
            not API_KEY
            or AUTH_SECRET != API_KEY
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
        "plugin_signing_key": bool(
            os.getenv(
                "HELIOS_PLUGIN_SIGNING_KEY",
                ""
            ).strip()
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
        if key not in {
            "voice_provider"
        }
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
    request: LoginRequest,
    response: Response
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
    response.set_cookie(
        "helios_session",
        token,
        httponly=True,
        secure=AUTH_COOKIE_SECURE,
        samesite="strict",
        max_age=TOKEN_TTL_MINUTES * 60,
        path="/"
    )
    return {
        "token": token,
        "user": user
    }


@app.post("/auth/logout")

async def logout_user(
    response: Response
):

    response.delete_cookie(
        "helios_session",
        path="/",
        secure=AUTH_COOKIE_SECURE,
        httponly=True,
        samesite="strict"
    )
    return {
        "status": "signed_out"
    }


@app.get("/auth/me")

async def current_user(
    request: Request
):

    user = getattr(
        request.state,
        "helios_user",
        None
    )
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required."
        )
    return {
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


@app.get("/plugins")
async def list_plugins_endpoint():
    return {
        "plugins": await run_in_threadpool(
            list_plugin_catalog
        ),
        "tools_count": len(list_tools())
    }

@app.post("/plugins/upload")
async def upload_plugin(request: PluginUploadRequest):
    try:
        file_path = await run_in_threadpool(
            save_plugin_code,
            request.name,
            request.code,
            version=request.version,
            description=request.description,
            dependencies=request.dependencies
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(
                error
            )
        ) from error
    loaded = await run_in_threadpool(
        load_plugins
    )
    return {
        "status": "success",
        "message": f"Plugin {file_path.name} uploaded and loaded.",
        "loaded_plugins": loaded
    }


@app.delete("/plugins/{name}")
async def delete_plugin(
    name: str
):
    try:
        filename = await run_in_threadpool(
            uninstall_plugin,
            name
        )
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(
                error
            )
        ) from error
    return {
        "status": "success",
        "message": f"Plugin {filename} uninstalled."
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
        request.objective,
        request.max_rounds
    )
    run = await run_in_threadpool(
        queue_run,
        run["id"]
    )

    return AutonomousRunResponse(
        run=run
    )


@app.get("/swarm/runs")

async def swarm_runs(
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
            await run_in_threadpool(
                reconcile_swarm_run,
                run[
                    "id"
                ]
            )
            for run in load_swarm_runs()[
                -safe_limit:
            ]
        ]
    }


@app.post("/swarm/runs")

async def create_isolated_swarm_run(
    request: SwarmRunRequest
):

    run = await run_in_threadpool(
        create_swarm_run,
        request.objective,
        "",
        "",
        request.conversation_context
    )
    return {
        "run": run
    }


@app.get("/swarm/runs/{run_id}")

async def isolated_swarm_run(
    run_id: str
):

    try:
        run = await run_in_threadpool(
            reconcile_swarm_run,
            run_id
        )
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(
                error
            )
        ) from error
    return {
        "run": run
    }


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


@app.get("/git/diff")

async def git_diff_endpoint(
    staged: bool = False,
    path: str | None = None
):

    return await run_in_threadpool(
        git_diff,
        staged,
        path
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


@app.post("/git/stage")

async def git_stage_endpoint(
    request: GitStageRequest
):

    return await run_in_threadpool(
        stage_files,
        request.paths,
        request.confirm
    )


@app.post("/git/branch")

async def git_branch_endpoint(
    request: GitBranchRequest
):

    return await run_in_threadpool(
        create_branch,
        request.name,
        request.confirm
    )


@app.post("/git/push")

async def git_push_endpoint(
    request: GitPushRequest
):

    return await run_in_threadpool(
        push_branch,
        request.branch,
        request.remote,
        request.confirm
    )


@app.post("/git/rollback")

async def git_rollback_endpoint(
    request: GitRollbackRequest
):

    return await run_in_threadpool(
        rollback_commit,
        request.commit,
        request.confirm
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


@app.get("/audit")

async def audit_events(
    limit: int = 100
):

    return {
        "events": await run_in_threadpool(
            load_audit_events,
            limit
        ),
        "chain": await run_in_threadpool(
            verify_audit_chain
        )
    }


@app.get("/approvals")
async def approval_requests(
    status: str | None = None,
    limit: int = 50
):

    return {
        "approvals": await run_in_threadpool(
            list_approval_requests,
            status,
            limit
        )
    }


@app.post("/approvals/{approval_id}")
async def decide_approval(
    approval_id: str,
    request: ApprovalDecisionRequest,
    http_request: Request
):

    user = getattr(
        http_request.state,
        "helios_user",
        None
    ) or {}
    actor = user.get(
        "username",
        "api-key"
    )
    approval = await run_in_threadpool(
        update_approval_request,
        approval_id,
        request.status,
        approved_by=actor
    )
    if not approval:
        raise HTTPException(
            status_code=404,
            detail="Approval request not found."
        )
    await run_in_threadpool(
        record_audit_event,
        f"approval_{request.status}",
        actor=actor,
        resource=approval.get(
            "tool",
            ""
        ),
        status=request.status,
        detail=approval.get(
            "reason",
            ""
        ),
        metadata={
            "approval_id": approval_id
        }
    )
    return {
        "approval": approval
    }


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
    request: ToolExecuteRequest,
    http_request: Request
):

    module = request.module.strip().lower()

    if module not in ALLOWED_MODULES:

        raise HTTPException(
            status_code=400,
            detail=f"Unsupported HELIOS module: {module}"
        )

    user = getattr(
        http_request.state,
        "helios_user",
        None
    )
    actor = (
        user.get(
            "username",
            "token-user"
        )
        if user
        else "HELIOS Dashboard"
    )
    if (
        request.tool == "deploy_project"
        and not (
            (
                API_KEY
                and http_request.headers.get(
                    "x-helios-api-key",
                    ""
                )
                == API_KEY
            )
            or (
                user is not None
                and has_permission(
                    user,
                    "admin"
                )
            )
        )
    ):
        raise HTTPException(
            status_code=403,
            detail="Deployments require an admin account or HELIOS API key."
        )

    if (
        request.tool in APPROVAL_REQUIRED_TOOLS
    ):
        approval_payload = {
            "tool": request.tool,
            "args": request.args,
            "kwargs": request.kwargs,
            "agent": request.agent,
            "module": module,
            "retries": request.retries
        }
        if not request.approval_id:
            approval = await run_in_threadpool(
                create_approval_request,
                request.tool,
                approval_payload,
                actor=actor,
                module=module,
                reason="This tool can modify project state and requires explicit approval."
            )
            await run_in_threadpool(
                record_audit_event,
                "approval_requested",
                actor=actor,
                resource=request.tool,
                status="pending",
                detail="State-changing tool execution is waiting for approval.",
                metadata={
                    "approval_id": approval.get(
                        "id"
                    )
                }
            )
            return ToolExecuteResponse(
                tool=request.tool,
                status="approval_required",
                result={
                    "reason": "This tool can modify project state and requires explicit approval.",
                    "approval_id": approval.get(
                        "id"
                    ),
                    "approval": approval
                },
                events=[],
                stats=execution_memory.execution_stats(),
                trace_id=approval.get(
                    "id"
                ),
                approval={
                    "required": True,
                    "approval_id": approval.get(
                        "id"
                    ),
                    "status": approval.get(
                        "status"
                    ),
                    "reason": "This tool can modify project state and requires explicit approval.",
                    "confirm_field": "approval_id"
                },
                retry_policy={
                    "requested_retries": request.retries,
                    "max_retries": 2,
                    "retryable_statuses": [
                        "failed",
                        "blocked"
                    ]
                }
            )
        approval = await run_in_threadpool(
            get_approval_request,
            request.approval_id
        )
        if not approval:
            raise HTTPException(
                status_code=404,
                detail="Approval request not found."
            )
        if approval.get(
            "tool"
        ) != request.tool or approval.get(
            "status"
        ) != "approved":
            return ToolExecuteResponse(
                tool=request.tool,
                status="approval_required",
                result={
                    "reason": "The referenced approval is not approved for this tool.",
                    "approval": approval
                },
                events=[],
                stats=execution_memory.execution_stats(),
                trace_id=request.approval_id,
                approval={
                    "required": True,
                    "approval_id": request.approval_id,
                    "status": approval.get(
                        "status"
                    )
                },
                retry_policy={
                    "requested_retries": request.retries,
                    "max_retries": 2,
                    "retryable_statuses": [
                        "failed",
                        "blocked"
                    ]
                }
            )

    before_count = len(
        execution_memory.load_execution_memory()
    )
    trace_id = str(
        uuid.uuid4()
    )

    try:

        if request.agent:

            result = await run_in_threadpool(
                execute_agent_tool,
                request.agent.strip().lower(),
                request.tool,
                *request.args,
                retries=request.retries,
                metadata={
                    "source": "api",
                    "trace_id": trace_id,
                    "approval_id": request.approval_id
                },
                **request.kwargs
            )

        else:

            result = await run_in_threadpool(
                execute_tool,
                request.tool,
                *request.args,
                actor=actor,
                module=module,
                retries=request.retries,
                metadata={
                    "source": "api",
                    "trace_id": trace_id,
                    "approval_id": request.approval_id
                },
                **request.kwargs
            )
        if request.approval_id:
            await run_in_threadpool(
                update_approval_request,
                request.approval_id,
                "used",
                approved_by=actor
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
            stats=execution_memory.execution_stats(),
            trace_id=trace_id,
            approval={
                "required": request.tool in APPROVAL_REQUIRED_TOOLS,
                "granted": bool(
                    request.approval_id
                ),
                "approval_id": request.approval_id
            },
            retry_policy={
                "requested_retries": request.retries,
                "max_retries": 2,
                "retryable_statuses": [
                    "failed",
                    "blocked"
                ]
            }
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
            stats=execution_memory.execution_stats(),
            trace_id=trace_id,
            approval={
                "required": request.tool in APPROVAL_REQUIRED_TOOLS,
                "granted": bool(
                    request.approval_id
                ),
                "approval_id": request.approval_id
            },
            retry_policy={
                "requested_retries": request.retries,
                "max_retries": 2,
                "retryable_statuses": [
                    "failed",
                    "blocked"
                ]
            }
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


@app.post("/missions/{mission_id}/recover")

async def recover_mission_endpoint(
    mission_id: str
):

    try:
        result = await run_in_threadpool(
            recover_mission,
            mission_id
        )
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(
                error
            )
        ) from error
    return {
        **result,
        "missions": latest_missions(),
        "stats": mission_stats(),
        "agents": agent_activity()
    }


@app.get("/missions/{mission_id}/export")

async def export_mission(
    mission_id: str
):

    events = [
        event
        for event in load_mission_events()
        if event.get(
            "mission_id"
        )
        == mission_id
    ]
    if not events:
        raise HTTPException(
            status_code=404,
            detail="Mission not found."
        )
    return {
        "mission": next(
            (
                mission
                for mission in latest_missions(
                    limit=100
                )
                if mission.get(
                    "id"
                )
                == mission_id
            ),
            None
        ),
        "events": events,
        "exported_at": time.strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    }


@app.get("/exports/{kind}")

async def export_project_data(
    kind: str
):

    export_kind = kind.strip().lower()
    exporters = {
        "memory": lambda: {
            "conversations": chat_memory.load_memory()
        },
        "sources": lambda: {
            "sources": load_sources(),
            "stats": source_stats()
        },
        "project-brain": lambda: build_project_brain(
            25
        ),
        "report": lambda: {
            "health": {
                "storage": storage_status(),
                "sources": source_stats(),
                "missions": mission_stats(),
                "execution": execution_memory.execution_stats()
            },
            "observability": build_observability_report(
                500
            ),
            "project_brain": build_project_brain(
                25
            )
        },
        "transcripts": lambda: {
            "turns": load_voice_transcripts(100)
        },
        "missions": lambda: {
            "missions": latest_missions(limit=100)
        }
    }
    if export_kind not in exporters:
        raise HTTPException(
            status_code=404,
            detail="Supported exports: memory, sources, project-brain, report, transcripts, missions."
        )
    return {
        "kind": export_kind,
        "exported_at": time.strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "data": await run_in_threadpool(
            exporters[
                export_kind
            ]
        )
    }


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
        graph=grounding["graph"],
        enforcement=grounding["enforcement"]
    )


@app.post("/sources/{source_id}/reindex")

async def reindex_existing_source(source_id: str):

    try:
        result = await run_in_threadpool(
            reindex_source,
            source_id
        )
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        ) from error

    await run_in_threadpool(
        record_mission_event,
        "Executed",
        f"Reindexed source: {result['name']}",
        agent="Nova",
        module="knowledge",
        status="executed",
        detail="Source content was refreshed in the indexed library."
    )

    return {
        "source": {
            key: value
            for key, value in result.items()
            if key != "stats" and key != "reindexed"
        },
        "stats": result.get("stats", source_stats())
    }


@app.delete("/sources/{source_id}")

async def remove_source(source_id: str):

    try:
        result = await run_in_threadpool(
            delete_source,
            source_id
        )
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        ) from error

    await run_in_threadpool(
        record_mission_event,
        "Archived",
        f"Removed source: {result['name']}",
        agent="Nova",
        module="knowledge",
        status="archived",
        detail="Source record deleted from the indexed library."
    )

    return {
        "deleted": True,
        "source": {
            key: value
            for key, value in result.items()
            if key != "stats" and key != "deleted"
        },
        "stats": result.get("stats", source_stats())
    }


@app.post("/sources", response_model=SourceResponse)

async def save_source(
    request: SourceRequest
):

    source_name = request.name.strip()
    source_type = request.type.strip().upper()
    source_content = (
        request.content
        if source_type in {
            "PDF",
            "DOCX"
        }
        else request.content[:MAX_SOURCE_CONTENT_CHARS]
    )

    if not source_name:

        raise HTTPException(
            status_code=400,
            detail="Source name is required."
        )

    try:
        source = await run_in_threadpool(
            upsert_source,
            source_name,
            source_type,
            request.size,
            source_content,
            request.scope
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(
                error
            )
        ) from error

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

    if request.module == "research":
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
            grounded=grounding["coverage"]["enforced"],
            enforcement=grounding["enforcement"]
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

        if request.require_grounding and not grounding["coverage"]["enforced"]:
            response = grounding["grounded_answer"]
        elif grounding["coverage"]["enforced"]:
            response = grounding["grounded_answer"]
        else:
            response = await run_in_threadpool(
                generate_response,
                request.message,
                request.mode
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
            ],
            citations=grounding["citations"],
            grounded=grounding["coverage"]["enforced"],
            enforcement=grounding["enforcement"]
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

    grounded = grounding["coverage"]["enforced"]
    return ChatResponse(
        response=clean_response(
            grounding["grounded_answer"]
            if grounded or request.require_grounding
            else response
        ),
        module=request.module,
        agent=request.agent,
        mode=request.mode,
        trace=status.get("trace", []),
        plan=status.get("plan", []),
        citations=grounding["citations"],
        grounded=grounded,
        enforcement=grounding["enforcement"]
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


@app.get("/conversation/modes")

async def conversation_modes():

    return {
        "default": "balanced",
        "modes": [
            {
                "id": mode,
                "directive": directive,
                **CONVERSATION_MODE_CONFIG[
                    mode
                ]
            }
            for mode, directive in CONVERSATION_MODES.items()
        ]
    }


@app.get("/voice/transcripts")

async def voice_transcripts(
    limit: int = 100
):

    return {
        "turns": await run_in_threadpool(
            load_voice_transcripts,
            limit
        )
    }


@app.post("/voice/transcripts")

async def persist_voice_transcript(
    request: VoiceTurnRequest
):

    return {
        "turn": await run_in_threadpool(
            save_voice_turn,
            request.role,
            request.text,
            request.session_id
        )
    }


@app.post("/voice/fallback")

async def voice_fallback(
    request: VoiceFallbackRequest
):

    mode = request.mode.strip().lower()
    if mode not in CONVERSATION_MODES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported conversation mode: {mode}"
        )
    await run_in_threadpool(
        save_voice_turn,
        "you",
        request.text,
        request.session_id
    )
    response = await run_in_threadpool(
        generate_response,
        request.text,
        mode
    )
    turn = await run_in_threadpool(
        save_voice_turn,
        "helios",
        response,
        request.session_id
    )
    return {
        "response": response,
        "turn": turn,
        "mode": mode,
        "playback": "browser_speech_synthesis",
        "provider_independent": True
    }


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

            raw_message = await (
                websocket.receive_text()
            )
            try:
                stream_payload = json.loads(
                    raw_message
                )
            except json.JSONDecodeError:
                stream_payload = {
                    "message": raw_message,
                    "stream": False
                }
            user_message = str(
                stream_payload.get(
                    "message",
                    raw_message
                )
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
                user_message,
                str(
                    stream_payload.get(
                        "module",
                        "dashboard"
                    )
                ),
                str(
                    stream_payload.get(
                        "agent",
                        "HELIOS"
                    )
                ),
                str(
                    stream_payload.get(
                        "mode",
                        "balanced"
                    )
                ),
                stream_payload.get(
                    "attachments",
                    []
                )
            )
            status = cognitive_engine.status()

            # =================================
            # SEND RESPONSE
            # =================================

            if stream_payload.get(
                "stream",
                False
            ):
                message_id = str(
                    uuid.uuid4()
                )
                await websocket.send_json(
                    {
                        "type": "chat.start",
                        "id": message_id,
                        "module": stream_payload.get(
                            "module",
                            "dashboard"
                        )
                    }
                )
                chunks = str(
                    ai_response
                ).split(
                    " "
                )
                for index, chunk in enumerate(
                    chunks
                ):
                    await websocket.send_json(
                        {
                            "type": "chat.delta",
                            "id": message_id,
                            "delta": chunk
                            + (
                                " "
                                if index < len(
                                    chunks
                                )
                                - 1
                                else ""
                            )
                        }
                    )
                    await asyncio.sleep(
                        0
                    )
                await websocket.send_json(
                    {
                        "type": "chat.done",
                        "id": message_id,
                        "response": ai_response,
                        "trace": status.get("trace", []),
                        "plan": status.get("plan", [])
                    }
                )
                continue

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
