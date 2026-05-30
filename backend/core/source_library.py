import json
import os
import re
import tempfile
import threading

from datetime import datetime
from hashlib import sha256
from pathlib import Path
from typing import Dict
from typing import List

from core.runtime_config import MEMORY_DIR
from core.runtime_config import ensure_runtime_dirs

SOURCE_FILE = MEMORY_DIR / "source_library.json"
MAX_SOURCE_CHARS = 12000
MAX_SOURCES = 200

source_lock = threading.Lock()

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
    clean_scope = str(scope or "project").strip() or "project"
    fingerprint = sha256(
        "|".join(
            [
                clean_name.lower(),
                clean_type.lower(),
                clean_scope.lower(),
                clean_content
            ]
        ).encode("utf-8")
    ).hexdigest()[:16]
    source_id = f"src_{fingerprint}"

    sources = load_sources()
    entry = {
        "id": source_id,
        "name": clean_name,
        "type": clean_type,
        "size": str(size or "unknown"),
        "scope": clean_scope,
        "content": clean_content,
        "status": "Indexed" if clean_content else "Pending",
        "content_chars": len(clean_content),
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
    limit: int = 5,
    scope: str | None = None
) -> List[Dict]:

    terms = {
        term
        for term in re.findall(
            r"[a-z0-9_]{3,}",
            str(query).lower()
        )
    }

    clean_scope = str(scope).strip().lower() if scope else None

    sources = load_sources()
    ranked = []

    for source in sources:

        if (
            clean_scope
            and
            str(source.get("scope", "")).lower() != clean_scope
        ):

            continue

        haystack = " ".join(
            [
                str(source.get("name", "")),
                str(source.get("type", "")),
                str(source.get("scope", "")),
                str(source.get("content", ""))
            ]
        ).lower()

        score = sum(
            haystack.count(term)
            for term in terms
        )

        if score or not terms:

            match_terms = [
                term
                for term in terms
                if term in haystack
            ]

            source_copy = {
                key: value
                for key, value in source.items()
                if key != "content"
            }

            content = str(
                source.get("content", "")
            )

            source_copy["snippet"] = content[:280]
            source_copy["match_terms"] = match_terms

            ranked.append(
                (
                    score,
                    source.get("updated_at", ""),
                    source_copy
                )
            )

    ranked.sort(
        key=lambda item: (
            item[0],
            item[1]
        ),
        reverse=True
    )

    return [
        source
        for _, __, source in ranked[:limit]
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
        "total_content_chars": sum(
            len(
                str(source.get("content", ""))
            )
            for source in sources
        ),
        "scopes": sorted(
            {
                str(source.get("scope", "project"))
                for source in sources
            }
        ),
        "source_file": str(SOURCE_FILE)
    }
