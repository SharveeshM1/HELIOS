import json
import os
import tempfile
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict
from typing import List

from core.agent_memory import remember_agent_result
from core.code_workflow import run_code_execution_workflow
from core.intent_router import route_objective
from core.intent_router import model_assisted_route_objective
from core.observability import build_observability_report
from core.planning_engine import PlanningEngine
from core.project_brain import build_project_brain
from core.research_grounding import build_grounded_research_artifact
from core.runtime_config import MEMORY_DIR
from core.runtime_store import load_document
from core.runtime_store import save_document
from core.runtime_store import enqueue_job
from core.runtime_store import get_job
from core.source_library import search_sources
from core.source_library import source_stats
from core.swarm_engine import run_swarm_artifact


AUTONOMOUS_RUNS_FILE = MEMORY_DIR / "autonomous_runs.json"
MAX_RUNS = 100
run_lock = threading.Lock()


def _plan_objective(
    objective: str
) -> Dict:
    if os.getenv(
        "HELIOS_MODEL_ASSISTED_PLANNING",
        "false"
    ).strip().lower() in {
        "1",
        "true",
        "yes",
        "on"
    }:
        return model_assisted_route_objective(
            objective,
            enabled=True
        )
    return {
        **route_objective(
            objective
        ),
        "planning_source": "rules",
        "model_assisted": False
    }


