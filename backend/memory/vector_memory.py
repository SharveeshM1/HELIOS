import hashlib
import logging
import math
import os
import re
from dataclasses import dataclass, field

from core.runtime_config import STORAGE_BACKEND
from core.runtime_config import VECTOR_BACKEND
from core.runtime_config import VECTOR_DATABASE_URL
from core.runtime_config import VECTOR_PERSIST_DIR
from core.runtime_store import load_semantic_memories
from core.runtime_store import upsert_semantic_memory

try:
    import chromadb
except Exception:
    chromadb = None

logger = logging.getLogger(
    "helios-vector-memory"
)

TOKEN_PATTERN = re.compile(
    r"[a-z0-9]+"
)


@dataclass
class VectorRecord:
    memory_id: str
    text: str
    embedding: list[float]
    metadata: dict = field(
        default_factory=dict
    )


class LocalVectorMemory:
    """Deterministic local vector memory used when no vector DB is available."""

    def __init__(
        self,
        dimensions=128
    ):
        self.dimensions = dimensions
        self.records = {}

    def clear(
        self
    ):
        self.records.clear()

    def store(
        self,
        memory_id,
        text,
        embedding=None,
        metadata=None
    ):
        text = str(
            text
        )

        record = VectorRecord(
            memory_id=str(
                memory_id
            ),
            text=text,
            embedding=embedding
            or hash_embedding(
                text,
                self.dimensions
            ),
            metadata=metadata
            or {}
        )

        self.records[
            record.memory_id
        ] = record

        return True

    def search(
        self,
        query,
        top_k=3
    ):
        query_embedding = hash_embedding(
            query,
            self.dimensions
        )

        ranked = sorted(
            self.records.values(),
            key=lambda record: cosine_similarity(
                query_embedding,
                record.embedding
            ),
            reverse=True
        )

        return [
            record.text
            for record in ranked[:top_k]
        ]


def tokenize(
    text
):
    return TOKEN_PATTERN.findall(
        str(
            text
        ).lower()
    )


def hash_embedding(
    text,
    dimensions=128
):
    vector = [
        0.0
        for _ in range(dimensions)
    ]

    for token in tokenize(
        text
    ):
        digest = hashlib.sha256(
            token.encode(
                "utf-8"
            )
        ).digest()

        index = int.from_bytes(
            digest[:2],
            "big"
        ) % dimensions

        sign = 1.0 if digest[2] % 2 == 0 else -1.0
        vector[index] += sign

    norm = math.sqrt(
        sum(
            value * value
            for value in vector
        )
    ) or 1.0

    return [
        value / norm
        for value in vector
    ]


def cosine_similarity(
    left,
    right
):
    return sum(
        left_value * right_value
        for left_value, right_value in zip(
            left,
            right
        )
    )


embedding_model = None
local_store = LocalVectorMemory()


def hydrate_memory():
    if STORAGE_BACKEND not in {
        "sqlite",
        "postgres"
    }:
        return 0
    count = 0
    for item in load_semantic_memories():
        local_store.store(
            item["id"],
            item["text"],
            embedding=item["embedding"],
            metadata=item.get(
                "metadata",
                {}
            )
        )
        count += 1
    return count


def _load_embedding_model():
    global embedding_model

    if embedding_model is not None:
        return embedding_model

    if os.getenv(
        "HELIOS_VECTOR_OFFLINE",
        ""
    ).lower() in {
        "1",
        "true",
        "yes"
    }:
        return None

    try:
        from sentence_transformers import (
            SentenceTransformer
        )

        embedding_model = SentenceTransformer(
            os.getenv(
                "HELIOS_VECTOR_MODEL",
                "all-MiniLM-L6-v2"
            )
        )

        return embedding_model

    except Exception as error:
        logger.warning(
            "Vector embedding model unavailable; using local hash embeddings: %s",
            str(
                error
            )
        )

        return None


def _embed(
    text
):
    model = _load_embedding_model()

    if model is None:
        return hash_embedding(
            text,
            local_store.dimensions
        )

    return model.encode(
        str(
            text
        )
    ).tolist()


