import html
import re

import streamlit as st


def esc(value):

    return html.escape(
        str(value),
        quote=True
    )


ICON_SVGS = {
    "command": """
        <svg viewBox="0 0 48 48" aria-hidden="true">
            <path d="M17 17h14v14H17z"></path>
            <path d="M17 17c-5 0-8-3-8-7s3-7 7-7 7 3 7 8v26c0 5-3 8-7 8s-7-3-7-7 3-7 8-7h14c5 0 8 3 8 7s-3 7-7 7-7-3-7-8V11c0-5 3-8 7-8s7 3 7 7-3 7-8 7H17z"></path>
        </svg>
    """,
    "code": """
        <svg viewBox="0 0 48 48" aria-hidden="true">
            <rect x="12" y="12" width="24" height="24"></rect>
            <rect x="17" y="17" width="14" height="14"></rect>
        </svg>
    """,
    "search": """
        <svg viewBox="0 0 48 48" aria-hidden="true">
            <circle cx="21" cy="21" r="10"></circle>
            <path d="M29 29l8 8"></path>
        </svg>
    """,
    "bars": """
        <svg viewBox="0 0 48 48" aria-hidden="true">
            <path d="M12 13h24M12 18h24M12 23h24M12 28h24M12 33h24"></path>
        </svg>
    """,
    "list": """
        <svg viewBox="0 0 48 48" aria-hidden="true">
            <path d="M14 12h20M14 18h20M14 24h20M14 30h20M14 36h20"></path>
        </svg>
    """,
    "voice": """
        <svg viewBox="0 0 48 48" aria-hidden="true">
            <circle cx="24" cy="24" r="12"></circle>
            <circle cx="24" cy="24" r="7" fill="currentColor" stroke="none"></circle>
        </svg>
    """,
    "infinity": """
        <svg viewBox="0 0 48 48" aria-hidden="true">
            <path d="M15 29c-5 0-8-3-8-7s3-7 8-7c7 0 11 14 18 14 5 0 8-3 8-7s-3-7-8-7c-7 0-11 14-18 14z"></path>
        </svg>
    """,
    "hexagon": """
        <svg viewBox="0 0 48 48" aria-hidden="true">
            <path d="M24 7l15 8.5v17L24 41 9 32.5v-17L24 7z"></path>
            <path d="M24 15l8 4.5v9L24 33l-8-4.5v-9L24 15z"></path>
        </svg>
    """,
    "diamond": """
        <svg viewBox="0 0 48 48" aria-hidden="true">
            <path d="M24 8l16 16-16 16L8 24 24 8z"></path>
        </svg>
    """,
    "bolt": """
        <svg viewBox="0 0 48 48" aria-hidden="true">
            <path d="M27 4L11 27h12l-2 17 16-24H25l2-16z"></path>
        </svg>
    """,
    "source": """
        <svg viewBox="0 0 48 48" aria-hidden="true">
            <rect x="11" y="11" width="26" height="26"></rect>
            <path d="M15 13l20 20M21 11l16 16M11 21l16 16"></path>
        </svg>
    """,
    "recursive": """
        <svg viewBox="0 0 48 48" aria-hidden="true">
            <path d="M24 7v34M7 24h34M12 12l24 24M36 12L12 36"></path>
            <path d="M24 7c8 5 13 10 17 17-4 7-9 12-17 17-8-5-13-10-17-17 4-7 9-12 17-17z"></path>
        </svg>
    """,
    "memory": """
        <svg viewBox="0 0 48 48" aria-hidden="true">
            <path d="M13 10h22v28H13z"></path>
            <path d="M18 15h12M18 21h12M18 27h8"></path>
        </svg>
    """,
}


ACTION_SVGS = {
    "agents": """
        <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M12 4a4 4 0 0 1 4 4v1h1a4 4 0 1 1-4 4v-1h-2v1a4 4 0 1 1-4-4h1V8a4 4 0 0 1 4-4z"></path>
        </svg>
    """,
    "command": """
        <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M9 9h6v6H9z"></path>
            <path d="M9 9H7a3 3 0 1 1 3-3v12a3 3 0 1 1-3-3h10a3 3 0 1 1-3 3V6a3 3 0 1 1 3 3H9z"></path>
        </svg>
    """,
    "upload": """
        <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M12 16V4"></path>
            <path d="M7 9l5-5 5 5"></path>
            <path d="M5 16v3h14v-3"></path>
        </svg>
    """,
    "fullscreen": """
        <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M8 3H3v5M16 3h5v5M8 21H3v-5M21 16v5h-5"></path>
        </svg>
    """,
    "moon": """
        <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M20 15.5A8 8 0 0 1 8.5 4a8.5 8.5 0 1 0 11.5 11.5z"></path>
        </svg>
    """,
    "arrow": """
        <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M12 19V5"></path>
            <path d="M5 12l7-7 7 7"></path>
        </svg>
    """,
    "search": """
        <svg viewBox="0 0 24 24" aria-hidden="true">
            <circle cx="11" cy="11" r="7"></circle>
            <path d="M16 16l5 5"></path>
        </svg>
    """,
}


