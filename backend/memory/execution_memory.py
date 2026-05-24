import json
import os

MEMORY_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

MEMORY_FILE = os.path.join(
    MEMORY_DIR,
    "execution_history.json"
)

MAX_TEXT_CHARS = 8000


def make_json_safe(value):

    if value is None or isinstance(
        value,
        (
            bool,
            int,
            float
        )
    ):
        return value

    if isinstance(
        value,
        str
    ):
        if len(value) <= MAX_TEXT_CHARS:
            return value

        return (
            value[:MAX_TEXT_CHARS]
            +
            "\n\n[TRUNCATED]"
        )

    if isinstance(
        value,
        dict
    ):
        return {
            str(key): make_json_safe(item)
            for key, item in value.items()
        }

    if isinstance(
        value,
        (
            list,
            tuple,
            set
        )
    ):
        return [
            make_json_safe(item)
            for item in value
        ]

    return repr(value)

# =========================================
# LOAD MEMORY
# =========================================

def load_execution_memory():

    if not os.path.exists(
        MEMORY_FILE
    ):

        return []

    try:

        with open(

            MEMORY_FILE,

            "r",

            encoding="utf-8"

        ) as file:

            return json.load(file)

    except Exception:

        return []

# =========================================
# SAVE MEMORY
# =========================================

def save_execution_memory(

    memory

):

    os.makedirs(
        MEMORY_DIR,
        exist_ok=True
    )

    with open(

        MEMORY_FILE,

        "w",

        encoding="utf-8"

    ) as file:

        json.dump(

            make_json_safe(
                memory
            ),

            file,

            indent=4
        )

# =========================================
# STORE EXECUTION
# =========================================

def store_execution(

    objective,

    actions,

    results

):

    memory = load_execution_memory()

    memory.append({

        "objective":
        make_json_safe(
            objective
        ),

        "actions":
        make_json_safe(
            actions
        ),

        "results":
        make_json_safe(
            results
        )
    })

    save_execution_memory(
        memory
    )

# =========================================
# GET RECENT EXECUTIONS
# =========================================

def get_recent_executions(

    limit=5

):

    memory = load_execution_memory()

    return memory[-limit:]
