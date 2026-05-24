from core.agent_registry import (
    AGENTS
)

# =========================================
# TASK PLANNER
# =========================================

def build_execution_plan(

    user_query

):

    query = str(
        user_query
    ).lower()

    plan = []

    # =====================================
    # RESEARCH TASKS
    # =====================================

    if any(

        word in query

        for word in [

            "research",
            "analyze",
            "trend",
            "future",
            "market"

        ]
    ):

        plan.append({

            "agent":
            "research",

            "objective":
            "Perform deep research analysis"
        })

    # =====================================
    # CODE TASKS
    # =====================================

    if any(

        word in query

        for word in [

            "build",
            "code",
            "create",
            "develop",
            "fix",
            "debug"

        ]
    ):

        plan.append({

            "agent":
            "code",

            "objective":
            "Generate and execute implementation"
        })

    # =====================================
    # ANALYTICS TASKS
    # =====================================

    if any(

        word in query

        for word in [

            "optimize",
            "performance",
            "scale",
            "monitor"

        ]
    ):

        plan.append({

            "agent":
            "analytics",

            "objective":
            "Analyze infrastructure and performance"
        })

    # =====================================
    # FALLBACK
    # =====================================

    if not plan:

        plan.append({

            "agent":
            "research",

            "objective":
            "General intelligence analysis"
        })

    return plan