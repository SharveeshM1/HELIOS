from tools import TOOL_REGISTRY
import time

from memory.execution_memory import (
    record_execution_event
)


def list_tools():
    return sorted(
        TOOL_REGISTRY.keys()
    )


def _tool_status(
    result
):
    if isinstance(
        result,
        dict
    ) and result.get(
        "status"
    ) == "blocked":
        return "blocked"

    if isinstance(
        result,
        dict
    ) and result.get(
        "success"
    ) is False:
        return "failed"

    return "success"

# =========================================
# EXECUTE TOOL
# =========================================

def execute_tool(

    tool_name,
    *args,
    actor="HELIOS",
    module="execution",
    retries=0,
    metadata=None,
    **kwargs

):

    if tool_name not in TOOL_REGISTRY:
        record_execution_event(
            label=f"Tool blocked: {tool_name}",
            status="blocked",
            actor=actor,
            module=module,
            tool=tool_name,
            detail=f"Tool not found: {tool_name}",
            input={
                "args": args,
                "kwargs": kwargs
            },
            metadata=metadata
        )

        raise Exception(
            f"Tool not found: {tool_name}"
        )

    tool_function = TOOL_REGISTRY[
        tool_name
    ]

    max_attempts = max(
        1,
        int(
            retries
        )
        + 1
    )
    last_error = None

    for attempt in range(
        1,
        max_attempts
        + 1
    ):
        parent_event = record_execution_event(
            label=f"Tool started: {tool_name}",
            status="running",
            actor=actor,
            module=module,
            tool=tool_name,
            detail=f"Attempt {attempt} of {max_attempts}.",
            input={
                "args": args,
                "kwargs": kwargs
            },
            attempt=attempt,
            metadata=metadata
        )

        started_at = time.perf_counter()

        try:
            result = tool_function(

                *args,

                **kwargs
            )

            duration_ms = round(
                (
                    time.perf_counter()
                    - started_at
                )
                * 1000,
                2
            )
            status = _tool_status(
                result
            )

            record_execution_event(
                label=f"Tool {status}: {tool_name}",
                status=status,
                actor=actor,
                module=module,
                tool=tool_name,
                detail=f"Attempt {attempt} completed in {duration_ms} ms.",
                result=result,
                duration_ms=duration_ms,
                attempt=attempt,
                parent_id=parent_event.get(
                    "id"
                ),
                metadata=metadata
            )

            return result

        except Exception as error:
            last_error = error
            duration_ms = round(
                (
                    time.perf_counter()
                    - started_at
                )
                * 1000,
                2
            )

            record_execution_event(
                label=f"Tool failed: {tool_name}",
                status="failed",
                actor=actor,
                module=module,
                tool=tool_name,
                detail=f"Attempt {attempt} failed in {duration_ms} ms.",
                error=str(
                    error
                ),
                duration_ms=duration_ms,
                attempt=attempt,
                parent_id=parent_event.get(
                    "id"
                ),
                metadata=metadata
            )

            if attempt == max_attempts:
                raise

    raise last_error
