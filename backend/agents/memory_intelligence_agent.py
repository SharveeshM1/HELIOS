from datetime import datetime
import traceback

from api.ai_provider import (
    generate_ai_response
)

from core.shared_bus import (
    shared_bus
)

from utils.ui_utils import (
    sanitize_text
)

# =========================================
# MEMORY INTELLIGENCE AGENT
# =========================================

def summarize_project(

    user_input,
    ai_output

):

    # =====================================
    # SANITIZE INPUTS
    # =====================================

    safe_user_input = sanitize_text(
        user_input
    )

    safe_ai_output = sanitize_text(
        ai_output
    )

    # =====================================
    # PROMPT
    # =====================================

    prompt = f"""

You are HELIOS Memory Intelligence Agent.

An advanced persistent cognition system
responsible for long-term project memory.

========================================
CORE OBJECTIVE
========================================

Your responsibilities:

- consolidate strategic memory
- extract technical intelligence
- identify project direction
- preserve architecture decisions
- detect future objectives
- retain high-value context
- maintain persistent cognition

========================================
PERSONALITY
========================================

You are:
- concise
- intelligent
- strategic
- futuristic
- context-aware
- systems-oriented

You NEVER:
- generate filler
- repeat information
- overexplain
- create bloated summaries
- sound generic

========================================
MEMORY STYLE
========================================

- high-signal
- technically aware
- strategically useful
- future-oriented
- concise

========================================
USER INPUT
========================================

{safe_user_input}

========================================
AI RESPONSE
========================================

{safe_ai_output}

========================================
REQUIRED OUTPUT
========================================

Generate ONLY:

# ⚡ Project Goals

# 💻 Technologies & Systems

# 🚀 Strategic Direction

# 🧠 Persistent Objectives

# 🔮 Future Plans

# ✅ Memory Snapshot

========================================
IMPORTANT RULES
========================================

- Use markdown formatting
- Keep summaries compact
- Preserve technical context
- Focus on future usefulness
- Avoid generic observations

"""

    # =====================================
    # GENERATE MEMORY
    # =====================================

    try:

        response = generate_ai_response(
            prompt
        )

        if not response:

            response = """

# ⚠️ Memory Snapshot Failure

No memory intelligence was generated.

"""

    except Exception as error:

        traceback.print_exc()

        response = f"""

# ⚠️ Memory Intelligence Failure

HELIOS memory systems encountered an execution error.

Error:
{str(error)}

"""

    # =====================================
    # TELEMETRY
    # =====================================

    try:

        shared_bus.send_message(

            "Memory Intelligence Agent",

            "Project Memory",

            f"""

Project memory consolidation completed.

Timestamp:
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

User Input Snapshot:
{safe_user_input[:300]}

Status:
SUCCESS

            """
        )

    except Exception:

        pass

    # =====================================
    # RETURN RESPONSE
    # =====================================

    return str(response)