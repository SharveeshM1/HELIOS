import argparse
import os
import socket
import time
import uuid

from core.autonomous_runs import execute_agent_step
from core.autonomous_runs import execute_run
from core.runtime_config import WORKER_LEASE_SECONDS
from core.runtime_store import claim_job
from core.runtime_store import complete_job
from core.swarm_engine import execute_swarm_agent


def worker_identity() -> str:
    return os.getenv(
        "HELIOS_WORKER_ID",
        f"{socket.gethostname()}-{os.getpid()}-{uuid.uuid4().hex[:6]}"
    )


def execute_job(
    job: dict
):
    kind = job.get(
        "kind"
    )
    payload = job.get(
        "payload",
        {}
    )
    if kind == "autonomous_run":
        return execute_run(
            payload.get(
                "run_id",
                ""
            )
        )
    if kind == "autonomous_step":
        return execute_agent_step(
            payload.get(
                "objective",
                ""
            ),
            payload.get(
                "step",
                {}
            )
        )
    if kind == "swarm_agent":
        return execute_swarm_agent(
            payload.get(
                "agent",
                ""
            ),
            payload.get(
                "query",
                ""
            ),
            payload.get(
                "web_results",
                ""
            ),
            payload.get(
                "file_content",
                ""
            ),
            payload.get(
                "conversation_context",
                ""
            )
        )
    raise ValueError(
        f"Unsupported worker job kind: {kind}"
    )


def run_worker(
    once: bool = False,
    poll_seconds: float = 1.0
) -> int:
    worker_id = worker_identity()
    processed = 0

    while True:
        job = claim_job(
            worker_id,
            WORKER_LEASE_SECONDS
        )
        if job is None:
            if once:
                return processed
            time.sleep(
                poll_seconds
            )
            continue

        try:
            result = execute_job(
                job
            )
            complete_job(
                job["id"],
                worker_id,
                result=result
            )
        except Exception as error:
            complete_job(
                job["id"],
                worker_id,
                error=str(
                    error
                )
            )
        processed += 1

        if once:
            return processed


def main() -> None:
    parser = argparse.ArgumentParser(
        description="HELIOS durable autonomous worker"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Process at most one queued job."
    )
    parser.add_argument(
        "--poll-seconds",
        type=float,
        default=1.0
    )
    args = parser.parse_args()
    run_worker(
        once=args.once,
        poll_seconds=max(
            0.1,
            args.poll_seconds
        )
    )


if __name__ == "__main__":
    main()
