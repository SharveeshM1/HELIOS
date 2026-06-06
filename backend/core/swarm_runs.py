import json
import uuid
from datetime import datetime
from typing import Dict
from typing import List

from core.runtime_config import MEMORY_DIR
from core.runtime_store import enqueue_job
from core.runtime_store import get_job
from core.runtime_store import load_document
from core.runtime_store import save_document
from core.swarm_engine import build_consensus


SWARM_RUNS_DOCUMENT = "swarm_runs"
SWARM_AGENTS = [
    "Research Agent",
    "Code Agent",
    "Analytics Agent"
]
MAX_SWARM_RUNS = 100
SWARM_RUNS_FILE = MEMORY_DIR / "swarm_runs.json"


def _timestamp() -> str:
    return datetime.now().isoformat(
        timespec="seconds"
    )


def load_swarm_runs() -> List[Dict]:
    runs = load_document(
        SWARM_RUNS_DOCUMENT,
        []
    )
    if isinstance(
        runs,
        list
    ):
        return runs
    if not SWARM_RUNS_FILE.exists():
        return []
    try:
        file_runs = json.loads(
            SWARM_RUNS_FILE.read_text(
                encoding="utf-8"
            )
        )
        return file_runs if isinstance(
            file_runs,
            list
        ) else []
    except Exception:
        return []


def save_swarm_runs(
    runs: List[Dict]
) -> None:
    trimmed = runs[
        -MAX_SWARM_RUNS:
    ]
    if save_document(
        SWARM_RUNS_DOCUMENT,
        trimmed
    ):
        return
    SWARM_RUNS_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )
    SWARM_RUNS_FILE.write_text(
        json.dumps(
            trimmed,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )


def get_swarm_run(
    run_id: str
) -> Dict | None:
    return next(
        (
            run
            for run in load_swarm_runs()
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
    runs = load_swarm_runs()
    for index, run in enumerate(
        runs
    ):
        if run.get(
            "id"
        ) == run_id:
            runs[
                index
            ] = {
                **run,
                **changes,
                "updated_at": _timestamp()
            }
            save_swarm_runs(
                runs
            )
            return runs[
                index
            ]
    raise ValueError(
        "Swarm run not found."
    )


def _queue_round(
    run: Dict,
    round_number: int,
    context: str = ""
) -> Dict:
    jobs = [
        enqueue_job(
            "swarm_agent",
            {
                "run_id": run[
                    "id"
                ],
                "round": round_number,
                "agent": agent,
                "query": run.get(
                    "objective",
                    ""
                ),
                "web_results": run.get(
                    "web_results",
                    ""
                ),
                "file_content": run.get(
                    "file_content",
                    ""
                ),
                "conversation_context": context
            }
        )
        for agent in SWARM_AGENTS
    ]
    return _update_run(
        run[
            "id"
        ],
        status="queued",
        round=round_number,
        worker_job_ids=[
            job[
                "id"
            ]
            for job in jobs
        ]
    )


def create_swarm_run(
    objective: str,
    web_results: str = "",
    file_content: str = "",
    conversation_context: str = ""
) -> Dict:
    run = {
        "id": str(
            uuid.uuid4()
        ),
        "objective": str(
            objective
        ),
        "web_results": str(
            web_results
        )[
            :5000
        ],
        "file_content": str(
            file_content
        )[
            :4000
        ],
        "conversation_context": str(
            conversation_context
        )[
            :4000
        ],
        "status": "queued",
        "round": 1,
        "rounds": [],
        "debate_protocol": {
            "mode": "two_round_worker_debate",
            "independent_agents": SWARM_AGENTS,
            "rounds": [
                "proposal",
                "critique_revision"
            ],
            "consensus_required": True,
            "assignments_generated": True
        },
        "created_at": _timestamp(),
        "updated_at": _timestamp()
    }
    runs = load_swarm_runs()
    runs.append(
        run
    )
    save_swarm_runs(
        runs
    )
    return _queue_round(
        run,
        1,
        run[
            "conversation_context"
        ]
    )


def reconcile_swarm_run(
    run_id: str
) -> Dict:
    run = get_swarm_run(
        run_id
    )
    if not run:
        raise ValueError(
            "Swarm run not found."
        )
    jobs = [
        job
        for job_id in run.get(
            "worker_job_ids",
            []
        )
        if (
            job := get_job(
                job_id
            )
        )
    ]
    if not jobs or not all(
        job.get(
            "status"
        )
        in {
            "completed",
            "failed"
        }
        for job in jobs
    ):
        return _update_run(
            run_id,
            status="running"
            if any(
                job.get(
                    "status"
                )
                == "running"
                for job in jobs
            )
            else "queued",
            worker_jobs=jobs
        )
    results = [
        job.get(
            "result"
        )
        if isinstance(
            job.get(
                "result"
            ),
            dict
        )
        else {
            "agent": job.get(
                "payload",
                {}
            ).get(
                "agent",
                "Unknown"
            ),
            "status": "failed",
            "output": job.get(
                "error",
                "Worker failed."
            ),
            "duration": 0
        }
        for job in jobs
    ]
    rounds = [
        *run.get(
            "rounds",
            []
        ),
        {
            "round": run.get(
                "round",
                1
            ),
            "type": "proposal"
            if run.get(
                "round",
                1
            )
            == 1
            else "review",
            "results": results
        }
    ]
    if run.get(
        "round",
        1
    ) == 1:
        first_consensus = build_consensus(
            results,
            rounds=rounds
        )
        context = "\n".join(
            [
                run.get(
                    "conversation_context",
                    ""
                ),
                "Review the other agent proposals and revise your recommendation:",
                *[
                    f"- {item.get('agent')}: {item.get('proposal')}"
                    for item in first_consensus.get(
                        "proposals",
                        []
                    )
                ]
            ]
        )
        updated = _update_run(
            run_id,
            rounds=rounds,
            worker_jobs=jobs,
            debate_state={
                "phase": "critique_revision",
                "completed_rounds": 1,
                "pending_agents": SWARM_AGENTS,
                "protocol": run.get(
                    "debate_protocol",
                    {}
                )
            }
        )
        return _queue_round(
            updated,
            2,
            context
        )
    consensus = build_consensus(
        results,
        rounds=rounds
    )
    return _update_run(
        run_id,
        status="completed",
        rounds=rounds,
        worker_jobs=jobs,
        consensus=consensus,
        debate_state={
            "phase": "consensus",
            "completed_rounds": len(
                rounds
            ),
            "pending_agents": [],
            "protocol": run.get(
                "debate_protocol",
                {}
            )
        },
        assignments=[
            {
                "agent": item.get(
                    "agent"
                ),
                "objective": item.get(
                    "proposal"
                ),
                "priority": index + 1
            }
            for index, item in enumerate(
                consensus.get(
                    "proposals",
                    []
                )
            )
        ]
    )
