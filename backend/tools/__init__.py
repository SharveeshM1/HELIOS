from tools.terminal_tool import (
    run_command
)

from tools.file_tool import (
    create_file,
    read_file
)

from tools.python_tool import (
    execute_python
)

# =========================================
# TOOL REGISTRY
# =========================================

TOOL_REGISTRY = {

    "run_command":
    run_command,

    "create_file":
    create_file,

    "read_file":
    read_file,

    "execute_python":
    execute_python
}