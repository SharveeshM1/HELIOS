from core.intent_router import route_objective
from core.task_planner import build_execution_plan


def test_intent_router_scores_multi_domain_objective():
    plan = route_objective(
        "Research citations, fix backend tests, and add observability metrics"
    )

    routes = [
        task["route"]
        for task in plan["tasks"]
    ]

    assert routes[:3] == [
        "code",
        "analytics",
        "research"
    ]
    assert plan["primary_route"] == "code"
    assert plan["risk"]["level"] == "low"
    assert plan["confidence"] > 0


def test_intent_router_flags_risky_terms():
    plan = route_objective(
        "Deploy production auth migration and commit the fix"
    )

    assert plan["risk"]["level"] == "high"
    assert "production" in plan["risk"]["terms"]
    assert "commit" in plan["risk"]["terms"]


def test_task_planner_preserves_legacy_list_shape():
    plan = build_execution_plan(
        "Fix frontend build and monitor latency"
    )

    assert isinstance(
        plan,
        list
    )
    assert plan[0]["agent"] == "code"
    assert "confidence" in plan[0]


def test_intent_router_supports_planning_knowledge_and_swarm_routes():
    plan = route_objective(
        "Plan a project brain memory workflow and run a multi agent debate"
    )
    routes = {
        task["route"]
        for task in plan["tasks"]
    }

    assert {
        "planning",
        "knowledge",
        "swarm"
    }.issubset(
        routes
    )