def _svg_icon(name):

    icon = ICON_SVGS.get(
        name,
        ICON_SVGS["command"]
    )

    return icon


def _action_icon(name):

    icon = ACTION_SVGS.get(
        name,
        ACTION_SVGS["command"]
    )

    return icon


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


def _prime_route(
    module_name,
    mode,
    agent,
    directive
):

    st.session_state["helios_selected_module"] = module_name
    st.session_state["helios_reactor_mode"] = mode
    st.session_state["helios_reactor_agent"] = agent
    st.session_state["helios_preferred_agent"] = agent
    st.session_state["helios_reactor_directive"] = directive
    st.session_state["helios_command_palette_open"] = False
    st.session_state["helios_toolbar_message"] = (
        f"{mode} route armed for {module_name}."
    )

    _rerun()


def _command_target(command):

    if command == "Open memory":

        return "Chat History"

    if command.startswith("Open "):

        return command.replace(
            "Open ",
            "",
            1
        )

    return None


REACTOR_MODES = {
    "Think": {
        "agent": "Orion",
        "tone": "think",
        "signal": "Deep synthesis",
        "slash": "/plan",
        "directive": "Reason carefully, compare alternatives, and return the clearest answer.",
        "intent": "Understand the problem, compare paths, and produce a clear answer.",
        "output": "Concise reasoning summary, recommendation, and next step.",
        "priority": "Clarity, tradeoffs, assumptions, and confidence.",
        "avoid": "Over-executing or inventing implementation details too early.",
    },
    "Search": {
        "agent": "Nova",
        "tone": "search",
        "signal": "Evidence scan",
        "slash": "/search",
        "directive": "Prioritize source discovery, comparison, citations, and freshness.",
        "intent": "Find, compare, and synthesize evidence from available context.",
        "output": "Findings, source notes, confidence, and open gaps.",
        "priority": "Freshness, relevance, contradictions, and traceability.",
        "avoid": "Presenting unsupported claims as settled facts.",
    },
    "Build": {
        "agent": "Vega",
        "tone": "build",
        "signal": "Patch route",
        "slash": "/code",
        "directive": "Focus on implementation, code structure, concrete edits, and verification.",
        "intent": "Move from request to practical implementation.",
        "output": "Changed files, behavior summary, and verification result.",
        "priority": "Scoped edits, existing patterns, tests, and regressions.",
        "avoid": "Broad redesigns unless explicitly requested.",
    },
    "Execute": {
        "agent": "Orion",
        "tone": "execute",
        "signal": "Action loop",
        "slash": "/workflow",
        "directive": "Turn the request into ordered actions with checkpoints and outcomes.",
        "intent": "Run or plan action steps with visible checkpoints.",
        "output": "Action sequence, current state, result, and recovery path.",
        "priority": "Progress, checkpoints, observable status, and safe recovery.",
        "avoid": "Silent long-running work or vague status updates.",
    },
    "Memory": {
        "agent": "Nova",
        "tone": "memory",
        "signal": "Recall field",
        "slash": "/memory",
        "directive": "Use project memory, uploaded context, and durable facts as the main lens.",
        "intent": "Answer through stored context and project memory.",
        "output": "Relevant memory, interpretation, and what should be remembered next.",
        "priority": "Durable context, source scope, continuity, and cleanup.",
        "avoid": "Ignoring uploaded or indexed project material.",
    },
}


AGENT_OPTIONS = {
    "Auto": {
        "role": "Route to best specialist",
        "load": "adaptive",
    },
    "Orion": {
        "role": "Planning, synthesis, execution",
        "load": "stable",
    },
    "Vega": {
        "role": "Code intelligence and build work",
        "load": "ready",
    },
    "Nova": {
        "role": "Research, sources, memory",
        "load": "ready",
    },
    "Lyra": {
        "role": "Voice, transcript, spoken flow",
        "load": "idle",
    },
}