def _timestamp() -> str:
    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def _atomic_write(
    path: Path,
    data
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with tempfile.NamedTemporaryFile(
        mode="w",
        delete=False,
        encoding="utf-8",
        dir=str(
            path.parent
        )
    ) as temp_file:
        json.dump(
            data,
            temp_file,
            indent=4,
            ensure_ascii=False
        )
        temp_path = temp_file.name

    os.replace(
        temp_path,
        path
    )


def load_runs() -> List[Dict]:
    with run_lock:
        stored = load_document(
            "autonomous_runs",
            None
        )

        if isinstance(
            stored,
            list
        ):
            return stored

        if not AUTONOMOUS_RUNS_FILE.exists():
            return []

        try:
            with AUTONOMOUS_RUNS_FILE.open(
                "r",
                encoding="utf-8"
            ) as file:
                data = json.load(
                    file
                )

            return data if isinstance(
                data,
                list
            ) else []

        except Exception:
            return []


def save_runs(
    runs: List[Dict]
) -> None:
    with run_lock:
        if save_document(
            "autonomous_runs",
            runs[-MAX_RUNS:]
        ):
            return

        _atomic_write(
            AUTONOMOUS_RUNS_FILE,
            runs[-MAX_RUNS:]
        )


def get_run(
    run_id: str
) -> Dict | None:
    return next(
        (
            run
            for run in load_runs()
            if run.get(
                "id"
            )
            == run_id
        ),
        None
    )


def _update_run(
    run_id: str,
    **changes
) -> Dict:
    runs = load_runs()

    for index, run in enumerate(
        runs
    ):
        if run.get(
            "id"
        ) == run_id:
            runs[index] = {
                **run,
                **changes,
                "updated_at": _timestamp()
            }
            save_runs(
                runs
            )
            return runs[index]

    raise ValueError(
        "Autonomous run not found."
    )


def _append_event(
    run_id: str,
    stage: str,
    status: str,
    detail: str,
    payload=None
) -> Dict:
    run = get_run(
        run_id
    )

    if not run:
        raise ValueError(
            "Autonomous run not found."
        )

    events = [
        *run.get(
            "events",
            []
        ),
        {
            "id": str(
                uuid.uuid4()
            ),
            "stage": stage,
            "status": status,
            "detail": detail,
            "payload": payload,
            "timestamp": _timestamp()
        }
    ]

    return _update_run(
        run_id,
        events=events
    )


def create_run(
    objective: str,
    max_rounds: int = 3
) -> Dict:
    plan = _plan_objective(
        objective
    )
    run = {
        "id": str(
            uuid.uuid4()
        ),
        "objective": str(
            objective
        ),
        "status": "queued",
        "cancel_requested": False,
        "plan": plan,
        "steps": [],
        "events": [],
        "round": 1,
        "max_rounds": max(
            1,
            min(
                int(
                    max_rounds
                ),
                6
            )
        ),
        "reviews": [],
        "execution_contract": {
            "mode": "durable_worker_queue",
            "independent_worker_steps": True,
            "long_running": True,
            "cancel_supported": True,
            "resume_supported": True,
            "max_rounds": max(
                1,
                min(
                    int(
                        max_rounds
                    ),
                    6
                )
            ),
            "approval_gates": [
                "state_changing_tools",
                "git_commit",
                "deploy"
            ]
        },
        "created_at": _timestamp(),
        "updated_at": _timestamp()
    }
    runs = load_runs()
    runs.append(
        run
    )
    save_runs(
        runs
    )
    _append_event(
        run["id"],
        "queued",
        "queued",
        "Autonomous run created with durable worker execution contract.",
        run["execution_contract"]
    )

    return get_run(
        run["id"]
    )


def queue_run(
    run_id: str
) -> Dict:
    run = get_run(
        run_id
    )
    if not run:
        raise ValueError(
            "Autonomous run not found."
        )
    completed_routes = {
        step.get(
            "route"
        )
        for step in run.get(
            "steps",
            []
        )
        if step.get(
            "status"
        )
        == "completed"
        and step.get(
            "round",
            1
        )
        == run.get(
            "round",
            1
        )
    }
    jobs = [
        enqueue_job(
            "autonomous_step",
            {
                "run_id": run_id,
                "objective": run.get(
                    "objective",
                    ""
                ),
                "step": {
                    **step,
                    "round": run.get(
                        "round",
                        1
                    )
                }
            }
        )
        for step in run.get(
            "plan",
            {}
        ).get(
            "tasks",
            []
        )
        if step.get(
            "route"
        )
        not in completed_routes
    ]
    _update_run(
        run_id,
        status="queued",
        worker_job_ids=[
            job["id"]
            for job in jobs
        ],
        worker_jobs=[
            {
                "id": job["id"],
                "kind": job["kind"],
                "status": job["status"],
                "attempts": job.get(
                    "attempts",
                    0
                )
            }
            for job in jobs
        ]
    )
    _append_event(
        run_id,
        "worker",
        "queued",
        "Run queued for a durable autonomous worker.",
        {
            "job_ids": [
                job["id"]
                for job in jobs
            ]
        }
    )
    return get_run(
        run_id
    )


def execute_agent_step(
    objective: str,
    step: Dict
) -> Dict:
    return _execute_step(
        objective,
        step
    )


def reconcile_run(
    run_id: str
) -> Dict | None:
    run = get_run(
        run_id
    )
    if not run:
        return None
    job_ids = run.get(
        "worker_job_ids",
        []
    )
    if not job_ids:
        return run
    jobs = [
        job
        for job_id in job_ids
        if (
            job := get_job(
                job_id
            )
        )
    ]
    completed_steps = [
        job.get(
            "result"
        )
        for job in jobs
        if job.get(
            "status"
        )
        == "completed"
        and isinstance(
            job.get(
                "result"
            ),
            dict
        )
    ]
    historical_steps = [
        step
        for step in run.get(
            "steps",
            []
        )
        if step.get(
            "round",
            1
        )
        != run.get(
            "round",
            1
        )
    ]
    all_steps = [
        *historical_steps,
        *completed_steps
    ]
    status = "running" if any(
        job.get(
            "status"
        )
        == "running"
        for job in jobs
    ) else "failed" if any(
        job.get(
            "status"
        )
        == "failed"
        for job in jobs
    ) else "completed" if jobs and all(
        job.get(
            "status"
        )
        == "completed"
        for job in jobs
    ) else "queued"
    updated = _update_run(
        run_id,
        status=status,
        steps=all_steps,
        worker_jobs=jobs,
        synthesis=_synthesize_steps(
            all_steps
        )
        if completed_steps
        else run.get(
            "synthesis"
        )
    )
    if status != "completed":
        return updated
    review = _review_goal(
        run.get(
            "objective",
            ""
        ),
        completed_steps
    )
    reviews = [
        *run.get(
            "reviews",
            []
        ),
        review
    ]
    updated = _update_run(
        run_id,
        reviews=reviews,
        goal_satisfied=review["satisfied"]
    )
    if review["satisfied"] or run.get(
        "round",
        1
    ) >= run.get(
        "max_rounds",
        3
    ):
        return updated
    next_round = run.get(
        "round",
        1
    ) + 1
    next_plan = _plan_objective(
        f"{run.get('objective', '')} Resolve these remaining gaps: "
        + "; ".join(
            review["gaps"]
        )
    )
    _update_run(
        run_id,
        round=next_round,
        plan=next_plan,
        worker_job_ids=[],
        status="queued"
    )
    _append_event(
        run_id,
        "review",
        "replanning",
        f"Goal review opened autonomous round {next_round}.",
        review
    )
    return queue_run(
        run_id
    )


def cancel_run(
    run_id: str
) -> Dict:
    run = _update_run(
        run_id,
        cancel_requested=True
    )
    _append_event(
        run_id,
        "cancel",
        "requested",
        "Cancellation requested."
    )

    return get_run(
        run_id
    ) or run


def _execute_step(
    objective: str,
    step: Dict
) -> Dict:
    route = step.get(
        "route"
    )

    if route == "code":
        output = run_code_execution_workflow(
            objective
        )

    elif route == "research":
        evidence = search_sources(
            objective,
            limit=8
        )
        output = build_grounded_research_artifact(
            objective,
            evidence,
            source_stats()
        )

    elif route == "analytics":
        output = build_observability_report()

    elif route == "planning":
        output = PlanningEngine().create_plan(
            objective
        )

    elif route == "knowledge":
        output = {
            "brain": build_project_brain(
                8
            ),
            "sources": search_sources(
                objective,
                limit=8
            ),
            "stats": source_stats()
        }

    elif route == "swarm":
        evidence = search_sources(
            objective,
            limit=5
        )
        output = run_swarm_artifact(
            objective,
            web_results="\n".join(
                str(
                    item.get(
                        "snippet",
                        ""
                    )
                )
                for item in evidence
            ),
            conversation_context="Durable autonomous run requested multi-agent consensus."
        )

    elif route == "voice":
        output = {
            "status": "requires_realtime_session",
            "detail": "Voice execution requires a configured realtime provider."
        }

    else:
        output = {
            "status": "skipped",
            "detail": f"Unsupported autonomous route: {route}"
        }

    result = {
        "agent": step.get(
            "agent"
        ),
        "route": route,
        "objective": step.get(
            "objective"
        ),
        "status": "completed",
        "round": step.get(
            "round",
            1
        ),
        "output": output,
        "completed_at": _timestamp()
    }
    remember_agent_result(
        str(
            step.get(
                "agent",
                route or "HELIOS"
            )
        ),
        str(
            step.get(
                "objective",
                objective
            )
        ),
        json.dumps(
            output,
            ensure_ascii=False
        ),
        metadata={
            "source": "autonomous_run",
            "route": route,
            "round": step.get(
                "round",
                1
            )
        }
    )
    return result


def _review_goal(
    objective: str,
    steps: List[Dict]
) -> Dict:
    gaps = []
    if not steps:
        gaps.append(
            "No autonomous steps completed."
        )
    for step in steps:
        output = step.get(
            "output"
        )
        if step.get(
            "status"
        ) != "completed":
            gaps.append(
                f"{step.get('route', 'step')} did not complete."
            )
            continue
        if isinstance(
            output,
            dict
        ):
            if output.get(
                "status"
            ) in {
                "failed",
                "blocked",
                "skipped"
            }:
                gaps.append(
                    f"{step.get('route', 'step')} reported {output.get('status')}."
                )
            if output.get(
                "blockers"
            ):
                gaps.append(
                    f"{step.get('route', 'step')} has unresolved blockers."
                )
            if (
                step.get(
                    "route"
                )
                == "research"
                and not output.get(
                    "coverage",
                    {}
                ).get(
                    "grounded",
                    False
                )
            ):
                gaps.append(
                    "Research output is not grounded in indexed evidence."
                )
            if (
                step.get(
                    "route"
                )
                == "code"
                and output.get(
                    "edits"
                )
                and not output.get(
                    "commit_ready",
                    False
                )
            ):
                gaps.append(
                    "Code changes are not verification-ready."
                )
    return {
        "objective": objective,
        "satisfied": not gaps,
        "gaps": gaps,
        "reviewed_at": _timestamp()
    }


def _synthesize_steps(
    steps: List[Dict]
) -> Dict:
    completed = [
        step
        for step in steps
        if step.get(
            "status"
        )
        == "completed"
    ]
    return {
        "status": "ready"
        if completed
        else "empty",
        "completed_routes": [
            step.get(
                "route"
            )
            for step in completed
        ],
        "agents": [
            step.get(
                "agent"
            )
            for step in completed
        ],
        "summary": (
            f"Completed {len(completed)} autonomous route(s): "
            + ", ".join(
                str(
                    step.get(
                        "route"
                    )
                )
                for step in completed
            )
        )
        if completed
        else "No autonomous steps completed yet."
    }


def execute_run(
    run_id: str
) -> Dict:
    run = get_run(
        run_id
    )

    if not run:
        raise ValueError(
            "Autonomous run not found."
        )

    if run.get(
        "status"
    ) == "completed":
        return run

    _update_run(
        run_id,
        status="running",
        cancel_requested=False
    )
    _append_event(
        run_id,
        "execution",
        "running",
        "Autonomous execution started."
    )

    completed_routes = {
        step.get(
            "route"
        )
        for step in run.get(
            "steps",
            []
        )
        if step.get(
            "status"
        )
        == "completed"
        and step.get(
            "round",
            1
        )
        == run.get(
            "round",
            1
        )
    }

    try:
        for step in run.get(
            "plan",
            {}
        ).get(
            "tasks",
            []
        ):
            current = get_run(
                run_id
            ) or {}

            if current.get(
                "cancel_requested"
            ):
                _update_run(
                    run_id,
                    status="cancelled"
                )
                _append_event(
                    run_id,
                    "execution",
                    "cancelled",
                    "Autonomous run stopped at a cancellation checkpoint."
                )
                return get_run(
                    run_id
                )

            if step.get(
                "route"
            ) in completed_routes:
                continue

            _append_event(
                run_id,
                step.get(
                    "route",
                    "step"
                ),
                "running",
                f"{step.get('agent')} step started.",
                step
            )
            result = _execute_step(
                run.get(
                    "objective",
                    ""
                ),
                {
                    **step,
                    "round": run.get(
                        "round",
                        1
                    )
                }
            )
            current = get_run(
                run_id
            ) or {}
            steps = [
                *current.get(
                    "steps",
                    []
                ),
                result
            ]
            _update_run(
                run_id,
                steps=steps
            )
            _append_event(
                run_id,
                step.get(
                    "route",
                    "step"
                ),
                "completed",
                f"{step.get('agent')} step completed."
            )

        current = get_run(
            run_id
        ) or {}
        steps = current.get(
            "steps",
            []
        )
        current_round_steps = [
            step
            for step in steps
            if step.get(
                "round",
                1
            )
            == run.get(
                "round",
                1
            )
        ]
        review = _review_goal(
            run.get(
                "objective",
                ""
            ),
            current_round_steps
        )
        reviews = [
            *current.get(
                "reviews",
                []
            ),
            review
        ]
        _update_run(
            run_id,
            status="completed",
            synthesis=_synthesize_steps(
                steps
            ),
            reviews=reviews,
            goal_satisfied=review["satisfied"]
        )
        _append_event(
            run_id,
            "execution",
            "completed",
            "Autonomous run completed."
        )
        current = get_run(
            run_id
        ) or {}
        if (
            not review["satisfied"]
            and current.get(
                "round",
                1
            )
            < current.get(
                "max_rounds",
                3
            )
        ):
            next_round = current.get(
                "round",
                1
            ) + 1
            next_plan = _plan_objective(
                f"{current.get('objective', '')} Resolve these remaining gaps: "
                + "; ".join(
                    review["gaps"]
                )
            )
            _update_run(
                run_id,
                round=next_round,
                plan=next_plan,
                status="queued"
            )
            _append_event(
                run_id,
                "review",
                "replanning",
                f"Goal review opened autonomous round {next_round}.",
                review
            )
            return execute_run(
                run_id
            )

    except Exception as error:
        _update_run(
            run_id,
            status="failed",
            error=str(
                error
            )
        )
        _append_event(
            run_id,
            "execution",
            "failed",
            str(
                error
            )
        )

    return get_run(
        run_id
    )


def resume_run(
    run_id: str
) -> Dict:
    run = get_run(
        run_id
    )

    if not run:
        raise ValueError(
            "Autonomous run not found."
        )

    if run.get(
        "status"
    ) not in {
        "cancelled",
        "failed",
        "queued"
    }:
        return run

    return execute_run(
        run_id
    )
