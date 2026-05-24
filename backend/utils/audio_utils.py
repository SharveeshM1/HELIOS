import os
import glob
import time
import shutil
import logging

from datetime import datetime

# =====================================
# LOGGER
# =====================================

logger = logging.getLogger(
    "helios-audio"
)

# =====================================
# AUDIO CONFIG
# =====================================

TEMP_AUDIO_DIR = "temp_audio"

MAX_AUDIO_FILES = 40

MAX_AUDIO_AGE_SECONDS = 3600

SUPPORTED_EXTENSIONS = [

    ".webm",

    ".wav",

    ".mp3"
]

# =====================================
# ENSURE DIRECTORY
# =====================================

os.makedirs(

    TEMP_AUDIO_DIR,

    exist_ok=True
)

# =====================================
# GET AUDIO FILES
# =====================================

def get_audio_files():

    files = []

    try:

        for ext in SUPPORTED_EXTENSIONS:

            files.extend(

                glob.glob(
                    f"{TEMP_AUDIO_DIR}/*{ext}"
                )
            )

    except Exception as e:

        logger.warning(

            "[HELIOS AUDIO SCAN ERROR]: %s",

            str(e)
        )

    return files

# =====================================
# FILE METADATA
# =====================================

def get_file_metadata(

    filepath

):

    try:

        stats = os.stat(filepath)

        return {

            "path":
            filepath,

            "size":
            stats.st_size,

            "created":
            stats.st_ctime,

            "modified":
            stats.st_mtime
        }

    except Exception:

        return None

# =====================================
# SAFE REMOVE
# =====================================

def safe_remove(

    filepath

):

    try:

        if os.path.exists(filepath):

            os.remove(filepath)

            return True

    except Exception as e:

        logger.warning(

            "[HELIOS AUDIO DELETE ERROR]: %s",

            str(e)
        )

    return False

# =====================================
# CLEANUP AUDIO FILES
# =====================================

def cleanup_audio_files():

    deleted = 0

    scanned = 0

    now = time.time()

    try:

        files = get_audio_files()

        scanned = len(files)

        for file in files:

            try:

                metadata = get_file_metadata(
                    file
                )

                if not metadata:

                    continue

                age = (
                    now - metadata["modified"]
                )

                # =========================
                # REMOVE OLD FILES
                # =========================

                if age > MAX_AUDIO_AGE_SECONDS:

                    if safe_remove(file):

                        deleted += 1

            except Exception as e:

                logger.warning(

                    "[HELIOS AUDIO CLEAN ERROR]: %s",

                    str(e)
                )

        # =================================
        # LIMIT FILE COUNT
        # =================================

        remaining_files = get_audio_files()

        if len(remaining_files) > MAX_AUDIO_FILES:

            remaining_files.sort(

                key=lambda x:
                os.path.getmtime(x)
            )

            overflow = (

                len(remaining_files)

                - MAX_AUDIO_FILES
            )

            for file in remaining_files[:overflow]:

                if safe_remove(file):

                    deleted += 1

        logger.info(

            "[HELIOS AUDIO CLEANUP] scanned=%s deleted=%s",

            scanned,

            deleted
        )

        return {

            "status":"completed",

            "scanned":
            scanned,

            "deleted":
            deleted,

            "timestamp":
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        }

    except Exception as e:

        logger.warning(

            "[AUDIO CLEANUP ERROR]: %s",

            str(e)
        )

        return {

            "status":"failed",

            "error":
            str(e)
        }

# =====================================
# GET AUDIO FILE COUNT
# =====================================

def get_audio_file_count():

    try:

        return len(
            get_audio_files()
        )

    except Exception:

        return 0

# =====================================
# AUDIO STORAGE SIZE
# =====================================

def get_audio_storage_size():

    try:

        total = 0

        for file in get_audio_files():

            if os.path.exists(file):

                total += os.path.getsize(
                    file
                )

        return round(

            total / (1024 * 1024),

            2
        )

    except Exception:

        return 0

# =====================================
# RESET AUDIO DIRECTORY
# =====================================

def reset_audio_directory():

    try:

        if os.path.exists(
            TEMP_AUDIO_DIR
        ):

            shutil.rmtree(
                TEMP_AUDIO_DIR
            )

        os.makedirs(

            TEMP_AUDIO_DIR,

            exist_ok=True
        )

        logger.info(
            "Audio directory reset."
        )

        return True

    except Exception as e:

        logger.warning(

            "[HELIOS AUDIO RESET ERROR]: %s",

            str(e)
        )

        return False

# =====================================
# AUDIO HEALTH REPORT
# =====================================

def audio_health_report():

    return {

        "directory":
        TEMP_AUDIO_DIR,

        "audio_files":
        get_audio_file_count(),

        "storage_mb":
        get_audio_storage_size(),

        "max_files":
        MAX_AUDIO_FILES,

        "max_age_seconds":
        MAX_AUDIO_AGE_SECONDS,

        "status":
        "healthy"
    }