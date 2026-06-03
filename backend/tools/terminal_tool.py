import subprocess
import shlex


SAFE_COMMANDS = [
    "ls",
    "pwd",
    "cd",
    "mkdir",
    "touch",
    "cat",
    "echo",
    "python",
    "python3",
    "pip",
    "git",
    "npm",
    "backend/venv/bin/python"
]

BLOCKED_TOKENS = {
    "&&",
    "||",
    ";",
    "|",
    ">",
    ">>",
    "<",
    "$(",
    "`"
}

# =========================================
# RUN TERMINAL COMMAND
# =========================================

def run_command(

    command,
    cwd=None

):

    try:

        raw_command = str(
            command
        ).strip()
        if any(
            token in raw_command
            for token in BLOCKED_TOKENS
        ):
            return {
                "status": "blocked",
                "reason": "Shell control operators are not allowed."
            }

        args = shlex.split(
            raw_command
        )
        if not args:
            return {
                "status": "blocked",
                "reason": "Empty command."
            }
        base_command = args[0]

        if base_command not in SAFE_COMMANDS:

            return {

                "status": "blocked",

                "reason": f"Unsafe command: {base_command}"
            }

        result = subprocess.run(

            args,

            capture_output=True,

            text=True,

            cwd=cwd
        )

        output = f"""

STDOUT:
{result.stdout}

STDERR:
{result.stderr}

RETURN CODE:
{result.returncode}

"""

        return output

    except Exception as e:

        return f"""

TERMINAL EXECUTION FAILED

Error:
{str(e)}

"""
