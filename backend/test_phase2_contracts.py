from types import SimpleNamespace

from core import intent_router
from core import observability
from core import plugin_loader
from core import swarm_runs


def test_model_assisted_planning_refines_valid_routes(
    monkeypatch
):
    monkeypatch.setattr(
        intent_router,
        "generate_ai_response",
        lambda prompt: '{"primary_route":"code","routes":["code","analytics"],"reason":"Implementation first."}'
    )

    plan = intent_router.model_assisted_route_objective(
        "Improve backend performance",
        enabled=True
    )

    assert plan["model_assisted"] is True
    assert plan["planning_source"] == "model_assisted"
    assert [
        task["route"]
        for task in plan["tasks"]
    ] == [
        "code",
        "analytics"
    ]


def test_observability_report_groups_traces_and_percentiles(
    monkeypatch
):
    monkeypatch.setattr(
        observability,
        "get_execution_events",
        lambda limit=100, event_type="tool_event": [
            {
                "id": "event-1",
                "parent_id": "trace-1",
                "tool": "read_file",
                "status": "success",
                "duration_ms": 10
            },
            {
                "id": "event-2",
                "parent_id": "trace-1",
                "tool": "run_command",
                "status": "failed",
                "duration_ms": 90
            }
        ]
    )
    monkeypatch.setattr(
        observability,
        "execution_stats",
        lambda: {}
    )

    report = observability.build_observability_report()

    assert report["latency_percentiles"]["p95_ms"] == 90
    assert report["traces"][0]["trace_id"] == "trace-1"
    assert report["traces"][0]["failed"] == 1


def test_signed_plugin_catalog_and_uninstall(
    tmp_path,
    monkeypatch
):
    monkeypatch.setattr(
        plugin_loader,
        "plugin_directory",
        lambda: tmp_path
    )
    monkeypatch.setenv(
        "HELIOS_PLUGIN_SIGNING_KEY",
        "test-signing-key"
    )

    plugin_loader.save_plugin_code(
        "sample",
        "def register_plugin(registry):\n    registry['sample_tool'] = lambda: 'ready'\n",
        version="2.0.0",
        description="Signed sample"
    )
    catalog = plugin_loader.list_plugin_catalog()

    assert catalog[0]["verified"] is True
    assert catalog[0]["version"] == "2.0.0"
    assert catalog[0]["isolation"] == "subprocess-no-runtime-dependencies"
    assert plugin_loader.load_plugins() == 1
    assert plugin_loader.TOOL_REGISTRY["sample_tool"]() == "ready"
    assert plugin_loader.uninstall_plugin(
        "sample"
    ) == "sample.py"
    assert plugin_loader.list_plugin_catalog() == []


def test_isolated_swarm_run_queues_two_worker_rounds(
    monkeypatch
):
    stored = []
    jobs = {}

    monkeypatch.setattr(
        swarm_runs,
        "load_swarm_runs",
        lambda: stored
    )
    monkeypatch.setattr(
        swarm_runs,
        "save_swarm_runs",
        lambda runs: stored.extend(
            runs[
                len(
                    stored
                ):
            ]
        )
    )

    def enqueue(
        kind,
        payload
    ):
        job = {
            "id": f"job-{len(jobs) + 1}",
            "kind": kind,
            "payload": payload,
            "status": "completed",
            "result": {
                "agent": payload["agent"],
                "status": "completed",
                "output": f"{payload['agent']} proposal",
                "duration": 0.1
            }
        }
        jobs[
            job[
                "id"
            ]
        ] = job
        return job

    monkeypatch.setattr(
        swarm_runs,
        "enqueue_job",
        enqueue
    )
    monkeypatch.setattr(
        swarm_runs,
        "get_job",
        lambda job_id: jobs.get(
            job_id
        )
    )

    run = swarm_runs.create_swarm_run(
        "Debate the release"
    )
    second_round = swarm_runs.reconcile_swarm_run(
        run[
            "id"
        ]
    )
    completed = swarm_runs.reconcile_swarm_run(
        second_round[
            "id"
        ]
    )

    assert second_round["round"] == 2
    assert second_round["debate_state"]["phase"] == "critique_revision"
    assert completed["status"] == "completed"
    assert completed["debate_protocol"]["consensus_required"] is True
    assert completed["debate_state"]["phase"] == "consensus"
    assert len(
        completed["rounds"]
    ) == 2
