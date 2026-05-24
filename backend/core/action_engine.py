import json

from api.ai_provider import (
    generate_ai_response
)

# =========================================
# HELIOS ACTION ENGINE
# =========================================

AVAILABLE_TOOLS = [

    "run_command",

    "create_file",

    "execute_python"
]

# =========================================
# GENERATE ACTION PLAN
# =========================================

def generate_actions(

    objective

):

    prompt = f"""

You are an autonomous AI action planner.

Available tools:

{AVAILABLE_TOOLS}

OBJECTIVE:
{objective}

Return ONLY valid JSON.

Format:

[
  {{
    "tool": "tool_name",
    "reason": "why",
    "input": "execution input"
  }}
]

Only choose tools required
to accomplish the task.

"""

    response = generate_ai_response(
        prompt
    )

    try:

        start = response.find("[")

        end = response.rfind("]") + 1

        cleaned = response[start:end]

        actions = json.loads(
            cleaned
        )

        return actions

    except Exception:

        return []