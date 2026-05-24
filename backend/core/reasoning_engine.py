import time

from datetime import datetime
from typing import Dict
from typing import List
from typing import Callable

from agents.analytics_agent import (
    run_analytics_agent
)

from agents.code_agent import (
    run_code_agent
)

from agents.research_agent import (
    run_research_agent
)

from core.shared_bus import (
    shared_bus
)

# =========================================
# NODE
# =========================================

def reasoning_node(

    stage: str,
    agent: str,
    output: str,
    duration: float

) -> Dict:

    return {

        "stage":
        stage,

        "agent":
        agent,

        "output":
        output,

        "duration":
        round(duration, 2),

        "timestamp":
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    }

# =========================================
# TELEMETRY
# =========================================

def send_reasoning_telemetry(

    stage: str,
    agent: str,
    duration: float,
    success: bool = True

):

    try:

        shared_bus.send_message(

            agent,

            "Reasoning Engine",

            f"""

Stage:
{stage}

Duration:
{round(duration, 2)}s

Status:
{"SUCCESS" if success else "FAILED"}

Timestamp:
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

            """
        )

    except Exception:

        pass

# =========================================
# SAFE EXECUTION
# =========================================

def execute_stage(

    stage: str,
    agent: str,
    executor: Callable,
    *args

):

    start = time.time()

    try:

        output = executor(*args)

        success = True

    except Exception as e:

        output = f"""

[HELIOS ERROR]

Stage:
{stage}

Agent:
{agent}

Error:
{str(e)}

"""

        success = False

    duration = time.time() - start

    send_reasoning_telemetry(

        stage,
        agent,
        duration,
        success
    )

    return reasoning_node(

        stage=stage,
        agent=agent,
        output=output,
        duration=duration
    )

# =========================================
# RECURSIVE ENGINE
# =========================================

def recursive_reasoning(

    query: str,
    web_results: str,
    file_content: str,
    conversation_context: str

) -> str:

    cognition_flow: List[Dict] = []

    total_start = time.time()

    # =====================================
    # RESEARCH
    # =====================================

    research_node = execute_stage(

        "Research Analysis",

        "Research Agent",

        run_research_agent,

        query,
        web_results,
        file_content,
        conversation_context
    )

    cognition_flow.append(
        research_node
    )

    research_output = (
        research_node["output"]
    )

    # =====================================
    # INITIAL IMPLEMENTATION
    # =====================================

    implementation_prompt = f"""

Research Intelligence:

{research_output}

Generate:

- scalable architecture
- implementation strategy
- execution pipeline
- infrastructure design
- production-ready systems

Keep the solution:

- modern
- clean
- scalable
- realistic
- optimized

"""

    implementation_node = execute_stage(

        "Implementation Generation",

        "Code Agent",

        run_code_agent,

        implementation_prompt,
        file_content,
        conversation_context
    )

    cognition_flow.append(
        implementation_node
    )

    implementation_output = (
        implementation_node["output"]
    )

    # =====================================
    # ANALYTICS
    # =====================================

    analytics_prompt = f"""

Implementation:

{implementation_output}

Critique deeply.

Analyze:

- scalability
- bottlenecks
- infra risks
- execution weaknesses
- optimization opportunities
- production readiness

Return intelligent systems analysis.

"""

    analytics_node = execute_stage(

        "Systems Critique",

        "Analytics Agent",

        run_analytics_agent,

        analytics_prompt,
        web_results,
        conversation_context
    )

    cognition_flow.append(
        analytics_node
    )

    analytics_output = (
        analytics_node["output"]
    )

    # =====================================
    # RECURSIVE REFINEMENT
    # =====================================

    recursive_prompt = f"""

Initial Implementation:

{implementation_output}

Systems Critique:

{analytics_output}

Improve the architecture significantly.

Generate:

- refined infrastructure
- superior execution strategy
- optimization improvements
- cleaner scalability pathways
- resilient production systems

Avoid repetition.

Push reasoning quality higher.

"""

    recursive_node = execute_stage(

        "Recursive Refinement",

        "Code Agent",

        run_code_agent,

        recursive_prompt,
        file_content,
        conversation_context
    )

    cognition_flow.append(
        recursive_node
    )

    recursive_output = (
        recursive_node["output"]
    )

    # =====================================
    # FINAL TELEMETRY
    # =====================================

    total_duration = round(

        time.time() - total_start,

        2
    )

    try:

        shared_bus.send_message(

            "Reasoning Engine",

            "System",

            f"""

Recursive cognition stabilized.

Stages:
{len(cognition_flow)}

Total Duration:
{total_duration}s

Timestamp:
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

            """
        )

    except Exception:

        pass

    # =====================================
    # FINAL REPORT
    # =====================================

    final_output = f"""

# HELIOS Recursive Cognition Report

Generated:
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Total Cognition Time:
{total_duration}s

---

## Research Analysis

{research_output}

---

## Initial Implementation

{implementation_output}

---

## Systems Critique

{analytics_output}

---

## Recursive Refinement

{recursive_output}

---

HELIOS recursive cognition completed successfully.

"""

    return final_output