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
