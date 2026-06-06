from core import mission_ledger


def test_mission_ledger_prefers_durable_runtime_document(
    monkeypatch
):
    stored = [
        {
            "id": "mission_1",
            "mission_id": "mission_1",
            "stage": "Created",
            "title": "Durable mission"
        }
    ]
    saved = {}

    monkeypatch.setattr(
        mission_ledger,
        "load_document",
        lambda key, default=None: stored
        if key == "mission_ledger"
        else default
    )
    monkeypatch.setattr(
        mission_ledger,
        "save_document",
        lambda key, value: saved.update(
            {
                key: value
            }
        ) or True
    )
    monkeypatch.setattr(
        mission_ledger,
        "_atomic_write",
        lambda *args: (_ for _ in ()).throw(
            AssertionError(
                "File fallback should not run."
            )
        )
    )

    assert mission_ledger.load_mission_events() == stored
    mission_ledger.save_mission_events(
        stored
    )
    assert saved["mission_ledger"] == stored


def test_mission_recovery_reuses_latest_artifact(
    tmp_path,
    monkeypatch
):
    monkeypatch.setattr(
        mission_ledger,
        "MISSION_LEDGER_FILE",
        tmp_path / "missions.json"
    )
    created = mission_ledger.create_mission(
        "Recover this mission",
        module="code",
        agent="Vega"
    )
    mission_id = created["mission"]["id"]
    mission_ledger.advance_mission(
        mission_id,
        "Executed",
        artifact={
            "kind": "code",
            "summary": "Checkpoint"
        }
    )

    recovered = mission_ledger.recover_mission(
        mission_id
    )

    assert recovered["mission"]["stage"] == "Assigned"
    assert recovered["checkpoint"]["summary"] == "Checkpoint"
