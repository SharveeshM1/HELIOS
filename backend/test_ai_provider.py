from api.ai_provider import (
    generate_ai_response
)


def main():
    response = generate_ai_response(

        "Explain AI agents in one paragraph"

    )

    print(response)


if __name__ == "__main__":
    main()
