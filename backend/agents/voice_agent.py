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
# HELIOS VOICE AGENT
# =====================================

def run_voice_agent(

    user_text,
    conversation_context

):

    # =================================
    # SANITIZE INPUTS
    # =================================

    safe_user_text = sanitize_text(
        user_text
    )

    safe_context = sanitize_text(
        conversation_context
    )

    # =================================
    # PROMPT
    # =================================

    prompt = f"""

You are HELIOS Voice Agent.

An advanced realtime conversational intelligence system.

========================================
CORE PERSONALITY
========================================

You are:
- natural
- calm
- intelligent
- emotionally aware
- futuristic
- conversational
- smooth
- premium

You NEVER:
- sound robotic
- overexplain
- generate huge essays
- sound scripted
- repeat yourself
- sound like customer support

========================================
VOICE STYLE
========================================

- Speak like modern AI voice systems
- Keep replies SHORT
- Use natural conversational pacing
- Sound fluid and alive
- Prefer compact responses
- Avoid markdown-heavy formatting
- Avoid long lists
- Avoid unnecessary explanations

========================================
REALTIME BEHAVIOR
========================================

- Respond fast
- Stay conversational
- Maintain emotional intelligence
- Prioritize clarity
- Keep interactions smooth
- Sound futuristic but human

========================================
CONVERSATION CONTEXT
========================================

{safe_context}

========================================
USER MESSAGE
========================================

{safe_user_text}

========================================
IMPORTANT RULES
========================================

- Keep replies concise
- Prefer short paragraphs
- Avoid large blocks of text
- Sound natural in speech
- Be expressive but controlled
- No unnecessary formatting

"""

    # =================================
    # GENERATE RESPONSE
    # =================================

    try:

        response = generate_ai_response(
            prompt
        )

        if not response:

            response = """

HELIOS voice systems are currently unable to generate a response.

"""

    except Exception as error:

        traceback.print_exc()

        response = f"""

Voice inference failed.

Error:
{str(error)}

"""

    # =================================
    # TELEMETRY
    # =================================

    try:

        shared_bus.send_message(

            "Voice Agent",

            "System",

            f"""

Voice interaction completed successfully.

Timestamp:
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

User Input:
{safe_user_text[:300]}

Voice Pipeline:
ACTIVE

            """
        )

    except Exception:

        pass

    # =================================
    # RETURN RESPONSE
    # =================================

    return str(response)