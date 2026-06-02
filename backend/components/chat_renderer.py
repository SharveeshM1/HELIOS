import html
import streamlit as st
import re
from utils.ui_utils import safe_text

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


def response_to_html(text):

    clean_text = clean_response(
        text
    )

    parts = []
    cursor = 0

    for match in re.finditer(
        r"```([a-zA-Z0-9_+-]*)\n?([\s\S]*?)```",
        clean_text
    ):

        before = clean_text[cursor:match.start()]

        if before.strip():

            parts.append(
                _plain_text_to_html(
                    before
                )
            )

        language = html.escape(
            match.group(1).strip()
        )

        code = html.escape(
            match.group(2).strip()
        )

        label = (
            f"<span>{language}</span>"
            if language
            else ""
        )

        parts.append(
            f"""
            <pre class="helios-code-block">{label}<code>{code}</code></pre>
            """
        )

        cursor = match.end()

    remainder = clean_text[cursor:]

    if remainder.strip():

        parts.append(
            _plain_text_to_html(
                remainder
            )
        )

    return "".join(
        parts
    )


def _plain_text_to_html(text):

    escaped = html.escape(
        str(text or "").strip()
    )

    escaped = re.sub(
        r"\*\*(.*?)\*\*",
        r"<strong>\1</strong>",
        escaped
    )

    lines = escaped.splitlines()
    html_lines = []

    for line in lines:

        stripped = line.strip()

        if not stripped:

            html_lines.append(
                "<br>"
            )
            continue

        if stripped.startswith("### "):

            html_lines.append(
                f"<h4>{stripped[4:]}</h4>"
            )
            continue

        if stripped.startswith(("- ", "* ")):

            html_lines.append(
                f"<p class=\"helios-answer-bullet\">{stripped[2:]}</p>"
            )
            continue

        html_lines.append(
            f"<p>{stripped}</p>"
        )

    return "\n".join(
        html_lines
    )

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

    safe_response = response_to_html(
        cleaned
    )

    confidence = (
        "Ready"
        if cleaned
        else "Draft"
    )

    st.markdown(
        f"""
<div class="ai-response-card helios-motion-card">
<div class="ai-card-header">
    <div class="ai-avatar">H</div>
    <div>
        <strong>HELIOS</strong>
        <span>Direct answer</span>
    </div>
    <em>{confidence}</em>
</div>
<div class="ai-response-body">
    {safe_response}
</div>
</div>
        """,
        unsafe_allow_html=True
    )

    return cleaned
