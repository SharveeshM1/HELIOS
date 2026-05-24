from core.llm_action_engine import (
    generate_actions
)

result = generate_actions(

    "code",

    "Create a Python file for a calculator"

)

print(result)
