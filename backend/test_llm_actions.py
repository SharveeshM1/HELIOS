from core.llm_action_engine import (
    generate_actions
)


def main():
    result = generate_actions(

        "code",

        "Create a Python file for a calculator"

    )

    print(result)


if __name__ == "__main__":
    main()
