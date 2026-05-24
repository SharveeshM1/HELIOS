import html
import streamlit as st
import re
from utils.ui_utils import safe_text
from components.ui import render_system_notice

# =========================================
# MAX RESPONSE SIZE
# =========================================

MAX_RESPONSE_CHARS = 45000

# =========================================
# CLEAN RESPONSE
# =========================================

def clean_response(text):

    if not text:
        return ""

    text = str(text)

    # =====================================
    # LIMIT SIZE
    # =====================================

    text = text[:MAX_RESPONSE_CHARS]

    # =====================================
    # REMOVE FENCED CODE BLOCKS
    # =====================================

    text = re.sub(
        r"```[a-zA-Z0-9_-]*[\s\S]*?```",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"```",
        "",
        text
    )

    # =====================================
    # REMOVE DANGEROUS TAGS
    # =====================================

    dangerous_tags = [

        "script",
        "style",
        "iframe",
        "object",
        "embed",
        "link",
        "meta"

    ]

    for tag in dangerous_tags:

        text = re.sub(
            rf"<{tag}.*?>.*?</{tag}>",
            "",
            text,
            flags=re.IGNORECASE | re.DOTALL
        )

    # =====================================
    # REMOVE INLINE EVENT HANDLERS
    # =====================================

    text = re.sub(
        r'on\w+=".*?"',
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"on\w+='.*?'",
        "",
        text,
        flags=re.IGNORECASE
    )

    # =====================================
    # REMOVE JAVASCRIPT URLS
    # =====================================

    text = re.sub(
        r"javascript:",
        "",
        text,
        flags=re.IGNORECASE
    )

    return text.strip()

# =========================================
# SANITIZE OUTPUT
# =========================================

def sanitize_output(text):

    return safe_text(text)


def render_user_message(message, module="Command Center", mode="Think"):

    clean_message = html.escape(
        str(message or "").strip()
    ).replace(
        "\n",
        "<br>"
    )

    clean_module = html.escape(
        str(module or "Command Center")
    )

    clean_mode = html.escape(
        str(mode or "Think")
    )

    if not clean_message:

        return

    st.markdown(
        f"""
<div class="helios-user-message helios-motion-card">
    <div class="helios-user-message-header">
        <div class="helios-user-avatar">U</div>
        <div>
            <strong>You</strong>
            <span>{clean_mode} reactor • {clean_module}</span>
        </div>
    </div>
    <div class="helios-user-message-body">
        {clean_message}
    </div>
</div>
        """,
        unsafe_allow_html=True
    )


def render_assistant_message(message, tone="Reply"):

    clean_message = html.escape(
        str(message or "").strip()
    ).replace(
        "\n",
        "<br>"
    )

    clean_tone = html.escape(
        str(tone or "Reply")
    )

    if not clean_message:

        return

    st.markdown(
        f"""
<div class="helios-assistant-message helios-motion-card">
    <div class="helios-assistant-message-header">
        <div class="ai-avatar">H</div>
        <div>
            <strong>HELIOS</strong>
            <span>{clean_tone}</span>
        </div>
    </div>
    <div class="helios-assistant-message-body">
        {clean_message}
    </div>
</div>
        """,
        unsafe_allow_html=True
    )

# =========================================
# AI RESPONSE RENDER
# =========================================

def render_ai_response(response):

    cleaned = clean_response(
        response
    )

    safe_response = sanitize_output(
        cleaned
    )

    line_count = len(
        [
            line
            for line in cleaned.splitlines()
            if line.strip()
        ]
    )

    confidence = (
        "High"
        if len(cleaned) > 120
        else "Draft"
    )

    st.markdown(
        f"""
<div class="ai-response-card helios-motion-card">
<div class="ai-card-header">
    <div class="ai-avatar">H</div>
    <div>
        <strong>HELIOS</strong>
        <span>Answer • reasoning summary • actions</span>
    </div>
    <em>{confidence}</em>
</div>
<div class="ai-response-grid">
    <section>
        <span>Answer</span>
        <div class="ai-response-body">
        {safe_response}
        </div>
    </section>
    <aside>
        <span>Reasoning Summary</span>
        <strong>{line_count} response lines analyzed</strong>
        <p>HELIOS routed the request through the active reactor mode, generated a concise answer, and stored this turn for session memory.</p>
        <div class="ai-action-list">
            <em>Review</em>
            <em>Export</em>
            <em>Follow up</em>
        </div>
    </aside>
</div>
</div>
        """,
        unsafe_allow_html=True
    )

    action_cols = st.columns(
        3,
        gap="small"
    )

    with action_cols[0]:

        if st.button(
            "Copy answer",
            key=f"copy_answer_{hash(cleaned)}",
            use_container_width=True
        ):

            render_system_notice(
                "success",
                "Copy prepared",
                "Browser clipboard access is limited in Streamlit, so export remains available beside it."
            )

    with action_cols[1]:

        st.download_button(
            "Export answer",
            data=cleaned,
            file_name="helios-answer.md",
            mime="text/markdown",
            key=f"export_answer_{hash(cleaned)}",
            use_container_width=True
        )

    with action_cols[2]:

        if st.button(
            "Create action",
            key=f"action_answer_{hash(cleaned)}",
            use_container_width=True
        ):

            render_system_notice(
                "success",
                "Action staged",
                "Use the Command Reactor to run the next step."
            )

    with st.expander(
        "Reasoning trace",
        expanded=False
    ):

        st.markdown(
            "- Reactor mode selected\n- Agent route resolved\n- Context checked\n- Response stored in session memory"
        )

    return cleaned
