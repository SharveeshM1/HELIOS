from datetime import datetime
import traceback

from agents.research_agent import (
    run_research_agent
)

from agents.code_agent import (
    run_code_agent
)

from agents.analytics_agent import (
    run_analytics_agent
)

from agents.voice_agent import (
    run_voice_agent
)

from core.shared_bus import (
    shared_bus
)

from utils.ui_utils import (
    sanitize_text
)

# =========================================
# HELIOS AGENT REGISTRY
# =========================================

AGENT_REGISTRY = {

    "Research Center":
    "Research Agent",

    "Code Intelligence":
    "Code Agent",

    "System Analytics":
    "Analytics Agent",

    "Voice AI":
    "Voice Agent"
}

# =========================================
# AGENT ROUTER
# =========================================

def route_agent(

    selected_agent,
    query,
    web_results,
    file_content,
    conversation_context

):

    # =====================================
    # SANITIZE INPUTS
    # =====================================

    safe_agent = sanitize_text(
        selected_agent
    )

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

    try:

        # =================================
        # RESEARCH AGENT
        # =================================

        if safe_agent == "Research Center":

            output = run_research_agent(

                safe_query,

                safe_web_results,

                safe_file_content,

                safe_context
            )

        # =================================
        # CODE AGENT
        # =================================

        elif safe_agent == "Code Intelligence":

            output = run_code_agent(

                safe_query,

                safe_file_content,

                safe_context
            )

        # =================================
        # ANALYTICS AGENT
        # =================================

        elif safe_agent == "System Analytics":

            output = run_analytics_agent(

                safe_query,

                safe_web_results,

                safe_context
            )

        # =================================
        # VOICE AGENT
        # =================================

        elif safe_agent == "Voice AI":

            output = run_voice_agent(

                safe_query,

                safe_context
            )

        # =================================
        # UNKNOWN ROUTE
        # =================================

        else:

            output = f"""

# ⚠️ Unknown Agent Route

HELIOS could not determine the correct orchestration route.

Requested Agent:
{safe_agent}

Available Agents:
- Research Center
- Code Intelligence
- System Analytics
- Voice AI

"""

        # =================================
        # SYSTEM TELEMETRY
        # =================================

        try:

            shared_bus.send_message(

                "Orchestration Layer",

                AGENT_REGISTRY.get(
                    safe_agent,
                    "Unknown Agent"
                ),

                f"""

Agent routing completed successfully.

Timestamp:
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Selected Agent:
{safe_agent}

Query:
{safe_query[:300]}

                """
            )

        except Exception:

            pass

        # =================================
        # FINAL OUTPUT
        # =================================

        final_output = f"""

# ⚡ HELIOS Orchestration Layer

Agent Selected:
{AGENT_REGISTRY.get(safe_agent, 'Unknown Agent')}

Timestamp:
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Status:
ACTIVE

---

{output}

"""

        return str(final_output)

    # =====================================
    # FAILURE HANDLER
    # =====================================

    except Exception as error:

        traceback.print_exc()

        return f"""

# ❌ HELIOS Orchestration Failure

Agent:
{safe_agent}

Timestamp:
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Status:
FAILED

---

Error:
{str(error)}

---

Possible Causes:
- agent execution failure
- invalid infrastructure state
- AI inference instability
- malformed orchestration request

"""