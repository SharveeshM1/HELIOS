from core.action_engine import (
    generate_actions
)

from core.tool_manager import (
    execute_tool
)

# =========================================
# EXECUTE ACTIONS
# =========================================

def execute_actions(

    objective

):

    actions = generate_actions(
        objective
    )

    results = []

    for action in actions:

        tool = action.get(
            "tool"
        )

        tool_input = action.get(
            "input"
        )

        try:

            result = execute_tool(

                tool,

                tool_input
            )

            results.append({

                "tool":
                tool,

                "status":
                "success",

                "result":
                result
            })

        except Exception as e:

            results.append({

                "tool":
                tool,

                "status":
                "failed",

                "result":
                str(e)
            })

    return {

        "objective":
        objective,

        "actions":
        actions,

        "results":
        results
    } 