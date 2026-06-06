from core.research_grounding import (
    build_grounded_research_artifact
)


def test_grounded_research_artifact_requires_citations_for_claims():
    artifact = build_grounded_research_artifact(
        "vector memory retrieval",
        [
            {
                "id": "src_1",
                "name": "memory.md",
                "scope": "project",
                "snippet": "Vector memory retrieval ranks stored knowledge by semantic similarity.",
                "match_terms": [
                    "vector",
                    "memory",
                    "retrieval"
                ]
            }
        ],
        {
            "total_sources": 1
        }
    )

    assert artifact["citations"][0]["id"] == "S1"
    assert artifact["claims"][0]["citations"] == [
        "S1"
    ]
    assert "[S1]" in artifact["grounded_answer"]
    assert artifact["coverage"]["grounded"] is True
    assert artifact["coverage"]["enforced"] is True
    assert artifact["enforcement"]["policy"] == "cite_or_refuse"


def test_grounded_research_artifact_refuses_unsupported_answer():
    artifact = build_grounded_research_artifact(
        "unindexed quantum roadmap",
        [],
        {
            "total_sources": 0
        }
    )

    assert artifact["citations"] == []
    assert artifact["claims"] == []
    assert "should not make source-backed claims" in artifact["grounded_answer"]
    assert artifact["coverage"]["grounded"] is False
    assert artifact["coverage"]["enforced"] is False


def test_grounded_research_artifact_refuses_thin_partial_coverage():
    artifact = build_grounded_research_artifact(
        "vector memory deployment rollback",
        [
            {
                "id": "src_1",
                "name": "memory.md",
                "scope": "project",
                "snippet": "Vector memory retrieves related context.",
                "match_terms": [
                    "vector"
                ]
            }
        ],
        {
            "total_sources": 1
        }
    )

    assert artifact["coverage"]["grounded"] is True
    assert artifact["coverage"]["enforced"] is False
    assert "coverage is too thin" in artifact["grounded_answer"]
    assert "deployment" in artifact["enforcement"]["unsupported_terms"]


def test_grounded_research_artifact_builds_claim_graph():
    artifact = build_grounded_research_artifact(
        "memory",
        [
            {
                "id": "source-1",
                "name": "Memory Notes",
                "snippet": "Semantic memory retrieves related project context.",
                "match_terms": [
                    "memory"
                ]
            }
        ],
        {
            "indexed_sources": 1
        }
    )

    assert any(
        node["kind"] == "claim"
        for node in artifact["graph"]["nodes"]
    )
    assert any(
        link["label"] == "grounds"
        for link in artifact["graph"]["links"]
    )
