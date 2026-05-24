import streamlit as st

from core.shared_bus import (
    shared_bus
)

from utils.ui_utils import (
    sanitize_text
)


# =========================================
# AGENT MONITOR
# =========================================

def render_agent_monitor():

    st.markdown(
        """
        <div style="
            margin-top:30px;
            margin-bottom:22px;
        ">

            <h2 style="
                margin:0;

                color:white;

                font-size:28px;
                font-weight:800;

                letter-spacing:-0.4px;
            ">
                Agent Collaboration Bus
            </h2>

            <p style="
                margin-top:10px;

                color:#94a3b8;

                font-size:14px;

                line-height:1.8;
            ">
                Distributed multi-agent orchestration and realtime HELIOS communication telemetry
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    messages = shared_bus.get_messages()

    # =====================================
    # EMPTY STATE
    # =====================================

    if not messages:

        st.markdown(
            """
            <div style="
                position:relative;

                overflow:hidden;

                padding:28px;

                border-radius:30px;

                background:
                linear-gradient(
                    180deg,
                    rgba(15,23,42,0.90),
                    rgba(2,6,23,0.98)
                );

                border:
                1px solid rgba(255,255,255,0.06);

                backdrop-filter:blur(24px);

                box-shadow:
                0 10px 35px rgba(0,0,0,0.22);
            ">

                <div style="
                    position:absolute;

                    width:220px;
                    height:220px;

                    border-radius:999px;

                    background:
                    rgba(124,58,237,0.12);

                    top:-100px;
                    right:-100px;

                    filter:blur(32px);
                "></div>

                <div style="
                    position:relative;
                    z-index:2;

                    display:flex;
                    align-items:center;

                    gap:18px;
                ">

                    <div style="
                        width:58px;
                        height:58px;

                        border-radius:18px;

                        background:
                        linear-gradient(
                            135deg,
                            #7c3aed,
                            #2563eb
                        );

                        display:flex;
                        align-items:center;
                        justify-content:center;

                        font-size:26px;

                        box-shadow:
                        0 0 26px rgba(124,58,237,0.35);
                    ">
                        AG
                    </div>

                    <div>

                        <div style="
                            color:white;

                            font-size:18px;
                            font-weight:800;

                            margin-bottom:8px;
                        ">
                            No Active Agent Communication
                        </div>

                        <div style="
                            color:#94a3b8;

                            font-size:14px;

                            line-height:1.8;
                        ">
                            HELIOS agent collaboration systems are currently idle
                        </div>

                    </div>

                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        return

    # =====================================
    # MESSAGE CARDS
    # =====================================

    for msg in reversed(messages[-6:]):

        sender = sanitize_text(
            msg.get(
                "sender",
                "Unknown"
            )
        )

        receiver = sanitize_text(
            msg.get(
                "receiver",
                "Unknown"
            )
        )

        content = sanitize_text(
            msg.get(
                "content",
                ""
            )
        ).replace(
            "\n",
            "<br>"
        )

        st.markdown(
            f"""
            <div style="
                position:relative;

                overflow:hidden;

                margin-bottom:22px;

                padding:26px;

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
                0 12px 34px rgba(0,0,0,0.22);

                transition:
                transform .25s ease,
                border .25s ease,
                box-shadow .25s ease;
            ">

                <div style="
                    position:absolute;

                    width:220px;
                    height:220px;

                    border-radius:999px;

                    background:
                    rgba(124,58,237,0.12);

                    top:-110px;
                    right:-110px;

                    filter:blur(34px);
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

                        flex-wrap:wrap;

                        gap:18px;

                        margin-bottom:22px;
                    ">

                        <div style="
                            display:flex;
                            align-items:center;

                            gap:16px;
                        ">

                            <div style="
                                width:60px;
                                height:60px;

                                border-radius:20px;

                                background:
                                linear-gradient(
                                    135deg,
                                    #7c3aed,
                                    #2563eb
                                );

                                display:flex;
                                align-items:center;
                                justify-content:center;

                                font-size:26px;

                                box-shadow:
                                0 0 28px rgba(124,58,237,0.35);
                            ">
                                AG
                            </div>

                            <div>

                                <div style="
                                    color:white;

                                    font-size:19px;
                                    font-weight:800;

                                    margin-bottom:6px;

                                    overflow-wrap:break-word;
                                    word-break:break-word;
                                ">
                                    {sender}
                                    →
                                    {receiver}
                                </div>

                                <div style="
                                    color:#94a3b8;

                                    font-size:13px;
                                ">
                                    HELIOS inter-agent communication pipeline
                                </div>

                            </div>

                        </div>

                        <div style="
                            padding:8px 15px;

                            border-radius:999px;

                            background:
                            rgba(34,197,94,0.12);

                            border:
                            1px solid rgba(34,197,94,0.18);

                            display:flex;
                            align-items:center;

                            gap:8px;

                            color:#86efac;

                            font-size:11px;
                            font-weight:800;

                            letter-spacing:0.5px;
                        ">

                            <div style="
                                width:10px;
                                height:10px;

                                border-radius:999px;

                                background:#22c55e;

                                box-shadow:
                                0 0 14px #22c55e;
                            "></div>

                            LIVE

                        </div>

                    </div>

                    <div style="
                        padding:20px;

                        border-radius:22px;

                        background:
                        rgba(255,255,255,0.03);

                        border:
                        1px solid rgba(255,255,255,0.05);

                        color:#cbd5e1;

                        font-size:14px;

                        line-height:1.9;

                        overflow-wrap:break-word;
                        word-break:break-word;

                        white-space:pre-wrap;
                    ">

                        {content}

                    </div>

                </div>

            </div>
            """,
            unsafe_allow_html=True
        )
