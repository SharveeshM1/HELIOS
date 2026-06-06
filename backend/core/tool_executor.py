from core.agent_registry import (
    AGENTS
)

from core.tool_manager import (
    execute_tool
)

# =========================================
# EXECUTE AGENT TOOL
# =========================================

def execute_agent_tool(

    agent_key,
    tool_name,
    *args,
    retries=0,
    metadata=None,
    **kwargs

):

    # =====================================
    # AGENT VALIDATION
    # =====================================

    if agent_key not in AGENTS:

        raise Exception(
            f"Unknown agent: {agent_key}"
        )

    agent = AGENTS[agent_key]

    # =====================================
    # TOOL ACCESS VALIDATION
    # =====================================

    allowed_tools = agent.get(
        "tools",
        []
    )

    if tool_name not in allowed_tools:

        raise Exception(
            f"{agent['name']} cannot access tool: {tool_name}"
        )

    # =====================================
    # EXECUTE
    # =====================================

    safe_metadata = {
        **(
            metadata
            or {}
        ),
        "agent_key": agent_key
    }

    return execute_tool(

        tool_name,

        *args,

        actor=agent[
            "name"
        ],

        module=agent_key,

        retries=retries,

        metadata=safe_metadata,

        **kwargs
    )
