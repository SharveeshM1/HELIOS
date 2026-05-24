from tools import TOOL_REGISTRY

# =========================================
# EXECUTE TOOL
# =========================================

def execute_tool(

    tool_name,
    *args,
    **kwargs

):

    if tool_name not in TOOL_REGISTRY:

        raise Exception(
            f"Tool not found: {tool_name}"
        )

    tool_function = TOOL_REGISTRY[
        tool_name
    ]

    return tool_function(

        *args,

        **kwargs
    )