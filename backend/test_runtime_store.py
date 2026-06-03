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
