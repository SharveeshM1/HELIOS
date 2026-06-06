from core import source_library
import base64
import pytest


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


def test_source_search_uses_semantic_vector_records(
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
        "semantic-note.txt",
        "TXT",
        "1 KB",
        "A production approval gate persists decisions before risky tools execute.",
        "project"
    )

    results = source_library.search_sources(
        "production approval workflow",
        scope="project"
    )

    assert results
    assert results[0]["name"] == "semantic-note.txt"
    assert results[0]["semantic_score"] > 0
    assert results[0]["retrieval"] in {
        "semantic",
        "hybrid"
    }


def test_source_delete_removes_entry_and_updates_stats(
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
        "keep.md",
        "MD",
        "1 KB",
        "Keep this for retrieval.",
        "project"
    )
    removed_source = source_library.upsert_source(
        "remove.md",
        "MD",
        "1 KB",
        "Remove this source.",
        "project"
    )

    removed = source_library.delete_source(removed_source["id"])

    assert removed["name"] == "remove.md"
    assert source_library.source_stats()["total_sources"] == 1
    assert source_library.load_sources()[0]["name"] == "keep.md"


def test_source_reindex_refreshes_source_record(
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

    inserted = source_library.upsert_source(
        "reindex.md",
        "MD",
        "1 KB",
        "Original retrieval note.",
        "project"
    )

    refreshed = source_library.reindex_source(inserted["id"], scope="research")

    assert refreshed["id"] == inserted["id"]
    assert refreshed["scope"] == "research"
    assert refreshed["content"] == "Original retrieval note."
    assert source_library.source_stats()["total_sources"] == 1


def test_pdf_source_requires_valid_base64():
    with pytest.raises(
        ValueError,
        match="valid base64"
    ):
        source_library.upsert_source(
            "broken.pdf",
            "PDF",
            "1 KB",
            "not base64!"
        )


def test_docx_source_routes_binary_content_to_extractor(
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
    monkeypatch.setattr(
        source_library,
        "extract_docx_text",
        lambda content: "Extracted DOCX project knowledge."
    )

    source = source_library.upsert_source(
        "architecture.docx",
        "DOCX",
        "4 KB",
        base64.b64encode(
            b"docx-bytes"
        ).decode(
            "ascii"
        )
    )

    assert source["type"] == "DOCX"
    assert source["content"].startswith(
        "Extracted DOCX"
    )
