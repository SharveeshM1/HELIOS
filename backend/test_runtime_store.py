from core import runtime_store


def test_sqlite_runtime_store_round_trip(
    tmp_path,
    monkeypatch
):
    monkeypatch.setattr(
        runtime_store,
        "STORAGE_BACKEND",
        "sqlite"
    )
    monkeypatch.setattr(
        runtime_store,
        "SQLITE_PATH",
        tmp_path / "runtime.db"
    )

    payload = [
        {
            "id": "1",
            "value": "stored"
        }
    ]

    assert runtime_store.save_document(
        "test",
        payload
    ) is True
    assert runtime_store.load_document(
        "test",
        []
    ) == payload
    assert runtime_store.storage_status()["durable"] is True


def test_json_runtime_store_uses_fallback(
    monkeypatch
):
    monkeypatch.setattr(
        runtime_store,
        "STORAGE_BACKEND",
        "json"
    )

    assert runtime_store.load_document(
        "missing",
        [
            "fallback"
        ]
    ) == [
        "fallback"
    ]
    assert runtime_store.save_document(
        "missing",
        []
    ) is False


def test_postgres_storage_status_is_multi_worker(
    monkeypatch
):
    monkeypatch.setattr(
        runtime_store,
        "STORAGE_BACKEND",
        "postgres"
    )
    monkeypatch.setattr(
        runtime_store,
        "DATABASE_URL",
        "postgresql://example"
    )

    status = runtime_store.storage_status()

    assert status["durable"] is True
    assert status["multi_worker"] is True
    assert status["database_url_configured"] is True


def test_rate_limit_store_blocks_after_limit(
    tmp_path,
    monkeypatch
):
    monkeypatch.setattr(
        runtime_store,
        "STORAGE_BACKEND",
        "sqlite"
    )
    monkeypatch.setattr(
        runtime_store,
        "SQLITE_PATH",
        tmp_path / "runtime.db"
    )

    assert runtime_store.allow_rate_limited_request(
        "client",
        2
    ) is True
    assert runtime_store.allow_rate_limited_request(
        "client",
        2
    ) is True
    assert runtime_store.allow_rate_limited_request(
        "client",
        2
    ) is False


def test_durable_approval_requests_round_trip(
    tmp_path,
    monkeypatch
):
    monkeypatch.setattr(
        runtime_store,
        "STORAGE_BACKEND",
        "sqlite"
    )
    monkeypatch.setattr(
        runtime_store,
        "SQLITE_PATH",
        tmp_path / "runtime.db"
    )

    approval = runtime_store.create_approval_request(
        "create_file",
        {
            "args": [
                "backend/memory/note.txt",
                "hello"
            ]
        },
        actor="admin",
        module="code",
        reason="state changing tool"
    )

    assert approval["status"] == "pending"
    assert approval["payload"]["args"][0] == "backend/memory/note.txt"

    approved = runtime_store.update_approval_request(
        approval["id"],
        "approved",
        approved_by="admin"
    )

    assert approved["status"] == "approved"
    assert runtime_store.list_approval_requests(
        "approved"
    )[0]["id"] == approval["id"]


def test_due_scheduled_missions_are_claimed_once(
    tmp_path,
    monkeypatch
):
    monkeypatch.setattr(
        runtime_store,
        "STORAGE_BACKEND",
        "sqlite"
    )
    monkeypatch.setattr(
        runtime_store,
        "SQLITE_PATH",
        tmp_path / "runtime.db"
    )

    mission = runtime_store.schedule_mission(
        "Run scheduled workflow",
        "Orion",
        "planning",
        100.0,
        recurrence_minutes=15
    )

    first = runtime_store.claim_due_scheduled_missions(
        now=101.0
    )
    second = runtime_store.claim_due_scheduled_missions(
        now=101.0
    )

    assert first[0]["id"] == mission["id"]
    assert first[0]["status"] == "executing"
    assert first[0]["recurrence_minutes"] == 15
    assert second == []
