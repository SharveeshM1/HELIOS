from core.agent_coordinator import (
    AgentCoordinator
)


def main():
    coordinator = AgentCoordinator()

    result = coordinator.execute_task(

        "code",

        "create_file",

        "memory/team_test.txt"
    )

    print(result)

    delegation = coordinator.delegate_task(

        "research",

        "code",

        "Build autonomous infrastructure"
    )

    print(delegation)

    print(coordinator.get_history())


if __name__ == "__main__":
    main()
