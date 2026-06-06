import json
import os
import time
import uuid

from core.runtime_store import load_document
from core.runtime_store import save_document

MEMORY_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

MEMORY_FILE = os.path.join(
    MEMORY_DIR,
    "execution_history.json"
)

MAX_TEXT_CHARS = 8000
MAX_EXECUTION_EVENTS = 500


def make_json_safe(value):

    if value is None or isinstance(
        value,
        (
            bool,
            int,
            float
        )
    ):
        return value

    if isinstance(
        value,
        str
    ):
        if len(value) <= MAX_TEXT_CHARS:
            return value

        return (
            value[:MAX_TEXT_CHARS]
            +
            "\n\n[TRUNCATED]"
        )

    if isinstance(
        value,
        dict
    ):
        return {
            str(key): make_json_safe(item)
            for key, item in value.items()
        }

    if isinstance(
        value,
        (
            list,
            tuple,
            set
        )
    ):
        return [
            make_json_safe(item)
            for item in value
        ]

    return repr(value)

# =========================================
# LOAD MEMORY
# =========================================

def load_execution_memory():

    stored = load_document(
        "execution_history",
        None
    )

    if isinstance(
        stored,
        list
    ):

        return stored

    if not os.path.exists(
        MEMORY_FILE
    ):

        return []

    try:

        with open(

            MEMORY_FILE,

            "r",

            encoding="utf-8"

        ) as file:

            return json.load(file)

    except Exception:

        return []

# =========================================
# SAVE MEMORY
# =========================================

def save_execution_memory(

    memory

):

    if save_document(
        "execution_history",
        make_json_safe(
            memory
        )
    ):

        return

    os.makedirs(
        MEMORY_DIR,
        exist_ok=True
    )

    with open(

        MEMORY_FILE,

        "w",

        encoding="utf-8"

    ) as file:

        json.dump(

            make_json_safe(
                memory
            ),

            file,

            indent=4
        )


def _timestamp():
    return time.strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def record_execution_event(
    label,
    status,
    actor="HELIOS",
    module="execution",
    tool=None,
    detail="",
    input=None,
    result=None,
    error=None,
    duration_ms=None,
    attempt=1,
    parent_id=None,
    trace_id=None,
    metadata=None
):
    memory = load_execution_memory()
    safe_metadata = make_json_safe(
        metadata
        or {}
    )
    safe_trace_id = trace_id or (
        safe_metadata.get(
            "trace_id"
        )
        if isinstance(
            safe_metadata,
            dict
        )
        else None
    )

    event = {
        "id": str(
            uuid.uuid4()
        ),
        "timestamp": _timestamp(),
        "type": "tool_event"
        if tool
        else "execution_event",
        "label": make_json_safe(
            label
        ),
        "status": status,
        "actor": actor,
        "module": module,
        "tool": tool,
        "detail": make_json_safe(
            detail
        ),
        "input": make_json_safe(
            input
        ),
        "result": make_json_safe(
            result
        ),
        "error": make_json_safe(
            error
        ),
        "duration_ms": duration_ms,
        "attempt": attempt,
        "parent_id": parent_id,
        "trace_id": safe_trace_id,
        "metadata": safe_metadata
    }

    memory.append(
        event
    )

    save_execution_memory(
        memory[-MAX_EXECUTION_EVENTS:]
    )

    return event

# =========================================
# STORE EXECUTION
# =========================================

def store_execution(

    objective,

    actions,

    results

):

    memory = load_execution_memory()

    memory.append({

        "id":
        str(
            uuid.uuid4()
        ),

        "timestamp":
        _timestamp(),

        "type":
        "execution_batch",

        "objective":
        make_json_safe(
            objective
        ),

        "actions":
        make_json_safe(
            actions
        ),

        "results":
        make_json_safe(
            results
        )
    })

    save_execution_memory(
        memory
    )

# =========================================
# GET RECENT EXECUTIONS
# =========================================

def get_recent_executions(

    limit=5

):

    memory = load_execution_memory()

    return memory[-limit:]


def get_execution_events(
    limit=25,
    status=None,
    event_type=None
):
    safe_limit = max(
        1,
        min(
            int(
                limit
            ),
            100
        )
    )

    events = load_execution_memory()

    if status:
        events = [
            event
            for event in events
            if event.get(
                "status"
            ) == status
        ]

    if event_type:
        events = [
            event
            for event in events
            if event.get(
                "type"
            ) == event_type
        ]

    return events[-safe_limit:]


def execution_stats():
    events = load_execution_memory()
    tool_events = [
        event
        for event in events
        if event.get(
            "type"
        ) == "tool_event"
    ]

    completed = [
        event
        for event in tool_events
        if event.get(
            "status"
        ) == "success"
    ]
    failed = [
        event
        for event in tool_events
        if event.get(
            "status"
        ) == "failed"
    ]
    blocked = [
        event
        for event in tool_events
        if event.get(
            "status"
        ) == "blocked"
    ]

    return {
        "total_events": len(
            events
        ),
        "tool_events": len(
            tool_events
        ),
        "successful_tools": len(
            completed
        ),
        "failed_tools": len(
            failed
        ),
        "blocked_tools": len(
            blocked
        )
    }
