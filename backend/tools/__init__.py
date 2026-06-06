from tools.terminal_tool import (
    run_command
)

from tools.file_tool import (
    append_file,
    create_file,
    read_file
)

from tools.python_tool import (
    execute_python
)

from tools.deploy_tool import (
    deploy_project
)

# =========================================
# TOOL REGISTRY
# =========================================

TOOL_REGISTRY = {

    "run_command":
    run_command,

    "create_file":
    create_file,

    "append_file":
    append_file,

    "read_file":
    read_file,

    "execute_python":
    execute_python,

    "deploy_project":
    deploy_project
}
