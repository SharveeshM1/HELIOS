from fastapi.testclient import TestClient

from backend.server import app
from core import mission_ledger
from core import source_library


client = TestClient(
    app
)


def test_health_exposes_runtime_contract():

    response = client.get(
        "/health"
    )

    assert response.status_code == 200
    assert response.headers.get("x-request-id")

    payload = response.json()

    assert payload["backend"] == "online"
    assert payload["version"]
    assert "uptime_seconds" in payload
    assert "request_count" in payload
    assert "sources" in payload


def test_chat_rejects_unknown_module():

    response = client.post(
        "/chat",
        json={
            "message": "hello",
            "module": "unknown",
            "agent": "HELIOS",
            "attachments": []
        }
    )

    assert response.status_code == 400
    assert "Unsupported HELIOS module" in response.json()["detail"]


def test_source_search_endpoint_limits_result_count():

    response = client.get(
        "/sources/search",
        params={
            "q": "memory",
            "limit": 500
        }
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["query"] == "memory"
    assert len(payload["sources"]) <= 25


def test_mission_events_endpoint_exposes_timeline_contract(
    tmp_path,
    monkeypatch
):

    monkeypatch.setattr(
        mission_ledger,
        "MISSION_LEDGER_FILE",
        tmp_path / "mission_ledger.json"
    )

    response = client.get(
        "/missions/events",
        params={
            "limit": 5
        }
    )

    assert response.status_code == 200

    payload = response.json()

    assert "events" in payload
    assert "missions" in payload
    assert "stats" in payload
    assert "agents" in payload
    assert len(payload["events"]) <= 5


def test_create_mission_records_created_and_assigned_events(
    tmp_path,
    monkeypatch
):

    monkeypatch.setattr(
        mission_ledger,
        "MISSION_LEDGER_FILE",
        tmp_path / "mission_ledger.json"
    )

    response = client.post(
        "/missions",
        json={
            "title": "Build a premium mission surface",
            "module": "planning",
            "agent": "Orion",
            "detail": "Contract test mission."
        }
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["mission"]["title"] == "Build a premium mission surface"
    assert payload["mission"]["status"] == "assigned"
    assert [
        event["stage"]
        for event in payload["events"]
    ] == [
        "Created",
        "Assigned"
    ]
    assert payload["agents"]["Orion"]["state"] == "Thinking"


def test_advance_mission_records_operational_stage(
    tmp_path,
    monkeypatch
):

    monkeypatch.setattr(
        mission_ledger,
        "MISSION_LEDGER_FILE",
        tmp_path / "mission_ledger.json"
    )

    created = client.post(
        "/missions",
        json={
            "title": "Execute a mission",
            "module": "workflow",
            "agent": "Vega"
        }
    ).json()

    response = client.post(
        f"/missions/{created['mission']['id']}/advance",
        json={
            "stage": "Executed",
            "detail": "Execution stage completed."
        }
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["event"]["stage"] == "Executed"
    assert payload["event"]["mission_id"] == created["mission"]["id"]
    assert payload["mission"]["status"] == "executed"
    assert payload["agents"]["Vega"]["state"] == "Building"


def test_run_research_mission_returns_evidence_artifact(
    tmp_path,
    monkeypatch
):

    monkeypatch.setattr(
        mission_ledger,
        "MISSION_LEDGER_FILE",
        tmp_path / "mission_ledger.json"
    )
    monkeypatch.setattr(
        source_library,
        "SOURCE_FILE",
        tmp_path / "source_library.json"
    )

    source_library.upsert_source(
        "research-note.md",
        "MD",
        "1 KB",
        "Mission workflows should produce evidence artifacts from indexed sources.",
        "project"
    )

    created = client.post(
        "/missions",
        json={
            "title": "mission workflows evidence",
            "module": "research",
            "agent": "Nova"
        }
    ).json()

    response = client.post(
        f"/missions/{created['mission']['id']}/run"
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["event"]["stage"] == "Executed"
    assert payload["artifact"]["kind"] == "research"
    assert payload["artifact"]["evidence"]
    assert payload["task"]["status"] == "completed"
    assert payload["agents"]["Nova"]["state"] == "Researching"


def test_run_code_mission_returns_project_file_signals(
    tmp_path,
    monkeypatch
):

    monkeypatch.setattr(
        mission_ledger,
        "MISSION_LEDGER_FILE",
        tmp_path / "mission_ledger.json"
    )

    created = client.post(
        "/missions",
        json={
            "title": "mission workflows backend server",
            "module": "code",
            "agent": "Vega"
        }
    ).json()

    response = client.post(
        f"/missions/{created['mission']['id']}/run"
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["artifact"]["kind"] == "code"
    assert payload["artifact"]["file_signals"]
    assert payload["artifact"]["target_files"]
    assert payload["task"]["result"]["kind"] == "code"
    assert payload["task"]["status"] == "completed"


def test_run_planning_mission_returns_routed_plan(
    tmp_path,
    monkeypatch
):

    monkeypatch.setattr(
        mission_ledger,
        "MISSION_LEDGER_FILE",
        tmp_path / "mission_ledger.json"
    )

    created = client.post(
        "/missions",
        json={
            "title": "build research analytics workflow",
            "module": "planning",
            "agent": "Orion"
        }
    ).json()

    response = client.post(
        f"/missions/{created['mission']['id']}/run"
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["artifact"]["kind"] == "planning"
    assert payload["artifact"]["plan"]["tasks"]
    assert payload["artifact"]["steps"]
    assert payload["task"]["result"]["plan"]["tasks"]


def test_event_stream_sends_initial_ledger_event():

    with client.websocket_connect(
        "/events"
    ) as websocket:

        payload = websocket.receive_json()

    assert payload["label"] == "Run ledger connected"
    assert payload["status"] == "live"