def _create_collection():
    if chromadb is None or VECTOR_BACKEND == "local":
        return None

    try:
        if VECTOR_BACKEND == "chroma_http":
            from urllib.parse import urlparse

            parsed = urlparse(
                VECTOR_DATABASE_URL
            )
            if not parsed.hostname:
                raise ValueError(
                    "HELIOS_VECTOR_DATABASE_URL is required for chroma_http."
                )
            client = chromadb.HttpClient(
                host=parsed.hostname,
                port=parsed.port
                or (
                    443
                    if parsed.scheme == "https"
                    else 8000
                ),
                ssl=parsed.scheme == "https"
            )
        else:
            client = chromadb.PersistentClient(
                path=VECTOR_PERSIST_DIR
            )

        return client.get_or_create_collection(
            name="helios_memory"
        )

    except Exception as error:
        logger.warning(
            "Vector DB unavailable; using local vector memory: %s",
            str(
                error
            )
        )

        return None


collection = _create_collection()
hydrate_memory()


def vector_status():
    return {
        "backend": VECTOR_BACKEND,
        "collection_available": collection is not None,
        "database_url_configured": bool(
            VECTOR_DATABASE_URL
        ),
        "persist_directory": VECTOR_PERSIST_DIR
        if VECTOR_BACKEND == "chroma_persistent"
        else None,
        "embedding_model": os.getenv(
            "HELIOS_VECTOR_MODEL",
            "all-MiniLM-L6-v2"
        ),
        "embedding_fallback": embedding_model is None
    }


def clear_memory():
    local_store.clear()

    if collection is not None:
        try:
            existing = collection.get()
            ids = existing.get(
                "ids",
                []
            )

            if ids:
                collection.delete(
                    ids=ids
                )

        except Exception as error:
            logger.warning(
                "Unable to clear vector DB collection: %s",
                str(
                    error
                )
            )

    return True


def store_memory(
    memory_id,
    text,
    metadata=None
):
    embedding = _embed(
        text
    )

    local_store.store(
        memory_id,
        text,
        embedding=embedding,
        metadata=metadata
    )
    if STORAGE_BACKEND in {
        "sqlite",
        "postgres"
    }:
        upsert_semantic_memory(
            str(
                memory_id
            ),
            str(
                text
            ),
            embedding,
            metadata or {}
        )

    if collection is None:
        return True

    payload = {
        "ids": [
            str(
                memory_id
            )
        ],
        "documents": [
            str(
                text
            )
        ],
        "embeddings": [
            embedding
        ],
    }

    if metadata:
        payload[
            "metadatas"
        ] = [
            metadata
        ]

    if hasattr(
        collection,
        "upsert"
    ):
        collection.upsert(
            **payload
        )
    else:
        collection.add(
            **payload
        )

    return True


def search_memory(
    query,
    top_k=3
):
    query_embedding = _embed(
        query
    )

    if collection is None:
        return local_store.search(
            query,
            top_k=top_k
        )

    try:
        results = collection.query(
            query_embeddings=[
                query_embedding
            ],
            n_results=top_k
        )

        documents = results.get(
            "documents",
            []
        )

        if documents:
            return documents[0]

    except Exception as error:
        logger.warning(
            "Vector DB search failed; using local vector memory: %s",
            str(
                error
            )
        )

    return local_store.search(
        query,
        top_k=top_k
    )


def search_memory_records(
    query,
    top_k=3
):
    query_embedding = _embed(
        query
    )
    ranked = sorted(
        local_store.records.values(),
        key=lambda record: cosine_similarity(
            query_embedding,
            record.embedding
        ),
        reverse=True
    )
    return [
        {
            "id": record.memory_id,
            "text": record.text,
            "metadata": record.metadata,
            "score": round(
                cosine_similarity(
                    query_embedding,
                    record.embedding
                ),
                4
            )
        }
        for record in ranked[:top_k]
    ]
