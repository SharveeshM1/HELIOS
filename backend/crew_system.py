from crewai import (

    Agent,
    Task,
    Crew,
    Process
)

from dotenv import load_dotenv

from api.ai_provider import (
    generate_ai_response
)

import logging
import time

# =========================================================
# LOAD ENV
# =========================================================

load_dotenv()

logger = logging.getLogger(
    "helios-crew"
)

# =========================================================
# HELIOS LLM WRAPPER
# =========================================================

class HeliosLLM:

    """
    CrewAI-compatible lightweight wrapper
    around HELIOS Gemini engine.
    """

    def call(

        self,
        prompt: str,
        **kwargs

    ) -> str:

        try:

            response = generate_ai_response(
                prompt
            )

            return str(response)

        except Exception as e:

            logger.exception(
                "HELIOS LLM failure"
            )

            return f"""

[HELIOS CREW ERROR]

{str(e)}

"""

# =========================================================
# GLOBAL LLM
# =========================================================

helios_llm = HeliosLLM()

# =========================================================
# RESEARCH AGENT
# =========================================================

research_agent = Agent(

    role=(
        "HELIOS Research Intelligence Agent"
    ),

    goal=(
        "Perform deep technical "
        "research and identify "
        "high-value intelligence."
    ),

    backstory="""

You are an elite AI research system.

You specialize in:
- emerging AI systems
- autonomous agents
- infrastructure intelligence
- futuristic technologies
- startup-level innovation
- technical deep analysis

You think:
- strategically
- analytically
- futuristically
- practically

You avoid:
- fluff
- robotic writing
- academic verbosity
- generic responses

""",

    verbose=True,

    allow_delegation=False,

    llm=helios_llm
)

# =========================================================
# STRATEGY AGENT
# =========================================================

strategy_agent = Agent(

    role=(
        "HELIOS Strategic Systems Planner"
    ),

    goal=(
        "Generate scalable execution "
        "strategies and architecture plans."
    ),

    backstory="""

You are an advanced AI strategist.

You specialize in:
- execution planning
- startup scaling
- AI infrastructure
- product architecture
- systems optimization
- autonomous workflows

You think like:
- a CTO
- AI systems architect
- futuristic startup founder

You prioritize:
- scalability
- performance
- realism
- production readiness

""",

    verbose=True,

    allow_delegation=False,

    llm=helios_llm
)

# =========================================================
# REPORT AGENT
# =========================================================

report_agent = Agent(

    role=(
        "HELIOS Intelligence Report Generator"
    ),

    goal=(
        "Generate premium-grade "
        "technical intelligence reports."
    ),

    backstory="""

You are an elite AI reporting engine.

You specialize in:
- technical reporting
- AI intelligence summaries
- architecture documentation
- futuristic product reports
- executive-grade analysis

Your reports are:
- clean
- intelligent
- concise
- modern
- premium

You avoid:
- bloated formatting
- repetitive text
- unnecessary filler

""",

    verbose=True,

    allow_delegation=False,

    llm=helios_llm
)

# =========================================================
# RUN HELIOS CREW
# =========================================================

def run_helios_crew(

    user_task

):

    started = time.time()

    # =====================================================
    # RESEARCH TASK
    # =====================================================

    research_task = Task(

        description=f"""

Perform deep intelligence research
on the following topic:

{user_task}

Generate:
- technical analysis
- emerging trends
- strategic opportunities
- future implications
- architecture insights

Keep it:
- concise
- premium
- futuristic
- high-signal

""",

        expected_output="""

A premium research intelligence report
containing:
- deep analysis
- strategic insights
- future opportunities
- technical intelligence

""",

        agent=research_agent
    )

    # =====================================================
    # STRATEGY TASK
    # =====================================================

    strategy_task = Task(

        description=f"""

Using the research findings,
generate an advanced execution strategy
for:

{user_task}

Focus on:
- execution roadmap
- infrastructure design
- scalability
- AI architecture
- deployment strategy
- optimization systems

Keep the strategy:
- realistic
- scalable
- production-oriented
- startup-grade

""",

        expected_output="""

A strategic execution blueprint
with:
- architecture plans
- scaling strategy
- optimization paths
- production recommendations

""",

        agent=strategy_agent
    )

    # =====================================================
    # REPORT TASK
    # =====================================================

    report_task = Task(

        description=f"""

Generate the final HELIOS intelligence
report for:

{user_task}

Combine:
- research intelligence
- strategy insights
- architecture recommendations
- scalability analysis
- optimization strategy

The report must feel:
- futuristic
- executive-grade
- premium
- modern

""",

        expected_output="""

A complete professional HELIOS report
with:
- research
- strategy
- architecture
- future roadmap
- optimization analysis

""",

        agent=report_agent
    )

    # =====================================================
    # CREW
    # =====================================================

    crew = Crew(

        agents=[

            research_agent,

            strategy_agent,

            report_agent
        ],

        tasks=[

            research_task,

            strategy_task,

            report_task
        ],

        process=Process.sequential,

        verbose=True
    )

    # =====================================================
    # EXECUTION
    # =====================================================

    try:

        result = crew.kickoff()

        duration = round(

            time.time() - started,

            2
        )

        return f"""

# ⚡ HELIOS Crew Intelligence Report

Execution Time:
{duration}s

Crew Synchronization:
Stable

Agents Active:
- Research Intelligence
- Strategic Planning
- Report Generation

---

{str(result)}

---

# ✅ HELIOS Crew Complete

Distributed AI coordination stabilized successfully.

"""

    except Exception as e:

        logger.exception(
            "Crew execution failed"
        )

        return f"""

# ❌ HELIOS Crew Failure

Error:
{str(e)}

"""