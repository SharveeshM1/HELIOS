import time

from datetime import datetime
from typing import Dict
from typing import List
from typing import Optional

from core.reasoning_engine import (
    recursive_reasoning
)

from core.shared_bus import (
    shared_bus
)

# =========================================
# CONFIG
# =========================================

MAX_OUTPUT_CHARS = 4000

MAX_QUERY_CHARS = 2500

MAX_ITERATIONS = 10

# =========================================
# SAFE TEXT
# =========================================

def safe_truncate(

    text: str,

    limit: int

) -> str:

    text = str(text)

    if len(text) <= limit:

        return text

    return text[:limit] + "\n\n[TRUNCATED]"

# =========================================
# ITERATION NODE
# =========================================

def create_iteration(

    iteration: int,
    output: str,
    duration: float,
    query: str

) -> Dict:

    return {

        "type":
        "iteration",

        "iteration":
        iteration,

        "query":
        safe_truncate(
            query,
            800
        ),

        "output":
        safe_truncate(
            output,
            MAX_OUTPUT_CHARS
        ),

        "duration":
        round(duration, 2),

        "timestamp":
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    }

# =========================================
# OUTPUT SUMMARIZER
# =========================================

def summarize_output(

    output: str

) -> str:

    output = str(output)

    if len(output) <= 1200:

        return output

    return (

        output[:1200]

        +

        "\n\n[SUMMARY TRUNCATED FOR RECURSIVE EVOLUTION]"
    )

# =========================================
# EVOLUTION PROMPT
# =========================================

def build_evolution_prompt(

    previous_output: str,
    iteration: int

) -> str:

    summarized_output = summarize_output(
        previous_output
    )

    prompt = f"""

You are operating inside HELIOS
recursive autonomous cognition.

Current iteration:
{iteration}

Objective:
evolve the previous intelligence layer.

Improve:

- architecture
- scalability
- reasoning quality
- execution logic
- optimization pathways
- infrastructure resilience
- orchestration
- production readiness

Previous cognition summary:

{summarized_output}

Generate a more refined version.

Avoid repetition.
Avoid excessive verbosity.
Focus on meaningful improvements.

"""

    return safe_truncate(
        prompt,
        MAX_QUERY_CHARS
    )

# =========================================
# TELEMETRY
# =========================================

def send_telemetry(

    receiver: str,
    content: str

):

    shared_bus.send_message(

        "Autonomous Loop",

        receiver,

        content.strip()
    )

# =========================================
# AUTONOMOUS LOOP
# =========================================

def run_autonomous_loop(

    query: str,
    web_results: str,
    file_content: str,
    conversation_context: str,
    iterations: int = 3,
    sleep_time: float = 0.15

) -> List[Dict]:

    # =====================================
    # VALIDATION
    # =====================================

    if iterations < 1:

        iterations = 1

    if iterations > MAX_ITERATIONS:

        iterations = MAX_ITERATIONS

    loop_history = []

    current_query = safe_truncate(
        query,
        MAX_QUERY_CHARS
    )

    loop_started = time.time()

    # =====================================
    # LOOP START
    # =====================================

    send_telemetry(

        "System",

        f"""
Recursive cognition initialized.

Iterations:
{iterations}
        """
    )

    # =====================================
    # ITERATIONS
    # =====================================

    for i in range(iterations):

        iteration_number = i + 1

        iteration_start = time.time()

        output = ""

        try:

            # =============================
            # REASONING
            # =============================

            output = recursive_reasoning(

                current_query,

                web_results,

                file_content,

                conversation_context
            )

            output = safe_truncate(

                output,

                MAX_OUTPUT_CHARS
            )

        except RuntimeError as e:

            output = f"""

[HELIOS RUNTIME ERROR]

Iteration:
{iteration_number}

Error:
{str(e)}

"""

        except ValueError as e:

            output = f"""

[HELIOS VALIDATION ERROR]

Iteration:
{iteration_number}

Error:
{str(e)}

"""

        except Exception as e:

            output = f"""

[HELIOS UNKNOWN ERROR]

Iteration:
{iteration_number}

Error:
{str(e)}

"""

        # =============================
        # DURATION
        # =============================

        iteration_duration = (

            time.time()
            - iteration_start
        )

        # =============================
        # STORE ITERATION
        # =============================

        iteration_data = create_iteration(

            iteration=iteration_number,

            output=output,

            duration=iteration_duration,

            query=current_query
        )

        loop_history.append(
            iteration_data
        )

        # =============================
        # TELEMETRY
        # =============================

        send_telemetry(

            "Reasoning Engine",

            f"""
Iteration {iteration_number} completed.

Duration:
{round(iteration_duration, 2)}s

Status:
Stable
            """
        )

        # =============================
        # STOP EVOLUTION ON ERROR
        # =============================

        if "[HELIOS" in output:

            send_telemetry(

                "System",

                f"""
Loop halted at iteration
{iteration_number} due to failure.
                """
            )

            break

        # =============================
        # BUILD NEXT QUERY
        # =============================

        current_query = build_evolution_prompt(

            previous_output=output,

            iteration=iteration_number
        )

        # =============================
        # STABILIZATION
        # =============================

        if sleep_time > 0:

            time.sleep(sleep_time)

    # =====================================
    # FINAL SUMMARY
    # =====================================

    total_duration = round(

        time.time()
        - loop_started,

        2
    )

    final_summary = {

        "type":
        "summary",

        "iterations":
        len(loop_history),

        "total_duration":
        total_duration,

        "timestamp":
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        "status":
        "Autonomous cognition stabilized"
    }

    loop_history.append(
        final_summary
    )

    # =====================================
    # FINAL TELEMETRY
    # =====================================

    send_telemetry(

        "System",

        f"""
Recursive cognition finalized.

Iterations:
{len(loop_history) - 1}

Total Duration:
{total_duration}s

Status:
Autonomous stabilization complete
        """
    )

    return loop_history