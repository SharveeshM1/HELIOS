import os
import sys

def check_env():
    example_path = ".env.example"
    env_path = ".env"

    if not os.path.exists(example_path):
        print(f"Error: {example_path} not found.")
        return

    if not os.path.exists(env_path):
        print(f"Warning: {env_path} not found. Please create it from {example_path}.")
        return

    with open(example_path, "r") as f:
        example_vars = {line.split("=")[0] for line in f if "=" in line and not line.startswith("#")}

    with open(env_path, "r") as f:
        env_vars = {line.split("=")[0] for line in f if "=" in line and not line.startswith("#")}

    missing = example_vars - env_vars

    if missing:
        print("❌ Missing environment variables in .env:")
        for var in sorted(missing):
            print(f"  - {var}")
        sys.exit(1)
    else:
        print("✅ Environment variables are up to date.")

if __name__ == "__main__":
    check_env()
