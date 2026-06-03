import os

os.environ.setdefault(
    "HELIOS_VECTOR_OFFLINE",
    "1"
)

from memory.vector_memory import (
    LocalVectorMemory,
    clear_memory,
    store_memory,
    search_memory
)
from core import vector_memory as core_vector_memory


def test_vector_memory_stores_and_searches_locally():
    clear_memory()

    store_memory(

        "1",

        "HELIOS uses autonomous AI agents with local Ollama inference."
    )

    store_memory(

        "2",

        "Vector databases enable semantic memory retrieval."
    )

    results = search_memory(

        "How does HELIOS remember information?"
    )

    assert results
    assert any(
        "memory" in result.lower()
        or "remember" in result.lower()
        for result in results
    )


def test_local_vector_memory_upserts_by_id():
    memory = LocalVectorMemory()

    memory.store(
        "same-id",
        "Old memory content"
    )
    memory.store(
        "same-id",
        "New memory retrieval content"
    )

    results = memory.search(
        "retrieval",
        top_k=3
    )

    assert results == [
        "New memory retrieval content"
    ]


def test_core_vector_memory_exports_memory_api_not_tool_dispatcher():
    clear_memory()

    assert not hasattr(
        core_vector_memory,
        "execute_tool"
    )

    core_vector_memory.store_memory(
        "core-1",
        "Core vector memory delegates to the memory backend."
    )

    results = core_vector_memory.search_memory(
        "memory backend"
    )

    assert results
    assert results[0] == "Core vector memory delegates to the memory backend."
