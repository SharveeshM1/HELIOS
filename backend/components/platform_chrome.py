from datetime import datetime
import html
import re

import streamlit as st


MODULE_PROFILES = {
    "Command Center": {
        "agent": "Orion",
        "signal": "AI OS",
        "summary": "Command overview, active execution, and global control.",
    },
    "Mission Control": {
        "agent": "Orion",
        "signal": "Mission",
        "summary": "Missions, risk radar, council review, memory, and archive.",
    },
    "System Analytics": {
        "agent": "Orion",
        "signal": "Telemetry",
        "summary": "Model health, memory pressure, performance, and runtime signals.",
    },
    "Voice AI": {
        "agent": "Lyra",
        "signal": "Voice",
        "summary": "Speech input, transcript flow, and hands-free control.",
    },
    "Research Center": {
        "agent": "Nova",
        "signal": "Research",
        "summary": "Source discovery, synthesis, citation, and evidence mapping.",
    },
    "Code Intelligence": {
        "agent": "Vega",
        "signal": "Build",
        "summary": "Repository analysis, implementation planning, and verification.",
    },
    "Collaborative AI": {
        "agent": "Orion",
        "signal": "Council",
        "summary": "Multi-agent handoffs, decisions, and shared artifacts.",
    },
    "Swarm Intelligence": {
        "agent": "Orion",
        "signal": "Swarm",
        "summary": "Parallel routing, queues, and agent load coordination.",
    },
    "Autonomous Loop": {
        "agent": "Orion",
        "signal": "Loop",
        "summary": "Observe, plan, act, reflect cycles with guardrails.",
    },
    "Planning Engine": {
        "agent": "Orion",
        "signal": "Plan",
        "summary": "Goals, milestones, dependency graphs, and next actions.",
    },
    "Recursive Reasoning": {
        "agent": "Orion",
        "signal": "Reason",
        "summary": "Trace layers, assumptions, branches, critique, and refinement.",
    },
    "Workflow Engine": {
        "agent": "Vega",
        "signal": "Workflow",
        "summary": "Automation runs, triggers, recovery, and artifact flow.",
    },
    "Knowledge Sources": {
        "agent": "Nova",
        "signal": "Memory",
        "summary": "Uploaded sources, scopes, indexing, and durable context.",
    },
    "Chat History": {
        "agent": "Nova",
        "signal": "Recall",
        "summary": "Conversation memory, session review, and context recovery.",
    },
}


AGENT_PRESENCE = [
    ("Orion", "strategy", "online"),
    ("Nova", "research", "online"),
    ("Vega", "build", "ready"),
    ("Lyra", "voice", "idle"),
]


QUICK_TARGETS = [
    "Mission Control",
    "Research Center",
    "Code Intelligence",
    "System Analytics",
    "Voice AI",
    "Workflow Engine",
]


def esc(value):
    return html.escape(
        str(value),
        quote=True
    )


def _slug(value):
    return re.sub(
        r"[^a-z0-9]+",
        "_",
        str(value).lower()
    ).strip("_")


def _rerun():
    rerun = getattr(
        st,
        "rerun",
        None
    )

    if rerun is None:
        rerun = getattr(
            st,
            "experimental_rerun",
            None
        )

    if rerun is not None:
        rerun()


def _set_module(module_name):
    st.session_state["helios_selected_module"] = module_name
    _rerun()


def _render_presence_agents(active_agent):
    return "".join(
        f"""
        <article class="{'active' if name == active_agent else ''}">
            <span>{esc(role)}</span>
            <strong>{esc(name)}</strong>
            <em>{esc(status)}</em>
        </article>
        """
        for name, role, status in AGENT_PRESENCE
    )


