from tools.terminal_tool import (
    run_command
)


def main():
    result = run_command(
        "pwd"
    )

    print(result)


if __name__ == "__main__":
    main()


def test_terminal_tool_blocks_shell_control_operators():
    result = run_command(
        "git status && echo unsafe"
    )

    assert result["status"] == "blocked"
