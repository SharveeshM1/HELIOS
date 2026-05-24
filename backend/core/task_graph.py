from concurrent.futures import (
    ThreadPoolExecutor
)

from core.agent_coordinator import (
    AgentCoordinator
)

# =========================================
# TASK GRAPH ENGINE
# =========================================

class TaskGraph:

    def __init__(self):

        self.coordinator = (
            AgentCoordinator()
        )

        self.tasks = []

    # =====================================
    # ADD TASK
    # =====================================

    def add_task(

        self,

        agent,

        tool,

        tool_input,

        depends_on=None

    ):

        self.tasks.append({

            "agent":
            agent,

            "tool":
            tool,

            "input":
            tool_input,

            "depends_on":
            depends_on
        })

    # =====================================
    # EXECUTE SINGLE TASK
    # =====================================

    def execute_task(

        self,

        task

    ):

        return self.coordinator.execute_task(

            task["agent"],

            task["tool"],

            task["input"]
        )

    # =====================================
    # RUN GRAPH
    # =====================================

    def run(self):

        completed = []

        with ThreadPoolExecutor(
            max_workers=4
        ) as executor:

            futures = []

            for task in self.tasks:

                dependency = task.get(
                    "depends_on"
                )

                if dependency:

                    dependency_met = any(

                        completed_task.get(
                            "tool"
                        ) == dependency

                        for completed_task in completed
                    )

                    if not dependency_met:

                        continue

                futures.append(

                    executor.submit(

                        self.execute_task,

                        task
                    )
                )

            for future in futures:

                result = future.result()

                completed.append(
                    result
                )

        return completed