from core.intent_router import (
    route_objective
)


def build_execution_plan(
    user_query
):
    plan = route_objective(
        user_query
    )

    return [
        {
            "agent": task["agent"],
            "objective": task["objective"],
            "route": task["route"],
            "priority": task["priority"],
            "confidence": task["confidence"],
            "matched_terms": task["matched_terms"]
        }
        for task in plan["tasks"]
    ]
