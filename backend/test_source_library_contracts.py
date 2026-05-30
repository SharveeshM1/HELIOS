from core import source_library


def test_source_upsert_uses_stable_fingerprint(
    tmp_path,
    monkeypatch
):

    monkeypatch.setattr(
        source_library,
        "MEMORY_DIR",
        tmp_path
    )
    monkeypatch.setattr(
        source_library,
        "SOURCE_FILE",
        tmp_path / "source_library.json"
    )

    first = source_library.upsert_source(
        "architecture.md",
        "MD",
        "2 KB",
        "HELIOS has source memory and scoped retrieval.",
        "project"
    )
    second = source_library.upsert_source(
        "architecture.md",
        "MD",
        "2 KB",
        "HELIOS has source memory and scoped retrieval.",
        "project"
    )

    assert first["id"] == second["id"]
    assert first["id"].startswith("src_")
    assert source_library.source_stats()["total_sources"] == 1


def test_source_search_returns_scoped_snippets(
    tmp_path,
    monkeypatch
):

    monkeypatch.setattr(
        source_library,
        "MEMORY_DIR",
        tmp_path
    )
    monkeypatch.setattr(
        source_library,
        "SOURCE_FILE",
        tmp_path / "source_library.json"
    )

    source_library.upsert_source(
        "chat-note.txt",
        "TXT",
        "1 KB",
        "Realtime voice belongs only to this chat.",
        "chat"
    )
    source_library.upsert_source(
        "project-note.txt",
        "TXT",
        "1 KB",
        "Source indexing powers project memory retrieval.",
        "project"
    )

    results = source_library.search_sources(
        "source memory retrieval",
        scope="project"
    )

    assert len(results) == 1
    assert results[0]["name"] == "project-note.txt"
    assert "content" not in results[0]
    assert results[0]["snippet"].startswith("Source indexing")
    assert "memory" in results[0]["match_terms"]
