from core import autonomous_runs


def test_autonomous_run_persists_and_completes(
    tmp_path,
    monkeypatch
):
    monkeypatch.setattr(
        autonomous_runs,
        "AUTONOMOUS_RUNS_FILE",
        tmp_path / "autonomous_runs.json"
    )
    monkeypatch.setattr(
        autonomous_runs,
        "_execute_step",
        lambda objective, step: {
            "agent": step["agent"],
            "route": step["route"],
            "objective": step["objective"],
            "status": "completed",
            "output": {
                "ok": True
            }
        }
    )

    run = autonomous_runs.create_run(
        "Research citations and analyze metrics"
    )
    completed = autonomous_runs.execute_run(
        run["id"]
    )

    assert completed["status"] == "completed"
    assert completed["steps"]
    assert autonomous_runs.get_run(
        run["id"]
    )["status"] == "completed"


def test_autonomous_run_can_be_cancelled_and_resumed(
    tmp_path,
    monkeypatch
):
    monkeypatch.setattr(
        autonomous_runs,
        "AUTONOMOUS_RUNS_FILE",
        tmp_path / "autonomous_runs.json"
    )
    monkeypatch.setattr(
        autonomous_runs,
        "_execute_step",
        lambda objective, step: {
            "agent": step["agent"],
            "route": step["route"],
            "objective": step["objective"],
            "status": "completed",
            "output": {}
        }
    )

    run = autonomous_runs.create_run(
        "Fix backend tests"
    )
    cancelled = autonomous_runs.cancel_run(
        run["id"]
    )

    assert cancelled["cancel_requested"] is True

    resumed = autonomous_runs.resume_run(
        run["id"]
    )

    assert resumed["status"] == "completed"
