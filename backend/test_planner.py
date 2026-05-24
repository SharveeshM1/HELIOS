from core.planning_engine import (
    PlanningEngine
)


def main():
    planner = PlanningEngine()

    plan = planner.create_plan(

        "Build and optimize an AI trading platform with scalable backend systems"

    )

    print(plan)


if __name__ == "__main__":
    main()
