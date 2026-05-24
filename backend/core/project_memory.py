import json
import logging
import os
import tempfile
import threading
import uuid

from datetime import datetime
from typing import Dict
from typing import List

# =========================================
# LOGGER
# =========================================

logger = logging.getLogger(
    "helios-project-memory"
)

# =========================================
# CONFIG
# =========================================

MEMORY_DIR = "memory"

MEMORY_PATH = (
    f"{MEMORY_DIR}/project_memory.json"
)

BACKUP_PATH = (
    f"{MEMORY_DIR}/project_memory.backup.json"
)

MAX_PROJECTS = 100

# =========================================
# THREAD LOCK
# =========================================

memory_lock = threading.Lock()

# =========================================
# ENSURE DIRECTORY
# =========================================

os.makedirs(

    MEMORY_DIR,

    exist_ok=True
)

# =========================================
# ATOMIC WRITE
# =========================================

def atomic_write(

    path: str,
    data

) -> bool:

    try:

        with tempfile.NamedTemporaryFile(

            "w",

            delete=False,

            encoding="utf-8",

            dir=MEMORY_DIR

        ) as temp_file:

            json.dump(

                data,

                temp_file,

                indent=4,

                ensure_ascii=False
            )

            temp_path = temp_file.name

        os.replace(

            temp_path,

            path
        )

        return True

    except Exception as e:

        logger.warning(

            "[PROJECT MEMORY WRITE ERROR]: %s",

            str(e)
        )

        return False

# =========================================
# VALIDATE PROJECT
# =========================================

def validate_project(

    item: Dict

) -> bool:

    required_keys = [

        "id",
        "title",
        "summary",
        "timestamp"
    ]

    return all(

        key in item

        for key in required_keys
    )

# =========================================
# LOAD MEMORY
# =========================================

def load_project_memory() -> List[Dict]:

    with memory_lock:

        if not os.path.exists(
            MEMORY_PATH
        ):

            return []

        try:

            with open(

                MEMORY_PATH,

                "r",

                encoding="utf-8"

            ) as file:

                data = json.load(file)

            if not isinstance(
                data,
                list
            ):

                logger.warning(
                    "Project memory structure invalid."
                )

                return []

            validated = [

                item

                for item in data

                if validate_project(
                    item
                )
            ]

            return validated

        except json.JSONDecodeError:

            logger.warning(
                "Project memory JSON corrupted."
            )

            # =============================
            # BACKUP RECOVERY
            # =============================

            if os.path.exists(
                BACKUP_PATH
            ):

                try:

                    with open(

                        BACKUP_PATH,

                        "r",

                        encoding="utf-8"

                    ) as backup:

                        backup_data = json.load(
                            backup
                        )

                    logger.warning(
                        "Recovered project memory from backup."
                    )

                    return backup_data

                except Exception:

                    return []

            return []

        except Exception as e:

            logger.warning(

                "[PROJECT MEMORY LOAD ERROR]: %s",

                str(e)
            )

            return []

# =========================================
# SAVE MEMORY
# =========================================

def save_project_memory(

    memory: List[Dict]

) -> bool:

    with memory_lock:

        try:

            trimmed_memory = (

                memory[
                    -MAX_PROJECTS:
                ]
            )

            # =============================
            # BACKUP CURRENT FILE
            # =============================

            if os.path.exists(
                MEMORY_PATH
            ):

                try:

                    with open(

                        MEMORY_PATH,

                        "r",

                        encoding="utf-8"

                    ) as original:

                        existing_data = json.load(
                            original
                        )

                    atomic_write(

                        BACKUP_PATH,

                        existing_data
                    )

                except Exception:

                    pass

            return atomic_write(

                MEMORY_PATH,

                trimmed_memory
            )

        except Exception as e:

            logger.warning(

                "[PROJECT MEMORY SAVE ERROR]: %s",

                str(e)
            )

            return False

# =========================================
# ADD PROJECT MEMORY
# =========================================

def add_project_memory(

    title: str,
    summary: str

) -> Dict:

    memory = load_project_memory()

    project = {

        "id":
        str(uuid.uuid4()),

        "title":
        str(title).strip(),

        "summary":
        str(summary).strip(),

        "timestamp":
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    }

    memory.append(
        project
    )

    save_project_memory(
        memory
    )

    return project

# =========================================
# SEARCH PROJECT MEMORY
# =========================================

def search_project_memory(

    keyword: str

) -> List[Dict]:

    memory = load_project_memory()

    keyword = str(
        keyword
    ).lower().strip()

    if not keyword:

        return []

    results = []

    for item in memory:

        title = str(
            item.get("title", "")
        ).lower()

        summary = str(
            item.get("summary", "")
        ).lower()

        if (

            keyword in title
            or
            keyword in summary

        ):

            results.append(
                item
            )

    return results

# =========================================
# GET RECENT PROJECTS
# =========================================

def get_recent_projects(

    limit: int = 10

) -> List[Dict]:

    memory = load_project_memory()

    if limit <= 0:

        return []

    return memory[-limit:]

# =========================================
# DELETE PROJECT
# =========================================

def delete_project_memory(

    project_id: str

) -> bool:

    try:

        memory = load_project_memory()

        filtered_memory = [

            item

            for item in memory

            if item.get("id")
            != project_id
        ]

        return save_project_memory(
            filtered_memory
        )

    except Exception as e:

        logger.warning(

            "[PROJECT MEMORY DELETE ERROR]: %s",

            str(e)
        )

        return False

# =========================================
# CLEAR MEMORY
# =========================================

def clear_project_memory() -> bool:

    with memory_lock:

        try:

            return atomic_write(

                MEMORY_PATH,

                []
            )

        except Exception as e:

            logger.warning(

                "[PROJECT MEMORY CLEAR ERROR]: %s",

                str(e)
            )

            return False

# =========================================
# MEMORY STATS
# =========================================

def get_project_memory_stats() -> Dict:

    memory = load_project_memory()

    total_projects = len(memory)

    total_characters = sum(

        len(
            str(item.get("title", ""))
        )

        +

        len(
            str(item.get("summary", ""))
        )

        for item in memory
    )

    usage = min(

        round(

            (
                total_projects
                / MAX_PROJECTS
            ) * 100,

            2
        ),

        100
    )

    return {

        "projects":
        total_projects,

        "max_capacity":
        MAX_PROJECTS,

        "storage":
        MEMORY_PATH,

        "backup":
        BACKUP_PATH,

        "storage_usage_percent":
        usage,

        "total_characters":
        total_characters
    }