from components.ui import (
    render_feature_grid,
    render_section_header
)


def render_quick_access():

    render_section_header(
        "HELIOS Modules",
        "Realtime cognitive systems, orchestration engines, and AI infrastructure."
    )

    render_feature_grid(
        [
            {
                "icon": "search",
                "title": "Research",
                "desc": "Realtime web intelligence and autonomous discovery.",
                "status": "ACTIVE",
                "target": "Research Center"
            },
            {
                "icon": "code",
                "title": "Code",
                "desc": "Autonomous software analysis, planning, and generation.",
                "status": "ACTIVE",
                "target": "Code Intelligence"
            },
            {
                "icon": "source",
                "title": "Files",
                "desc": "Document indexing and contextual memory retrieval.",
                "status": "ACTIVE",
                "target": "Knowledge Sources"
            },
            {
                "icon": "bars",
                "title": "Analytics",
                "desc": "Telemetry monitoring and inference diagnostics.",
                "status": "ACTIVE",
                "target": "System Analytics"
            },
            {
                "icon": "hexagon",
                "title": "Agents",
                "desc": "Distributed multi-agent collaboration systems.",
                "status": "ACTIVE",
                "target": "Collaborative AI"
            },
            {
                "icon": "voice",
                "title": "Voice",
                "desc": "Realtime conversational cognition engine.",
                "status": "ACTIVE",
                "target": "Voice AI"
            }
        ],
        columns=3
    )
