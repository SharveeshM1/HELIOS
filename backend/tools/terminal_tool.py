import subprocess


SAFE_COMMANDS = [
    "ls",
    "pwd",
    "cd",
    "mkdir",
    "touch",
    "cat",
    "echo",
    "python",
    "pip",
    "git"
]

# =========================================
# RUN TERMINAL COMMAND
# =========================================

def run_command(

    command,
    cwd=None

):

    try:

        base_command = str(command).split()[0]

        if base_command not in SAFE_COMMANDS:

            return {

                "status": "blocked",

                "reason": f"Unsafe command: {base_command}"
            }

        result = subprocess.run(

            command,

            shell=True,

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