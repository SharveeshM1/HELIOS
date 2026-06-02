# =========================================================
# HELIOS AI — MAIN.PY
# Production Hardened Version
# =========================================================

import os
import logging
import traceback
import threading
import textwrap
import re
import sys
import types
import inspect
import time


from dotenv import load_dotenv # type: ignore

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

TEMP_AUDIO_DIR = os.path.join(
    BASE_DIR,
    "temp_audio"
)

TEMP_AUDIO_FILE = os.path.join(
    TEMP_AUDIO_DIR,
    "current.webm"
)

try:
    from streamlit_mic_recorder import mic_recorder # type: ignore
except ModuleNotFoundError:
    mic_recorder = None

# =========================================================
# LOAD ENV
# =========================================================

load_dotenv(
    os.path.join(
        BASE_DIR,
        ".env"
    )
)

# =========================================================
# LOGGER
# =========================================================

logging.basicConfig(
    level=logging.WARNING,
    format=(
        "[HELIOS] %(levelname)s | "
        "%(message)s"
    )
)

logger = logging.getLogger(
    "helios"
)


class _HeadlessPlaceholder:
    def markdown(self, *args, **kwargs):
        return None

    def empty(self):
        return None


class _HeadlessContext:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def empty(self):
        return _HeadlessPlaceholder()


def _noop(*args, **kwargs):
    return None


def _ensure_streamlit_compat(st_module):

    if not hasattr(st_module, "session_state"):
        st_module.session_state = {}

    if not hasattr(st_module, "sidebar"):
        st_module.sidebar = _HeadlessContext()

    if not hasattr(st_module, "set_page_config"):
        st_module.set_page_config = _noop

    if not hasattr(st_module, "markdown"):
        st_module.markdown = _noop

    if not hasattr(st_module, "title"):
        st_module.title = _noop

    if not hasattr(st_module, "warning"):
        st_module.warning = lambda msg="", *args, **kwargs: logger.warning(msg)

    if not hasattr(st_module, "success"):
        st_module.success = lambda msg="", *args, **kwargs: logger.info(msg)

    if not hasattr(st_module, "error"):
        st_module.error = lambda msg="", *args, **kwargs: logger.error(msg)

    if not hasattr(st_module, "button"):
        st_module.button = lambda *args, **kwargs: False

    if not hasattr(st_module, "chat_input"):
        st_module.chat_input = lambda prompt="", *args, **kwargs: None
        st_module._helios_chat_input_accepts_files = True
    else:
        try:
            chat_input_params = inspect.signature(
                st_module.chat_input
            ).parameters

            st_module._helios_chat_input_accepts_files = (
                "accept_file" in chat_input_params
            )

        except Exception:
            st_module._helios_chat_input_accepts_files = False

    if not hasattr(st_module, "chat_message"):
        st_module.chat_message = lambda *args, **kwargs: _HeadlessContext()

    if not hasattr(st_module, "file_uploader"):
        st_module.file_uploader = lambda *args, **kwargs: None

    if not hasattr(st_module, "empty"):
        st_module.empty = lambda *args, **kwargs: _HeadlessPlaceholder()

    if not hasattr(st_module, "columns"):
        st_module.columns = lambda count, *args, **kwargs: [
            _HeadlessContext()
            for _ in range(count if isinstance(count, int) else len(count))
        ]

    for chart_name in (
        "line_chart",
        "area_chart",
        "bar_chart",
        "audio"
    ):
        if not hasattr(st_module, chart_name):
            setattr(
                st_module,
                chart_name,
                _noop
            )

    if not hasattr(st_module, "components"):
        st_module.components = types.SimpleNamespace(
            v1=types.SimpleNamespace(
                iframe=_noop
            )
        )

    return st_module


try:
    import streamlit as st  # type: ignore
except Exception:
    try:
        import streamlit_stub as st  # type: ignore
    except Exception:
        st = types.ModuleType(
            "streamlit"
        )

    st = _ensure_streamlit_compat(
        st
    )

    sys.modules["streamlit"] = st

    if hasattr(st, "components"):
        sys.modules.setdefault(
            "streamlit.components",
            st.components
        )

        if hasattr(st.components, "v1"):
            sys.modules.setdefault(
                "streamlit.components.v1",
                st.components.v1
            )

else:
    st = _ensure_streamlit_compat(
        st
    )

# =========================================================
# APP IMPORTS
# =========================================================

from api.web_search import (
    search_web
)

from api.ai_provider import (
    generate_response
)

from api.voice_api import (
    transcribe_audio
)

from agents.router_agent import (
    detect_best_agent
)

from agents.memory_intelligence_agent import (
    summarize_project
)

from components.hero import (
    render_hero
)

from components.quick_access import (
    render_quick_access
)

from components.analytics import (
    render_analytics
)

from components.mission_control import (
    render_mission_control
)

from components.platform_chrome import (
    render_platform_chrome
)

from components.sidebar import (
    render_sidebar,
    render_nav_toggle
)

from components.console import (
    render_console
)

from components.realtime_voice import (
    render_realtime_voice
)

from components.chat_renderer import (
    render_user_message,
    render_assistant_message,
    render_ai_response
)

from components.chat_ui import (
    render_chat_history
)

from components.upload_manager import (
    render_upload_manager
)

from components.source_intelligence import (
    render_source_intelligence_panel
)

from components.thinking import (
    render_thinking,
    render_processing_state
)

