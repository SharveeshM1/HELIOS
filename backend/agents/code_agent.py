from datetime import datetime
import traceback

from api.ai_provider import (
    generate_ai_response
)

from core.tool_executor import (
    execute_agent_tool
)

from core.shared_bus import (
    shared_bus
)

from utils.ui_utils import (
    sanitize_text
)


# =========================================
# CODE INTELLIGENCE AGENT
# =========================================


# =========================================
# AUTONOMOUS TOOL EXECUTION
# =========================================

def autonomous_execute(

    objective

):

    logs = []

    objective_comment = "\n".join(
        f"# {line}"
        for line in str(objective).splitlines()
    )

    try:

        # =================================
        # CREATE FILE
        # =================================

        result = execute_agent_tool(

            "code",

            "create_file",

            "memory/auto_generated.py",

            f"# HELIOS GENERATED FILE\n\n# OBJECTIVE\n{objective_comment}\n"
        )

        logs.append(
            str(result)
        )

    except Exception as e:

        logs.append(
            str(e)
        )

    return "\n".join(logs)


def run_code_agent(

    query,
    file_content,
    conversation_context

):

    # =====================================
    # SANITIZE INPUTS
    # =====================================

    safe_query = sanitize_text(
        query
    )

    safe_file_content = sanitize_text(
        file_content
    )

    safe_context = sanitize_text(
        conversation_context
    )

    # =====================================
    # SHARED AGENT MEMORY
    # =====================================

    messages = shared_bus.get_messages()

    shared_context = ""

    try:

        for message in messages[-12:]:

            sender = sanitize_text(
                message.get("sender", "Unknown")
            )

            receiver = sanitize_text(
                message.get("receiver", "Unknown")
            )

            content = sanitize_text(
                message.get("content", "")
            )

            shared_context += f"""

FROM:
{sender}

TO:
{receiver}

CONTENT:
{content}

-----------------------------------

"""

    except Exception:

        shared_context = "Shared agent memory unavailable."

    # =====================================
    # SYSTEM PROMPT
    # =====================================

    prompt = f"""

You are HELIOS Code Intelligence Agent.

An elite AI software architect,
systems engineer,
and production infrastructure specialist.

========================================
CORE IDENTITY
========================================

You are:
- highly technical
- architecture-focused
- optimization-driven
- concise
- futuristic
- production-oriented

You NEVER:
- overexplain basics
- generate beginner fluff
- create bloated architecture
- produce messy code
- repeat generic advice
- write unnecessary filler

========================================
MISSION
========================================

Your responsibilities:

- debugging
- software architecture
- optimization
- scalability engineering
- performance tuning
- infrastructure analysis
- production hardening
- clean implementation strategy

========================================
ENGINEERING STYLE
========================================

- Think like a principal engineer
- Prefer scalable architecture
- Optimize intelligently
- Focus on maintainability
- Prefer clean abstractions
- Use modern engineering practices
- Keep explanations compact but high IQ

========================================
CONVERSATION CONTEXT
========================================

{safe_context}

========================================
SHARED AGENT MEMORY
========================================

{shared_context}

========================================
UPLOADED FILES / SOURCE CODE
========================================

{safe_file_content}

========================================
USER REQUEST
========================================

{safe_query}

========================================
RESPONSE STRUCTURE
========================================

Generate ONLY these sections:

# ⚡ Problem Analysis

# 🧠 Architecture Strategy

# 💻 Optimized Solution

# 🚀 Scalability Improvements

# 🔒 Production Recommendations

========================================
IMPORTANT RULES
========================================

- Use markdown formatting
- Prefer production-grade thinking
- Avoid fake claims
- Avoid hallucinated APIs
- Keep responses concise
- Focus on engineering quality
- Think like a senior architect

"""

    # =====================================
    # GENERATE RESPONSE
    # =====================================

    try:

        response = generate_ai_response(
            prompt
        )

        execution_logs = autonomous_execute(

            safe_query

        )

        response += f"""

# 🤖 Autonomous Execution

{execution_logs}

"""

        if not response:

            response = """

# ⚡ Problem Analysis

No response generated.

# 🧠 Architecture Strategy

The code intelligence pipeline returned an empty result.

# 💻 Optimized Solution

Unable to generate implementation guidance.

# 🚀 Scalability Improvements

Scalability analysis unavailable.

# 🔒 Production Recommendations

Retry the request after validating the AI infrastructure.

"""

    except Exception as error:

        traceback.print_exc()

        response = f"""

# ⚡ Problem Analysis

Code intelligence execution failed.

# 🧠 Architecture Strategy

An internal processing error occurred.

# 💻 Optimized Solution

{str(error)}

# 🚀 Scalability Improvements

Unable to evaluate scalability conditions.

# 🔒 Production Recommendations

Validate AI connectivity and production inference systems.

"""

    # =====================================
    # TELEMETRY
    # =====================================

    try:

        shared_bus.send_message(

            "Code Agent",

            "System",

            f"""

Code intelligence execution completed.

Timestamp:
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Request:
{safe_query[:300]}

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
