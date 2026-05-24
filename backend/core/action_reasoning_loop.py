from core.action_engine import (
    generate_actions
)

from core.tool_manager import (
    execute_tool
)

from core.autonomous_loop import (
    run_autonomous_loop
)

from memory.execution_memory import (
    store_execution,
    get_recent_executions
)

# =========================================
# ACTION REASONING LOOP
# =========================================

def run_action_reasoning_loop(

    objective,

    iterations=3

):

    history = []

    previous_executions = get_recent_executions()

    current_objective = f"""

OBJECTIVE:
{objective}

PREVIOUS EXECUTIONS:
{previous_executions}

Learn from previous attempts.

"""

    for i in range(iterations):

        # =================================
        # REASONING
        # =================================

        reasoning = run_autonomous_loop(

            query=current_objective,

            web_results="",

            file_content="",

            conversation_context="",

            iterations=1
        )

        # =================================
        # ACTIONS
        # =================================

        actions = generate_actions(
            current_objective
        )

        action_results = []

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

                action_results.append({

                    "tool":
                    tool,

                    "status":
                    "success",

                    "result":
                    result
                })

            except Exception as e:

                action_results.append({

                    "tool":
                    tool,

                    "status":
                    "failed",

                    "result":
                    str(e)
                })

        # =================================
        # STORE
        # =================================

        history.append({

            "iteration":
            i + 1,

            "reasoning":
            reasoning,

            "actions":
            actions,

            "results":
            action_results
        })

        store_execution(

            current_objective,

            actions,

            action_results
        )

        # =================================
        # EVOLUTION
        # =================================

        current_objective = f"""

Previous execution results:

{action_results}

Improve execution strategy
and continue evolving.

"""

    return history