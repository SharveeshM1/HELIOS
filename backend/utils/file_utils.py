import os
import logging

# =====================================
# LOGGER
# =====================================

logger = logging.getLogger(
    "helios-file-reader"
)

# =====================================
# CONFIG
# =====================================

MAX_FILE_SIZE_MB = 5

MAX_CHARS = 15000

SUPPORTED_TEXT_TYPES = [

    ".txt",

    ".py",

    ".js",

    ".ts",

    ".tsx",

    ".jsx",

    ".json",

    ".md",

    ".html",

    ".css",

    ".yaml",

    ".yml",

    ".xml",

    ".csv",

    ".java",

    ".cpp",

    ".c",

    ".rs",

    ".go",

    ".php",

    ".sql"
]

# =====================================
# SAFE TEXT
# =====================================

def safe_text(

    text

):

    try:

        return str(text).strip()

    except Exception:

        return ""

# =====================================
# FILE SIZE
# =====================================

def get_file_size_mb(

    uploaded_file

):

    try:

        uploaded_file.seek(

            0,

            os.SEEK_END
        )

        size = uploaded_file.tell()

        uploaded_file.seek(0)

        return round(

            size / (1024 * 1024),

            2
        )

    except Exception:

        return 0

# =====================================
# FILE EXTENSION
# =====================================

def get_extension(

    filename

):

    try:

        return os.path.splitext(

            str(filename)

        )[1].lower()

    except Exception:

        return ""

# =====================================
# VALIDATE FILE
# =====================================

def validate_uploaded_file(

    uploaded_file

):

    if uploaded_file is None:

        return (

            False,

            "No uploaded file detected."
        )

    file_size = get_file_size_mb(
        uploaded_file
    )

    if file_size > MAX_FILE_SIZE_MB:

        return (

            False,

            f"""

File exceeds maximum size.

Current:
{file_size} MB

Maximum:
{MAX_FILE_SIZE_MB} MB

            """
        )

    extension = get_extension(

        uploaded_file.name
    )

    if extension not in SUPPORTED_TEXT_TYPES:

        return (

            False,

            f"""

Unsupported file type.

Detected:
{extension}

Supported:
{', '.join(SUPPORTED_TEXT_TYPES)}

            """
        )

    return (

        True,

        "valid"
    )

# =====================================
# DECODE CONTENT
# =====================================

def decode_content(

    raw_data

):

    encodings = [

        "utf-8",

        "utf-16",

        "latin-1"
    ]

    for encoding in encodings:

        try:

            return raw_data.decode(
                encoding
            )

        except Exception:

            continue

    return raw_data.decode(

        "utf-8",

        errors="ignore"
    )

# =====================================
# CLEAN CONTENT
# =====================================

def clean_content(

    content

):

    content = safe_text(
        content
    )

    while "\n\n\n" in content:

        content = content.replace(

            "\n\n\n",

            "\n\n"
        )

    return content

# =====================================
# TRUNCATE CONTENT
# =====================================

def truncate_content(

    content,
    max_chars=MAX_CHARS

):

    if len(content) <= max_chars:

        return content

    return (

        content[:max_chars]

        +

        """



[FILE TRUNCATED]

Additional content omitted for
context optimization.

"""
    )

# =====================================
# READ FILE
# =====================================

def read_uploaded_file(

    uploaded_file

):

    try:

        # =================================
        # VALIDATION
        # =================================

        valid, message = (

            validate_uploaded_file(
                uploaded_file
            )
        )

        if not valid:

            return message

        # =================================
        # READ RAW DATA
        # =================================

        uploaded_file.seek(0)

        raw_data = uploaded_file.read()

        if not raw_data:

            return (
                "Uploaded file is empty."
            )

        # =================================
        # DECODE
        # =================================

        content = decode_content(
            raw_data
        )

        # =================================
        # CLEAN
        # =================================

        content = clean_content(
            content
        )

        if not content:

            return (
                "Uploaded file contains no readable content."
            )

        # =================================
        # TRUNCATE
        # =================================

        content = truncate_content(
            content
        )

        # =================================
        # METADATA HEADER
        # =================================

        metadata = f"""

[FILE CONTEXT]

Filename:
{uploaded_file.name}

Size:
{get_file_size_mb(uploaded_file)} MB

Extension:
{get_extension(uploaded_file.name)}

========================================

"""

        return metadata + content

    except Exception as e:

        logger.warning(

            "[HELIOS FILE READ ERROR]: %s",

            str(e)
        )

        return f"""

Unable to process uploaded file.

Error:
{str(e)}

"""

# =====================================
# FILE SUMMARY
# =====================================

def summarize_uploaded_file(

    uploaded_file

):

    try:

        return {

            "filename":
            uploaded_file.name,

            "size_mb":
            get_file_size_mb(
                uploaded_file
            ),

            "extension":
            get_extension(
                uploaded_file.name
            ),

            "supported":
            (

                get_extension(
                    uploaded_file.name
                )

                in

                SUPPORTED_TEXT_TYPES
            )
        }

    except Exception:

        return {

            "filename":"unknown",

            "size_mb":0,

            "extension":"unknown",

            "supported":False
        }