from components.ui import (
    render_feature_grid,
    render_command_shell,
    render_command_reactor,
    render_command_palette,
    render_mission_stack,
    render_status_strip,
    render_execution_lanes,
    render_agent_matrix,
    render_voice_cockpit,
    render_system_notice,
    render_agent_status,
    render_system_snapshot
)

from core.styles import (
    APP_CSS
)

from core.shared_bus import (
    shared_bus
)

from core.memory import (
    load_memory,
    add_to_memory
)

from core.project_memory import (
    add_project_memory
)

from core.source_library import (
    upsert_source
)

from core.task_engine import (
    create_task,
    execute_task
)

from core.cognitive_engine import (
    CognitiveEngine
)

from utils.audio_utils import (
    cleanup_audio_files
)

from utils.file_utils import (
    read_uploaded_file
)

st = _ensure_streamlit_compat(
    st
)

try:
    from streamlit.delta_generator import DeltaGenerator  # type: ignore

except Exception:
    DeltaGenerator = None


def _normalize_markdown_html(body):

    if not isinstance(body, str):
        return body

    body = textwrap.dedent(body).lstrip("\n")

    def _compact_style(match):

        style_value = match.group(1)

        style_value = re.sub(r"\s+", " ", style_value).strip()

        return f'style="{style_value}"'

    body = re.sub(
        r'style="([\s\S]*?)"',
        _compact_style,
        body,
        flags=re.IGNORECASE
    )

    if body.lstrip().startswith(("<", "<!--")):

        body = re.sub(
            r"\s+",
            " ",
            body
        )

        body = re.sub(
            r">\s+<",
            "><",
            body
        )

    return body


if not hasattr(st, "_helios_original_markdown"):

    st._helios_original_markdown = st.markdown


def _markdown_with_dedent(body, *args, **kwargs):

    return st._helios_original_markdown(
        _normalize_markdown_html(body),
        *args,
        **kwargs
    )


st.markdown = _markdown_with_dedent

if DeltaGenerator is not None:

    if not hasattr(DeltaGenerator, "_helios_original_markdown"):

        DeltaGenerator._helios_original_markdown = (
            DeltaGenerator.markdown
        )


    def _delta_markdown_with_dedent(self, body, *args, **kwargs):

        return DeltaGenerator._helios_original_markdown(
            self,
            _normalize_markdown_html(body),
            *args,
            **kwargs
        )


    DeltaGenerator.markdown = _delta_markdown_with_dedent

# =========================================================
# CONSTANTS
# =========================================================

MAX_CHAT_RENDER = 18
MAX_RESPONSE_CHARS = 45000
MAX_CONTEXT_CHARS = 12000
SESSION_SCHEMA_VERSION = "ollama_streamlit_v1"

cognitive_engine = CognitiveEngine()

# =========================================================
# APP CONFIG
# =========================================================

