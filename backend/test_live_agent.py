from core.live_agent_runtime import (
    run_live_agent
)


def main():
    result = run_live_agent(

        "code",

        "Create a file and calculate using python"

    )

    print(result)


if __name__ == "__main__":
    main()
