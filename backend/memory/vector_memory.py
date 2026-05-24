import hashlib
import logging
import math
import os

try:
    import chromadb
except Exception:
    chromadb = None

logger = logging.getLogger(
    "helios-vector-memory"
)

# =========================================
# VECTOR DB
# =========================================

if chromadb is not None:

    client = chromadb.Client()

    collection = client.get_or_create_collection(
        name="helios_memory"
    )

else:

    client = None
    collection = None

fallback_store = {}

# =========================================
# EMBEDDING MODEL
# =========================================

embedding_model = None


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
            str(error)
        )

        return None


def _hash_embedding(
    text,
    dimensions=64
):

    vector = [
        0.0
        for _ in range(dimensions)
    ]

    for word in str(text).lower().split():

        digest = hashlib.sha256(
            word.encode("utf-8")
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


def _embed(
    text
):

    model = _load_embedding_model()

    if model is None:

        return _hash_embedding(
            text
        )

    return model.encode(
        text
    ).tolist()

# =========================================
# STORE MEMORY
# =========================================

def store_memory(

    memory_id,
    text

):

    embedding = _embed(
        text
    )

    if collection is None:

        fallback_store[str(memory_id)] = {
            "text": str(text),
            "embedding": embedding
        }

        return True

    if hasattr(
        collection,
        "upsert"
    ):

        collection.upsert(

            ids=[memory_id],

            documents=[text],

            embeddings=[embedding]
        )

    else:

        collection.add(

            ids=[memory_id],

            documents=[text],

            embeddings=[embedding]
        )

    return True

# =========================================
# SEARCH MEMORY
# =========================================

def search_memory(

    query,
    top_k=3

):

    query_embedding = _embed(
        query
    )

    if collection is None:

        def score(item):

            return sum(
                left * right
                for left, right in zip(
                    query_embedding,
                    item["embedding"]
                )
            )

        ranked = sorted(
            fallback_store.values(),
            key=score,
            reverse=True
        )

        return [
            item["text"]
            for item in ranked[:top_k]
        ]

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

    if not documents:

        return []

    return documents[0]
