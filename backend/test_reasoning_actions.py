from core.action_reasoning_loop import (
    run_action_reasoning_loop
)


def main():
    result = run_action_reasoning_loop(

        "Create a python calculator script",

        iterations=2
    )

    print(result)


if __name__ == "__main__":
    main()
