import time
import traceback

from datetime import datetime

from agents.research_agent import (
    run_research_agent
)

from agents.code_agent import (
    run_code_agent
)

from agents.analytics_agent import (
    run_analytics_agent
)

from core.shared_bus import (
    shared_bus
)

from utils.ui_utils import (
    sanitize_text
)


# =========================================
# HELIOS COLLABORATIVE WORKFLOW ENGINE
# =========================================

def run_collaborative_workflow(

    query,
    web_results,
    file_content,
    conversation_context

):

    workflow_started = time.time()

    workflow_steps = []

    # =====================================
    # SANITIZE INPUTS
    # =====================================

    safe_query = sanitize_text(query)

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
    # RESEARCH STAGE
    # =====================================

    try:

        research_output = run_research_agent(

            safe_query,

            safe_web_results,

            safe_file_content,

            safe_context
        )

        workflow_steps.append({

            "agent": "Research Agent",

            "status": "SUCCESS"
        })

        shared_bus.send_message(

            "Research Agent",

            "Code Agent",

            f"""

Research intelligence generated successfully.

Primary Query:
{safe_query[:300]}

Research Summary:
{str(research_output)[:1200]}

            """
        )

    except Exception as error:

        traceback.print_exc()

        research_output = f"""

# ⚠️ Research Failure

Research agent execution failed.

Error:
{str(error)}

"""

        workflow_steps.append({

            "agent": "Research Agent",

            "status": "FAILED"
        })

    # =====================================
    # CODE STAGE
    # =====================================

    try:

        code_query = f"""

Using this research intelligence:

{research_output}

Generate:

- architecture strategy
- implementation design
- optimization paths
- scalable infrastructure ideas
- production engineering recommendations

"""

        code_output = run_code_agent(

            code_query,

            safe_file_content,

            safe_context
        )

        workflow_steps.append({

            "agent": "Code Agent",

            "status": "SUCCESS"
        })

        shared_bus.send_message(

            "Code Agent",

            "Analytics Agent",

            f"""

Code intelligence pipeline completed.

Architecture Summary:
{str(code_output)[:1200]}

            """
        )

    except Exception as error:

        traceback.print_exc()

        code_output = f"""

# ⚠️ Code Intelligence Failure

Code agent execution failed.

Error:
{str(error)}

"""

        workflow_steps.append({

            "agent": "Code Agent",

            "status": "FAILED"
        })

    # =====================================
    # ANALYTICS STAGE
    # =====================================

    try:

        analytics_query = f"""

Analyze this proposed system deeply.

========================================
SYSTEM ARCHITECTURE
========================================

{code_output}

========================================
EVALUATION REQUIREMENTS
========================================

Evaluate:
- scalability
- performance
- bottlenecks
- infrastructure risks
- optimization opportunities
- production readiness
- distributed orchestration efficiency

"""

        analytics_output = run_analytics_agent(

            analytics_query,

            safe_web_results,

            safe_context
        )

        workflow_steps.append({

            "agent": "Analytics Agent",

            "status": "SUCCESS"
        })

    except Exception as error:

        traceback.print_exc()

        analytics_output = f"""

# ⚠️ Analytics Failure

Analytics agent execution failed.

Error:
{str(error)}

"""

        workflow_steps.append({

            "agent": "Analytics Agent",

            "status": "FAILED"
        })

    # =====================================
    # EXECUTION METADATA
    # =====================================

    total_duration = round(

        time.time() - workflow_started,

        2
    )

    successful_agents = len([

        step for step in workflow_steps

        if step["status"] == "SUCCESS"

    ])

    failed_agents = len([

        step for step in workflow_steps

        if step["status"] == "FAILED"

    ])

    # =====================================
    # SYSTEM TELEMETRY
    # =====================================

    try:

        shared_bus.send_message(

            "Workflow Engine",

            "System",

            f"""

Collaborative workflow completed.

Timestamp:
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Execution Time:
{total_duration}s

Successful Agents:
{successful_agents}

Failed Agents:
{failed_agents}

Query:
{safe_query[:400]}

            """
        )

    except Exception:

        pass

    # =====================================
    # FINAL RESPONSE
    # =====================================

    final_output = f"""

# 🤝 HELIOS Collaborative Intelligence

Generated:
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Execution Time:
{total_duration}s

Distributed cognition synchronization complete.

---

# 🧪 Research Intelligence

{research_output}

---

# 💻 Code Intelligence

{code_output}

---

# 📊 Analytics Intelligence

{analytics_output}

---

# 📡 Workflow Telemetry

Successful Agents:
{successful_agents}

Failed Agents:
{failed_agents}

Workflow Status:
{"OPERATIONAL" if failed_agents == 0 else "PARTIAL FAILURE"}

---

# ✅ Collaborative Workflow Complete

HELIOS successfully:

- coordinated multiple AI agents
- synchronized distributed cognition
- generated architecture intelligence
- evaluated scalability conditions
- analyzed optimization pathways
- produced production-grade insights

"""

    return str(final_output)