def render_command_reactor(
    module_name,
    session_stats,
    system_state,
    *,
    file_enabled=False,
):

    mode_names = list(
        REACTOR_MODES.keys()
    )

    current_mode = st.session_state.get(
        "helios_reactor_mode",
        "Think"
    )

    if current_mode not in mode_names:

        current_mode = "Think"

    st.markdown(
        """
        <section class="helios-reactor-head helios-motion-card">
            <div>
                <span>Reactor</span>
                <strong>Route the next move</strong>
            </div>
            <em>/search /code /plan /voice</em>
        </section>
        """,
        unsafe_allow_html=True
    )

    control_cols = st.columns(
        [
            0.42,
            2.36,
            1.08,
            0.54
        ],
        gap="small"
    )

    with control_cols[0]:

        if st.button(
            "+",
            key="helios_action_tray_toggle",
            help="Open command actions",
            use_container_width=True
        ):

            st.session_state["helios_action_tray_open"] = (
                not st.session_state.get(
                    "helios_action_tray_open",
                    False
                )
            )

            _rerun()

    with control_cols[1]:

        selected_mode = st.segmented_control(
            "Command Reactor Mode",
            mode_names,
            key="helios_reactor_mode",
            label_visibility="collapsed",
            width="stretch"
        )

    with control_cols[2]:

        agent_names = list(
            AGENT_OPTIONS.keys()
        )

        preferred_agent = st.session_state.get(
            "helios_preferred_agent",
            "Auto"
        )

        if preferred_agent not in agent_names:

            preferred_agent = "Auto"

        selected_agent = st.selectbox(
            "Preferred agent",
            agent_names,
            index=agent_names.index(
                preferred_agent
            ),
            key="helios_preferred_agent",
            label_visibility="collapsed"
        )

    with control_cols[3]:

        if st.button(
            "Stop",
            key="helios_stop_generation",
            help="Cancel the next HELIOS execution checkpoint",
            use_container_width=True
        ):

            st.session_state["helios_cancel_requested"] = True

    if not selected_mode:

        selected_mode = current_mode

    mode_config = REACTOR_MODES.get(
        selected_mode,
        REACTOR_MODES["Think"]
    )

    routed_agent = (
        mode_config["agent"]
        if selected_agent == "Auto"
        else selected_agent
    )

    st.session_state["helios_reactor_agent"] = routed_agent
    st.session_state["helios_reactor_directive"] = mode_config["directive"]
    st.session_state["helios_reactor_tone"] = mode_config["tone"]
    st.session_state["helios_conversation_mode_profile"] = {
        "mode": selected_mode,
        "intent": mode_config["intent"],
        "output": mode_config["output"],
        "priority": mode_config["priority"],
        "avoid": mode_config["avoid"],
    }

    request_count = session_stats.get(
        "requests",
        0
    )

    uploaded_count = session_stats.get(
        "uploaded_files",
        0
    )

    runtime_state = system_state.get(
        "status",
        "operational"
    )

    active_agents = system_state.get(
        "active_agents",
        []
    )

    agent_line = (
        ", ".join(active_agents)
        if active_agents
        else routed_agent
    )

    file_signal = (
        "Files armed"
        if file_enabled
        else "Text only"
    )

    web_signal = (
        "Web ready"
        if selected_mode in {
            "Search",
            "Think"
        }
        else "Web standby"
    )

    cancel_signal = (
        "Stop armed"
        if st.session_state.get("helios_cancel_requested")
        else "Stop idle"
    )

    telemetry_chips = [
        ("Mode", selected_mode),
        ("Agent", agent_line),
        ("Memory", f"{uploaded_count} files"),
        ("Context", file_signal),
        ("Web", web_signal),
        ("Core", runtime_state),
        ("Runs", str(request_count)),
        ("Stop", cancel_signal.replace("Stop ", "")),
    ]

    telemetry_html = "".join(
        f"""
        <span>
            <small>{esc(label)}</small>
            <b>{esc(value)}</b>
        </span>
        """
        for label, value in telemetry_chips
    )

    st.markdown(
        f"""
        <div class="helios-mode-signal helios-mode-{esc(mode_config["tone"])}"></div>
        <section class="helios-reactor-shell reactor-{esc(mode_config["tone"])}">
            <div class="helios-reactor-orb" aria-hidden="true">
                <span></span>
                <i></i>
            </div>
            <div class="helios-reactor-main">
                <div class="helios-reactor-label">{esc(mode_config["slash"])} route</div>
                <strong>{esc(selected_mode)} mode</strong>
                <p>{esc(mode_config["signal"])} routed through {esc(agent_line)}.</p>
            </div>
            <div class="helios-reactor-pills">
                {telemetry_html}
            </div>
        </section>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <section class="helios-mode-contract helios-motion-card">
            <div class="helios-mode-contract-head">
                <span>Conversation Mode</span>
                <strong>{esc(selected_mode)} Contract</strong>
            </div>
            <div class="helios-mode-contract-grid">
                <article>
                    <span>Intent</span>
                    <p>{esc(mode_config["intent"])}</p>
                </article>
                <article>
                    <span>Output</span>
                    <p>{esc(mode_config["output"])}</p>
                </article>
                <article>
                    <span>Priority</span>
                    <p>{esc(mode_config["priority"])}</p>
                </article>
                <article>
                    <span>Avoid</span>
                    <p>{esc(mode_config["avoid"])}</p>
                </article>
            </div>
        </section>
        """,
        unsafe_allow_html=True
    )

    if st.session_state.get(
        "helios_action_tray_open"
    ):

        st.markdown(
            """
            <section class="helios-action-tray helios-motion-card">
                <div>
                    <strong>Action Tray</strong>
                    <span>Attach context, jump modules, or open command tools.</span>
                </div>
            </section>
            """,
            unsafe_allow_html=True
        )

        actions = [
            ("Upload", "Knowledge Sources"),
            ("Voice", "Voice AI"),
            ("Mission", "Mission Control"),
            ("Memory", "Chat History"),
            ("Search", "Research Center"),
            ("Plan", "Planning Engine"),
            ("Palette", None),
        ]

        action_cols = st.columns(
            len(actions),
            gap="small"
        )

        for index, (label, target) in enumerate(actions):

            with action_cols[index]:

                if st.button(
                    label,
                    key=f"reactor_action_{_slug(label)}",
                    use_container_width=True
                ):

                    if target:

                        _set_module(
                            target
                        )

                    else:

                        st.session_state["helios_command_palette_open"] = (
                            not st.session_state.get(
                                "helios_command_palette_open",
                                False
                            )
                        )

                        _rerun()

    return selected_mode


