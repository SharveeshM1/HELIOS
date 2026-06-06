from core import mission_scheduler


def test_schedule_next_occurrence_requeues_recurring_missions(monkeypatch):
    captured = {}

    def fake_schedule_mission(**kwargs):
        captured.update(kwargs)
        return {"id": "next-run", **kwargs}

    monkeypatch.setattr(mission_scheduler, "schedule_mission", fake_schedule_mission)

    mission = {
        "title": "Recurring sync",
        "agent": "Orion",
        "module": "planning",
        "detail": "Run every 15 minutes.",
        "recurrence_minutes": 15,
    }

    result = mission_scheduler.schedule_next_occurrence(mission)

    assert result["id"] == "next-run"
    assert captured["title"] == "Recurring sync"
    assert captured["recurrence_minutes"] == 15
    assert captured["scheduled_at"] > mission_scheduler.time.time()


def test_scheduled_mission_executes_workflow(
    monkeypatch
):
    monkeypatch.setattr(
        mission_scheduler,
        "create_mission",
        lambda **kwargs: {
            "mission": {
                "id": "mission-1",
                **kwargs
            }
        }
    )
    monkeypatch.setattr(
        mission_scheduler,
        "run_mission_workflow",
        lambda mission: {
            "artifact": {
                "summary": "Workflow ran."
            },
            "task": {
                "id": "task-1"
            }
        }
    )
    captured = {}

    def advance(
        mission_id,
        stage,
        **kwargs
    ):
        captured.update(
            {
                "mission_id": mission_id,
                "stage": stage,
                **kwargs
            }
        )
        return {
            "mission": {
                "id": mission_id,
                "status": "executed"
            }
        }

    monkeypatch.setattr(
        mission_scheduler,
        "advance_mission",
        advance
    )

    result = mission_scheduler.execute_scheduled_mission(
        {
            "title": "Scheduled work",
            "agent": "Orion",
            "module": "planning",
            "detail": "Run later."
        }
    )

    assert captured["stage"] == "Executed"
    assert captured["artifact"]["summary"] == "Workflow ran."
    assert result["mission"]["status"] == "executed"
