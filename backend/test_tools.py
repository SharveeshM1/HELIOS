import tools

from core.tool_executor import (
    execute_agent_tool
)

# =========================================
# CODE AGENT CREATES FILE
# =========================================

result = execute_agent_tool(

    "code",

    "create_file",

    "memory/agent_test.txt",

    "HELIOS AGENT EXECUTION ONLINE"
)

print(result)

# =========================================
# CODE AGENT READS FILE
# =========================================

content = execute_agent_tool(

    "code",

    "read_file",

    "memory/agent_test.txt"
)

print(content)

# =========================================
# CODE AGENT EXECUTES PYTHON
# =========================================

python_result = execute_agent_tool(

    "code",

    "execute_python",

    """

x = 10
y = 22

result = x * y

"""
)

print(python_result)