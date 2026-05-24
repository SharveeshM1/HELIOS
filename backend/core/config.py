MODEL_NAME = "qwen2.5:3b"

# =========================================
# HELIOS CONFIG
# =========================================

APP_NAME = "HELIOS"

VERSION = "1.0.0"

# =========================================
# GEMINI
# =========================================

TEMPERATURE = 0.7

TOP_P = 0.95

TOP_K = 40

MAX_OUTPUT_TOKENS = 4096

# =========================================
# AUTONOMOUS LOOP
# =========================================

MAX_ITERATIONS = 10

MAX_QUERY_CHARS = 2500

MAX_OUTPUT_CHARS = 4000

LOOP_SLEEP_TIME = 0.15

# =========================================
# MEMORY
# =========================================

MAX_SHARED_MEMORY = 500

MAX_CHAT_HISTORY = 100

MAX_PROJECT_MEMORY = 200

# =========================================
# FILES
# =========================================

SUPPORTED_FILE_TYPES = [

    "txt",
    "md",
    "py"
]

MAX_FILE_SIZE_MB = 15

# =========================================
# UI
# =========================================

THEME = "dark"

PRIMARY_COLOR = "#7c3aed"

SECONDARY_COLOR = "#2563eb"

SUCCESS_COLOR = "#22c55e"

ERROR_COLOR = "#ef4444"

WARNING_COLOR = "#f59e0b"

# =========================================
# VOICE
# =========================================

VOICE_ENABLED = True

VOICE_LANGUAGE = "en"

TTS_ENABLED = True

# =========================================
# SYSTEM
# =========================================

DEBUG = False

ENABLE_TELEMETRY = True

ENABLE_REASONING = True

ENABLE_SWARM = True

ENABLE_AUTONOMOUS_LOOP = True
