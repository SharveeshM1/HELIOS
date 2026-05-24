import os

os.environ.setdefault(
    "HELIOS_VECTOR_OFFLINE",
    "1"
)

from memory.vector_memory import (
    store_memory,
    search_memory
)


def test_vector_memory_stores_and_searches_locally():

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
