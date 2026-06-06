import asyncio
import logging
import time

from core.mission_ledger import advance_mission
from core.mission_ledger import create_mission
from core.mission_workflows import run_mission_workflow
from core.runtime_store import claim_due_scheduled_missions
from core.runtime_store import schedule_mission
from core.runtime_store import update_scheduled_mission_status

logger = logging.getLogger("helios-scheduler")


def schedule_next_occurrence(mission: dict) -> dict | None:
    recurrence_minutes = int(mission.get("recurrence_minutes") or 0)
    if recurrence_minutes <= 0:
        return None

    return schedule_mission(
        title=mission["title"],
        agent=mission["agent"],
        module=mission["module"],
        scheduled_at=time.time() + recurrence_minutes * 60,
        detail=mission.get("detail") or "Recurring scheduled mission.",
        recurrence_minutes=recurrence_minutes,
    )


def execute_scheduled_mission(
    scheduled_mission: dict
) -> dict:
    created = create_mission(
        title=scheduled_mission["title"],
        agent=scheduled_mission["agent"],
        module=scheduled_mission["module"],
        detail=scheduled_mission.get("detail") or "Scheduled mission execution."
    )
    mission = created["mission"]
    workflow = run_mission_workflow(
        mission
    )
    result = advance_mission(
        mission["id"],
        "Executed",
        detail=workflow["artifact"].get(
            "summary",
            "Scheduled mission workflow executed."
        ),
        artifact=workflow["artifact"]
    )
    return {
        "mission": result["mission"],
        "artifact": workflow["artifact"],
        "task": workflow["task"]
    }


async def start_mission_scheduler():
    """Background loop to check and execute scheduled missions."""
    logger.info("HELIOS Mission Scheduler initialized.")
    while True:
        try:
            pending = await asyncio.to_thread(
                claim_due_scheduled_missions
            )

            for mission in pending:
                logger.info(
                    "Triggering scheduled mission: %s (ID: %s)",
                    mission["title"],
                    mission["id"]
                )
                try:
                    await asyncio.to_thread(
                        execute_scheduled_mission,
                        mission
                    )
                    next_run = await asyncio.to_thread(
                        schedule_next_occurrence,
                        mission
                    )
                    if next_run:
                        logger.info(
                            "Requeued recurring mission %s for %s minutes from now.",
                            mission["title"],
                            mission.get("recurrence_minutes")
                        )
                    await asyncio.to_thread(
                        update_scheduled_mission_status,
                        mission["id"],
                        "completed"
                    )
                    logger.info(
                        "Successfully executed scheduled mission: %s",
                        mission["title"]
                    )
                except Exception as trigger_error:
                    logger.exception(
                        "Failed to trigger mission %s: %s",
                        mission["id"],
                        trigger_error
                    )
                    await asyncio.to_thread(
                        update_scheduled_mission_status,
                        mission["id"],
                        "failed"
                    )
        except Exception as e:
            logger.exception(
                "Mission scheduler loop encountered an error: %s",
                e
            )

        await asyncio.sleep(30)
