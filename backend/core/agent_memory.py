import json
import os
import re
import tempfile
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict
from typing import List

from core.runtime_config import MEMORY_DIR
from core.runtime_store import load_document
from core.runtime_store import save_document
from memory.vector_memory import search_memory_records
from memory.vector_memory import store_memory


AGENT_MEMORY_FILE = MEMORY_DIR / "agent_memory.json"
MAX_AGENT_MEMORIES = 200
agent_memory_lock = threading.RLock()


def _agent_key(
    agent: str
) -> str:
    return re.sub(
        r"[^a-z0-9_-]+",
        "-",
        str(
            agent or "helios"
        ).strip().lower()
    ).strip(
        "-"
    ) or "helios"


def _load_file() -> Dict[str, List[Dict]]:
    if not AGENT_MEMORY_FILE.exists():
        return {}
    try:
        data = json.loads(
            AGENT_MEMORY_FILE.read_text(
                encoding="utf-8"
            )
        )
        return data if isinstance(
            data,
            dict
        ) else {}
    except Exception:
        return {}


def _save_file(
    data: Dict[str, List[Dict]]
) -> None:
    MEMORY_DIR.mkdir(
        parents=True,
        exist_ok=True
    )
    with tempfile.NamedTemporaryFile(
        mode="w",
        delete=False,
        encoding="utf-8",
        dir=str(
            MEMORY_DIR
        )
    ) as temp_file:
        json.dump(
            data,
            temp_file,
            indent=2,
            ensure_ascii=False
        )
        temp_path = temp_file.name
    os.replace(
        temp_path,
        AGENT_MEMORY_FILE
    )


def load_agent_memories(
    agent: str
) -> List[Dict]:
    key = _agent_key(
        agent
    )
    with agent_memory_lock:
        stored = load_document(
            f"agent_memory:{key}",
            None
        )
        if isinstance(
            stored,
            list
        ):
            return stored
        return _load_file().get(
            key,
            []
        )


def remember_agent_result(
    agent: str,
    objective: str,
    result: str,
    *,
    metadata: Dict | None = None
) -> Dict:
    key = _agent_key(
        agent
    )
    item = {
        "id": str(
            uuid.uuid4()
        ),
        "agent": str(
            agent or "HELIOS"
        ),
        "objective": str(
            objective or ""
        )[:1000],
        "result": str(
            result or ""
        )[:12000],
        "metadata": metadata or {},
        "timestamp": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    }
    with agent_memory_lock:
        memories = load_agent_memories(
            agent
        )
        memories.append(
            item
        )
        memories = memories[
            -MAX_AGENT_MEMORIES:
        ]
        if not save_document(
            f"agent_memory:{key}",
            memories
        ):
            data = _load_file()
            data[
                key
            ] = memories
            _save_file(
                data
            )
    store_memory(
        f"agent:{key}:{item['id']}",
        f"{item['objective']}\n\n{item['result']}",
        metadata={
            "kind": "agent_memory",
            "agent": key,
            **(
                metadata or {}
            )
        }
    )
    return item


def search_agent_memory(
    agent: str,
    query: str,
    limit: int = 5
) -> List[Dict]:
    key = _agent_key(
        agent
    )
    semantic = [
        item
        for item in search_memory_records(
            query,
            top_k=max(
                limit * 3,
                10
            )
        )
        if item.get(
            "metadata",
            {}
        ).get(
            "kind"
        )
        == "agent_memory"
        and item.get(
            "metadata",
            {}
        ).get(
            "agent"
        )
        == key
    ][
        :limit
    ]
    if semantic:
        return semantic
    terms = {
        term
        for term in re.findall(
            r"[a-z0-9_]{3,}",
            str(
                query
            ).lower()
        )
    }
    ranked = []
    for item in load_agent_memories(
        agent
    ):
        text = (
            f"{item.get('objective', '')} "
            f"{item.get('result', '')}"
        ).lower()
        score = sum(
            text.count(
                term
            )
            for term in terms
        )
        if score:
            ranked.append(
                (
                    score,
                    item
                )
            )
    ranked.sort(
        key=lambda pair: pair[0],
        reverse=True
    )
    return [
        item
        for _, item in ranked[
            :limit
        ]
    ]
