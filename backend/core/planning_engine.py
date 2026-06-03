from core.agent_registry import (
    AGENTS
)
from core.intent_router import (
    route_objective
)


class PlanningEngine:

    def __init__(self):

        self.available_agents = AGENTS

    def create_plan(
        self,
        objective
    ):
        return route_objective(
            objective
        )