st.set_page_config(
    page_title="HELIOS AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CSS
# =========================================================

# Streamlit reruns the script while preserving session_state. Keeping a
# "css_loaded" flag makes style edits look stale until the session is reset.
st.markdown(
    APP_CSS,
    unsafe_allow_html=True
)

# =========================================================
# DIRECTORIES
# =========================================================

os.makedirs(
    TEMP_AUDIO_DIR,
    exist_ok=True
)

# =========================================================
# SESSION STATE
# =========================================================

def initialize_session():

    previous_schema_version = st.session_state.get(
        "session_schema_version"
    )

    defaults = {

        "session_schema_version":
        SESSION_SCHEMA_VERSION,

        "chat_history":
        load_memory(),

        "tasks":
        [],

        "audio_processed":
        False,

        "last_audio_id":
        None,

        "last_uploaded_file_name":
        None,

        "session_stats":{

            "requests":0,
            "voice_requests":0,
            "uploaded_files":0
        },

        "system_state":{

            "mode":"idle",

            "active_agents":[],

            "last_agent":None,

            "reasoning_depth":0,

            "status":"operational"
        },

        "helios_reactor_mode":
        "Think",

        "helios_nav_open":
        True,

        "helios_focus_mode":
        False,

        "helios_preferred_agent":
        "Auto",

        "helios_action_tray_open":
        False,

        "helios_cancel_requested":
        False,

        "helios_processing_stage":
        "Done",

        "helios_execution_timeline":
        [],

        "helios_run_ledger":
        [],

        "helios_last_run_summary":
        "No completed run in this session yet.",

        "helios_last_latency_ms":
        0,

        "helios_last_transcript":
        "",

        "helios_voice_response_enabled":
        True
    }

    for key, value in defaults.items():

        if key not in st.session_state:

            st.session_state[key] = value

    if previous_schema_version != SESSION_SCHEMA_VERSION:

        st.session_state["session_schema_version"] = (
            SESSION_SCHEMA_VERSION
        )

        st.session_state["chat_history"] = load_memory()

initialize_session()

st.session_state["helios_nav_open"] = True
st.session_state["helios_focus_mode"] = False

# =========================================================
# SAFE HELPERS
# =========================================================

def safe_trim(
    text,
    limit=MAX_CONTEXT_CHARS
):

    if not text:
        return ""

    text = str(text)

    if len(text) <= limit:
        return text

    return text[-limit:]


def safe_response(
    text
):

    if not text:
        return ""

    text = str(text)

    if len(text) <= MAX_RESPONSE_CHARS:
        return text

    return (
        text[:MAX_RESPONSE_CHARS]
        +
        "\n\n[HELIOS OUTPUT TRUNCATED]"
    )


VOICE_TRANSCRIPTION_FAILURES = {
    "Audio conversion failed.",
    "No speech detected.",
    "Speech could not be recognized.",
    "Speech recognition service unavailable.",
    "SpeechRecognition is not installed in the Python environment running Streamlit.",
    "Voice transcription failed."
}


def is_voice_transcription_failure(text):

    return (
        not text
        or str(text).strip()
        in VOICE_TRANSCRIPTION_FAILURES
    )


def safe_background_task(
    fn,
    *args,
    **kwargs
):

    def runner():

        try:

            fn(*args, **kwargs)

        except Exception:

            logger.exception(
                "Background task failure"
            )

    threading.Thread(
        target=runner,
        daemon=True
    ).start()


def persist_project_memory_async(
    user_input,
    assistant_output
):

    summary = summarize_project(
        user_input,
        assistant_output
    )

    add_project_memory(
        user_input,
        summary
    )


def add_execution_event(
    label,
    message,
    *,
    status="OK",
    actor=None,
    module=None
):

    ledger = st.session_state.setdefault(
        "helios_run_ledger",
        []
    )

    ledger.append(
        {
            "time": time.strftime("%H:%M:%S"),
            "label": str(label or "RUN"),
            "message": safe_trim(
                message,
                220
            ),
            "status": str(status or "OK"),
            "actor": actor or st.session_state.get(
                "helios_reactor_agent",
                "Orion"
            ),
            "module": module or st.session_state.get(
                "helios_selected_module",
                "Command Center"
            )
        }
    )

    st.session_state["helios_run_ledger"] = ledger[-80:]


def collect_chat_file_context(
    chat_files
):

    if not chat_files:
        return ""

    contexts = []

    for chat_file in chat_files:

        try:

            context = read_uploaded_file(
                chat_file
            )

            if context:

                contexts.append(
                    context
                )

        except Exception:

            logger.exception(
                "Chat file ingestion failed"
            )

    return "\n\n---\n\n".join(
        contexts
    )


def persist_chat_turn(
    user_text,
    assistant_text,
    engine_text=""
):

    latest_history = load_memory()

    if latest_history:

        latest = latest_history[-1]

        if (
            latest.get("user") == str(user_text).strip()
            and
            latest.get("assistant") in {
                str(assistant_text).strip(),
                str(engine_text).strip()
            }
        ):

            st.session_state["chat_history"] = latest_history
            return latest_history

    st.session_state["chat_history"] = (
        add_to_memory(
            latest_history,
            user_text,
            assistant_text
        )
    )

    return st.session_state["chat_history"]


def render_module_shell(
    title,
    eyebrow,
    description,
    signals,
    *,
    kicker=None,
    status=None,
    icon="command",
    tabs=None
):

    render_command_shell(
        title=title,
        subtitle=description,
        kicker=kicker or eyebrow,
        status=status or f"{eyebrow} • BACKEND READY",
        icon=icon,
        tabs=tabs,
        metrics=signals
    )

# =========================================================
# SIDEBAR
# =========================================================

selected = render_sidebar()

render_nav_toggle()

render_status_strip(
    selected,
    st.session_state["session_stats"],
    st.session_state["system_state"]
)

render_platform_chrome(
    selected,
    st.session_state["session_stats"],
    st.session_state["system_state"]
)

# =========================================================
# DASHBOARD
# =========================================================

if selected == "Command Center":

    render_hero(
        st.session_state["session_stats"],
        st.session_state["system_state"]
    )

    render_mission_stack(
        st.session_state["session_stats"],
        st.session_state["system_state"]
    )

    render_execution_lanes(
        st.session_state["system_state"]
    )

    render_agent_matrix(
        st.session_state["system_state"]
    )

    render_quick_access()

    render_console(
        st.session_state.get(
            "helios_run_ledger",
            []
        )
    )

# =========================================================
# ANALYTICS
# =========================================================

elif selected == "System Analytics":

    render_analytics(
        st.session_state["session_stats"]
    )

# =========================================================
# MISSION CONTROL
# =========================================================

elif selected == "Mission Control":

    render_mission_control()

# =========================================================
# RESEARCH CENTER
# =========================================================

elif selected == "Research Center":

    render_module_shell(
        "Research Center",
        "SOURCES",
        "Search, compare, cite, and synthesize external knowledge.",
        [
            {"label":"Sources queued", "value":"18"},
            {"label":"Verified", "value":"11"},
            {"label":"Contradictions", "value":"2"},
            {"label":"Reports", "value":"4"}
        ],
        status="NOVA • BACKEND READY",
        icon="search",
        tabs=[
            "Search",
            "Sources",
            "Notes",
            "Reports"
        ]
    )

# =========================================================
# CODE INTELLIGENCE
# =========================================================

elif selected == "Code Intelligence":

    render_module_shell(
        "Code Intelligence",
        "ENGINEERING",
        "Inspect files, explain code paths, propose patches, and track test risk.",
        [
            {"label":"Files indexed", "value":"86"},
            {"label":"Risk flags", "value":"3"},
            {"label":"Tests mapped", "value":"14"},
            {"label":"Patch queue", "value":"2"}
        ],
        status="VEGA • BACKEND READY",
        icon="code",
        tabs=[
            "Files",
            "Analysis",
            "Patches",
            "Terminal"
        ]
    )

# =========================================================
# VOICE AI
# =========================================================

elif selected == "Voice AI":

    render_voice_cockpit(
        mic_recorder is not None,
        transcript=st.session_state.get(
            "helios_last_transcript",
            ""
        )
    )

# =========================================================
# CHAT HISTORY
# =========================================================

elif selected == "Chat History":

    render_chat_history(
        st.session_state["chat_history"]
    )

# =========================================================
# COLLABORATIVE AI
# =========================================================

elif selected == "Collaborative AI":

    render_module_shell(
        "Collaborative AI",
        "MULTI-AGENT",
        "Coordinate specialist agents around shared goals and review handoffs.",
        [
            {"label":"Agents", "value":"4"},
            {"label":"Handoffs", "value":"7"},
            {"label":"Decisions", "value":"5"},
            {"label":"Open asks", "value":"2"}
        ],
        status="ORION • BACKEND READY",
        icon="diamond",
        tabs=[
            "Room",
            "Handoffs",
            "Decisions",
            "Artifacts"
        ]
    )

# =========================================================
# PLANNING ENGINE
# =========================================================

elif selected == "Planning Engine":

    render_module_shell(
        "Planning Engine",
        "PLANNING",
        "Break goals into milestones, task graphs, dependencies, and next actions.",
        [
            {"label":"Milestones", "value":"5"},
            {"label":"Blocked", "value":"1"},
            {"label":"Ready tasks", "value":"8"},
            {"label":"Depth", "value":"4"}
        ],
        status="ORION • BACKEND READY",
        icon="list",
        tabs=[
            "Overview",
            "Task Graph",
            "Reasoning",
            "History"
        ]
    )

    render_feature_grid(
        [
            {
                "icon": "list",
                "title": "Goal Decomposition",
                "desc": "Break large requests into staged execution paths.",
                "status": "READY"
            },
            {
                "icon": "hexagon",
                "title": "Dependencies",
                "desc": "Map prerequisites, blockers, and execution ordering.",
                "status": "TRACKED"
            },
            {
                "icon": "bolt",
                "title": "Next Actions",
                "desc": "Generate clear next steps for autonomous or manual follow-through.",
                "status": "ONLINE"
            }
        ],
        columns=3
    )

# =========================================================
# RECURSIVE REASONING
# =========================================================

elif selected == "Recursive Reasoning":

    render_module_shell(
        "Recursive Reasoning",
        "REASONING",
        "Inspect reasoning traces, assumptions, alternatives, and refinement loops.",
        [
            {"label":"Trace depth", "value":"6"},
            {"label":"Branches", "value":"4"},
            {"label":"Risks", "value":"2"},
            {"label":"Confidence", "value":"82%"}
        ],
        status="ORION • BACKEND READY",
        icon="recursive",
        tabs=[
            "Trace",
            "Assumptions",
            "Branches",
            "Critique"
        ]
    )

    render_feature_grid(
        [
            {
                "icon": "recursive",
                "title": "Decompose",
                "desc": "Split hard requests into inspectable reasoning layers.",
                "status": "ACTIVE"
            },
            {
                "icon": "search",
                "title": "Critique",
                "desc": "Check intermediate answers for gaps and contradictions.",
                "status": "ACTIVE"
            },
            {
                "icon": "bolt",
                "title": "Refine",
                "desc": "Collapse the best path into a stable final response.",
                "status": "ACTIVE"
            }
        ],
        columns=3
    )

# =========================================================
# AUTONOMOUS LOOP
# =========================================================

elif selected == "Autonomous Loop":

    render_module_shell(
        "Autonomous Loop",
        "EXECUTION",
        "Run observe-plan-act-reflect cycles with guardrails and visible checkpoints.",
        [
            {"label":"Cycle", "value":"Observe"},
            {"label":"Actions", "value":"9"},
            {"label":"Approvals", "value":"2"},
            {"label":"Safety", "value":"On"}
        ],
        status="ORION • BACKEND READY",
        icon="infinity",
        tabs=[
            "Loop",
            "Guardrails",
            "Actions",
            "Review"
        ]
    )

    render_feature_grid(
        [
            {
                "icon": "list",
                "title": "Plan",
                "desc": "Create a short execution path for the current objective.",
                "status": "READY"
            },
            {
                "icon": "bolt",
                "title": "Act",
                "desc": "Run bounded actions through HELIOS tools and agents.",
                "status": "READY"
            },
            {
                "icon": "search",
                "title": "Observe",
                "desc": "Review output, detect failures, and choose the next move.",
                "status": "READY"
            }
        ],
        columns=3
    )

# =========================================================
# SWARM
# =========================================================

elif selected == "Swarm Intelligence":

    render_module_shell(
        "Swarm Intelligence",
        "DELEGATION",
        "Visualize agent load, routing, parallel work, and active task delegation.",
        [
            {"label":"Routes", "value":"12"},
            {"label":"Parallel jobs", "value":"3"},
            {"label":"Queue", "value":"6"},
            {"label":"Stable", "value":"Yes"}
        ],
        status="ORION • BACKEND READY",
        icon="hexagon",
        tabs=[
            "Network",
            "Queue",
            "Load",
            "Messages"
        ]
    )

    render_feature_grid(
        [
            {
                "icon": "search",
                "title": "Research Swarm",
                "desc": "Parallel discovery and source triage.",
                "status": "READY"
            },
            {
                "icon": "code",
                "title": "Code Swarm",
                "desc": "Disjoint implementation and review lanes.",
                "status": "READY"
            },
            {
                "icon": "hexagon",
                "title": "Synthesis",
                "desc": "Merge findings into one coherent result.",
                "status": "READY"
            }
        ],
        columns=3
    )

# =========================================================
# WORKFLOW
# =========================================================

elif selected == "Workflow Engine":

    render_module_shell(
        "Workflow Engine",
        "AUTOMATION",
        "Build workflows with triggers, steps, runs, logs, and recovery paths.",
        [
            {"label":"Workflows", "value":"9"},
            {"label":"Running", "value":"1"},
            {"label":"Paused", "value":"2"},
            {"label":"Artifacts", "value":"17"}
        ],
        status="VEGA • BACKEND READY",
        icon="bolt",
        tabs=[
            "Overview",
            "Builder",
            "Runs",
            "Triggers"
        ]
    )

    render_feature_grid(
        [
            {
                "icon": "list",
                "title": "Queue",
                "desc": "Organize staged workflow items and handoffs.",
                "status": "IDLE"
            },
            {
                "icon": "hexagon",
                "title": "Routing",
                "desc": "Send work to the best available HELIOS agent.",
                "status": "ONLINE"
            },
            {
                "icon": "bolt",
                "title": "Recovery",
                "desc": "Retry, repair, or escalate failed workflow steps.",
                "status": "ARMED"
            }
        ],
        columns=3
    )

# =========================================================
# KNOWLEDGE SOURCES
# =========================================================

elif selected == "Knowledge Sources":

    render_module_shell(
        "Knowledge Sources",
        "SOURCES",
        "Upload, index, scope, and manage files used by HELIOS.",
        [
            {"label":"Uploaded", "value":"3"},
            {"label":"Indexed", "value":"2"},
            {"label":"Pending", "value":"1"},
            {"label":"Scopes", "value":"5"}
        ],
        status="NOVA • BACKEND READY",
        icon="source",
        tabs=[
            "Sources",
            "Indexing",
            "Scopes",
            "Cleanup"
        ]
    )

# =========================================================
# FILE UPLOAD
# =========================================================

uploaded_file = None
file_content = ""

if selected in {
    "Research Center",
    "Code Intelligence",
    "Knowledge Sources"
}:

    uploaded_file, file_content = (
        render_upload_manager()
    )

if (
    uploaded_file
    and
    st.session_state.get("last_uploaded_file_name")
    != uploaded_file.name
):
    st.session_state["last_uploaded_file_name"] = uploaded_file.name
    st.session_state["session_stats"]["uploaded_files"] += 1

    if file_content:

        try:

            upsert_source(
                uploaded_file.name,
                uploaded_file.name.split(".")[-1].upper(),
                f"{round(uploaded_file.size / 1024, 2)} KB",
                file_content,
                st.session_state.get(
                    "helios_source_scope",
                    "Project"
                )
            )

        except Exception:

            logger.exception(
                "Source indexing failed"
            )

    add_execution_event(
        "SOURCE",
        f"Uploaded {uploaded_file.name}",
        actor="Nova",
        module=selected
    )

if selected in {
    "Research Center",
    "Code Intelligence",
    "Knowledge Sources"
}:

    render_source_intelligence_panel()

# =========================================================
# VOICE INPUT
# =========================================================

voice_text = ""

audio = None

if selected == "Voice AI" and mic_recorder is not None:

    audio = mic_recorder(
        start_prompt="Start voice",
        stop_prompt="Send voice",
        just_once=True,
        key="helios_voice_input",
        use_container_width=True
    )

elif selected == "Voice AI":

    message = (
        "Voice input needs streamlit-mic-recorder. "
        "Start HELIOS with ./venv/bin/streamlit run main.py from the backend folder."
    )

    render_system_notice(
        "warning",
        "Voice input package missing",
        message
    )

    if not st.session_state.get(
        "voice_dependency_warning_logged"
    ):

        logger.warning(
            message
        )

        st.session_state["voice_dependency_warning_logged"] = True

if audio and audio.get("bytes"):

    audio_id = str(
        hash(audio["bytes"])
    )

    if (
        st.session_state["last_audio_id"]
        != audio_id
    ):

        st.session_state["last_audio_id"] = audio_id

        try:

            transcript = transcribe_audio(
                audio["bytes"]
            )

            if is_voice_transcription_failure(
                transcript
            ):

                render_system_notice(
                    "error",
                    "Voice transcription issue",
                    transcript or "Voice transcription failed."
                )

            else:

                voice_text = transcript

                st.session_state["helios_last_transcript"] = voice_text

                render_system_notice(
                    "success",
                    "Transcript captured",
                    f"You said: {voice_text}"
                )

                st.session_state["session_stats"]["voice_requests"] += 1

        except Exception:

            logger.exception(
                "Voice transcription failed"
            )

# =========================================================
# CHAT INPUT
# =========================================================

CHAT_PLACEHOLDERS = {
    "Knowledge Sources":
    "Ask HELIOS to index files, summarize sources, or forget stale context...",
    "Research Center":
    "Ask HELIOS to search, compare, cite, or synthesize sources...",
    "Mission Control":
    "Ask HELIOS to turn a goal into a mission, agent lanes, checkpoints, and artifacts...",
    "Code Intelligence":
    "Ask HELIOS to inspect files, explain paths, or propose a patch...",
    "System Analytics":
    "Ask HELIOS about model health, memory pressure, latency, or logs...",
    "Voice AI":
    "Ask HELIOS to manage transcripts, voice profile, or hands-free sessions...",
    "Collaborative AI":
    "Ask HELIOS to coordinate agents, handoffs, decisions, or artifacts...",
    "Swarm Intelligence":
    "Ask HELIOS to route work, inspect queue load, or stabilize delegation...",
    "Autonomous Loop":
    "Ask HELIOS to run observe-plan-act-reflect cycles with guardrails...",
    "Planning Engine":
    "Ask HELIOS to break goals into milestones, task graphs, and next actions...",
    "Recursive Reasoning":
    "Ask HELIOS to inspect assumptions, branches, risks, or confidence...",
    "Workflow Engine":
    "Ask HELIOS to build workflows with triggers, runs, logs, and recovery...",
}


SLASH_COMMANDS = {
    "/search": {
        "module": "Research Center",
        "mode": "Search",
        "directive": "Search, compare, cite, and synthesize sources."
    },
    "/code": {
        "module": "Code Intelligence",
        "mode": "Build",
        "directive": "Inspect code, propose implementation, and verify risk."
    },
    "/plan": {
        "module": "Planning Engine",
        "mode": "Think",
        "directive": "Break the goal into milestones, dependencies, and next actions."
    },
    "/mission": {
        "module": "Mission Control",
        "mode": "Execute",
        "directive": "Turn the request into a mission with agent lanes, checkpoints, risks, and artifacts."
    },
    "/memory": {
        "module": "Knowledge Sources",
        "mode": "Memory",
        "directive": "Use stored context, files, and project memory as the main lens."
    },
    "/voice": {
        "module": "Voice AI",
        "mode": "Execute",
        "directive": "Route this as a voice workflow or transcript action."
    },
    "/workflow": {
        "module": "Workflow Engine",
        "mode": "Execute",
        "directive": "Turn the request into workflow steps, runs, logs, and recovery."
    },
}


def parse_slash_command(text):

    if not text:
        return None, text

    stripped = str(text).strip()

    if not stripped.startswith("/"):
        return None, text

    command, _, remainder = stripped.partition(" ")

    route = SLASH_COMMANDS.get(
        command.lower()
    )

    if not route:
        return None, text

    return route, (
        remainder.strip()
        or f"Run {command}."
    )


def get_simple_greeting_reply(text):

    normalized = re.sub(
        r"[^a-zA-Z\s']",
        "",
        str(text or "").lower()
    )

    normalized = re.sub(
        r"\s+",
        " ",
        normalized
    ).strip()

    greetings = {
        "hello",
        "hi",
        "hey",
        "heyy",
        "yo",
        "sup",
        "wassup",
        "whats up",
        "good morning",
        "good afternoon",
        "good evening"
    }

    if normalized in greetings:

        return "Hey, I'm here."

    return None


def should_use_web_search(text, route):

    if route:

        return route.get("module") == "Research Center"

    normalized = str(text or "").lower()

    search_terms = [
        "search",
        "web",
        "internet",
        "latest",
        "current",
        "today",
        "news",
        "source",
        "cite",
        "lookup",
        "look up"
    ]

    return any(
        term in normalized
        for term in search_terms
    )


def should_use_fast_chat(text, mode, module, route, files):

    if route or files:

        return False

    normalized = str(text or "").lower()

    heavy_terms = [
        "build",
        "fix",
        "debug",
        "implement",
        "analyze this file",
        "analyze these files",
        "research",
        "search",
        "latest",
        "current",
        "cite",
        "source",
        "workflow",
        "plan",
        "mission",
        "autonomous",
        "execute",
        "deploy",
        "rollback",
        "terminal",
        "shell command"
    ]

    if any(term in normalized for term in heavy_terms):

        return False

    return mode in {
        "Think",
        "Chat",
        "Build"
    }


def generate_fast_chat_response(text, directive):

    prompt = f"""
You are HELIOS.

Answer the user directly and conversationally.
Keep it concise unless the user asks for depth.
For code requests, provide the code first, then a brief note.
Do not add internal routing summaries, fake metrics, or reasoning labels.

Directive:
{directive}

User:
{text}
"""

    return generate_response(
        prompt
    )

chat_input_kwargs = {}

if getattr(
    st,
    "_helios_chat_input_accepts_files",
    False
):

    chat_input_kwargs = {
        "accept_file":"multiple",
        "file_type":[
            "txt",
            "py",
            "md"
        ]
    }

reactor_mode = render_command_reactor(
    selected,
    st.session_state["session_stats"],
    st.session_state["system_state"],
    file_enabled=bool(chat_input_kwargs)
)

if st.session_state.get(
    "helios_command_palette_open"
):

    render_command_palette()

chat_prompt = CHAT_PLACEHOLDERS.get(
    selected,
    "Ask HELIOS anything..."
)

chat_payload = st.chat_input(
    f"{reactor_mode} reactor • {chat_prompt}",
    **chat_input_kwargs
)

user_input = ""
chat_files = []

if isinstance(chat_payload, str):

    user_input = chat_payload

elif chat_payload:

    user_input = getattr(
        chat_payload,
        "text",
        ""
    )

    chat_files = getattr(
        chat_payload,
        "files",
        []
    )

    if not user_input and isinstance(chat_payload, dict):

        user_input = chat_payload.get(
            "text",
            ""
        )

        chat_files = chat_payload.get(
            "files",
            []
        )

    if chat_files:

        st.session_state["session_stats"]["uploaded_files"] += len(
            chat_files
        )

        chat_file_context = collect_chat_file_context(
            chat_files
        )

        if chat_file_context:

            file_content = "\n\n".join(
                item
                for item in [
                    file_content,
                    chat_file_context
                ]
                if item
            )

        if not user_input:

            user_input = (
                f"Index {len(chat_files)} uploaded source file(s)."
            )

final_input = (
    user_input
    or
    voice_text
)

active_module = selected

slash_route, routed_input = parse_slash_command(
    final_input
)

if slash_route:

    final_input = routed_input
    active_module = slash_route["module"]
    reactor_mode = slash_route["mode"]

    st.session_state["helios_selected_module"] = active_module
    st.session_state["helios_reactor_mode"] = reactor_mode
    st.session_state["helios_last_slash_command"] = slash_route

reactor_directive = st.session_state.get(
    "helios_reactor_directive",
    "Reason carefully and return the clearest answer."
)

if slash_route:

    reactor_directive = slash_route["directive"]

reactor_agent_hint = st.session_state.get(
    "helios_reactor_agent",
    "Orion"
)

conversation_profile = st.session_state.get(
    "helios_conversation_mode_profile",
    {}
)

engine_input = final_input

if final_input:

    engine_input = f"""
HELIOS COMMAND REACTOR
Mode: {reactor_mode}
Preferred agent: {reactor_agent_hint}
Active module: {active_module}
Directive: {reactor_directive}
Conversation intent: {conversation_profile.get("intent", "Answer clearly and stay scoped.")}
Expected output: {conversation_profile.get("output", "Clear response with useful next step.")}
Priority: {conversation_profile.get("priority", "Accuracy, clarity, and continuity.")}
Avoid: {conversation_profile.get("avoid", "Unnecessary sprawl.")}

USER REQUEST:
{final_input}
"""

# =========================================================
# MAIN EXECUTION
# =========================================================

if final_input:

    if st.session_state.get(
        "helios_cancel_requested"
    ):

        st.session_state["helios_cancel_requested"] = False
        st.session_state["helios_processing_stage"] = "Cancelled"

        render_system_notice(
            "warning",
            "HELIOS execution cancelled",
            "The stop control was armed before this run, so no model call was made."
        )

        add_execution_event(
            "CANCEL",
            "Stop control was armed before execution.",
            status="WARN",
            actor=reactor_agent_hint,
            module=active_module
        )

        st.stop()

    render_user_message(
        final_input,
        module=active_module,
        mode=reactor_mode
    )

    simple_reply = get_simple_greeting_reply(
        final_input
    )

    if simple_reply:

        render_assistant_message(
            simple_reply,
            tone="Quick reply"
        )

        from voice.voice_output import speak

        if st.session_state.get(
            "helios_voice_response_enabled",
            True
        ):

            safe_background_task(
                speak,
                simple_reply
            )

        st.session_state["chat_history"] = (
            persist_chat_turn(
                final_input,
                simple_reply
            )
        )

        st.session_state["session_stats"]["requests"] += 1
        st.session_state["helios_last_latency_ms"] = 0
        st.session_state["helios_last_run_summary"] = (
            "HELIOS handled a quick greeting."
        )
        st.session_state["helios_processing_stage"] = "Done"
        st.session_state["system_state"]["mode"] = "idle"
        st.session_state["system_state"]["status"] = "operational"

        add_execution_event(
            "DONE",
            "Handled quick greeting.",
            status="OK",
            actor=reactor_agent_hint,
            module=active_module
        )

        st.stop()

    run_started_at = time.perf_counter()

    thinking_placeholder = (
        render_thinking()
    )

    st.session_state["system_state"]["mode"] = "processing"
    st.session_state["system_state"]["status"] = "processing"
    st.session_state["helios_execution_timeline"] = []

    add_execution_event(
        "RUN",
        f"Started {reactor_mode} request.",
        status="LIVE",
        actor=reactor_agent_hint,
        module=active_module
    )

    def update_stage(stage, detail):

        st.session_state["helios_processing_stage"] = stage
        st.session_state["helios_execution_timeline"].append(
            f"{stage}: {detail}"
        )

        add_execution_event(
            stage.upper(),
            detail,
            status="LIVE" if stage != "Done" else "OK",
            actor=reactor_agent_hint,
            module=active_module
        )

        render_processing_state(
            thinking_placeholder,
            stage,
            detail,
            agent=reactor_agent_hint,
            mode=reactor_mode
        )

    fast_chat_run = should_use_fast_chat(
        final_input,
        reactor_mode,
        active_module,
        slash_route,
        chat_files
    )

    try:

        # =================================
        # WEB SEARCH
        # =================================

        web_results = ""

        if should_use_web_search(
            final_input,
            slash_route
        ):

            update_stage(
                "Using Tool",
                "Checking search routes, uploaded files, and active context."
            )

            try:

                web_results = search_web(
                    final_input,
                    max_results=3
                )

            except Exception:

                logger.exception(
                    "Web search failed"
                )

                web_results = ""

        # =================================
        # AGENT
        # =================================

        update_stage(
            "Routing",
            "Selecting the active HELIOS specialist for this request."
        )

        preferred_agent = st.session_state.get(
            "helios_preferred_agent",
            "Auto"
        )

        auto_agent = (
            preferred_agent
            if preferred_agent != "Auto"
            else detect_best_agent(
                engine_input
            )
        )

        st.session_state["system_state"][
            "last_agent"
        ] = auto_agent

        st.session_state["system_state"][
            "active_agents"
        ] = [
            auto_agent
        ]

        add_execution_event(
            "AGENT",
            f"Routed request to {auto_agent}.",
            status="OK",
            actor=auto_agent,
            module=active_module
        )

        # =================================
        # TASK
        # =================================

        if not fast_chat_run:

            try:

                update_stage(
                    "Thinking",
                    "Creating a visible task record and preparing execution memory."
                )

                task = create_task(
                    title="AI Request",
                    description=final_input,
                    agent=auto_agent
                )

                st.session_state["tasks"].append(
                    task
                )

                add_execution_event(
                    "TASK",
                    "Created task record for the current request.",
                    status="OK",
                    actor=auto_agent,
                    module=active_module
                )

                safe_background_task(
                    execute_task,
                    task
                )

            except Exception:

                logger.exception(
                    "Task creation failed"
                )

        # =================================
        # COGNITIVE ENGINE
        # =================================

        update_stage(
            "Writing",
            (
                "Composing a fast HELIOS response."
                if fast_chat_run
                else "Running the cognitive engine and composing the HELIOS response."
            )
        )

        if fast_chat_run:

            engine_output = generate_fast_chat_response(
                final_input,
                reactor_directive
            )

            cognitive_engine.last_trace = [
                {
                    "stage": "fast_chat",
                    "actor": "HELIOS",
                    "payload": {
                        "status": "completed"
                    },
                    "timestamp": time.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                }
            ]

        else:

            engine_output = cognitive_engine.execute(
                engine_input,
                web_results=web_results,
                file_content=file_content
            )

        # =================================
        # SAFE OUTPUT
        # =================================

        update_stage(
            "Done",
            "Finalizing response, memory, and dashboard telemetry."
        )

        output = safe_response(
            engine_output
        )

        st.session_state["helios_last_latency_ms"] = int(
            (
                time.perf_counter()
                -
                run_started_at
            )
            * 1000
        )

        st.session_state["system_state"]["reasoning_depth"] = len(
            getattr(
                cognitive_engine,
                "last_trace",
                []
            )
        )

        # =================================
        # REMOVE THINKING
        # =================================

        thinking_placeholder.empty()

        # =================================
        # STATUS
        # =================================

        render_agent_status(
            auto_agent
        )

        import platform

        try:

            import psutil

            cpu = f"{psutil.cpu_percent()}%"

            ram = f"{psutil.virtual_memory().percent}%"

        except ModuleNotFoundError:

            cpu = "Unavailable"

            ram = "Unavailable"

        system_name = platform.system()

        render_system_snapshot(
            system_name,
            cpu,
            ram
        )

        # =================================
        # RENDER RESPONSE
        # =================================

        full_response = (
            render_ai_response(
                output
            )
        )

        from voice.voice_output import speak

        if st.session_state.get(
            "helios_voice_response_enabled",
            True
        ):

            safe_background_task(
                speak,
                full_response
            )

        # =================================
        # SHARED BUS
        # =================================

        try:

            shared_bus.send_message(
                auto_agent,
                "System",
                safe_trim(
                    full_response,
                    3000
                )
            )

        except Exception:

            logger.exception(
                "Shared bus failure"
            )

        # =================================
        # PROJECT MEMORY
        # =================================

        try:

            safe_background_task(
                persist_project_memory_async,
                final_input,
                full_response
            )

        except Exception:

            logger.exception(
                "Project memory failure"
            )

        # =================================
        # CHAT MEMORY
        # =================================

        st.session_state["chat_history"] = (
            persist_chat_turn(
                final_input,
                full_response,
                engine_output
            )
        )

        # =================================
        # STATS
        # =================================

        st.session_state["session_stats"]["requests"] += 1
        st.session_state["helios_last_run_summary"] = (
            f"{auto_agent} handled {reactor_mode} mode in "
            f"{st.session_state['helios_last_latency_ms']} ms."
        )
        st.session_state["helios_processing_stage"] = "Done"

        add_execution_event(
            "DONE",
            st.session_state["helios_last_run_summary"],
            status="OK",
            actor=auto_agent,
            module=active_module
        )

        st.session_state["system_state"]["mode"] = "idle"
        st.session_state["system_state"]["status"] = "operational"
        st.session_state["system_state"]["active_agents"] = []

        # =================================
        # CLEANUP
        # =================================

        if (
            st.session_state["session_stats"]["requests"] % 5 == 0
        ):

            safe_background_task(
                cleanup_audio_files
            )

    except Exception as e:

        thinking_placeholder.empty()

        st.session_state["system_state"]["mode"] = "idle"
        st.session_state["system_state"]["status"] = "error"
        st.session_state["system_state"]["active_agents"] = []

        logger.error(
            traceback.format_exc()
        )

        add_execution_event(
            "ERROR",
            str(e),
            status="ERR",
            actor=reactor_agent_hint,
            module=active_module
        )

        render_system_notice(
            "error",
            "HELIOS execution failure",
            str(e)
        )