def render_mission_stack(session_stats, system_state):

    requests = session_stats.get(
        "requests",
        0
    )

    voice_requests = session_stats.get(
        "voice_requests",
        0
    )

    uploaded_files = session_stats.get(
        "uploaded_files",
        0
    )

    last_agent = system_state.get(
        "last_agent"
    ) or st.session_state.get(
        "helios_reactor_agent",
        "Orion"
    )

    reasoning_depth = system_state.get(
        "reasoning_depth",
        0
    )

    mode = st.session_state.get(
        "helios_reactor_mode",
        "Think"
    )

    cards = [
        ("Mission", "Route every request through a visible intent, context, and execution path."),
        ("Next Move", f"Use {mode} mode with {last_agent} for the next instruction."),
        ("Memory", f"{uploaded_files} uploaded sources and {requests} completed runs available."),
    ]

    card_html = "".join(
        f"""
        <article>
            <span>{esc(label)}</span>
            <strong>{esc(body)}</strong>
        </article>
        """
        for label, body in cards
    )

    st.markdown(
        f"""
        <section class="helios-mission-stack helios-motion-card">
            <div class="helios-mission-head">
                <div>
                    <span>Live Mission Stack</span>
                    <strong>Command Center Operational</strong>
                </div>
                <div class="helios-mission-badges">
                    <span>{requests} runs</span>
                    <span>{voice_requests} voice</span>
                    <span>{reasoning_depth} trace</span>
                </div>
            </div>
            <div class="helios-mission-grid">
                {card_html}
            </div>
        </section>
        """,
        unsafe_allow_html=True
    )


def render_status_strip(module_name, session_stats, system_state):

    uploaded_files = session_stats.get(
        "uploaded_files",
        0
    )

    request_count = session_stats.get(
        "requests",
        0
    )

    status = system_state.get(
        "status",
        "operational"
    )

    active_agents = system_state.get(
        "active_agents",
        []
    )

    agent = (
        ", ".join(active_agents)
        if active_agents
        else st.session_state.get(
            "helios_reactor_agent",
            "Orion"
        )
    )

    latency = st.session_state.get(
        "helios_last_latency_ms",
        0
    )

    cards = [
        ("Module", module_name),
        ("Model", "qwen2.5:3b"),
        ("Backend", "ready" if status == "operational" else status),
        ("Memory", f"{uploaded_files} files"),
        ("Agent", agent),
        ("Latency", f"{latency} ms"),
        ("Runs", request_count),
    ]

    cards_html = "".join(
        f"""
        <div>
            <span>{esc(label)}</span>
            <strong>{esc(value)}</strong>
        </div>
        """
        for label, value in cards
    )

    st.markdown(
        f"""
        <section class="helios-status-strip helios-motion-card">
            {cards_html}
        </section>
        """,
        unsafe_allow_html=True
    )


