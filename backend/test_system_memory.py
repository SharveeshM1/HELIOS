from memory.system_memory import (

    store_fact,

    get_fact
)


def main():
    store_fact(

        "model_name",

        "qwen2.5:3b"
    )

    result = get_fact(
        "model_name"
    )

    print(result)


if __name__ == "__main__":
    main()
