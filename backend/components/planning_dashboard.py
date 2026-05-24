import streamlit as st

from utils.ui_utils import (
    sanitize_text
)


# =========================================
# PLANNING DASHBOARD
# =========================================

def render_planning_dashboard():

    # =====================================
    # HERO SECTION
    # =====================================

    st.markdown(
        """
        <div style="
            position:relative;

            overflow:hidden;

            padding:40px;

            border-radius:36px;

            background:
            linear-gradient(
                180deg,
                rgba(15,23,42,0.94),
                rgba(2,6,23,0.99)
            );

            border:
            1px solid rgba(255,255,255,0.06);

            backdrop-filter:blur(26px);

            margin-bottom:32px;

            box-shadow:
            0 14px 40px rgba(0,0,0,0.24);
        ">

            <div style="
                position:absolute;

                width:300px;
                height:300px;

                border-radius:999px;

                background:
                rgba(124,58,237,0.16);

                top:-130px;
                right:-100px;

                filter:blur(46px);
            "></div>

            <div style="
                position:absolute;

                inset:0;

                background:
                linear-gradient(
                    135deg,
                    rgba(255,255,255,0.03),
                    transparent 45%
                );

                pointer-events:none;
            "></div>

            <div style="
                position:relative;
                z-index:2;

                display:flex;
                align-items:center;
                justify-content:space-between;

                flex-wrap:wrap;

                gap:36px;
            ">

                <div>

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

                        margin-bottom:24px;
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

                            font-size:13px;
                            font-weight:800;

                            letter-spacing:0.6px;
                        ">
                            HELIOS PLANNING CORE
                        </span>

                    </div>

                    <h1 style="
                        margin:0;

                        font-size:54px;
                        font-weight:900;

                        line-height:1.02;

                        letter-spacing:-1.4px;

                        color:white;
                    ">
                        Autonomous <br/>
                        Planning Engine
                    </h1>

                    <p style="
                        margin-top:24px;

                        max-width:760px;

                        color:#94a3b8;

                        font-size:16px;

                        line-height:1.95;
                    ">
                        HELIOS autonomously generates workflows, assigns intelligent agents, builds execution pipelines, and optimizes orchestration strategies dynamically using realtime contextual cognition.
                    </p>

                </div>

                <div style="
                    width:220px;
                    height:220px;

                    border-radius:44px;

                    background:
                    radial-gradient(
                        circle at top,
                        rgba(168,85,247,0.60),
                        rgba(37,99,235,0.14)
                    );

                    border:
                    1px solid rgba(255,255,255,0.08);

                    display:flex;
                    align-items:center;
                    justify-content:center;

                    backdrop-filter:blur(24px);

                    box-shadow:
                    0 0 70px rgba(124,58,237,0.32);
                ">

                    <div style="
                        font-size:88px;
                    ">
                        🧠
                    </div>

                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    # =====================================
    # CAPABILITIES
    # =====================================

    st.markdown(
        """
        <div style="
            margin-top:10px;
            margin-bottom:24px;
        ">

            <h2 style="
                margin:0;

                color:white;

                font-size:30px;
                font-weight:900;

                letter-spacing:-0.5px;
            ">
                ⚡ Planning Capabilities
            </h2>

            <p style="
                margin-top:10px;

                color:#94a3b8;

                font-size:15px;

                line-height:1.8;
            ">
                Autonomous orchestration and intelligent workflow generation systems
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    capabilities = [

        {
            "icon":"🧩",
            "title":"Workflow Generation",
            "desc":"Build intelligent execution chains dynamically"
        },

        {
            "icon":"🤖",
            "title":"Agent Assignment",
            "desc":"Select optimal AI agents for every task"
        },

        {
            "icon":"⚡",
            "title":"Execution Optimization",
            "desc":"Continuously optimize orchestration strategies"
        },

        {
            "icon":"📈",
            "title":"Adaptive Planning",
            "desc":"Refine plans using realtime contextual cognition"
        }
    ]

    cols = st.columns(2)

    for index, item in enumerate(capabilities):

        icon = sanitize_text(item["icon"])
        title = sanitize_text(item["title"])
        desc = sanitize_text(item["desc"])

        with cols[index % 2]:

            st.markdown(
                f"""
                <div style="
                    position:relative;

                    overflow:hidden;

                    min-height:250px;

                    margin-bottom:22px;

                    padding:28px;

                    border-radius:30px;

                    background:
                    linear-gradient(
                        180deg,
                        rgba(15,23,42,0.92),
                        rgba(2,6,23,0.98)
                    );

                    border:
                    1px solid rgba(255,255,255,0.06);

                    backdrop-filter:blur(24px);

                    box-shadow:
                    0 12px 34px rgba(0,0,0,0.20);

                    transition:
                    transform .25s ease,
                    border .25s ease,
                    box-shadow .25s ease;
                ">

                    <div style="
                        position:absolute;

                        width:200px;
                        height:200px;

                        border-radius:999px;

                        background:
                        rgba(124,58,237,0.10);

                        top:-90px;
                        right:-90px;

                        filter:blur(30px);
                    "></div>

                    <div style="
                        position:absolute;

                        inset:0;

                        background:
                        linear-gradient(
                            135deg,
                            rgba(255,255,255,0.03),
                            transparent 45%
                        );

                        pointer-events:none;
                    "></div>

                    <div style="
                        position:relative;
                        z-index:2;
                    ">

                        <div style="
                            display:flex;
                            align-items:center;
                            justify-content:space-between;

                            margin-bottom:26px;
                        ">

                            <div style="
                                font-size:34px;
                            ">
                                {icon}
                            </div>

                            <div style="
                                padding:7px 14px;

                                border-radius:999px;

                                background:
                                rgba(124,58,237,0.12);

                                border:
                                1px solid rgba(168,85,247,0.16);

                                color:#d8b4fe;

                                font-size:11px;
                                font-weight:800;

                                letter-spacing:0.5px;
                            ">
                                ACTIVE
                            </div>

                        </div>

                        <div style="
                            color:white;

                            font-size:22px;
                            font-weight:900;

                            margin-bottom:14px;

                            overflow-wrap:break-word;
                            word-break:break-word;
                        ">
                            {title}
                        </div>

                        <div style="
                            color:#94a3b8;

                            font-size:15px;

                            line-height:1.95;

                            overflow-wrap:break-word;
                            word-break:break-word;
                        ">
                            {desc}
                        </div>

                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

    # =====================================
    # TELEMETRY
    # =====================================

    st.markdown(
        """
        <div style="
            margin-top:12px;
            margin-bottom:22px;
        ">

            <h2 style="
                margin:0;

                color:white;

                font-size:30px;
                font-weight:900;

                letter-spacing:-0.5px;
            ">
                📡 Planning Telemetry
            </h2>

            <p style="
                margin-top:10px;

                color:#94a3b8;

                font-size:15px;

                line-height:1.8;
            ">
                Realtime autonomous orchestration and workflow execution monitoring
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    telemetry = [

        "Workflow generation engine operational",

        "Agent routing synchronized",

        "Execution planning stable",

        "Autonomous orchestration active",

        "Optimization systems healthy"
    ]

    for item in telemetry:

        telemetry_text = sanitize_text(item)

        st.markdown(
            f"""
            <div style="
                position:relative;

                overflow:hidden;

                margin-bottom:16px;

                padding:22px;

                border-radius:26px;

                background:
                linear-gradient(
                    180deg,
                    rgba(15,23,42,0.92),
                    rgba(2,6,23,0.98)
                );

                border:
                1px solid rgba(255,255,255,0.06);

                display:flex;
                align-items:center;

                gap:16px;

                box-shadow:
                0 10px 24px rgba(0,0,0,0.16);
            ">

                <div style="
                    width:12px;
                    height:12px;

                    border-radius:999px;

                    background:#22c55e;

                    box-shadow:
                    0 0 16px #22c55e;
                "></div>

                <div style="
                    color:white;

                    font-size:15px;
                    font-weight:700;

                    overflow-wrap:break-word;
                    word-break:break-word;
                ">
                    {telemetry_text}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )