import streamlit as st

from components.cards import (
    render_glass_card
)

from utils.ui_utils import (
    sanitize_text
)


# =========================================
# METRICS SECTION
# =========================================

def render_metrics(chat_history):

    total_memory = len(chat_history)

    metrics = [

        {
            "icon": "AI",
            "title": "AI Agents",
            "value": "11",
            "sub": "Distributed orchestration intelligence"
        },

        {
            "icon": "EX",
            "title": "Tasks",
            "value": "128",
            "sub": "Autonomous execution pipelines"
        },

        {
            "icon": "MM",
            "title": "Memory",
            "value": str(total_memory),
            "sub": "Persistent contextual cognition"
        },

        {
            "icon": "OK",
            "title": "System",
            "value": "ONLINE",
            "sub": "Infrastructure operating normally"
        }
    ]

    # =====================================
    # SECTION HEADER
    # =====================================

    st.markdown(
        """
        <div style="
            position:relative;
            overflow:hidden;

            margin-top:12px;
            margin-bottom:28px;

            padding:28px;

            border-radius:32px;

            background:
            linear-gradient(
                135deg,
                rgba(15,23,42,0.92),
                rgba(2,6,23,0.98)
            );

            border:
            1px solid rgba(255,255,255,0.05);

            backdrop-filter:blur(24px);

            box-shadow:
            0 10px 36px rgba(0,0,0,0.18);
        ">

            <div style="
                position:absolute;

                width:220px;
                height:220px;

                border-radius:999px;

                background:
                rgba(124,58,237,0.10);

                top:-100px;
                right:-80px;

                filter:blur(38px);
            "></div>

            <div style="
                position:relative;
                z-index:2;
            ">

                <div style="
                    display:inline-flex;
                    align-items:center;
                    gap:10px;

                    padding:8px 16px;

                    border-radius:999px;

                    background:
                    rgba(124,58,237,0.12);

                    border:
                    1px solid rgba(168,85,247,0.18);

                    margin-bottom:20px;
                ">

                    <div style="
                        width:10px;
                        height:10px;

                        border-radius:999px;

                        background:#22c55e;

                        box-shadow:
                        0 0 14px #22c55e;
                    "></div>

                    <span style="
                        color:#d8b4fe;

                        font-size:12px;
                        font-weight:800;

                        letter-spacing:0.5px;
                    ">
                        HELIOS CORE
                    </span>

                </div>

                <h2 style="
                    margin:0;

                    color:white;

                    font-size:34px;
                    font-weight:900;

                    letter-spacing:-0.8px;
                ">
                    Core Infrastructure
                </h2>

                <p style="
                    margin-top:14px;

                    color:#94a3b8;

                    font-size:15px;

                    line-height:1.9;

                    max-width:760px;
                ">
                    Realtime HELIOS infrastructure telemetry, distributed orchestration intelligence, and autonomous cognitive system activity.
                </p>

            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    # =====================================
    # RESPONSIVE GRID
    # =====================================

    cols = st.columns(
        len(metrics)
    )

    for index, metric in enumerate(metrics):

        title = sanitize_text(
            metric.get("title", "")
        )

        value = sanitize_text(
            metric.get("value", "")
        )

        subtitle = sanitize_text(
            metric.get("sub", "")
        )

        icon = sanitize_text(
            metric.get("icon", "AI")
        )

        with cols[index]:

            render_glass_card(

                title=title,

                value=value,

                subtitle=subtitle,

                icon=icon
            )

    # =====================================
    # LIVE STATUS STRIP
    # =====================================

    st.markdown(
        """
        <div style="
            position:relative;
            overflow:hidden;

            margin-top:10px;

            padding:20px 24px;

            border-radius:26px;

            background:
            linear-gradient(
                180deg,
                rgba(15,23,42,0.88),
                rgba(2,6,23,0.95)
            );

            border:
            1px solid rgba(255,255,255,0.05);

            backdrop-filter:blur(20px);

            display:flex;
            align-items:center;
            justify-content:space-between;

            flex-wrap:wrap;

            gap:18px;

            box-shadow:
            0 10px 30px rgba(0,0,0,0.18);
        ">

            <div style="
                display:flex;
                align-items:center;

                gap:14px;
            ">

                <div style="
                    width:14px;
                    height:14px;

                    border-radius:999px;

                    background:#22c55e;

                    box-shadow:
                    0 0 18px #22c55e;
                "></div>

                <div style="
                    color:white;

                    font-size:15px;
                    font-weight:800;
                ">
                    HELIOS Infrastructure Stable
                </div>

            </div>

            <div style="
                color:#94a3b8;

                font-size:13px;

                line-height:1.8;

                overflow-wrap:break-word;
                word-break:break-word;
            ">
                All cognition layers synchronized successfully.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )
