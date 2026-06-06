from core import agent_memory


def test_agent_memory_is_durable_and_scoped(
    monkeypatch
):
    documents = {}
    vectors = []

    monkeypatch.setattr(
        agent_memory,
        "load_document",
        lambda key, default=None: documents.get(
            key,
            default
        )
    )
    monkeypatch.setattr(
        agent_memory,
        "save_document",
        lambda key, value: documents.update(
            {
                key: value
            }
        ) or True
    )
    monkeypatch.setattr(
        agent_memory,
        "store_memory",
        lambda key, text, metadata=None: vectors.append(
            {
                "key": key,
                "text": text,
                "metadata": metadata or {}
            }
        )
    )
    monkeypatch.setattr(
        agent_memory,
        "search_memory_records",
        lambda query, top_k=5: vectors
    )

    agent_memory.remember_agent_result(
        "Athena",
        "Review citations",
        "The research answer is grounded."
    )
    agent_memory.remember_agent_result(
        "Forge",
        "Repair tests",
        "The code workflow is commit ready."
    )

    athena = agent_memory.search_agent_memory(
        "Athena",
        "citations"
    )

    assert len(
        documents["agent_memory:athena"]
    ) == 1
    assert athena
    assert all(
        item["metadata"]["agent"] == "athena"
        for item in athena
    )

