from core.agent_brain import (
    think_and_decide
)

from core.tool_executor import (
    execute_agent_tool
)

# =========================================
# LIVE AGENT RUNTIME
# =========================================

def run_live_agent(

    agent_key,
    user_goal

):

    cognition = think_and_decide(

        agent_key,

        user_goal
    )

    if "error" in cognition:

        return cognition

    actions = cognition.get(
        "actions",
        []
    )

    execution_results = []

    # =====================================
    # ACTION LOOP
    # =====================================

    for action in actions:

        tool_name = action.get(
            "tool"
        )

        args = action.get(
            "args",
            []
        )

        try:

            result = execute_agent_tool(

                agent_key,

                tool_name,

                *args
            )

            execution_results.append({

                "tool":
                tool_name,

                "status":
                "success",

                "result":
                str(result)
            })

        except Exception as e:

            execution_results.append({

                "tool":
                tool_name,

                "status":
                "failed",

                "error":
                str(e)
            })

    return {

        "agent":
        cognition["agent"],

        "goal":
        user_goal,

        "executions":
        execution_results
    }