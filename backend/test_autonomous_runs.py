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


def test_autonomous_step_supports_planning_and_knowledge(
    monkeypatch
):
    monkeypatch.setattr(
        autonomous_runs,
        "build_project_brain",
        lambda limit: {
            "summary": {
                "total_nodes": limit
            }
        }
    )
    monkeypatch.setattr(
        autonomous_runs,
        "search_sources",
        lambda objective, limit=8: [
            {
                "name": objective,
                "limit": limit
            }
        ]
    )
    monkeypatch.setattr(
        autonomous_runs,
        "source_stats",
        lambda: {
            "indexed_sources": 1
        }
    )

    planning = autonomous_runs.execute_agent_step(
        "Plan the release",
        {
            "agent": "planning",
            "route": "planning",
            "objective": "Create a plan"
        }
    )
    knowledge = autonomous_runs.execute_agent_step(
        "Recall project memory",
        {
            "agent": "memory",
            "route": "knowledge",
            "objective": "Retrieve memory"
        }
    )

    assert planning["output"]["tasks"]
    assert knowledge["output"]["brain"]["summary"]["total_nodes"] == 8
    assert knowledge["output"]["sources"]


def test_autonomous_run_replans_until_goal_review_passes(
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
        "route_objective",
        lambda objective: {
            "primary_route": "code",
            "tasks": [
                {
                    "agent": "Forge",
                    "route": "code",
                    "objective": objective
                }
            ]
        }
    )

    def fake_step(
        objective,
        step
    ):
        return {
            "agent": step["agent"],
            "route": step["route"],
            "objective": step["objective"],
            "round": step["round"],
            "status": "completed",
            "output": {
                "edits": [
                    "backend/main.py"
                ],
                "commit_ready": step["round"] > 1
            }
        }

    monkeypatch.setattr(
        autonomous_runs,
        "_execute_step",
        fake_step
    )

    run = autonomous_runs.create_run(
        "Repair and verify the backend",
        max_rounds=2
    )
    completed = autonomous_runs.execute_run(
        run["id"]
    )

    assert completed["round"] == 2
    assert completed["goal_satisfied"] is True
    assert len(
        completed["reviews"]
    ) == 2
