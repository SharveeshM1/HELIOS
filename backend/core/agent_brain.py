from core.agent_registry import (
    AGENTS
)

# =========================================
# AGENT BRAIN
# =========================================

def think_and_decide(

    agent_key,
    user_goal

):

    if agent_key not in AGENTS:

        return {

            "error":
            "Unknown agent"
        }

    agent = AGENTS[
        agent_key
    ]

    capabilities = agent.get(
        "capabilities",
        []
    )

    tools = agent.get(
        "tools",
        []
    )

    goal = str(
        user_goal
    ).lower()

    actions = []

    # =====================================
    # FILE ACTIONS
    # =====================================

    if any(

        word in goal

        for word in [

            "create",
            "file",
            "save",
            "write"

        ]
    ):

        if "create_file" in tools:

            actions.append({

                "tool":
                "create_file",

                "args":[

                    "memory/brain_output.txt",

                    f"HELIOS autonomous action for: {user_goal}"
                ]
            })

    # =====================================
    # PYTHON ACTIONS
    # =====================================

    if any(

        word in goal

        for word in [

            "calculate",
            "python",
            "compute"

        ]
    ):

        if "execute_python" in tools:

            actions.append({

                "tool":
                "execute_python",

                "args":[
                    "result = 55 * 22"
                ]
            })

    # =====================================
    # TERMINAL ACTIONS
    # =====================================

    if any(

        word in goal

        for word in [

            "install",
            "package",
            "terminal",
            "command"

        ]
    ):

        if "run_command" in tools:

            actions.append({

                "tool":
                "run_command",

                "args":[
                    "pwd"
                ]
            })

    return {

        "agent":
        agent["name"],

        "goal":
        user_goal,

        "actions":
        actions
    }