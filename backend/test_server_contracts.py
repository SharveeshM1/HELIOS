from fastapi.testclient import TestClient

import backend.server as server
from backend.server import app
from core import autonomous_runs
from core import mission_ledger
from core import source_library
from memory import execution_memory


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
    assert "storage" in payload
    assert "security" in payload
    assert response.headers.get("x-content-type-options") == "nosniff"


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


def test_api_key_gate_blocks_private_routes(
    monkeypatch
):

    monkeypatch.setattr(
        server,
        "API_KEY",
        "secret-test-key"
    )
    monkeypatch.setattr(
        server,
        "RATE_BUCKETS",
        {}
    )

    blocked = client.post(
        "/chat",
        json={
            "message": "hello",
            "module": "dashboard",
            "agent": "HELIOS",
            "attachments": []
        }
    )

    allowed = client.post(
        "/chat",
        headers={
            "x-helios-api-key": "secret-test-key"
        },
        json={
            "message": "hello",
            "module": "unknown",
            "agent": "HELIOS",
            "attachments": []
        }
    )

    assert blocked.status_code == 401
    assert allowed.status_code == 400


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


def test_source_intelligence_endpoint_returns_citations(
    tmp_path,
    monkeypatch
):

    monkeypatch.setattr(
        source_library,
        "SOURCE_FILE",
        tmp_path / "source_library.json"
    )

    source_library.upsert_source(
        "retrieval.md",
        "MD",
        "1 KB",
        "Source intelligence cites retrieval evidence for research answers.",
        "project"
    )

    response = client.get(
        "/sources/intelligence",
        params={
            "q": "source intelligence retrieval",
            "limit": 5
        }
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["citations"]
    assert payload["claims"][0]["citations"]
    assert "[S1]" in payload["grounded_answer"]
    assert payload["coverage"]["grounded"] is True


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


def test_autonomous_run_endpoint_exposes_durable_run(
    tmp_path,
    monkeypatch
):

    monkeypatch.setattr(
        autonomous_runs,
        "AUTONOMOUS_RUNS_FILE",
        tmp_path / "autonomous_runs.json"
    )
    monkeypatch.setattr(
        server,
        "create_run",
        autonomous_runs.create_run
    )
    monkeypatch.setattr(
        server,
        "execute_run",
        lambda run_id: autonomous_runs.get_run(
            run_id
        )
    )

    response = client.post(
        "/autonomy/runs",
        json={
            "objective": "Research citations"
        }
    )

    assert response.status_code == 200

    run = response.json()["run"]
    assert run["status"] == "queued"
    assert run["plan"]["tasks"]


def test_tools_endpoint_lists_registered_tools():

    response = client.get(
        "/tools"
    )

    assert response.status_code == 200

    payload = response.json()

    tool_names = {
        tool["name"]
        for tool in payload["tools"]
    }

    assert "read_file" in tool_names
    assert "execute_python" in tool_names
    assert "stats" in payload


def test_git_commit_endpoint_returns_preview(
    monkeypatch
):

    monkeypatch.setattr(
        server,
        "commit_staged_changes",
        lambda message, confirm=False: {
            "status": "preview",
            "reason": "Set confirm=true to commit staged files.",
            "message": message,
            "git": {
                "staged": [
                    "M  backend/main.py"
                ]
            }
        }
    )

    response = client.post(
        "/git/commit",
        json={
            "message": "Preview commit",
            "confirm": False
        }
    )

    assert response.status_code == 200
    assert response.json()["status"] == "preview"


def test_project_brain_endpoint_exposes_graph_contract():

    response = client.get(
        "/project/brain",
        params={
            "limit": 5
        }
    )

    assert response.status_code == 200

    payload = response.json()

    assert "nodes" in payload
    assert "links" in payload
    assert "stats" in payload
    assert "summary" in payload
    assert any(
        node["id"] == "brain"
        for node in payload["nodes"]
    )
    assert payload["summary"]["total_nodes"] == len(
        payload["nodes"]
    )


def test_observability_endpoint_exposes_metrics_contract():

    response = client.get(
        "/observability",
        params={
            "limit": 20
        }
    )

    assert response.status_code == 200

    payload = response.json()

    assert "stats" in payload
    assert "rates" in payload
    assert "tool_counts" in payload
    assert "recommendations" in payload


def test_voice_status_reports_configuration():

    response = client.get(
        "/voice/status"
    )

    assert response.status_code == 200

    payload = response.json()

    assert "realtime_available" in payload
    assert payload["model"]
    assert payload["voice"]


def test_readiness_reports_missing_production_requirements(
    monkeypatch
):

    monkeypatch.setattr(
        server,
        "STORAGE_BACKEND",
        "json"
    )
    monkeypatch.setattr(
        server,
        "AUTH_SECRET",
        ""
    )
    monkeypatch.delenv(
        "HELIOS_ADMIN_PASSWORD",
        raising=False
    )

    response = client.get(
        "/ready"
    )

    assert response.status_code == 503
    assert response.json()["ready"] is False


def test_realtime_session_forwards_valid_offer(
    monkeypatch
):

    monkeypatch.setenv(
        "OPENAI_API_KEY",
        "test-key"
    )
    captured = {}

    class FakeResponse:
        status_code = 200
        text = "v=0\nanswer"

    class FakeClient:
        def __init__(
            self,
            timeout
        ):
            captured["timeout"] = timeout

        async def __aenter__(
            self
        ):
            return self

        async def __aexit__(
            self,
            exc_type,
            exc,
            traceback
        ):
            return False

        async def post(
            self,
            url,
            headers,
            files
        ):
            captured["url"] = url
            captured["headers"] = headers
            captured["files"] = files
            return FakeResponse()

    monkeypatch.setattr(
        server.httpx,
        "AsyncClient",
        FakeClient
    )

    response = client.post(
        "/realtime/session",
        content="v=0\nfake-offer",
        headers={
            "Content-Type": "application/sdp"
        }
    )

    assert response.status_code == 200
    assert response.text == "v=0\nanswer"
    assert captured["url"] == "https://api.openai.com/v1/realtime/calls"
    assert captured["headers"]["Authorization"] == "Bearer test-key"
    assert server.OPENAI_REALTIME_VOICE in captured["files"]["session"][1]


def test_realtime_session_rejects_missing_key(
    monkeypatch
):

    monkeypatch.setenv(
        "OPENAI_API_KEY",
        ""
    )

    response = client.post(
        "/realtime/session",
        content="v=0\nfake-offer",
        headers={
            "Content-Type": "application/sdp"
        }
    )

    assert response.status_code == 501


def test_execute_tool_endpoint_records_ledger_events(
    tmp_path,
    monkeypatch
):

    monkeypatch.setattr(
        execution_memory,
        "MEMORY_FILE",
        tmp_path / "execution_history.json"
    )

    target_file = tmp_path / "tool-target.txt"
    target_file.write_text(
        "HELIOS tool ledger contract.",
        encoding="utf-8"
    )

    response = client.post(
        "/tools/execute",
        json={
            "tool": "read_file",
            "args": [
                str(
                    target_file
                )
            ],
            "module": "dashboard"
        }
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["tool"] == "read_file"
    assert payload["status"] == "success"
    assert payload["result"] == "HELIOS tool ledger contract."
    assert [
        event["status"]
        for event in payload["events"]
    ] == [
        "running",
        "success"
    ]
    assert payload["stats"]["successful_tools"] == 1

    ledger = client.get(
        "/execution/events",
        params={
            "event_type": "tool_event"
        }
    ).json()

    assert ledger["events"][-1]["tool"] == "read_file"
    assert ledger["events"][-1]["duration_ms"] >= 0


def test_execute_tool_endpoint_blocks_unknown_tools(
    tmp_path,
    monkeypatch
):

    monkeypatch.setattr(
        execution_memory,
        "MEMORY_FILE",
        tmp_path / "execution_history.json"
    )

    response = client.post(
        "/tools/execute",
        json={
            "tool": "missing_tool",
            "args": [],
            "module": "dashboard"
        }
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["status"] == "failed"
    assert "Tool not found" in payload["error"]
    assert payload["events"][-1]["status"] == "blocked"


def test_execute_tool_endpoint_supports_agent_tool_access(
    tmp_path,
    monkeypatch
):

    monkeypatch.setattr(
        execution_memory,
        "MEMORY_FILE",
        tmp_path / "execution_history.json"
    )

    response = client.post(
        "/tools/execute",
        json={
            "tool": "execute_python",
            "agent": "code",
            "args": [
                "result = 7 * 6"
            ],
            "module": "code"
        }
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["status"] == "success"
    assert payload["result"]["success"] is True
    assert payload["result"]["locals"]["result"] == 42
    assert payload["events"][-1]["actor"] == "Code Agent"


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
    monkeypatch.setattr(
        execution_memory,
        "MEMORY_FILE",
        tmp_path / "execution_history.json"
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
    monkeypatch.setattr(
        execution_memory,
        "MEMORY_FILE",
        tmp_path / "execution_history.json"
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
