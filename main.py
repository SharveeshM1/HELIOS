import os
import runpy
import sys


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")


def main():

    os.chdir(BACKEND_DIR)

    if BACKEND_DIR not in sys.path:
        sys.path.insert(0, BACKEND_DIR)

    runpy.run_path(
        os.path.join(BACKEND_DIR, "main.py"),
        run_name="__main__"
    )


if __name__ == "__main__":
    main()