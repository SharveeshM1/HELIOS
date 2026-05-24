from datetime import datetime
import traceback

from api.ai_provider import ( # type: ignore
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
# ANALYTICS TOOL EXECUTION
# =========================================

def analytics_execution(

    objective

):

    logs = []

    try:

        result = execute_agent_tool(

            "analytics",

            "run_command",

            "pwd"

        )

        logs.append(
            str(result)
        )

    except Exception as e:

        logs.append(
            str(e)
        )

    return "\n".join(logs)


# =========================================
# ANALYTICS AGENT
# =========================================

def run_analytics_agent(

    query,
    web_results,
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

    safe_context = sanitize_text(
        conversation_context
    )

    # =====================================
    # SYSTEM PROMPT
    # =====================================

    prompt = f"""

You are HELIOS Analytics Agent.

An elite AI telemetry,
optimization,
and infrastructure intelligence system.

========================================
CORE IDENTITY
========================================

You are:
- analytical
- futuristic
- concise
- systems-focused
- performance-oriented
- optimization-driven

You NEVER:
- sound robotic
- overexplain
- generate filler
- sound like customer support
- give generic advice
- repeat the same points

========================================
MISSION
========================================

Your responsibilities:

- analyze system behavior
- detect infrastructure bottlenecks
- optimize execution pipelines
- improve scalability
- identify weak points
- evaluate performance
- forecast operational risks
- generate strategic insights

========================================
THINKING STYLE
========================================

- Think like a principal systems architect
- Think in terms of scaling + optimization
- Focus on infrastructure efficiency
- Prioritize practical improvements
- Be concise but high IQ
- Avoid bloated explanations

========================================
CONVERSATION CONTEXT
========================================

{safe_context}

========================================
WEB RESULTS
========================================

{safe_web_results}

========================================
USER REQUEST
========================================

{safe_query}

========================================
RESPONSE STRUCTURE
========================================

Generate ONLY these sections:

# ⚡ Metrics Analysis

# 📊 Performance Insights

# 🚨 System Bottlenecks

# 🚀 Optimization Strategy

# 🌍 Scalability Forecast

# ✅ Operational Summary

========================================
IMPORTANT RULES
========================================

- Use markdown formatting
- Keep responses sharp
- Avoid walls of text
- Avoid repeating headers
- No fake metrics
- No hallucinated infrastructure
- No corporate fluff

"""

    # =====================================
    # GENERATE RESPONSE
    # =====================================

    try:

        response = generate_ai_response(
            prompt
        )

        execution_logs = analytics_execution(

            safe_query

        )

        response += f"""

# 📡 Analytics Execution

{execution_logs}

"""

        if not response:

            response = """

# ⚡ Metrics Analysis

No analytics response generated.

# 📊 Performance Insights

The analytics pipeline returned an empty result.

# 🚨 System Bottlenecks

Unable to evaluate infrastructure conditions.

# 🚀 Optimization Strategy

Retry analytics execution.

# 🌍 Scalability Forecast

Forecast unavailable.

# ✅ Operational Summary

Analytics engine completed with empty output.

"""

    except Exception as error:

        traceback.print_exc()

        response = f"""

# ⚡ Metrics Analysis

Analytics execution failed.

# 📊 Performance Insights

An internal processing error occurred.

# 🚨 System Bottlenecks

{str(error)}

# 🚀 Optimization Strategy

Validate AI connectivity and analytics infrastructure.

# 🌍 Scalability Forecast

Unavailable due to execution failure.

# ✅ Operational Summary

HELIOS Analytics Agent terminated unexpectedly.

"""

    # =====================================
    # SHARED BUS TELEMETRY
    # =====================================

    try:

        shared_bus.send_message(

            "Analytics Agent",

            "System",

            f"""

Analytics evaluation completed successfully.

Timestamp:
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Query:
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
