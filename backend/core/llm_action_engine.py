import json

from api.ai_provider import (
    generate_ai_response
)

from core.agent_registry import (
    AGENTS
)

# =========================================
# LLM ACTION ENGINE
# =========================================

def generate_actions(

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

    tools = agent.get(
        "tools",
        []
    )

    capabilities = agent.get(
        "capabilities",
        []
    )

    # =====================================
    # PROMPT
    # =====================================

    prompt = f"""

You are an autonomous AI agent.

Agent:
{agent['name']}

Capabilities:
{capabilities}

Available Tools:
{tools}

User Goal:
{user_goal}

Your task:

Decide which tools should be used.

Return ONLY valid JSON.

Format:

{{
    "actions":[
        {{
            "tool":"tool_name",
            "args":[]
        }}
    ]
}}

Rules:

- Use only available tools
- Keep actions minimal
- Prefer execution efficiency
- No explanations
- Output valid JSON only

"""

    response = generate_ai_response(
        prompt
    )

    # =====================================
    # PARSE JSON
    # =====================================

    try:

        cleaned = response.strip()

        if "```json" in cleaned:

            cleaned = cleaned.replace(
                "```json",
                ""
            )

            cleaned = cleaned.replace(
                "```",
                ""
            )

        parsed = json.loads(
            cleaned
        )

        return parsed

    except Exception:

        return {

            "actions":[]
        }