def render_platform_chrome(
    selected_module,
    session_stats,
    system_state
):
    profile = MODULE_PROFILES.get(
        selected_module,
        MODULE_PROFILES["Command Center"]
    )

    active_agent = system_state.get(
        "last_agent"
    ) or st.session_state.get(
        "helios_reactor_agent",
        profile["agent"]
    )

    requests = session_stats.get(
        "requests",
        0
    )

    uploaded_files = session_stats.get(
        "uploaded_files",
        0
    )

    latency = st.session_state.get(
        "helios_last_latency_ms",
        0
    )

    clock = datetime.now().strftime(
        "%H:%M"
    )

    presence_html = _render_presence_agents(
        active_agent
    )

    st.markdown(
        f"""
        <section class="helios-platform-chrome helios-motion-card">
            <div class="helios-platform-main">
                <span>HELIOS Platform</span>
                <h2>{esc(selected_module)}</h2>
                <p>{esc(profile.get("summary", ""))}</p>
            </div>
            <div class="helios-platform-orbit" aria-hidden="true">
                <span></span>
                <i></i>
                <b></b>
            </div>
            <div class="helios-platform-signals">
                <div>
                    <span>Signal</span>
                    <strong>{esc(profile.get("signal", "AI OS"))}</strong>
                </div>
                <div>
                    <span>Agent</span>
                    <strong>{esc(active_agent)}</strong>
                </div>
                <div>
                    <span>Runs</span>
                    <strong>{esc(requests)}</strong>
                </div>
                <div>
                    <span>Files</span>
                    <strong>{esc(uploaded_files)}</strong>
                </div>
                <div>
                    <span>Latency</span>
                    <strong>{esc(latency)} ms</strong>
                </div>
                <div>
                    <span>Local</span>
                    <strong>{esc(clock)}</strong>
                </div>
            </div>
        </section>
        <section class="helios-agent-presence helios-motion-card">
            <div class="helios-presence-head">
                <span>Agent Presence</span>
                <strong>{esc(active_agent)} is steering this workspace</strong>
            </div>
            <div class="helios-presence-grid">
                {presence_html}
            </div>
        </section>
        """,
        unsafe_allow_html=True
    )

    action_labels = [
        ("Palette", "palette"),
        ("Mission", "Mission Control"),
        ("Research", "Research Center"),
        ("Code", "Code Intelligence"),
        ("Voice", "Voice AI"),
        ("Analytics", "System Analytics"),
    ]

    action_cols = st.columns(
        len(action_labels),
        gap="small"
    )

    for index, (label, target) in enumerate(
        action_labels
    ):
        with action_cols[index]:
            if st.button(
                label,
                key=f"helios_global_action_{_slug(label)}",
                use_container_width=True
            ):
                if target == "palette":
                    st.session_state["helios_platform_palette_open"] = (
                        not st.session_state.get(
                            "helios_platform_palette_open",
                            False
                        )
                    )
                    _rerun()
                else:
                    _set_module(
                        target
                    )

    if st.session_state.get(
        "helios_platform_palette_open",
        False
    ):
        _render_platform_palette(
            selected_module
        )


def _render_platform_palette(selected_module):
    st.markdown(
        """
        <section class="helios-platform-palette helios-motion-card">
            <div class="helios-palette-copy">
                <span>Command Palette 2.0</span>
                <strong>Jump modules and route work from anywhere.</strong>
            </div>
        </section>
        """,
        unsafe_allow_html=True
    )

    query = st.text_input(
        "Search HELIOS modules",
        key="helios_platform_palette_query",
        placeholder="Search modules...",
        label_visibility="collapsed"
    )

    visible_targets = [
        target
        for target in QUICK_TARGETS
        if (
            not query
            or query.lower() in target.lower()
        )
    ]

    if not visible_targets:
        st.markdown(
            """
            <div class="helios-platform-empty">
                No matching module.
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    cols = st.columns(
        min(
            len(visible_targets),
            3
        ),
        gap="small"
    )

    for index, target in enumerate(
        visible_targets
    ):
        with cols[index % len(cols)]:
            profile = MODULE_PROFILES.get(
                target,
                {}
            )
            selected = target == selected_module
            st.markdown(
                f"""
                <section class="helios-platform-jump {'active' if selected else ''}">
                    <span>{esc(profile.get("signal", "Module"))}</span>
                    <strong>{esc(target)}</strong>
                    <p>{esc(profile.get("summary", ""))}</p>
                </section>
                """,
                unsafe_allow_html=True
            )

            if not selected and st.button(
                f"Open {target}",
                key=f"helios_platform_jump_{_slug(target)}",
                use_container_width=True
            ):
                _set_module(
                    target
                )
