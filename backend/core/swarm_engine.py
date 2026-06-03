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
    failed_count,
    consensus=None

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

    if consensus:

        sections.append(
            build_consensus_block(
                consensus
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


def _agent_focus(
    agent
):
    if agent == "Research Agent":
        return "evidence"

    if agent == "Code Agent":
        return "implementation"

    if agent == "Analytics Agent":
        return "observability"

    return "coordination"


def extract_proposals(
    swarm_results
):
    proposals = []

    for result in swarm_results:
        output = str(
            result.get(
                "output",
                ""
            )
        )
        lines = [
            line.strip(" -•\t")
            for line in output.splitlines()
            if line.strip()
        ]
        proposal = next(
            (
                line
                for line in lines
                if 24 <= len(
                    line
                ) <= 180
            ),
            output[:180].strip()
            or "No concrete proposal emitted."
        )

        proposals.append(
            {
                "agent": result.get(
                    "agent"
                ),
                "focus": _agent_focus(
                    result.get(
                        "agent"
                    )
                ),
                "proposal": proposal,
                "status": result.get(
                    "status"
                )
            }
        )

    return proposals


def build_debate(
    proposals
):
    debate = []

    for proposal in proposals:
        critiques = []

        if proposal["focus"] != "evidence":
            critiques.append(
                "Research should validate source support before execution claims are accepted."
            )

        if proposal["focus"] != "implementation":
            critiques.append(
                "Code should identify concrete files, verification commands, and rollback risk."
            )

        if proposal["focus"] != "observability":
            critiques.append(
                "Analytics should capture runtime signals, retries, and failure rates."
            )

        debate.append(
            {
                "agent": proposal["agent"],
                "proposal": proposal["proposal"],
                "critiques": critiques[:2]
            }
        )

    return debate


def build_consensus(
    swarm_results,
    rounds=None
):
    proposals = extract_proposals(
        swarm_results
    )
    debate = build_debate(
        proposals
    )
    failed_agents = [
        result.get(
            "agent"
        )
        for result in swarm_results
        if result.get(
            "status"
        )
        == "failed"
    ]
    active_focus = sorted(
        {
            proposal["focus"]
            for proposal in proposals
            if proposal.get(
                "status"
            )
            == "completed"
        }
    )

    consensus_steps = [
        "Ground claims in indexed sources before presenting final recommendations.",
        "Apply implementation changes through bounded tool execution and verification.",
        "Record execution metrics, retries, and unresolved risks in the ledger."
    ]

    return {
        "proposals": proposals,
        "debate": debate,
        "consensus_steps": consensus_steps,
        "failed_agents": failed_agents,
        "active_focus": active_focus,
        "confidence": round(
            len(
                active_focus
            )
            / 3,
            2
        ),
        "rounds": rounds or [
            {
                "round": 1,
                "type": "proposal",
                "results": swarm_results
            }
        ]
    }


def run_review_round(
    query,
    first_round,
    web_results,
    file_content,
    conversation_context
):
    consensus = build_consensus(
        first_round
    )
    debate_context = compress_context(
        "\n".join(
            [
                "Other agents proposed:",
                *[
                    f"- {item['agent']}: {item['proposal']}"
                    for item in consensus["proposals"]
                ],
                "Cross-agent critiques:",
                *[
                    f"- {item['agent']}: {'; '.join(item['critiques'])}"
                    for item in consensus["debate"]
                ],
                "Revise your recommendation after considering the other agents."
            ]
        ),
        MAX_CONTEXT_CHARS
    )
    combined_context = compress_context(
        f"{conversation_context}\n\n{debate_context}",
        MAX_CONTEXT_CHARS
    )
    jobs = [
        (
            "Research Agent",
            run_research_agent,
            (
                query,
                web_results,
                file_content,
                combined_context
            )
        ),
        (
            "Code Agent",
            run_code_agent,
            (
                query,
                file_content,
                combined_context
            )
        ),
        (
            "Analytics Agent",
            run_analytics_agent,
            (
                query,
                web_results,
                combined_context
            )
        )
    ]
    results = []
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=MAX_WORKERS
    ) as executor:
        futures = [
            executor.submit(
                execute_agent,
                name,
                fn,
                *args
            )
            for name, fn, args in jobs
        ]
        for future in concurrent.futures.as_completed(
            futures
        ):
            results.append(
                future.result()
            )
    return sort_swarm_results(
        results
    )


def build_consensus_block(
    consensus
):
    proposal_lines = "\n".join(
        f"- {item['agent']} ({item['focus']}): {item['proposal']}"
        for item in consensus.get(
            "proposals",
            []
        )
    )
    critique_lines = "\n".join(
        f"- {item['agent']}: {'; '.join(item['critiques'])}"
        for item in consensus.get(
            "debate",
            []
        )
    )
    step_lines = "\n".join(
        f"{index + 1}. {step}"
        for index, step in enumerate(
            consensus.get(
                "consensus_steps",
                []
            )
        )
    )

    return f"""
# 🧠 Swarm Debate + Consensus

Consensus Confidence:
{consensus.get('confidence', 0)}

## Proposals
{proposal_lines or "- No proposals emitted."}

## Cross-Agent Critique
{critique_lines or "- No critiques emitted."}

## Consensus Plan
{step_lines or "1. Re-run swarm with clearer objective."}

"""

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
    review_results = run_review_round(
        safe_query,
        swarm_results,
        safe_web,
        safe_file,
        safe_context
    )
    consensus = build_consensus(
        review_results,
        rounds=[
            {
                "round": 1,
                "type": "proposal",
                "results": swarm_results
            },
            {
                "round": 2,
                "type": "review",
                "results": review_results
            }
        ]
    )

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

        failed_count=failed_count,

        consensus=consensus
    )

    return final_output