def render_execution_lanes(system_state):

    runtime_mode = system_state.get(
        "mode",
        "idle"
    )

    current_stage = st.session_state.get(
        "helios_processing_stage",
        "Done"
    )

    lanes = [
        ("Observe", "Collect prompt, files, memory, and web hints."),
        ("Plan", "Choose mode, agent, tools, and response shape."),
        ("Act", "Run search, task routing, and cognitive engine."),
        ("Reflect", "Store memory, summarize, and suggest next action."),
    ]

    lane_html = "".join(
        f"""
        <article class="{'active' if runtime_mode == 'processing' and index < 3 else ''}">
            <span>{esc(label)}</span>
            <strong>{esc(body)}</strong>
        </article>
        """
        for index, (label, body) in enumerate(lanes)
    )

    timeline = st.session_state.get(
        "helios_execution_timeline",
        []
    )[-5:]

    if not timeline:

        timeline = [
            "Waiting for the next HELIOS instruction."
        ]

    timeline_html = "".join(
        f"<li>{esc(item)}</li>"
        for item in timeline
    )

    last_summary = st.session_state.get(
        "helios_last_run_summary",
        "No completed run in this session yet."
    )

    st.markdown(
        f"""
        <section class="helios-execution-lanes helios-motion-card">
            <div class="helios-execution-head">
                <div>
                    <span>Execution Lanes</span>
                    <strong>Observe -> Plan -> Act -> Reflect</strong>
                </div>
                <em>{esc(current_stage)}</em>
            </div>
            <div class="helios-lane-grid">
                {lane_html}
            </div>
            <div class="helios-run-summary">
                <strong>Last run summary</strong>
                <p>{esc(last_summary)}</p>
                <ul>{timeline_html}</ul>
            </div>
        </section>
        """,
        unsafe_allow_html=True
    )


def render_agent_matrix(system_state):

    active_agents = set(
        system_state.get(
            "active_agents",
            []
        )
    )

    preferred_agent = st.session_state.get(
        "helios_preferred_agent",
        "Auto"
    )

    cards_html = "".join(
        f"""
        <article class="{'active' if name in active_agents or name == preferred_agent else ''}">
            <span>{esc(name)}</span>
            <strong>{esc(config["role"])}</strong>
            <em>{esc(config["load"])}</em>
        </article>
        """
        for name, config in AGENT_OPTIONS.items()
        if name != "Auto"
    )

    st.markdown(
        f"""
        <section class="helios-agent-matrix helios-motion-card">
            <div class="helios-agent-head">
                <span>Agent Routing</span>
                <strong>Manual override: {esc(preferred_agent)}</strong>
            </div>
            <div class="helios-agent-grid">
                {cards_html}
            </div>
        </section>
        """,
        unsafe_allow_html=True
    )


def render_system_notice(kind, title, detail=""):

    st.markdown(
        f"""
        <section class="helios-system-notice notice-{esc(kind)} helios-motion-card">
            <strong>{esc(title)}</strong>
            <p>{esc(detail)}</p>
        </section>
        """,
        unsafe_allow_html=True
    )


def render_agent_status(agent):

    st.markdown(
        f"""
        <section class="helios-agent-status helios-motion-card">
            <span></span>
            <strong>HELIOS activated</strong>
            <em>{esc(agent)}</em>
        </section>
        """,
        unsafe_allow_html=True
    )


def render_system_snapshot(system_name, cpu, ram):

    st.markdown(
        f"""
        <section class="helios-system-snapshot helios-motion-card">
            <div>
                <span>System</span>
                <strong>{esc(system_name)}</strong>
            </div>
            <div>
                <span>CPU</span>
                <strong>{esc(cpu)}</strong>
            </div>
            <div>
                <span>RAM</span>
                <strong>{esc(ram)}</strong>
            </div>
        </section>
        """,
        unsafe_allow_html=True
    )


def render_voice_cockpit(mic_available, transcript="", error_message=""):

    transcript_text = (
        transcript
        if transcript
        else "Transcript stream is waiting for microphone input."
    )

    mic_state = (
        "Mic package online"
        if mic_available
        else "Mic package missing"
    )

    bars = "".join(
        "<span></span>"
        for _ in range(18)
    )

    st.markdown(
        f"""
        <section class="helios-voice-cockpit helios-motion-card">
            <div class="helios-voice-orb">
                <span></span>
            </div>
            <div class="helios-voice-main">
                <div class="helios-voice-head">
                    <span>Voice Cockpit</span>
                    <strong>{esc(mic_state)}</strong>
                </div>
                <div class="helios-waveform">{bars}</div>
                <p>{esc(transcript_text)}</p>
            </div>
        </section>
        """,
        unsafe_allow_html=True
    )

    toggle = getattr(
        st,
        "toggle",
        st.checkbox
    )

    voice_defaults = {
        "helios_voice_push_to_talk": True,
        "helios_voice_hands_free": False,
        "helios_voice_response_enabled": True,
    }

    for key, value in voice_defaults.items():

        if key not in st.session_state:

            st.session_state[key] = value

    voice_cols = st.columns(
        3,
        gap="small"
    )

    with voice_cols[0]:

        toggle(
            "Push-to-talk",
            key="helios_voice_push_to_talk"
        )

    with voice_cols[1]:

        toggle(
            "Hands-free mode",
            key="helios_voice_hands_free"
        )

    with voice_cols[2]:

        toggle(
            "Voice response",
            key="helios_voice_response_enabled"
        )

    if error_message:

        render_system_notice(
            "error",
            "Voice transcription issue",
            error_message
        )


