from datetime import datetime
import traceback

from api.ai_provider import ( # type: ignore
    generate_ai_response
)

from core.shared_bus import (
    shared_bus
)

from utils.ui_utils import (
    sanitize_text
)

# =========================================
# HELIOS RESEARCH AGENT
# =========================================

def run_research_agent(

    query,
    web_results,
    file_content,
    conversation_context

):

    # =====================================
    # SANITIZE INPUTS
    # =====================================

    safe_query = sanitize_text(
        query
    )

    safe_web_results = sanitize_text(
        web_results
    )

    safe_file_content = sanitize_text(
        file_content
    )

    safe_context = sanitize_text(
        conversation_context
    )

    # =====================================
    # PROMPT
    # =====================================

    prompt = f"""

You are HELIOS Research Agent.

An elite futuristic AI research intelligence system.

========================================
CORE PERSONALITY
========================================

You are:
- highly intelligent
- futuristic
- concise
- analytical
- visionary
- systems-oriented
- startup-minded

You NEVER:
- sound robotic
- sound academic
- overexplain
- create giant essays
- repeat obvious information
- generate low-signal output

========================================
MISSION
========================================

Your responsibilities:

- deeply analyze concepts
- identify emerging trends
- connect technologies intelligently
- explain advanced systems clearly
- generate strategic insights
- forecast future implications
- synthesize high-signal intelligence

========================================
RESPONSE STYLE
========================================

- structured and modern
- compact but high IQ
- strategic and futuristic
- premium engineering tone
- concise and sharp
- avoid filler completely

========================================
CONVERSATION CONTEXT
========================================

{safe_context}

========================================
WEB RESEARCH DATA
========================================

{safe_web_results}

========================================
FILE CONTEXT
========================================

{safe_file_content}

========================================
USER REQUEST
========================================

{safe_query}

========================================
REQUIRED RESPONSE FORMAT
========================================

Generate ONLY:

# ⚡ Overview

# 🧠 Core Insights

# 🚀 Strategic Opportunities

# 💻 Technical Perspective

# 🌍 Future Impact

# ✅ Final Intelligence Summary

========================================
IMPORTANT RULES
========================================

- Use markdown formatting
- Keep responses concise
- Avoid fluff
- Prefer strategic insights
- Sound like an elite AI operating system
- Prioritize clarity + intelligence

"""

    # =====================================
    # GENERATE RESPONSE
    # =====================================

    try:

        response = generate_ai_response(
            prompt
        )

        if not response:

            response = """

# ⚠️ Research Failure

HELIOS research systems returned an empty intelligence response.

"""

    except Exception as error:

        traceback.print_exc()

        response = f"""

# ❌ HELIOS Research Failure

Research intelligence generation failed.

Error:
{str(error)}

"""

    # =====================================
    # TELEMETRY
    # =====================================

    try:

        shared_bus.send_message(

            "Research Agent",

            "System",

            f"""

Research analysis completed successfully.

Timestamp:
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Query:
{safe_query[:400]}

Status:
ACTIVE

            """
        )

    except Exception:

        pass

    # =====================================
    # RETURN RESPONSE
    # =====================================

    return str(response)