import json
import os

MEMORY_FILE = "memory/user_memory.json"

os.makedirs("memory", exist_ok=True)

def load_memory():

    if not os.path.exists(MEMORY_FILE):
        return {}

    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_memory(memory):

    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

def remember(key, value):

    memory = load_memory()

    memory[key] = value

    save_memory(memory)

def recall(key):

    memory = load_memory()

    return memory.get(key) 