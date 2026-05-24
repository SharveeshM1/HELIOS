from core.task_graph import (
    TaskGraph
)


def main():
    graph = TaskGraph()

    graph.add_task(

        "code",

        "create_file",

        "memory/graph1.txt"
    )

    graph.add_task(

        "code",

        "create_file",

        "memory/graph2.txt"
    )

    graph.add_task(

        "code",

        "create_file",

        "memory/final.txt",

        depends_on="create_file"
    )

    results = graph.run()

    print(results)


if __name__ == "__main__":
    main()
