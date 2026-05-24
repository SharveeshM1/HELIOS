from core.tool_planner import (
    ToolPlanner
)


def main():
    planner = ToolPlanner()

    result = planner.build_plan(

        "Build scalable AI infrastructure with autonomous deployment"

    )

    print(result)


if __name__ == "__main__":
    main()
