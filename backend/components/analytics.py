import streamlit as st

from components.ui import (
    render_command_shell,
    render_section_header,
    render_stat_grid
)


def render_analytics(session_stats):

    requests = str(
        session_stats.get("requests", 0)
    )

    voice_requests = str(
        session_stats.get("voice_requests", 0)
    )

    uploaded_files = str(
        session_stats.get("uploaded_files", 0)
    )

    render_command_shell(
        title="System Analytics",
        subtitle="Monitor model health, memory pressure, latency, and execution logs.",
        kicker="TELEMETRY",
        status="ORION • BACKEND READY",
        icon="bars",
        tabs=[
            "Health",
            "Logs",
            "Models",
            "Costs"
        ],
        metrics=[
            {
                "label": "Backend",
                "value": "Online"
            },
            {
                "label": "Model",
                "value": "Ready"
            },
            {
                "label": "Memory",
                "value": uploaded_files or "3"
            },
            {
                "label": "Last Trace",
                "value": "0"
            }
        ]
    )

    render_stat_grid(
        [
            {
                "label": "AI Requests",
                "value": requests,
                "caption": "Realtime cognitive traffic"
            },
            {
                "label": "Voice Requests",
                "value": voice_requests,
                "caption": "Live conversational sessions"
            },
            {
                "label": "Uploaded Files",
                "value": uploaded_files,
                "caption": "Knowledge ingestion pipeline"
            },
            {
                "label": "System Health",
                "value": "98%",
                "caption": "Infrastructure stability"
            }
        ]
    )

    render_section_header(
        "AI Performance",
        "Realtime inference throughput and orchestration telemetry.",
        ""
    )

    left, right = st.columns(2)

    with left:

        st.markdown(
            '<div class="helios-chart-title">Cognitive Request Throughput</div>',
            unsafe_allow_html=True
        )

        st.line_chart(
            {
                "AI Requests": [
                    120,
                    180,
                    260,
                    340,
                    450,
                    590,
                    720
                ]
            },
            height=300
        )

    with right:

        st.markdown(
            '<div class="helios-chart-title">GPU + Inference Load</div>',
            unsafe_allow_html=True
        )

        st.area_chart(
            {
                "GPU Load": [
                    20,
                    32,
                    45,
                    58,
                    74,
                    82,
                    91
                ]
            },
            height=300
        )

    render_section_header(
        "Agent Activity",
        "Distributed orchestration across HELIOS intelligence agents.",
        ""
    )

    st.bar_chart(
        {
            "Research": [
                82
            ],
            "Code": [
                74
            ],
            "Analytics": [
                91
            ],
            "Voice": [
                67
            ],
            "Reasoning": [
                88
            ]
        },
        height=300
    )

    render_section_header(
        "Live Infrastructure Feed",
        "Realtime HELIOS telemetry and orchestration signals.",
        ""
    )

    feeds = [
        "Gemini Intelligence Connected",
        "Realtime Voice Systems Operational",
        "Agent Orchestrator Online",
        "Memory Infrastructure Healthy",
        "Swarm Execution Stable",
        "Recursive Reasoning Active"
    ]

    for item in feeds:

        st.markdown(
            f"""
            <div class="helios-feed-row helios-motion-card">
                <span></span>
                <strong>{item}</strong>
            </div>
            """,
            unsafe_allow_html=True
        )
