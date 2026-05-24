from core.planning_engine import (
    PlanningEngine
)

from agents.research_agent import (
    run_research_agent
)

from agents.code_agent import (
    run_code_agent
)

from agents.analytics_agent import (
    run_analytics_agent
)

# =========================================
# HELIOS ORCHESTRATOR
# =========================================

class Orchestrator:

    def __init__(self):

        self.planner = PlanningEngine()

    # =====================================
    # EXECUTE TASK
    # =====================================

    def execute_task(

        self,

        task

    ):

        agent = task["agent"]

        objective = task["objective"]

        # =================================
        # RESEARCH
        # =================================

        if agent == "research":

            result = run_research_agent(

                objective,

                "",

                "",

                ""
            )

        # =================================
        # CODE
        # =================================

        elif agent == "code":

            result = run_code_agent(

                objective,

                "",

                ""
            )

        # =================================
        # ANALYTICS
        # =================================

        elif agent == "analytics":

            result = run_analytics_agent(

                objective,

                "",

                ""
            )

        else:

            result = f"Unknown agent: {agent}"

        return {

            "agent":
            agent,

            "objective":
            objective,

            "result":
            result
        }

    # =====================================
    # EXECUTE OBJECTIVE
    # =====================================

    def execute(

        self,

        objective

    ):

        plan = self.planner.create_plan(
            objective
        )

        results = []

        for task in plan["tasks"]:

            result = self.execute_task(
                task
            )

            results.append(
                result
            )

        return {

            "objective":
            objective,

            "plan":
            plan,

            "results":
            results
        }