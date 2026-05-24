import json
import os
import tempfile
import threading

from datetime import datetime
from pathlib import Path
from typing import Dict
from typing import List


BASE_DIR = Path(__file__).resolve().parents[1]
MEMORY_DIR = BASE_DIR / "memory"
SOURCE_FILE = MEMORY_DIR / "source_library.json"
MAX_SOURCE_CHARS = 12000
MAX_SOURCES = 200

source_lock = threading.Lock()

MEMORY_DIR.mkdir(
    exist_ok=True
)


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


def load_sources() -> List[Dict]:

    with source_lock:

        if not SOURCE_FILE.exists():

            return []

        try:

            with SOURCE_FILE.open(
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
                and item.get("name")
            ]

        except Exception:

            return []


def save_sources(
    sources: List[Dict]
) -> None:

    with source_lock:

        _atomic_write(
            SOURCE_FILE,
            sources[-MAX_SOURCES:]
        )


def upsert_source(
    name: str,
    source_type: str,
    size: str,
    content: str,
    scope: str = "project"
) -> Dict:

    clean_name = str(name).strip() or "source"
    clean_type = str(source_type).strip() or "FILE"
    clean_content = str(content or "")[:MAX_SOURCE_CHARS]
    source_id = f"{clean_name}:{clean_type}:{len(clean_content)}"

    sources = load_sources()
    entry = {
        "id": source_id,
        "name": clean_name,
        "type": clean_type,
        "size": str(size or "unknown"),
        "scope": str(scope or "project"),
        "content": clean_content,
        "status": "Indexed" if clean_content else "Pending",
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    updated = False

    for index, item in enumerate(sources):

        if item.get("id") == source_id:

            sources[index] = entry
            updated = True
            break

    if not updated:

        sources.append(entry)

    save_sources(
        sources
    )

    return entry


def search_sources(
    query: str,
    limit: int = 5
) -> List[Dict]:

    terms = [
        term
        for term in str(query).lower().split()
        if len(term) > 2
    ]

    sources = load_sources()
    ranked = []

    for source in sources:

        haystack = " ".join(
            [
                str(source.get("name", "")),
                str(source.get("type", "")),
                str(source.get("content", ""))
            ]
        ).lower()

        score = sum(
            haystack.count(term)
            for term in terms
        )

        if score or not terms:

            ranked.append(
                (
                    score,
                    source
                )
            )

    ranked.sort(
        key=lambda item: item[0],
        reverse=True
    )

    return [
        source
        for _, source in ranked[:limit]
    ]


def source_stats() -> Dict:

    sources = load_sources()
    indexed = [
        source
        for source in sources
        if source.get("status") == "Indexed"
    ]

    return {
        "total_sources": len(sources),
        "indexed_sources": len(indexed),
        "pending_sources": len(sources) - len(indexed),
        "source_file": str(SOURCE_FILE)
    }
