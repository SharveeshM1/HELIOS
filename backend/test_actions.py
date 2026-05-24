from core.action_engine import (
    generate_actions
)


def main():
    actions = generate_actions(

        "Create a python hello world file"

    )

    print(actions)


if __name__ == "__main__":
    main()
