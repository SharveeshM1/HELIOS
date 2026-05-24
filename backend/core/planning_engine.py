from datetime import datetime

from core.agent_registry import (
    AGENTS
)

# =========================================
# HELIOS PLANNING ENGINE
# =========================================

class PlanningEngine:

    def __init__(self):

        self.available_agents = AGENTS

    # =====================================
    # BUILD EXECUTION PLAN
    # =====================================

    def create_plan(

        self,

        objective

    ):

        objective = str(objective).lower()

        tasks = []

        # =================================
        # RESEARCH TASK
        # =================================

        if any(

            keyword in objective

            for keyword in [

                "research",
                "analyze",
                "trend",
                "market",
                "future",
                "strategy"
            ]

        ):

            tasks.append({

                "agent":
                "research",

                "objective":
                objective,

                "priority":
                1
            })

        # =================================
        # CODE TASK
        # =================================

        if any(

            keyword in objective

            for keyword in [

                "build",
                "code",
                "develop",
                "system",
                "architecture",
                "backend",
                "frontend",
                "api",
                "automation"
            ]

        ):

            tasks.append({

                "agent":
                "code",

                "objective":
                objective,

                "priority":
                2
            })

        # =================================
        # ANALYTICS TASK
        # =================================

        if any(

            keyword in objective

            for keyword in [

                "optimize",
                "performance",
                "scale",
                "analytics",
                "monitor",
                "infrastructure"
            ]

        ):

            tasks.append({

                "agent":
                "analytics",

                "objective":
                objective,

                "priority":
                3
            })

        # =================================
        # DEFAULT FALLBACK
        # =================================

        if not tasks:

            tasks.append({

                "agent":
                "research",

                "objective":
                objective,

                "priority":
                1
            })

        return {

            "objective":
            objective,

            "tasks":
            tasks,

            "timestamp":
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        }