from core import runtime_store
from core.autonomous_worker import execute_job


def test_worker_job_can_be_claimed_and_completed(tmp_path, monkeypatch):
    monkeypatch.setattr(
        runtime_store,
        "SQLITE_PATH",
        tmp_path / "worker.db"
    )
    job = runtime_store.enqueue_job(
        "unknown",
        {
            "value": 1
        }
    )
    claimed = runtime_store.claim_job(
        "worker-1",
        30
    )

    assert claimed["id"] == job["id"]
    assert claimed["status"] == "running"
    assert claimed["attempts"] == 1

    completed = runtime_store.complete_job(
        job["id"],
        "worker-1",
        result={
            "ok": True
        }
    )
    assert completed["status"] == "completed"
    assert completed["result"] == {
        "ok": True
    }


def test_worker_rejects_unknown_job_kind():
    try:
        execute_job(
            {
                "kind": "unknown",
                "payload": {}
            }
        )
    except ValueError as error:
        assert "Unsupported worker job kind" in str(
            error
        )
    else:
        raise AssertionError(
            "Unknown worker job kind should fail."
        )
