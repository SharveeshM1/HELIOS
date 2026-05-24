import json
import os

# =========================================
# MEMORY FILE
# =========================================

MEMORY_FILE = (
    "memory/system_memory.json"
)

# =========================================
# LOAD MEMORY
# =========================================

def load_memory():

    if not os.path.exists(
        MEMORY_FILE
    ):

        return {}

    with open(

        MEMORY_FILE,

        "r",

        encoding="utf-8"

    ) as file:

        return json.load(file)

# =========================================
# SAVE MEMORY
# =========================================

def save_memory(memory):

    with open(

        MEMORY_FILE,

        "w",

        encoding="utf-8"

    ) as file:

        json.dump(

            memory,

            file,

            indent=4
        )

# =========================================
# STORE FACT
# =========================================

def store_fact(

    key,
    value

):

    memory = load_memory()

    memory[key] = value

    save_memory(memory)

# =========================================
# GET FACT
# =========================================

def get_fact(key):

    memory = load_memory()

    return memory.get(
        key,
        None
    )