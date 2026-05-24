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

# =====================================
# HELIOS MEMORY AGENT
# =====================================

def summarize_conversation(

    chat_history

):

    if not chat_history:

        return """

# 🧠 HELIOS Memory Core

No conversation history available for consolidation.

"""

    # =====================================
    # BUILD MEMORY CONTEXT
    # =====================================

    history_text = ""

    for chat in chat_history:

        try:

            user_message = sanitize_text(

                chat.get("user", "")

            )

            assistant_message = sanitize_text(

                chat.get("assistant", "")

            )

            history_text += f"""

========================================
USER
========================================

{user_message}

========================================
ASSISTANT
========================================

{assistant_message}

"""

        except Exception:

            continue

    # =====================================
    # MEMORY PROMPT
    # =====================================

    prompt = f"""

You are HELIOS Memory Intelligence Agent.

An advanced persistent cognition system
responsible for long-term contextual memory.

========================================
PERSONALITY
========================================

You are:
- strategic
- concise
- intelligent
- memory-focused
- context-aware
- systems-oriented

You NEVER:
- generate filler
- repeat unnecessary details
- overexplain
- produce bloated summaries
- sound robotic

========================================
OBJECTIVE
========================================

Your responsibilities:
- compress conversation history
- preserve important intelligence
- retain technical context
- identify ongoing projects
- detect future objectives
- maintain persistent cognition

========================================
MEMORY STYLE
========================================

- concise
- high-signal
- strategically useful
- future-oriented
- technically aware

========================================
CONVERSATION HISTORY
========================================

{history_text}

========================================
REQUIRED OUTPUT
========================================

Generate:

# ⚡ Key Topics

# 💻 Technical Discussions

# 🚀 Ongoing Projects

# 🧠 Persistent Objectives

# 🔮 Future Intentions

# ✅ Memory Summary

Keep the summary:
- concise
- strategically useful
- technically aware
- future-oriented

"""

    # =====================================
    # GENERATE MEMORY
    # =====================================

    try:

        response = generate_ai_response(
            prompt
        )

    except Exception as error:

        traceback.print_exc()

        response = f"""

# ⚠️ Memory Consolidation Failure

HELIOS memory systems encountered an execution failure.

Error:
{str(error)}

"""

    # =====================================
    # TELEMETRY
    # =====================================

    try:

        shared_bus.send_message(

            "Memory Agent",

            "System",

            f"""

Conversation memory consolidation completed.

Timestamp:
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Memory Entries:
{len(chat_history)}

Status:
SUCCESS

            """
        )

    except Exception:

        pass

    # =====================================
    # FINAL RESPONSE
    # =====================================

    return str(response)