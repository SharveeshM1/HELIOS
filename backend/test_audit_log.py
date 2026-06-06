from core import audit_log


def test_audit_log_builds_verifiable_hash_chain(
    monkeypatch
):
    stored = []

    monkeypatch.setattr(
        audit_log,
        "load_document",
        lambda name, fallback: list(
            stored
        )
    )
    monkeypatch.setattr(
        audit_log,
        "save_document",
        lambda name, payload: stored.extend(
            payload[len(stored):]
        )
        or True
    )

    first = audit_log.record_audit_event(
        "POST /missions",
        actor="admin"
    )
    second = audit_log.record_audit_event(
        "POST /git/commit",
        actor="admin"
    )

    assert second["previous_hash"] == first["hash"]
    assert audit_log.verify_audit_chain()["valid"] is True
