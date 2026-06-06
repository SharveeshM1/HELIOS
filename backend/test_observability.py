from core import observability
from memory import execution_memory


def test_observability_report_summarizes_tool_events(
    tmp_path,
    monkeypatch
):
    monkeypatch.setattr(
        execution_memory,
        "MEMORY_FILE",
        tmp_path / "execution_history.json"
    )
    monkeypatch.setattr(
        observability,
        "get_execution_events",
        execution_memory.get_execution_events
    )
    monkeypatch.setattr(
        observability,
        "execution_stats",
        execution_memory.execution_stats
    )

    execution_memory.record_execution_event(
        "Tool success: read_file",
        "success",
        tool="read_file",
        duration_ms=10,
        trace_id="trace-a"
    )
    execution_memory.record_execution_event(
        "Tool failed: run_command",
        "failed",
        tool="run_command",
        duration_ms=40,
        attempt=2,
        trace_id="trace-a"
    )

    report = observability.build_observability_report()

    assert report["window"]["completed_events"] == 2
    assert report["rates"]["failure_rate"] == 0.5
    assert report["tool_counts"]["run_command"] == 1
    assert report["slow_tools"][0]["tool"] == "run_command"
    assert report["traces"][0]["trace_id"] == "trace-a"
    assert report["traces"][0]["attempts"] == 2
    assert report["traces"][0]["needs_attention"] is True
