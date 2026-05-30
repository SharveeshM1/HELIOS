import json
import logging
import os
import re
import tempfile
import threading

from datetime import datetime
from pathlib import Path
from typing import Dict
from typing import List

from core.runtime_config import MEMORY_DIR as RUNTIME_MEMORY_DIR
from core.runtime_config import ensure_runtime_dirs

# =========================================
# LOGGER
# =========================================

logger = logging.getLogger(
    "helios-memory"
)

# =========================================
# MEMORY CONFIG
# =========================================

MEMORY_DIR = str(
    RUNTIME_MEMORY_DIR
)

MEMORY_FILE = (
    str(
        Path(MEMORY_DIR) / "chat_history.json"
    )
)

BACKUP_FILE = (
    str(
        Path(MEMORY_DIR) / "chat_history.backup.json"
    )
)

MAX_MEMORY_ITEMS = 100

# =========================================
# THREAD LOCK
# =========================================

memory_lock = threading.Lock()

# =========================================
# ENSURE DIRECTORY
# =========================================

ensure_runtime_dirs()

# =========================================
# SAFE JSON WRITE
# =========================================

def atomic_write(
    path: str,
    data
) -> bool:

    try:

        with tempfile.NamedTemporaryFile(
            mode="w",
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
            "[HELIOS ATOMIC WRITE ERROR]: %s",
            str(e)
        )

        return False

# =========================================
# VALIDATE MEMORY ITEM
# =========================================

def validate_memory_item(
    item: Dict
) -> bool:

    required_keys = [

        "timestamp",

        "user",

        "assistant"
    ]

    return all(
        key in item
        for key in required_keys
    )

# =========================================
# LOAD MEMORY
# =========================================

def load_memory() -> List[Dict]:

    with memory_lock:

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

                data = json.load(file)

            if not isinstance(
                data,
                list
            ):

                logger.warning(
                    "Memory file invalid structure."
                )

                return []

            validated = [

                item

                for item in data

                if validate_memory_item(
                    item
                )
            ]

            return validated

        except json.JSONDecodeError:

            logger.warning(
                "Memory JSON corrupted."
            )

            # =================================
            # BACKUP RECOVERY
            # =================================

            if os.path.exists(
                BACKUP_FILE
            ):

                try:

                    with open(
                        BACKUP_FILE,
                        "r",
                        encoding="utf-8"
                    ) as backup:

                        backup_data = json.load(
                            backup
                        )

                    logger.warning(
                        "Recovered from backup memory."
                    )

                    if isinstance(
                        backup_data,
                        list
                    ):

                        return [
                            item
                            for item in backup_data
                            if validate_memory_item(
                                item
                            )
                        ]

                    return []

                except Exception:

                    return []

            return []

        except Exception as e:

            logger.warning(
                "[HELIOS MEMORY LOAD ERROR]: %s",
                str(e)
            )

            return []

# =========================================
# SAVE MEMORY
# =========================================

def save_memory(
    chat_history: List[Dict]
) -> bool:

    with memory_lock:

        try:

            trimmed_history = (

                chat_history[
                    -MAX_MEMORY_ITEMS:
                ]
            )

            # =================================
            # BACKUP CURRENT MEMORY
            # =================================

            if os.path.exists(
                MEMORY_FILE
            ):

                try:

                    with open(
                        MEMORY_FILE,
                        "r",
                        encoding="utf-8"
                    ) as original:

                        current_data = json.load(
                            original
                        )

                    atomic_write(
                        BACKUP_FILE,
                        current_data
                    )

                except Exception:

                    pass

            return atomic_write(
                MEMORY_FILE,
                trimmed_history
            )

        except Exception as e:

            logger.warning(
                "[HELIOS MEMORY SAVE ERROR]: %s",
                str(e)
            )

            return False

# =========================================
# ADD MEMORY
# =========================================

def add_to_memory(
    chat_history: List[Dict],
    user: str,
    assistant: str
) -> List[Dict]:

    memory_item = {

        "timestamp":
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        "user":
        str(user).strip(),

        "assistant":
        str(assistant).strip()
    }

    chat_history.append(
        memory_item
    )

    save_memory(
        chat_history
    )

    return chat_history

# =========================================
# CLEAR MEMORY
# =========================================

def clear_memory() -> bool:

    with memory_lock:

        try:

            return atomic_write(
                MEMORY_FILE,
                []
            )

        except Exception as e:

            logger.warning(
                "[HELIOS MEMORY CLEAR ERROR]: %s",
                str(e)
            )

            return False

# =========================================
# DELETE MEMORY ITEM
# =========================================

def delete_memory_item(
    chat_history: List[Dict],
    index: int
) -> List[Dict]:

    try:

        if (
            0 <= index
            < len(chat_history)
        ):

            del chat_history[index]

            save_memory(
                chat_history
            )

    except Exception as e:

        logger.warning(
            "[HELIOS MEMORY DELETE ERROR]: %s",
            str(e)
        )

    return chat_history

# =========================================
# SEARCH MEMORY
# =========================================

def search_memory(
    chat_history: List[Dict],
    query: str
) -> List[Dict]:

    query = str(query).lower().strip()

    if not query:

        return []

    query_terms = {
        term
        for term in re.findall(
            r"[a-z0-9_]{3,}",
            query
        )
    }

    ranked = []

    for item in chat_history:

        user_text = str(
            item.get("user", "")
        ).lower()

        assistant_text = str(
            item.get("assistant", "")
        ).lower()

        combined = f"{user_text} {assistant_text}"

        exact_match = query in combined

        score = sum(
            combined.count(term)
            for term in query_terms
        )

        if exact_match:

            score += 5

        if score:

            ranked.append(
                (
                    score,
                    item.get("timestamp", ""),
                    item
                )
            )

    ranked.sort(
        key=lambda result: (
            result[0],
            result[1]
        ),
        reverse=True
    )

    return [
        item
        for _, __, item in ranked
    ]

# =========================================
# RECENT MEMORY
# =========================================

def get_recent_memory(
    chat_history: List[Dict],
    limit: int = 10
) -> List[Dict]:

    if limit <= 0:

        return []

    return chat_history[-limit:]

# =========================================
# MEMORY STATS
# =========================================

def get_memory_stats(
    chat_history: List[Dict]
) -> Dict:

    total_items = len(
        chat_history
    )

    total_chars = sum(

        len(
            str(item.get("user", ""))
        )

        +

        len(
            str(item.get("assistant", ""))
        )

        for item in chat_history
    )

    usage = min(

        round(

            (
                total_items
                / MAX_MEMORY_ITEMS
            ) * 100,

            2
        ),

        100
    )

    return {

        "total_conversations":
        total_items,

        "memory_file":
        MEMORY_FILE,

        "backup_file":
        BACKUP_FILE,

        "max_capacity":
        MAX_MEMORY_ITEMS,

        "storage_usage_percent":
        usage,

        "total_characters":
        total_chars
    }
