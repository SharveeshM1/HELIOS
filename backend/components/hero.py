from components.ui import (
    render_command_shell
)


def render_hero(session_stats=None, system_state=None):

    session_stats = session_stats or {}
    system_state = system_state or {}

    requests = session_stats.get(
        "requests",
        0
    )

    uploaded_files = session_stats.get(
        "uploaded_files",
        0
    )

    reasoning_depth = system_state.get(
        "reasoning_depth",
        0
    )

    backend_status = system_state.get(
        "status",
        "operational"
    )

    render_command_shell(
        title="Command Center",
        subtitle="Live control surface for models, agents, memory, and active execution.",
        kicker="AI OS",
        status="ORION • BACKEND READY",
        icon="command",
        tabs=[
            "Overview",
            "Activity",
            "Launchpad"
        ],
        metrics=[
            {
                "label": "Backend",
                "value": backend_status.title()
            },
            {
                "label": "Runs",
                "value": str(requests)
            },
            {
                "label": "Memory",
                "value": str(uploaded_files)
            },
            {
                "label": "Last Trace",
                "value": str(reasoning_depth)
            }
        ],
    )
