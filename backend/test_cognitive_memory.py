from core import cognitive_engine


def test_cognitive_memory_context_includes_semantic_matches(
    monkeypatch
):
    monkeypatch.setattr(
        cognitive_engine,
        "get_recent_memory",
        lambda memory, limit=6: []
    )
    monkeypatch.setattr(
        cognitive_engine,
        "search_memory",
        lambda memory, query: []
    )
    monkeypatch.setattr(
        cognitive_engine,
        "search_memory_records",
        lambda query, top_k=4: [
            {
                "text": "Semantic project architecture",
                "score": 0.91
            }
        ]
    )

    engine = cognitive_engine.CognitiveEngine()
    context = engine._build_memory_context(
        [],
        "architecture"
    )

    assert "Semantic project architecture" in context
    assert engine.last_trace[-1]["payload"]["semantic_matches"] == 1


def test_cognitive_agent_context_uses_agent_specific_memory(
    monkeypatch
):
    monkeypatch.setattr(
        cognitive_engine,
        "search_agent_memory",
        lambda agent, query, limit=4: [
            {
                "result": f"{agent} remembered {query}"
            }
        ]
    )

    context = cognitive_engine.CognitiveEngine()._agent_memory_context(
        "Forge",
        "verification"
    )

    assert context == "Forge remembered verification"
