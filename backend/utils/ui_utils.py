import re
import streamlit as st

# =====================================
# DANGEROUS PATTERNS
# =====================================

_DANGEROUS_PATTERNS = [

    r"<script[\s\S]*?>[\s\S]*?</script>",
    r"<iframe[\s\S]*?>[\s\S]*?</iframe>",
    r"<object[\s\S]*?>[\s\S]*?</object>",
    r"<embed[\s\S]*?>[\s\S]*?</embed>",
    r"<style[\s\S]*?>[\s\S]*?</style>",
    r"<svg[\s\S]*?>[\s\S]*?</svg>",
    r"javascript:",
    r"vbscript:",
    r"onerror=",
    r"onload=",
    r"onclick="
]

# =====================================
# REMOVE DANGEROUS CONTENT
# =====================================

def strip_dangerous_content(text):

    if text is None:
        return ""

    cleaned = str(text)

    for pattern in _DANGEROUS_PATTERNS:

        cleaned = re.sub(

            pattern,

            "",

            cleaned,

            flags=re.IGNORECASE
        )

    return cleaned

# =====================================
# SANITIZE TEXT
# =====================================

def sanitize_text(text):

    if text is None:
        return ""

    cleaned = strip_dangerous_content(
        text
    )
    return cleaned

# =====================================
# SAFE TEXT
# =====================================

def safe_text(text):

    if text is None:
        return ""

    cleaned = sanitize_text(
        text
    )

    cleaned = cleaned.replace(
        "\r\n",
        "\n"
    )

    cleaned = cleaned.replace(
        "\r",
        "\n"
    )

    cleaned = cleaned.replace(
        "\n",
        "<br>"
    )

    return cleaned

# =====================================
# SAFE MARKDOWN
# =====================================

def safe_markdown(text):

    if text is None:
        return ""

    text = str(text)

    # remove markdown code fences
    text = re.sub(
        r"```html",
        "",
        text
    )

    text = re.sub(
        r"```",
        "",
        text
    )

    # remove raw html tags
    text = re.sub(
        r"<[^>]+>",
        "",
        text
    )

    return safe_text(text)

# =====================================
# RENDER SAFE HTML
# =====================================

def render_safe_html(

    content,
    wrapper_style=""
):

    safe_content = safe_markdown(
        content
    )

    st.markdown(

        f"""

<div style="
overflow:hidden;
word-wrap:break-word;
white-space:normal;

{wrapper_style}
">

{safe_content}

</div>

        """,

        unsafe_allow_html=True
    )

# =====================================
# SPACER
# =====================================

def add_spacer(height=20):

    st.markdown(

        f"""

<div style="
height:{height}px;
overflow:hidden;
"></div>

        """,

        unsafe_allow_html=True
    )

# =====================================
# SECTION TITLE
# =====================================

def render_section_title(

    title,
    subtitle=""
):

    safe_title = safe_text(title)

    safe_subtitle = safe_text(subtitle)

    st.markdown(

        f"""

<div style="
margin-bottom:20px;
overflow:hidden;
">

<div style="
display:flex;
align-items:center;
gap:12px;
">

<div style="
width:10px;
height:10px;
border-radius:999px;

background:
linear-gradient(
135deg,
#7c3aed,
#2563eb
);

box-shadow:
0 0 18px rgba(124,58,237,0.42);
"></div>

<h2 style="
margin:0;
color:white;
font-size:28px;
font-weight:800;
">
{safe_title}
</h2>

</div>

<p style="
margin-top:10px;
color:#94a3b8;
font-size:14px;
line-height:1.7;
">
{safe_subtitle}
</p>

</div>

        """,

        unsafe_allow_html=True
    )

# =====================================
# GLASS CARD
# =====================================

def render_glass_card(

    title,
    content
):

    safe_title = safe_text(title)

    safe_content = safe_markdown(content)

    st.markdown(

        f"""

<div style="
position:relative;
overflow:hidden;
padding:24px;
border-radius:28px;
margin-bottom:20px;

background:
linear-gradient(
180deg,
rgba(15,23,42,0.92),
rgba(2,6,23,0.98)
);

border:
1px solid rgba(255,255,255,0.06);

backdrop-filter:blur(22px);

box-shadow:
0 10px 36px rgba(0,0,0,0.18);
">

<div style="
color:white;
font-size:18px;
font-weight:800;
margin-bottom:16px;
">

{safe_title}

</div>

<div style="
color:#cbd5e1;
font-size:15px;
line-height:1.9;
overflow-wrap:break-word;
word-break:break-word;
">

{safe_content}

</div>

</div>

        """,

        unsafe_allow_html=True
    )

# =====================================
# STATUS BADGE
# =====================================

def render_status_badge(

    label,
    status="online"
):

    colors = {

        "online":"#22c55e",
        "warning":"#f59e0b",
        "error":"#ef4444",
        "idle":"#64748b"
    }

    color = colors.get(
        status,
        "#22c55e"
    )

    safe_label = safe_text(label)

    st.markdown(

        f"""

<div style="
display:inline-flex;
align-items:center;
gap:8px;

padding:8px 14px;

border-radius:999px;

background:
rgba(255,255,255,0.04);

border:
1px solid rgba(255,255,255,0.06);

font-size:13px;
font-weight:700;

color:white;
">

<div style="
width:8px;
height:8px;

border-radius:999px;

background:{color};

box-shadow:
0 0 12px {color};
"></div>

{safe_label}

</div>

        """,

        unsafe_allow_html=True
    )

# =====================================
# DIVIDER
# =====================================

def render_divider():

    st.markdown(

        """

<div style="
margin:30px 0;

height:1px;

background:
linear-gradient(
90deg,
transparent,
rgba(255,255,255,0.08),
transparent
);
"></div>

        """,

        unsafe_allow_html=True
    )