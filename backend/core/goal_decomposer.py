try:
    from api.ai_provider import (
        generate_ai_response
    )
except Exception:
    generate_ai_response = None

# =========================================
# GOAL DECOMPOSER
# =========================================

class GoalDecomposer:

    def decompose(

        self,

        objective

    ):

        prompt = f"""

You are HELIOS Goal Planner.

Break this objective into
small executable AI tasks.

OBJECTIVE:
{objective}

RULES:

- concise
- actionable
- technical
- execution-oriented
- no explanations

Return ONLY a Python list.

Example:

[
 "task 1",
 "task 2"
]

"""

        if generate_ai_response is None:

            base_tasks = [
                objective
            ]

            enhanced_tasks = []

            for task in base_tasks:

                enhanced_tasks.append({

                    "task": task,

                    "assigned_agents": [

                        "research",
                        "code",
                        "analytics"
                    ]
                })

            return enhanced_tasks

        response = generate_ai_response(
            prompt
        )

        try:

            tasks = eval(response)

            if isinstance(
                tasks,
                list
            ):

                enhanced_tasks = []

                for task in tasks:

                    enhanced_tasks.append({

                        "task": task,

                        "assigned_agents": [

                            "research",
                            "code",
                            "analytics"
                        ]
                    })

                return enhanced_tasks

        except Exception:

            pass

        base_tasks = [
            objective
        ]

        enhanced_tasks = []

        for task in base_tasks:

            enhanced_tasks.append({

                "task": task,

                "assigned_agents": [

                    "research",

                    "code",

                    "analytics"
                ]
            })

        return enhanced_tasks