import base64
import binascii
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
from core.runtime_store import load_document
from core.runtime_store import save_document
from core.ingestion_engine import extract_github_repo
from core.ingestion_engine import extract_docx_text
from core.ingestion_engine import extract_pdf_text
from core.ingestion_engine import extract_web_text
from memory.vector_memory import search_memory_records
from memory.vector_memory import store_memory

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

        stored = load_document(
            "source_library",
            None
        )

        if isinstance(
            stored,
            list
        ):

            return [
                item
                for item in stored
                if isinstance(item, dict)
                and item.get("id")
                and item.get("name")
            ]

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

        if save_document(
            "source_library",
            sources[-MAX_SOURCES:]
        ):

            return

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
    clean_type = str(source_type).strip().upper() or "FILE"
    clean_content = str(content or "")
    clean_scope = str(scope or "project").strip() or "project"

    if clean_type in {
        "PDF",
        "DOCX"
    } and clean_content:
        try:
            pdf_bytes = base64.b64decode(
                clean_content,
                validate=True
            )
        except (
            binascii.Error,
            ValueError
        ) as error:
            raise ValueError(
                f"{clean_type} source content must be valid base64."
            ) from error
        clean_content = (
            extract_pdf_text(
                pdf_bytes
            )
            if clean_type == "PDF"
            else extract_docx_text(
                pdf_bytes
            )
        )
    elif clean_type == "WEB":
        clean_content = extract_web_text(
            clean_content
        )
    elif clean_type == "GITHUB":
        clean_content = extract_github_repo(
            clean_content
        )

    clean_content = clean_content[:MAX_SOURCE_CHARS]

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

    store_memory(
        f"source:{source_id}",
        "\n".join(
            [
                clean_name,
                clean_type,
                clean_scope,
                clean_content
            ]
        ),
        metadata={
            "kind": "source",
            "source_id": source_id,
            "name": clean_name,
            "type": clean_type,
            "scope": clean_scope
        }
    )

    return entry


def reindex_source(source_identifier: str, scope: str | None = None) -> Dict:

    clean_identifier = str(source_identifier).strip()

    if not clean_identifier:

        raise ValueError("Source identifier is required.")

    sources = load_sources()
    target = None

    for item in sources:

        if str(item.get("id", "")) == clean_identifier or str(item.get("name", "")) == clean_identifier:

            target = item
            break

    if target is None:

        raise ValueError("Source not found.")

    refreshed = dict(target)
    refreshed["scope"] = str(scope or target.get("scope", "project") or "project")
    refreshed["status"] = "Indexed" if refreshed.get("content") else "Pending"
    refreshed["content_chars"] = len(str(refreshed.get("content", "")))
    refreshed["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    remaining = [item for item in sources if item.get("id") != target.get("id")]
    remaining.append(refreshed)
    save_sources(remaining)

    return {
        **refreshed,
        "reindexed": True,
        "stats": source_stats(),
    }


def delete_source(source_identifier: str) -> Dict:

    clean_identifier = str(source_identifier).strip()

    if not clean_identifier:

        raise ValueError("Source identifier is required.")

    sources = load_sources()
    target = None

    for item in sources:

        if str(item.get("id", "")) == clean_identifier or str(item.get("name", "")) == clean_identifier:

            target = item
            break

    if target is None:

        raise ValueError("Source not found.")

    remaining = [item for item in sources if item.get("id") != target.get("id")]
    save_sources(remaining)

    return {
        **target,
        "deleted": True,
        "stats": source_stats(),
    }


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
    sources_by_id = {
        str(
            source.get("id", "")
        ): source
        for source in sources
    }
    semantic_scores = {}
    if str(query).strip():
        for record in search_memory_records(
            query,
            top_k=max(
                limit * 4,
                12
            )
        ):
            metadata = record.get(
                "metadata",
                {}
            )
            if metadata.get("kind") != "source":
                continue
            source_id = str(
                metadata.get(
                    "source_id",
                    ""
                )
            )
            source = sources_by_id.get(
                source_id
            )
            if source is None:
                continue
            if (
                clean_scope
                and
                str(
                    source.get(
                        "scope",
                        ""
                    )
                ).lower() != clean_scope
            ):
                continue
            semantic_scores[source_id] = max(
                float(
                    record.get(
                        "score",
                        0
                    )
                ),
                semantic_scores.get(
                    source_id,
                    0.0
                )
            )
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

        semantic_score = semantic_scores.get(
            str(
                source.get(
                    "id",
                    ""
                )
            ),
            0.0
        )

        if score or semantic_score > 0 or not terms:

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
            source_copy["semantic_score"] = round(
                semantic_score,
                4
            )
            source_copy["retrieval"] = "semantic"
            if score and semantic_score > 0:
                source_copy["retrieval"] = "hybrid"
            elif score:
                source_copy["retrieval"] = "keyword"

            ranked.append(
                (
                    score + semantic_score,
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
