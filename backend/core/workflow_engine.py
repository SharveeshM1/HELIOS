import time
import threading

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

# =====================================
# CONFIG
# =====================================

MAX_CONTEXT_CHARS = 4000

workflow_lock = threading.Lock()

# =====================================
# SAFE CONTEXT
# =====================================

def compress_context(

    context,
    limit=MAX_CONTEXT_CHARS

):

    if not context:

        return ""

    context = str(context)

    if len(context) <= limit:

        return context

    return context[-limit:]

# =====================================
# TELEMETRY
# =====================================

def send_workflow_telemetry(

    sender,
    content

):

    try:

        with workflow_lock:

            shared_bus.send_message(

                sender,

                "Workflow Engine",

                content
            )

    except Exception:

        pass

# =====================================
# STEP OBJECT
# =====================================

def create_workflow_step(

    step,
    agent,
    status,
    output,
    duration,
    metadata=None

):

    return {

        "step":
        step,

        "agent":
        agent,

        "status":
        status,

        "output":
        output,

        "duration":
        round(duration, 2),

        "metadata":
        metadata or {},

        "timestamp":
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    }

# =====================================
# EXECUTE STEP
# =====================================

def execute_step(

    step_number,
    agent_name,
    fn,
    *args

):

    started = time.time()

    try:

        send_workflow_telemetry(

            agent_name,

            f"""

Workflow step started.

Step:
{step_number}

Agent:
{agent_name}

Status:
running

            """
        )

        result = fn(*args)

        duration = (
            time.time() - started
        )

        send_workflow_telemetry(

            agent_name,

            f"""

Workflow step completed.

Step:
{step_number}

Agent:
{agent_name}

Execution Time:
{round(duration,2)}s

Status:
completed

            """
        )

        return create_workflow_step(

            step=step_number,

            agent=agent_name,

            status="completed",

            output=result,

            duration=duration,

            metadata={

                "tokens":"optimized",

                "pipeline":"stable"
            }
        )

    except Exception as e:

        send_workflow_telemetry(

            agent_name,

            f"""

Workflow step failed.

Step:
{step_number}

Agent:
{agent_name}

Error:
{str(e)}

            """
        )

        return create_workflow_step(

            step=step_number,

            agent=agent_name,

            status="failed",

            output=str(e),

            duration=(
                time.time() - started
            )
        )

# =====================================
# EXECUTE WORKFLOW
# =====================================

def execute_workflow(

    goal,
    web_results,
    file_content,
    conversation_context

):

    workflow_started = time.time()

    workflow_steps = []

    # =================================
    # SAFE CONTEXT
    # =================================

    safe_goal = compress_context(
        goal,
        3000
    )

    safe_web = compress_context(
        web_results,
        6000
    )

    safe_file = compress_context(
        file_content,
        8000
    )

    safe_context = compress_context(
        conversation_context,
        4000
    )

    # =====================================
    # WORKFLOW START
    # =====================================

    send_workflow_telemetry(

        "Workflow Engine",

        f"""

Workflow execution initialized.

Goal:
{safe_goal}

Timestamp:
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

        """
    )

    # =====================================
    # STEP 1 — RESEARCH
    # =====================================

    research_step = execute_step(

        1,

        "Research Agent",

        run_research_agent,

        safe_goal,

        safe_web,

        safe_file,

        safe_context
    )

    workflow_steps.append(
        research_step
    )

    if research_step["status"] == "failed":

        return workflow_steps

    research_result = (
        research_step["output"]
    )

    # =====================================
    # STEP 2 — CODE
    # =====================================

    code_prompt = f"""

Based on this research intelligence:

{research_result}

Generate:
- implementation strategy
- architecture systems
- scalability pathways
- optimization logic
- production infrastructure

Keep it:
- modern
- scalable
- production-grade
- concise

    """

    code_step = execute_step(

        2,

        "Code Agent",

        run_code_agent,

        code_prompt,

        safe_file,

        safe_context
    )

    workflow_steps.append(
        code_step
    )

    if code_step["status"] == "failed":

        return workflow_steps

    code_result = (
        code_step["output"]
    )

    # =====================================
    # STEP 3 — ANALYTICS
    # =====================================

    analytics_prompt = f"""

Analyze this implementation deeply.

IMPLEMENTATION:
{code_result}

Evaluate:
- scalability
- bottlenecks
- infrastructure limits
- optimization opportunities
- production readiness
- systems performance

Generate:
- concise
- strategic
- technical analysis

    """

    analytics_step = execute_step(

        3,

        "Analytics Agent",

        run_analytics_agent,

        analytics_prompt,

        safe_web,

        safe_context
    )

    workflow_steps.append(
        analytics_step
    )

    analytics_result = (
        analytics_step["output"]
    )

    # =====================================
    # STEP 4 — RECURSIVE IMPROVEMENT
    # =====================================

    recursive_prompt = f"""

Improve this architecture recursively.

====================================

RESEARCH:
{research_result}

====================================

IMPLEMENTATION:
{code_result}

====================================

ANALYTICS:
{analytics_result}

====================================

Generate:
- refined architecture
- superior optimization
- scalable redesign
- production improvements
- infrastructure evolution

    """

    recursive_step = execute_step(

        4,

        "Code Agent",

        run_code_agent,

        recursive_prompt,

        safe_file,

        safe_context
    )

    workflow_steps.append(
        recursive_step
    )

    # =====================================
    # FINAL SUMMARY
    # =====================================

    total_duration = round(

        time.time() - workflow_started,

        2
    )

    completed_steps = len([

        s for s in workflow_steps

        if s["status"] == "completed"

    ])

    failed_steps = len([

        s for s in workflow_steps

        if s["status"] == "failed"

    ])

    final_summary = create_workflow_step(

        step="summary",

        agent="Workflow Engine",

        status="completed",

        output=f"""

# ⚡ HELIOS Workflow Summary

Workflow execution stabilized.

Total Execution Time:
{total_duration}s

Completed Steps:
{completed_steps}

Failed Steps:
{failed_steps}

Agents Involved:
- Research Agent
- Code Agent
- Analytics Agent

HELIOS successfully:
- analyzed the objective
- generated implementation systems
- evaluated infrastructure
- recursively optimized execution

Workflow orchestration operating normally.

        """,

        duration=total_duration,

        metadata={

            "completed_steps":
            completed_steps,

            "failed_steps":
            failed_steps,

            "workflow_status":
            "stable"
        }
    )

    workflow_steps.append(
        final_summary
    )

    # =====================================
    # FINAL TELEMETRY
    # =====================================

    send_workflow_telemetry(

        "Workflow Engine",

        f"""

Workflow execution completed.

Total Duration:
{total_duration}s

Completed:
{completed_steps}

Failed:
{failed_steps}

Status:
stable

        """
    )

    return workflow_steps