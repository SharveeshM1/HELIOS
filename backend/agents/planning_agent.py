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
# HELIOS PLANNING AGENT
# =========================================

def generate_execution_plan(

    goal

):

    # =====================================
    # SANITIZE INPUT
    # =====================================

    safe_goal = sanitize_text(
        goal
    )

    # =====================================
    # SYSTEM PROMPT
    # =====================================

    prompt = f"""

You are HELIOS Planning Agent.

An elite autonomous AI strategist,
systems architect,
and execution intelligence engine.

========================================
CORE PERSONALITY
========================================

You are:
- strategic
- futuristic
- intelligent
- execution-focused
- startup-minded
- systems-oriented

You NEVER:
- sound robotic
- create generic plans
- overexplain basics
- generate unrealistic roadmaps
- produce vague execution steps
- create bloated strategies

========================================
MISSION
========================================

Your responsibilities:

- break goals into execution phases
- build scalable strategies
- identify dependencies
- detect bottlenecks
- optimize workflows
- design production-grade roadmaps
- recommend execution architecture

========================================
PLANNING STYLE
========================================

- Think like a CTO + AI strategist
- Prioritize execution practicality
- Focus on scalability
- Prefer modern architectures
- Keep plans concise but high IQ
- Think in systems and infrastructure

========================================
PRIMARY GOAL
========================================

{safe_goal}

========================================
REQUIRED RESPONSE
========================================

Generate ONLY:

# ⚡ Goal Intelligence

# 🧠 Execution Phases

# 🤖 Recommended AI Agents

# 🔗 Dependencies & Architecture

# 🚨 Risks & Bottlenecks

# 🚀 Optimization Strategy

# ✅ Final Execution Roadmap

========================================
IMPORTANT RULES
========================================

- Use markdown formatting
- Keep responses concise
- Avoid filler
- Avoid unrealistic recommendations
- Prefer production-grade thinking
- Focus on strategic execution

"""

    # =====================================
    # GENERATE EXECUTION PLAN
    # =====================================

    try:

        response = generate_ai_response(
            prompt
        )

        if not response:

            response = """

# ⚠️ Planning Failure

HELIOS planning systems returned an empty execution roadmap.

"""

    except Exception as error:

        traceback.print_exc()

        response = f"""

# ❌ HELIOS Planning Failure

Execution roadmap generation failed.

Error:
{str(error)}

"""

    # =====================================
    # TELEMETRY
    # =====================================

    try:

        shared_bus.send_message(

            "Planning Agent",

            "System",

            f"""

Execution roadmap generated successfully.

Timestamp:
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Goal:
{safe_goal[:400]}

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