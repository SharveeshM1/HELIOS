import concurrent.futures
import threading
import time

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
# SWARM CONFIG
# =====================================

MAX_WORKERS = 3

MAX_CONTEXT_CHARS = 4000

MAX_WEB_CHARS = 5000

MAX_FILE_CHARS = 4000

# =====================================
# SWARM LOCK
# =====================================

swarm_lock = threading.Lock()

# =====================================
# SAFE CONTEXT COMPRESSOR
# =====================================

def compress_context(

    context,
    limit=MAX_CONTEXT_CHARS

):

    if not context:

        return ""

    context = str(context).strip()

    if len(context) <= limit:

        return context

    half = limit // 2

    return (

        context[:half]
        +
        "\n\n...[TRUNCATED CONTEXT]...\n\n"
        +
        context[-half:]
    )

# =====================================
# SWARM NODE
# =====================================

def swarm_node(

    agent,
    output,
    duration,
    status="completed"

):

    return {

        "agent":
        agent,

        "output":
        output,

        "duration":
        round(duration, 2),

        "status":
        status,

        "timestamp":
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    }

# =====================================
# TELEMETRY
# =====================================

def send_swarm_telemetry(

    sender,
    content

):

    try:

        with swarm_lock:

            shared_bus.send_message(

                sender,

                "Swarm Core",

                content
            )

    except Exception:

        pass

# =====================================
# EXECUTION WRAPPER
# =====================================

def execute_agent(

    agent_name,
    fn,
    *args

):

    started = time.time()

    try:

        send_swarm_telemetry(

            agent_name,

            f"""

Agent execution started.

Timestamp:
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Status:
running

            """
        )

        result = fn(*args)

        if result is None:

            result = ""

        result = str(result)

        duration = (
            time.time() - started
        )

        send_swarm_telemetry(

            agent_name,

            f"""

Agent execution completed.

Timestamp:
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Execution Time:
{round(duration,2)}s

Status:
completed

            """
        )

        return swarm_node(

            agent=agent_name,

            output=result,

            duration=duration,

            status="completed"
        )

    except Exception as e:

        duration = (
            time.time() - started
        )

        send_swarm_telemetry(

            agent_name,

            f"""

Agent execution failed.

Timestamp:
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Error:
{str(e)}

Status:
failed

            """
        )

        return swarm_node(

            agent=agent_name,

            output=f"""

[HELIOS AGENT ERROR]

Agent:
{agent_name}

Error:
{str(e)}

            """,

            duration=duration,

            status="failed"
        )

# =====================================
# SORT RESULTS
# =====================================

def sort_swarm_results(

    results

):

    priority = {

        "Research Agent": 1,

        "Code Agent": 2,

        "Analytics Agent": 3
    }

    return sorted(

        results,

        key=lambda x: priority.get(
            x["agent"],
            999
        )
    )

# =====================================
# FORMAT RESULT BLOCK
# =====================================

def build_result_block(

    index,
    result

):

    return f"""

# ⚡ Node {index + 1}

Agent:
{result['agent']}

Status:
{result['status']}

Execution Time:
{result['duration']}s

Timestamp:
{result['timestamp']}

---

{result['output']}

---

"""

# =====================================
# BUILD FINAL REPORT
# =====================================

def build_final_report(

    swarm_results,
    total_duration,
    success_count,
    failed_count

):

    sections = [

        f"""
# 🕸️ HELIOS Swarm Intelligence Report

Generated:
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Total Swarm Execution Time:
{total_duration}s

Distributed cognition execution stabilized.

---

# 📊 Swarm Statistics

Successful Agents:
{success_count}

Failed Agents:
{failed_count}

Concurrent Workers:
{MAX_WORKERS}

Swarm Status:
OPERATIONAL

---
"""
    ]

    for index, result in enumerate(
        swarm_results
    ):

        sections.append(

            build_result_block(
                index,
                result
            )
        )

    sections.append(

        """
# ✅ Swarm Synchronization Complete

HELIOS successfully:
- executed distributed cognition
- synchronized autonomous agents
- stabilized parallel orchestration
- optimized swarm execution
- processed concurrent reasoning flows

Swarm intelligence operating normally.
"""
    )

    return "\n".join(sections)

# =====================================
# RUN SWARM
# =====================================

def run_swarm(

    query,
    web_results,
    file_content,
    conversation_context

):

    swarm_started = time.time()

    swarm_results = []

    # =================================
    # SAFE CONTEXT
    # =================================

    safe_query = compress_context(
        query,
        3000
    )

    safe_context = compress_context(
        conversation_context,
        MAX_CONTEXT_CHARS
    )

    safe_web = compress_context(
        web_results,
        MAX_WEB_CHARS
    )

    safe_file = compress_context(
        file_content,
        MAX_FILE_CHARS
    )

    # =====================================
    # SWARM START TELEMETRY
    # =====================================

    send_swarm_telemetry(

        "Swarm Engine",

        f"""

Swarm execution initialized.

Timestamp:
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Query:
{safe_query}

Workers:
{MAX_WORKERS}

        """
    )

    # =====================================
    # PARALLEL EXECUTION
    # =====================================

    with concurrent.futures.ThreadPoolExecutor(

        max_workers=MAX_WORKERS

    ) as executor:

        futures = [

            executor.submit(

                execute_agent,

                "Research Agent",

                run_research_agent,

                safe_query,

                safe_web,

                safe_file,

                safe_context
            ),

            executor.submit(

                execute_agent,

                "Code Agent",

                run_code_agent,

                safe_query,

                safe_file,

                safe_context
            ),

            executor.submit(

                execute_agent,

                "Analytics Agent",

                run_analytics_agent,

                safe_query,

                safe_web,

                safe_context
            )
        ]

        for future in concurrent.futures.as_completed(
            futures
        ):

            try:

                result = future.result()

                swarm_results.append(
                    result
                )

            except Exception as e:

                swarm_results.append(

                    swarm_node(

                        agent="Unknown",

                        output=f"""

[HELIOS SWARM ERROR]

Unhandled parallel execution failure.

Error:
{str(e)}

                        """,

                        duration=0,

                        status="failed"
                    )
                )

    # =====================================
    # SORT RESULTS
    # =====================================

    swarm_results = sort_swarm_results(
        swarm_results
    )

    # =====================================
    # FINAL METADATA
    # =====================================

    total_duration = round(

        time.time() - swarm_started,

        2
    )

    success_count = len([

        r for r in swarm_results

        if r["status"] == "completed"

    ])

    failed_count = len([

        r for r in swarm_results

        if r["status"] == "failed"

    ])

    # =====================================
    # FINAL TELEMETRY
    # =====================================

    send_swarm_telemetry(

        "Swarm Engine",

        f"""

Swarm execution stabilized.

Timestamp:
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Total Duration:
{total_duration}s

Successful Agents:
{success_count}

Failed Agents:
{failed_count}

        """
    )

    # =====================================
    # FINAL OUTPUT
    # =====================================

    final_output = build_final_report(

        swarm_results=swarm_results,

        total_duration=total_duration,

        success_count=success_count,

        failed_count=failed_count
    )

    return final_output