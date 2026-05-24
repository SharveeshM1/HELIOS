import os

def create_file(path, content=""):

    try:

        directory = os.path.dirname(path)

        if directory:

            os.makedirs(
                directory,
                exist_ok=True
            )

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(str(content))

        return f"File created: {path}"

    except Exception as e:

        return f"FILE CREATION FAILED: {str(e)}"


def read_file(path):

    try:

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            return file.read()

    except Exception as e:

        return f"FILE READ FAILED: {str(e)}"


def append_file(path, content):

    try:

        with open(
            path,
            "a",
            encoding="utf-8"
        ) as file:

            file.write(str(content))

        return f"Updated: {path}"

    except Exception as e:

        return f"FILE APPEND FAILED: {str(e)}"
