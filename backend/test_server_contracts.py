from fastapi.testclient import TestClient

from backend.server import app


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


def test_event_stream_sends_initial_ledger_event():

    with client.websocket_connect(
        "/events"
    ) as websocket:

        payload = websocket.receive_json()

    assert payload["label"] == "Run ledger connected"
    assert payload["status"] == "live"
