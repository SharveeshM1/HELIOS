import hashlib
import json
import uuid
from datetime import datetime
from typing import Dict
from typing import List

from core.runtime_store import load_document
from core.runtime_store import save_document


AUDIT_DOCUMENT = "audit_log"
MAX_AUDIT_EVENTS = 5000


def load_audit_events(
    limit: int = 100
) -> List[Dict]:
    events = load_document(
        AUDIT_DOCUMENT,
        []
    )
    if not isinstance(
        events,
        list
    ):
        return []
    safe_limit = max(
        1,
        min(
            int(
                limit
            ),
            1000
        )
    )
    return events[-safe_limit:]


def record_audit_event(
    action: str,
    *,
    actor: str = "anonymous",
    resource: str = "",
    status: str = "success",
    detail: str = "",
    metadata: Dict | None = None
) -> Dict:
    events = load_document(
        AUDIT_DOCUMENT,
        []
    )
    if not isinstance(
        events,
        list
    ):
        events = []
    previous_hash = (
        events[-1].get(
            "hash",
            ""
        )
        if events
        else ""
    )
    event = {
        "id": str(
            uuid.uuid4()
        ),
        "action": str(
            action
        )[:120],
        "actor": str(
            actor
        )[:120],
        "resource": str(
            resource
        )[:240],
        "status": str(
            status
        )[:40],
        "detail": str(
            detail
        )[:1000],
        "metadata": metadata or {},
        "previous_hash": previous_hash,
        "timestamp": datetime.now().isoformat(
            timespec="seconds"
        )
    }
    event["hash"] = hashlib.sha256(
        json.dumps(
            event,
            sort_keys=True,
            ensure_ascii=False
        ).encode(
            "utf-8"
        )
    ).hexdigest()
    events.append(
        event
    )
    save_document(
        AUDIT_DOCUMENT,
        events[-MAX_AUDIT_EVENTS:]
    )
    return event


def verify_audit_chain() -> Dict:
    events = load_document(
        AUDIT_DOCUMENT,
        []
    )
    if not isinstance(
        events,
        list
    ):
        events = []
    previous_hash = ""
    for index, event in enumerate(
        events
    ):
        candidate = {
            key: value
            for key, value in event.items()
            if key != "hash"
        }
        expected = hashlib.sha256(
            json.dumps(
                candidate,
                sort_keys=True,
                ensure_ascii=False
            ).encode(
                "utf-8"
            )
        ).hexdigest()
        if (
            event.get(
                "previous_hash",
                ""
            )
            != previous_hash
            or event.get(
                "hash"
            )
            != expected
        ):
            return {
                "valid": False,
                "events": len(
                    events
                ),
                "broken_index": index
            }
        previous_hash = event.get(
            "hash",
            ""
        )
    return {
        "valid": True,
        "events": len(
            events
        ),
        "broken_index": None
    }
