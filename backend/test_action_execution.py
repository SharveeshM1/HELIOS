from core.action_executor import (
    execute_actions
)


def main():
    result = execute_actions(

        "Create a file named ai.txt"

    )

    print(result)


if __name__ == "__main__":
    main()
