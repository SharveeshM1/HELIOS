import streamlit as st
from api.ai_provider import (
    stream_ai_response
)
from memory.vector_memory import (
    store_memory,
    search_memory
)
from memory.system_memory import (

    store_fact,

    get_fact
)

# =========================================
# PAGE CONFIG
# =========================================

st.set_page_config(
    page_title="HELIOS",
    page_icon="⚡",
    layout="wide"
)

# =========================================
# CUSTOM CSS
# =========================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #0b0f19;
        color: white;
    }

    .main-title {
        font-size: 52px;
        font-weight: 800;
        color: #00ffd5;
        text-align: center;
        margin-top: 10px;
    }

    .subtitle {
        text-align: center;
        color: #7f8ea3;
        margin-bottom: 30px;
    }

    .response-box {
        background: #111827;
        padding: 20px;
        border-radius: 18px;
        border: 1px solid #1f2937;
        margin-top: 20px;
        font-size: 17px;
        line-height: 1.7;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# =========================================
# HEADER
# =========================================

st.markdown(
    '<div class="main-title">⚡ HELIOS</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Autonomous AI Operating System</div>',
    unsafe_allow_html=True
)

# =========================================
# LIVE METRICS & CONSOLE
# =========================================

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Agents",
    "4"
)

col2.metric(
    "Memory",
    "Persistent"
)

col3.metric(
    "Model",
    "qwen2.5"
)

col4.metric(
    "Execution",
    "Active"
)

# realtime execution console placeholder
console = st.empty()

# thinking and agent/tool placeholders
thinking_box = st.empty()
agent_box = st.empty()
tool_box = st.empty()

# execution timeline
timeline = st.container()

# autonomous status sidebar
with st.sidebar:
    st.header("HELIOS Core")
    st.success("Ollama Connected")
    st.success("Memory Active")
    st.success("Agents Online")
    st.success("Streaming Enabled")

# =========================================
# INPUT
# =========================================

query = st.text_area(
    "Enter your objective:",
    height=160,
    placeholder="Build an autonomous AI trading system..."
)

# =========================================
# FACT STORAGE DETECTION
# =========================================

if "uses" in query.lower():

    parts = query.split("uses")

    if len(parts) > 1:

        fact_value = parts[1].strip()

        store_fact(

            "startup_stack",

            fact_value
        )

# =========================================
# BUTTON
# =========================================

if st.button("Launch HELIOS"):

    if query.strip():

        with st.spinner("HELIOS reasoning..."):

            response_container = st.empty()

            full_response = ""

            # =========================================
            # MEMORY RETRIEVAL
            # =========================================

            memories = search_memory(
                query
            )

            memory_context = "\n".join(
                memories
            )

            stored_stack = get_fact(
                "startup_stack"
            )

            system_memory_context = f"""

HELIOS SYSTEM CONFIGURATION:

startup_stack:
{stored_stack}

IMPORTANT:
The exact configured model is:
qwen2.5:3b

This is authoritative system memory.
Do not alter or summarize it.

"""

            enhanced_query = f"""

            SYSTEM MEMORY:

            {system_memory_context}

            VECTOR MEMORY:

            {memory_context}

            USER REQUEST:

            {query}

            """

            for chunk in stream_ai_response(
                enhanced_query
            ):

                full_response += chunk

                response_container.markdown(
                    f'''
                    <div class="response-box">
                    {full_response}
                    </div>
                    ''',
                    unsafe_allow_html=True
                )

                # also update realtime execution console
                console.code(
                    full_response,
                    language="python"
                )

                # live thinking / agent / tool updates
                agent = "HELIOS"
                tool = "Reasoner"

                agent_box.info(
                    f"Active Agent: {agent}"
                )

                tool_box.warning(
                    f"Executing Tool: {tool}"
                )

                thinking_box.code(
                    f"Objective: {query}"
                )

            # =========================================
            # STORE MEMORY
            # =========================================

            store_memory(

                str(hash(query)),

                f"""

USER:
{query}

HELIOS:
{full_response}

"""
            )

            # update execution timeline
            with timeline:
                st.markdown(
                    f"""
✅ Agent `{agent}` executed `{tool}`
"""
                )

            # show self-reflection area
            st.markdown("## 🧠 HELIOS Self Reflection")

            reflection_output = full_response

            st.write(
                reflection_output
            )

    else:

        st.warning("Enter a valid query.")