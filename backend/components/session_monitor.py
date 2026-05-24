import streamlit as st

from utils.ui_utils import (
    sanitize_text
)


def render_session_monitor(stats):

    requests = sanitize_text(
        stats.get("requests", 0)
    )

    voice_requests = sanitize_text(
        stats.get("voice_requests", 0)
    )

    uploaded_files = sanitize_text(
        stats.get("uploaded_files", 0)
    )

    st.markdown(
        """

        <div style="
            margin-top:34px;
            margin-bottom:20px;
        ">

            <h2 style="
                margin:0;

                color:white;

                font-size:30px;
                font-weight:900;
            ">
                ⚡ Session Monitor
            </h2>

            <p style="
                margin-top:10px;

                color:#94a3b8;

                font-size:15px;

                line-height:1.8;
            ">
                Realtime cognitive telemetry and HELIOS interaction analytics
            </p>

        </div>

        """,
        unsafe_allow_html=True
    )

    metrics = [

        {
            "title": "Requests",
            "value": requests,
            "sub": "Inference execution pipelines",
            "icon": "🧠",
            "gradient": "linear-gradient(135deg,#7c3aed,#2563eb)"
        },

        {
            "title": "Voice",
            "value": voice_requests,
            "sub": "Realtime speech intelligence",
            "icon": "🎤",
            "gradient": "linear-gradient(135deg,#2563eb,#06b6d4)"
        },

        {
            "title": "Files",
            "value": uploaded_files,
            "sub": "Document cognition systems",
            "icon": "📁",
            "gradient": "linear-gradient(135deg,#7c3aed,#9333ea)"
        }
    ]

    cols = st.columns(3)

    for col, metric in zip(cols, metrics):

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
            metric.get("icon", "⚡")
        )

        gradient = metric.get(
            "gradient",
            "linear-gradient(135deg,#7c3aed,#2563eb)"
        )

        with col:

            st.markdown(
                f"""

                <div style="
                    position:relative;

                    overflow:hidden;

                    min-height:240px;

                    padding:24px;

                    margin-bottom:20px;

                    border-radius:28px;

                    background:
                    linear-gradient(
                        180deg,
                        rgba(15,23,42,0.96),
                        rgba(2,6,23,0.98)
                    );

                    border:
                    1px solid rgba(255,255,255,0.05);

                    backdrop-filter:blur(24px);

                    box-shadow:
                    0 12px 28px rgba(0,0,0,0.18);
                ">

                    <div style="
                        position:absolute;

                        width:180px;
                        height:180px;

                        border-radius:999px;

                        background:
                        rgba(124,58,237,0.10);

                        top:-80px;
                        right:-80px;

                        filter:blur(28px);
                    "></div>

                    <div style="
                        position:relative;
                        z-index:2;
                    ">

                        <div style="
                            display:flex;
                            align-items:center;
                            justify-content:space-between;

                            gap:12px;

                            margin-bottom:24px;
                        ">

                            <div style="
                                width:58px;
                                height:58px;

                                flex-shrink:0;

                                border-radius:18px;

                                background:{gradient};

                                display:flex;
                                align-items:center;
                                justify-content:center;

                                font-size:28px;

                                box-shadow:
                                0 0 24px rgba(124,58,237,0.35);
                            ">
                                {icon}
                            </div>

                            <div style="
                                padding:7px 12px;

                                border-radius:999px;

                                background:
                                rgba(124,58,237,0.12);

                                border:
                                1px solid rgba(168,85,247,0.18);

                                color:#d8b4fe;

                                font-size:11px;
                                font-weight:800;

                                letter-spacing:0.4px;

                                white-space:nowrap;
                            ">
                                LIVE
                            </div>

                        </div>

                        <div style="
                            color:#94a3b8;

                            font-size:14px;

                            margin-bottom:10px;

                            overflow-wrap:break-word;
                            word-break:break-word;
                        ">
                            {title}
                        </div>

                        <div style="
                            color:white;

                            font-size:42px;
                            font-weight:900;

                            line-height:1;

                            overflow-wrap:break-word;
                            word-break:break-word;
                        ">
                            {value}
                        </div>

                        <div style="
                            margin-top:16px;

                            color:#94a3b8;

                            font-size:14px;

                            line-height:1.8;

                            overflow-wrap:break-word;
                            word-break:break-word;
                        ">
                            {subtitle}
                        </div>

                        <div style="
                            margin-top:24px;

                            height:8px;

                            border-radius:999px;

                            overflow:hidden;

                            background:
                            rgba(255,255,255,0.06);
                        ">

                            <div style="
                                width:88%;

                                height:100%;

                                border-radius:999px;

                                background:{gradient};

                                box-shadow:
                                0 0 16px rgba(124,58,237,0.4);
                            "></div>

                        </div>

                    </div>

                </div>

                """,
                unsafe_allow_html=True
            )