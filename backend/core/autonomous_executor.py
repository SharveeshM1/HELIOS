from core.task_planner import (
    build_execution_plan
)

from core.tool_executor import (
    execute_agent_tool
)

# =========================================
# AUTONOMOUS EXECUTOR
# =========================================

def run_autonomous_execution(

    user_query

):

    execution_plan = build_execution_plan(
        user_query
    )

    results = []

    # =====================================
    # EXECUTION LOOP
    # =====================================

    for step in execution_plan:

        agent = step["agent"]

        objective = step["objective"]

        # =================================
        # RESEARCH
        # =================================

        if agent == "research":

            result = {

                "agent":
                agent,

                "objective":
                objective,

                "status":
                "completed",

                "output":
                f"Research completed for: {user_query}"
            }

        # =================================
        # CODE
        # =================================

        elif agent == "code":

            result = execute_agent_tool(

                "code",

                "create_file",

                "memory/autonomous_output.txt",

                f"HELIOS generated execution for: {user_query}"
            )

            results.append({

                "agent":
                agent,

                "objective":
                objective,

                "status":
                "completed",

                "output":
                result
            })

            continue

        # =================================
        # ANALYTICS
        # =================================

        elif agent == "analytics":

            result = {

                "agent":
                agent,

                "objective":
                objective,

                "status":
                "completed",

                "output":
                "Infrastructure analytics completed"
            }

        else:

            result = {

                "agent":
                agent,

                "status":
                "failed",

                "output":
                "Unknown agent"
            }

        results.append(
            result
        )

    return {

        "query":
        user_query,

        "steps":
        results
    }