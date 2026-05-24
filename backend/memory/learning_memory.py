import json
import os

MEMORY_FILE = "memory/learning_memory.json"

# =====================================
# LOAD MEMORY
# =====================================

if os.path.exists(MEMORY_FILE):

    with open(MEMORY_FILE, "r") as f:

        learning_memory = json.load(f)

else:

    learning_memory = []

# =====================================
# STORE LEARNING
# =====================================

def store_learning(entry):

    learning_memory.append(entry)

    with open(MEMORY_FILE, "w") as f:

        json.dump(
            learning_memory,
            f,
            indent=2
        )

# =====================================
# GET MEMORY
# =====================================

def get_learning_memory():

    return learning_memory[-20:]