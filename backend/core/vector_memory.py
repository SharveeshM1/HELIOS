"""Core vector memory interface.

This module intentionally mirrors the public vector-memory API from
``memory.vector_memory``. Tool execution belongs in ``core.tool_manager``.
"""

try:
    from memory.vector_memory import (
        LocalVectorMemory,
        clear_memory,
        search_memory_records,
        search_memory,
        store_memory,
    )
except ModuleNotFoundError:
    from backend.memory.vector_memory import (
        LocalVectorMemory,
        clear_memory,
        search_memory_records,
        search_memory,
        store_memory,
    )

__all__ = [
    "LocalVectorMemory",
    "clear_memory",
    "search_memory_records",
    "search_memory",
    "store_memory",
]
