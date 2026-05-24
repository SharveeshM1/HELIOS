from api.ai_provider import (
    generate_ai_response
)

# =========================================
# TOOL PLANNER
# =========================================

class ToolPlanner:

    def build_plan(

        self,

        objective
    ):

        prompt = f"""

You are HELIOS Tool Planning Engine.

Analyze the objective and determine:

1. best agent
2. best tools

AVAILABLE AGENTS:
- research
- code
- analytics

AVAILABLE TOOLS:
- create_file
- read_file
- append_file
- execute_python
- run_command
- search_codebase

OBJECTIVE:
{objective}

Return ONLY valid Python dictionary format.

Example:

{{
    "agent": "code",
    "tools": [
        "create_file",
        "execute_python"
    ]
}}

Tool examples:

- search_codebase: find occurrences of functions/classes before editing

"""

        response = generate_ai_response(
            prompt
        )

        try:

            plan = eval(response)

            return plan

        except Exception:

            return {

                "agent":
                "research",

                "tools":
                ["read_file"]
            }