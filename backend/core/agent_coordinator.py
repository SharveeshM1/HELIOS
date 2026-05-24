from core.agent_registry import (
    AGENTS
)

from core.tool_executor import (
    execute_agent_tool
)

# =========================================
# AGENT COORDINATOR
# =========================================

class AgentCoordinator:

    def __init__(self):

        self.history = []

    # =====================================
    # EXECUTE TASK
    # =====================================

    def execute_task(

        self,

        agent,

        tool,

        tool_input

    ):

        result = execute_agent_tool(

            agent,

            tool,

            tool_input
        )

        execution = {

            "agent":
            agent,

            "tool":
            tool,

            "input":
            tool_input,

            "result":
            result
        }

        self.history.append(
            execution
        )

        return execution

    # =====================================
    # DELEGATE TASK
    # =====================================

    def delegate_task(

        self,

        from_agent,

        to_agent,

        objective

    ):

        delegation = {

            "from":
            from_agent,

            "to":
            to_agent,

            "objective":
            objective
        }

        self.history.append(
            delegation
        )

        return delegation

    # =====================================
    # GET HISTORY
    # =====================================

    def get_history(self):

        return self.history