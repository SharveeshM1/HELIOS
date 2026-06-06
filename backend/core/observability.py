from collections import Counter
from collections import defaultdict
from typing import Dict
from typing import List

from memory.execution_memory import execution_stats
from memory.execution_memory import get_execution_events


def _duration(
    event
):
    value = event.get(
        "duration_ms"
    )

    return value if isinstance(
        value,
        (
            int,
            float
        )
    ) else None


def _percentile(
    values,
    percentile: float
):
    if not values:
        return 0
    ordered = sorted(
        values
    )
    index = min(
        len(
            ordered
        )
        - 1,
        max(
            0,
            round(
                (
                    len(
                        ordered
                    )
                    - 1
                )
                * percentile
            )
        )
    )
    return round(
        ordered[
            index
        ],
        2
    )


def build_observability_report(
    limit: int = 100
) -> Dict:
    events = get_execution_events(
        limit=limit,
        event_type="tool_event"
    )
    completed = [
        event
        for event in events
        if event.get(
            "status"
        )
        in {
            "success",
            "failed",
            "blocked"
        }
    ]
    durations = [
        _duration(
            event
        )
        for event in completed
        if _duration(
            event
        )
        is not None
    ]
    failed = [
        event
        for event in completed
        if event.get(
            "status"
        )
        == "failed"
    ]
    blocked = [
        event
        for event in completed
        if event.get(
            "status"
        )
        == "blocked"
    ]
    tool_counts = Counter(
        event.get(
            "tool",
            "unknown"
        )
        for event in completed
    )
    status_counts = Counter(
        event.get(
            "status",
            "unknown"
        )
        for event in completed
    )
    duration_by_tool = defaultdict(
        list
    )
    trace_groups = defaultdict(
        list
    )

    for event in completed:
        duration = _duration(
            event
        )

        if duration is not None:
            duration_by_tool[
                event.get(
                    "tool",
                    "unknown"
                )
            ].append(
                duration
            )
        trace_groups[
            event.get(
                "trace_id"
            )
            or (
                event.get(
                    "metadata"
                )
                or {}
            ).get(
                "trace_id"
            )
            or event.get(
                "parent_id"
            )
            or event.get(
                "id",
                "unscoped"
            )
        ].append(
            event
        )

    slow_tools = sorted(
        [
            {
                "tool": tool,
                "average_duration_ms": round(
                    sum(
                        values
                    )
                    / len(
                        values
                    ),
                    2
                ),
                "max_duration_ms": max(
                    values
                ),
                "samples": len(
                    values
                )
            }
            for tool, values in duration_by_tool.items()
            if values
        ],
        key=lambda item: item["average_duration_ms"],
        reverse=True
    )[:5]

    total_completed = len(
        completed
    )
    failure_rate = round(
        (
            len(
                failed
            )
            + len(
                blocked
            )
        )
        / total_completed,
        2
    ) if total_completed else 0

    recommendations: List[str] = []

    if failure_rate >= 0.25:
        recommendations.append(
            "Review failed and blocked tool calls before allowing longer autonomous runs."
        )

    if slow_tools:
        recommendations.append(
            f"Watch {slow_tools[0]['tool']} latency; it has the highest average duration."
        )

    if not recommendations:
        recommendations.append(
            "Execution health is stable; keep collecting ledger events for deeper trends."
        )

    return {
        "stats": execution_stats(),
        "window": {
            "events_analyzed": len(
                events
            ),
            "completed_events": total_completed
        },
        "rates": {
            "failure_rate": failure_rate,
            "average_duration_ms": round(
                sum(
                    durations
                )
                / len(
                    durations
                ),
                2
            ) if durations else 0,
            "max_duration_ms": max(
                durations
            ) if durations else 0
        },
        "latency_percentiles": {
            "p50_ms": _percentile(
                durations,
                0.50
            ),
            "p95_ms": _percentile(
                durations,
                0.95
            ),
            "p99_ms": _percentile(
                durations,
                0.99
            )
        },
        "traces": [
            {
                "trace_id": trace_id,
                "events": len(
                    trace_events
                ),
                "failed": sum(
                    1
                    for event in trace_events
                    if event.get(
                        "status"
                    )
                    in {
                        "failed",
                        "blocked"
                    }
                ),
                "duration_ms": round(
                    sum(
                        _duration(
                            event
                        )
                        or 0
                        for event in trace_events
                    ),
                    2
                ),
                "attempts": max(
                    [
                        int(
                            event.get(
                                "attempt",
                                1
                            )
                            or 1
                        )
                        for event in trace_events
                    ]
                    or [
                        1
                    ]
                ),
                "needs_attention": any(
                    event.get(
                        "status"
                    )
                    in {
                        "failed",
                        "blocked"
                    }
                    for event in trace_events
                ),
                "tools": sorted(
                    {
                        str(
                            event.get(
                                "tool",
                                "unknown"
                            )
                        )
                        for event in trace_events
                    }
                )
            }
            for trace_id, trace_events in list(
                trace_groups.items()
            )[
                -20:
            ]
        ],
        "tool_counts": dict(
            tool_counts
        ),
        "status_counts": dict(
            status_counts
        ),
        "slow_tools": slow_tools,
        "recent_failures": failed[-5:]
        + blocked[-5:],
        "recommendations": recommendations
    }
