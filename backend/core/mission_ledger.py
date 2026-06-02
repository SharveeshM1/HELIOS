import json
import os
import tempfile
import threading

from datetime import datetime
from hashlib import sha256
from pathlib import Path
from typing import Dict
from typing import List

from core.runtime_config import MEMORY_DIR
from core.runtime_config import ensure_runtime_dirs


MISSION_LEDGER_FILE = MEMORY_DIR / "mission_ledger.json"
MAX_MISSION_EVENTS = 300

mission_ledger_lock = threading.Lock()

ensure_runtime_dirs()


def _atomic_write(
    path: Path,
    data
) -> None:

    with tempfile.NamedTemporaryFile(
        mode="w",
        delete=False,
        encoding="utf-8",
        dir=str(MEMORY_DIR)
    ) as temp_file:

        json.dump(
            data,
            temp_file,
            indent=4,
            ensure_ascii=False
        )

        temp_path = temp_file.name

    os.replace(
        temp_path,
        path
    )


def load_mission_events() -> List[Dict]:

    with mission_ledger_lock:

        if not MISSION_LEDGER_FILE.exists():

            return []

        try:

            with MISSION_LEDGER_FILE.open(
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

            if not isinstance(
                data,
                list
            ):

                return []

            return [
                item
                for item in data
                if isinstance(item, dict)
                and item.get("id")
                and item.get("stage")
            ]

        except Exception:

            return []


def save_mission_events(
    events: List[Dict]
) -> None:

    with mission_ledger_lock:

        _atomic_write(
            MISSION_LEDGER_FILE,
            events[-MAX_MISSION_EVENTS:]
        )


def record_mission_event(
    stage: str,
    title: str,
    *,
    agent: str = "HELIOS",
    module: str = "dashboard",
    status: str = "active",
    detail: str = "",
    mission_id: str | None = None,
    artifact: Dict | None = None
) -> Dict:

    safe_stage = str(stage or "Created").strip() or "Created"
    safe_title = str(title or "Untitled mission").strip()[:180] or "Untitled mission"
    safe_agent = str(agent or "HELIOS").strip() or "HELIOS"
    safe_module = str(module or "dashboard").strip() or "dashboard"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    safe_mission_id = (
        str(mission_id).strip()
        if mission_id
        else ""
    )
    event_id = (
        f"mission_{timestamp.replace('-', '').replace(':', '').replace(' ', '_')}_"
        f"{len(load_mission_events()) + 1}"
    )

    event = {
        "id": event_id,
        "stage": safe_stage,
        "mission_id": safe_mission_id or event_id,
        "title": safe_title,
        "agent": safe_agent,
        "module": safe_module,
        "status": str(status or "active"),
        "detail": str(detail or "")[:360],
        "artifact": artifact or {},
        "timestamp": timestamp
    }

    events = load_mission_events()
    events.append(
        event
    )
    save_mission_events(
        events
    )

    return event


def create_mission(
    title: str,
    *,
    agent: str = "Orion",
    module: str = "planning",
    detail: str = ""
) -> Dict:

    clean_title = str(title or "Untitled mission").strip()[:180] or "Untitled mission"
    mission_id = (
        "mission_"
        + sha256(
            f"{clean_title}|{agent}|{module}|{datetime.now().isoformat()}".encode("utf-8")
        ).hexdigest()[:14]
    )

    created = record_mission_event(
        "Created",
        clean_title,
        agent=agent,
        module=module,
        status="active",
        detail=detail or "Mission created from HELIOS command surface.",
        mission_id=mission_id
    )

    assigned = record_mission_event(
        "Assigned",
        clean_title,
        agent=agent,
        module=module,
        status="assigned",
        detail=f"{agent} assigned to {module}.",
        mission_id=mission_id
    )

    return {
        "mission": {
            "id": mission_id,
            "title": created["title"],
            "agent": agent,
            "module": module,
            "status": "assigned",
            "created_at": created["timestamp"]
        },
        "events": [
            created,
            assigned
        ]
    }


def mission_summary(
    mission_id: str
) -> Dict | None:

    safe_mission_id = str(mission_id or "").strip()

    if not safe_mission_id:

        return None

    events = [
        event
        for event in load_mission_events()
        if event.get("mission_id") == safe_mission_id
        or event.get("id") == safe_mission_id
    ]

    if not events:

        return None

    latest = events[-1]

    return {
        "id": safe_mission_id,
        "title": latest.get("title", "Untitled mission"),
        "agent": latest.get("agent", "HELIOS"),
        "module": latest.get("module", "dashboard"),
        "status": latest.get("status", "active"),
        "stage": latest.get("stage", "Created"),
        "created_at": events[0].get("timestamp"),
        "updated_at": latest.get("timestamp")
    }


def advance_mission(
    mission_id: str,
    stage: str,
    *,
    agent: str | None = None,
    module: str | None = None,
    detail: str = "",
    artifact: Dict | None = None
) -> Dict:

    mission = mission_summary(
        mission_id
    )

    if mission is None:

        raise ValueError(
            "Mission not found."
        )

    safe_stage = str(stage or "Executed").strip() or "Executed"
    status_map = {
        "Created": "active",
        "Assigned": "assigned",
        "Executed": "executed",
        "Reviewed": "reviewed",
        "Archived": "archived"
    }
    event = record_mission_event(
        safe_stage,
        mission["title"],
        agent=agent or mission["agent"],
        module=module or mission["module"],
        status=status_map.get(
            safe_stage,
            safe_stage.lower()
        ),
        detail=detail or f"Mission advanced to {safe_stage}.",
        mission_id=mission["id"],
        artifact=artifact
    )

    return {
        "mission": mission_summary(
            mission["id"]
        ),
        "event": event
    }


def latest_missions(
    limit: int = 12
) -> List[Dict]:

    grouped: Dict[str, List[Dict]] = {}

    for event in load_mission_events():

        mission_id = str(
            event.get("mission_id")
            or event.get("id")
        )

        grouped.setdefault(
            mission_id,
            []
        ).append(
            event
        )

    missions = []

    for mission_id, events in grouped.items():

        latest = events[-1]
        missions.append(
            {
                "id": mission_id,
                "title": latest.get("title", "Untitled mission"),
                "agent": latest.get("agent", "HELIOS"),
                "module": latest.get("module", "dashboard"),
                "status": latest.get("status", "active"),
                "stage": latest.get("stage", "Created"),
                "event_count": len(events),
                "created_at": events[0].get("timestamp"),
                "updated_at": latest.get("timestamp")
            }
        )

    missions.sort(
        key=lambda item: str(
            item.get("updated_at", "")
        ),
        reverse=True
    )

    return missions[:limit]


def agent_activity() -> Dict:

    states = {
        "Orion": {
            "state": "Idle",
            "module": "dashboard",
            "last_event": None
        },
        "Nova": {
            "state": "Idle",
            "module": "research",
            "last_event": None
        },
        "Vega": {
            "state": "Idle",
            "module": "code",
            "last_event": None
        },
        "Lyra": {
            "state": "Idle",
            "module": "voice",
            "last_event": None
        }
    }

    stage_states = {
        "Created": "Thinking",
        "Assigned": "Thinking",
        "Executed": "Executing",
        "Reviewed": "Reviewing",
        "Archived": "Idle"
    }

    for event in load_mission_events()[-80:]:

        agent = str(
            event.get(
                "agent",
                ""
            )
        )

        if agent not in states:

            continue

        module = str(
            event.get(
                "module",
                states[agent]["module"]
            )
        )
        stage = str(
            event.get(
                "stage",
                ""
            )
        )
        state = stage_states.get(
            stage,
            "Thinking"
        )

        if agent == "Nova" and module == "research":

            state = "Researching"

        if agent == "Vega" and module in {
            "code",
            "workflow"
        }:

            state = "Building"

        if agent == "Lyra" and module == "voice":

            state = "Listening"

        states[agent] = {
            "state": state,
            "module": module,
            "last_event": event.get("title"),
            "updated_at": event.get("timestamp")
        }

    return states


def mission_stats() -> Dict:

    events = load_mission_events()

    return {
        "total_events": len(events),
        "active_events": len(
            [
                event
                for event in events
                if event.get("status") != "archived"
            ]
        ),
        "ledger_file": str(MISSION_LEDGER_FILE)
    }