def render_command_shell(
    title,
    subtitle,
    kicker="AI OS",
    status="ORION • BACKEND READY",
    icon="command",
    tabs=None,
    metrics=None,
    assistant_note="HELIOS is online. Choose a module and I will keep the workspace scoped to that mode.",
):

    tabs = tabs or [
        "Overview",
        "Activity",
        "Launchpad"
    ]

    metrics = metrics or []

    metric_html = "".join(
        f"""
        <div class="tone-{index % 4}">
            <span>{esc(item.get("label", ""))}</span>
            <strong>{esc(item.get("value", ""))}</strong>
        </div>
        """
        for index, item in enumerate(metrics)
    )

    metrics_block = (
        f'<div class="helios-command-metrics">{metric_html}</div>'
        if metric_html else ""
    )

    shell_id = _slug(title)

    if st.session_state.get("helios_focus_mode"):

        st.markdown(
            """
            <style>
            section[data-testid="stSidebar"]{
                display:block !important;
                visibility:visible !important;
                width:72px !important;
                min-width:72px !important;
                max-width:72px !important;
                overflow:hidden !important;
            }
            section[data-testid="stSidebar"] > div,
            section[data-testid="stSidebar"] [data-testid="stSidebarContent"]{
                width:72px !important;
                min-width:72px !important;
                max-width:72px !important;
                overflow:hidden !important;
            }
            section[data-testid="stSidebar"] .stTextInput,
            section[data-testid="stSidebar"] .helios-module-rail,
            section[data-testid="stSidebar"] .helios-nav-group-label{
                display:none !important;
            }
            section[data-testid="stSidebar"] .stButton button{
                justify-content:center !important;
                padding:0 !important;
            }
            .block-container{
                max-width:1440px !important;
                padding-left:22px !important;
                padding-right:22px !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

    if st.session_state.get("helios_theme") == "calm":

        st.markdown(
            """
            <style>
            .stApp,
            div[data-testid="stAppViewContainer"],
            section[data-testid="stMain"]{
                background:
                linear-gradient(rgba(46,72,99,0.16) 1px, transparent 1px),
                linear-gradient(90deg, rgba(46,72,99,0.14) 1px, transparent 1px),
                radial-gradient(circle at 70% 8%, rgba(31,109,169,0.18), transparent 28%),
                linear-gradient(180deg,#050812 0%,#07101c 100%) !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        f"""
        <section class="helios-command-bridge helios-motion-card">
            <div class="helios-bridge-copy">
                <span>HELIOS AI</span>
                <h1>{esc(title)}</h1>
                <p>{esc(subtitle)}</p>
            </div>
            <div class="helios-bridge-status">
                <span class="is-live">Live</span>
                <span>{esc(status.replace(" • BACKEND READY", " ready"))}</span>
                <span>qwen</span>
            </div>
        </section>
        """,
        unsafe_allow_html=True
    )

    toolbar_cols = st.columns(
        [
            1,
            1,
            1,
            1,
            1
        ],
        gap="small"
    )

    toolbar_actions = [
        ("Agents", "agents"),
        ("Command", "command"),
        ("Export", "upload"),
        ("Focus", "fullscreen"),
        ("Theme", "moon")
    ]

    for label, icon_name in toolbar_actions:

        with toolbar_cols[
            toolbar_actions.index((label, icon_name))
        ]:

            if st.button(
                label,
                key=f"toolbar_{shell_id}_{_slug(label)}",
                use_container_width=True
            ):

                if label == "Command":

                    st.session_state["helios_command_palette_open"] = (
                        not st.session_state.get(
                            "helios_command_palette_open",
                            False
                        )
                    )

                elif label == "Export":

                    st.session_state["helios_export_ready"] = title

                elif label == "Focus":

                    st.session_state["helios_focus_mode"] = (
                        not st.session_state.get(
                            "helios_focus_mode",
                            False
                        )
                    )

                elif label == "Theme":

                    st.session_state["helios_theme"] = (
                        "calm"
                        if st.session_state.get("helios_theme") != "calm"
                        else "signal"
                    )

                else:

                    st.session_state["helios_toolbar_message"] = (
                        f"{label} controls ready for {title}."
                    )

                _rerun()

    toolbar_message = st.session_state.get(
        "helios_toolbar_message"
    )

    if toolbar_message:

        toolbar_message = str(toolbar_message).replace(
            "Agents controls",
            "Agent controls"
        ).replace(
            "controls armed",
            "controls ready"
        )

        st.session_state["helios_toolbar_message"] = toolbar_message

        st.markdown(
            f"""
            <div class="helios-action-notice">
                {esc(toolbar_message)}
            </div>
            """,
            unsafe_allow_html=True
        )

    if st.session_state.get("helios_export_ready") == title:

        st.download_button(
            "Download module brief",
            data=(
                f"# {title}\n\n"
                f"{subtitle}\n\n"
                f"Status: {status}\n"
            ),
            file_name=f"helios-{shell_id}.md",
            mime="text/markdown",
            use_container_width=True
        )

    st.markdown(
        f"""
        <section class="helios-command-card helios-motion-card">
            <div class="helios-command-icon">{_svg_icon(icon)}</div>
            <div>
                <div class="helios-command-status">{esc(kicker)} workspace</div>
                <h2>{esc(title)}</h2>
                <p>{esc(subtitle)}</p>
            </div>
            <div class="helios-command-card-aside">
                <span>{esc(status)}</span>
                <strong>Ready</strong>
            </div>
        </section>
        """,
        unsafe_allow_html=True
    )

    tab_key = f"helios_tab_{shell_id}"

    if (
        tab_key not in st.session_state
        or
        st.session_state[tab_key] not in tabs
    ):

        st.session_state[tab_key] = tabs[0]

    selected_tab = st.radio(
        "Module section",
        tabs,
        horizontal=True,
        key=tab_key,
        label_visibility="collapsed"
    )

    st.markdown(
        f"""
        <div class="helios-tab-panel helios-motion-card">
            <strong>{esc(selected_tab)}</strong>
            <span>{esc(title)} workspace is scoped to {esc(selected_tab.lower())}.</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <section class="helios-command-page helios-motion-card">

            {metrics_block}
            <div class="helios-command-message">
                <strong>HELIOS</strong>
                <p>{esc(assistant_note or "")}</p>
            </div>
        </section>
        """,
        unsafe_allow_html=True
    )

    return selected_tab


def render_command_palette(active="Open Command Center"):

    route_commands = [
        {
            "label": "Plan a mission",
            "module": "Mission Control",
            "mode": "Execute",
            "agent": "Orion",
            "desc": "Create agent lanes, checkpoints, risks, and artifacts.",
            "directive": "Turn the next request into a mission with agent lanes, checkpoints, risks, and artifacts."
        },
        {
            "label": "Search with sources",
            "module": "Research Center",
            "mode": "Search",
            "agent": "Nova",
            "desc": "Prime HELIOS for evidence, citations, and comparisons.",
            "directive": "Prioritize source discovery, comparison, citations, and freshness."
        },
        {
            "label": "Inspect code",
            "module": "Code Intelligence",
            "mode": "Build",
            "agent": "Vega",
            "desc": "Route the next ask toward files, patches, and verification.",
            "directive": "Focus on implementation, code structure, concrete edits, and verification."
        },
        {
            "label": "Use memory",
            "module": "Knowledge Sources",
            "mode": "Memory",
            "agent": "Nova",
            "desc": "Use indexed files and durable project context first.",
            "directive": "Use project memory, uploaded context, and durable facts as the main lens."
        },
        {
            "label": "Build workflow",
            "module": "Workflow Engine",
            "mode": "Execute",
            "agent": "Orion",
            "desc": "Convert a goal into ordered workflow steps and recovery.",
            "directive": "Turn the next request into workflow steps, runs, logs, and recovery."
        },
        {
            "label": "Reason deeply",
            "module": "Recursive Reasoning",
            "mode": "Think",
            "agent": "Orion",
            "desc": "Inspect assumptions, alternatives, risks, and confidence.",
            "directive": "Reason carefully, compare alternatives, and return the clearest answer."
        },
    ]

    utility_commands = [
        {
            "label": "New chat",
            "desc": "Clear local chat history for a fresh workspace.",
            "action": "new_chat"
        },
        {
            "label": "Upload source",
            "desc": "Jump to Knowledge Sources and index context.",
            "action": "upload_source"
        },
        {
            "label": "Open memory",
            "desc": "Review saved chat memory.",
            "action": "open_memory"
        },
        {
            "label": "Export thread",
            "desc": "Prepare the current thread for export.",
            "action": "export_thread"
        },
    ]

    st.markdown(
        """
        <section class="helios-command-palette helios-motion-card">
            <div class="helios-palette-title">
                <strong>Command Palette 2.0</strong>
                <span>Prime module, mode, agent, and directive for the next move.</span>
            </div>
        </section>
        """,
        unsafe_allow_html=True
    )

    query = st.text_input(
        "Search commands or jump to a module",
        key="helios_command_query",
        placeholder="Search commands or jump to a module...",
        label_visibility="collapsed"
    )

    normalized_query = query.lower().strip()

    filtered_routes = [
        command
        for command in route_commands
        if not normalized_query
        or normalized_query in (
            f"{command['label']} {command['module']} "
            f"{command['mode']} {command['agent']} {command['desc']}"
        ).lower()
    ]

    filtered_utilities = [
        command
        for command in utility_commands
        if not normalized_query
        or normalized_query in (
            f"{command['label']} {command['desc']}"
        ).lower()
    ]

    if not filtered_routes and not filtered_utilities:

        render_empty_state(
            "No matching commands."
        )

        return

    st.markdown(
        """
        <div class="helios-palette-group-label">Routes</div>
        """,
        unsafe_allow_html=True
    )

    for index, command in enumerate(filtered_routes):

        st.markdown(
            f"""
            <div class="helios-palette-command-card">
                <div>
                    <strong>{esc(command["label"])}</strong>
                    <span>{esc(command["desc"])}</span>
                </div>
                <em>{esc(command["mode"])} • {esc(command["agent"])} • {esc(command["module"])}</em>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(
            f"Arm {command['label']}",
            key=f"palette_route_{index}_{_slug(command['label'])}",
            use_container_width=True
        ):

            _prime_route(
                command["module"],
                command["mode"],
                command["agent"],
                command["directive"]
            )

    st.markdown(
        """
        <div class="helios-palette-group-label">Utilities</div>
        """,
        unsafe_allow_html=True
    )

    for index, command in enumerate(filtered_utilities):

        st.markdown(
            f"""
            <div class="helios-palette-command-card compact">
                <div>
                    <strong>{esc(command["label"])}</strong>
                    <span>{esc(command["desc"])}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(
            command["label"],
            key=f"palette_utility_{index}_{_slug(command['label'])}",
            use_container_width=True
        ):

            action = command["action"]

            if action == "new_chat":

                st.session_state["chat_history"] = []
                st.session_state["helios_toolbar_message"] = (
                    "New chat workspace opened."
                )

            elif action == "upload_source":

                st.session_state["helios_selected_module"] = (
                    "Knowledge Sources"
                )
                st.session_state["helios_reactor_mode"] = "Memory"
                st.session_state["helios_reactor_agent"] = "Nova"

            elif action == "open_memory":

                st.session_state["helios_selected_module"] = "Chat History"

            elif action == "export_thread":

                st.session_state["helios_export_ready"] = "Command Center"
                st.session_state["helios_toolbar_message"] = (
                    "Thread export prepared."
                )

            st.session_state["helios_command_palette_open"] = False

            _rerun()


def render_section_header(title, subtitle="", icon=""):

    st.markdown(
        f"""
        <div class="helios-section-header">
            <h2>{esc(icon)} {esc(title)}</h2>
            <p>{esc(subtitle)}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_feature_grid(items, columns=3):

    columns = max(1, min(columns, 4))

    cols = st.columns(columns)

    for index, item in enumerate(items):

        with cols[index % columns]:

            st.markdown(
                f"""
                <div class="helios-feature-card helios-motion-card">
                    <div class="helios-feature-top">
                        <div class="helios-feature-icon">{_svg_icon(item.get("icon", "command"))}</div>
                        <div class="helios-feature-status">{esc(item.get("status", "ACTIVE"))}</div>
                    </div>
                    <h3>{esc(item.get("title", "Module"))}</h3>
                    <p>{esc(item.get("desc", ""))}</p>
                    <div class="helios-feature-foot">
                        <span></span>
                        SYSTEM ONLINE
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            target = item.get(
                "target"
            )

            button_label = (
                f"Open {target}"
                if target
                else f"Activate {item.get('title', 'Module')}"
            )

            if st.button(
                button_label,
                key=f"feature_{index}_{_slug(item.get('title', 'module'))}",
                use_container_width=True
            ):

                if target:

                    _set_module(
                        target
                    )

                else:

                    st.session_state["helios_active_feature"] = item.get(
                        "title",
                        "Module"
                    )

                    st.session_state["helios_toolbar_message"] = (
                        f"{item.get('title', 'Module')} is active."
                    )

                    _rerun()

    active_feature = st.session_state.get(
        "helios_active_feature"
    )

    if active_feature:

        st.markdown(
            f"""
            <div class="helios-action-notice">
                {esc(active_feature)} is ready. Use the chat command bar below to run it with your next instruction.
            </div>
            """,
            unsafe_allow_html=True
        )


def render_stat_grid(items, columns=4):

    columns = max(1, min(columns, 4))

    cols = st.columns(columns)

    for index, item in enumerate(items):

        with cols[index % columns]:

            st.markdown(
                f"""
                <div class="helios-stat-card helios-motion-card tone-{index % 4}">
                    <span>{esc(item.get("label", ""))}</span>
                    <strong>{esc(item.get("value", ""))}</strong>
                    <p>{esc(item.get("caption", ""))}</p>
                </div>
                """,
                unsafe_allow_html=True
            )


def render_empty_state(message):

    st.markdown(
        f"""
        <div class="helios-empty-state helios-motion-card">
            {esc(message)}
        </div>
        """,
        unsafe_allow_html=True
    )
