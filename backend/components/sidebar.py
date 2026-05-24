import re
from urllib.parse import quote

import streamlit as st


NAV_GROUPS = {
    "Core": [
        "Command Center",
        "Mission Control",
        "System Analytics",
        "Voice AI",
        "Chat History",
    ],
    "Intelligence": [
        "Research Center",
        "Code Intelligence",
        "Collaborative AI",
        "Recursive Reasoning",
    ],
    "Execution": [
        "Swarm Intelligence",
        "Autonomous Loop",
        "Planning Engine",
        "Workflow Engine",
    ],
    "Memory": [
        "Knowledge Sources",
    ],
}


NAV_ITEMS = [
    item
    for group_items in NAV_GROUPS.values()
    for item in group_items
]


NAV_ICONS = {
    "Command Center": "⌘",
    "Mission Control": "◬",
    "Research Center": "◇",
    "Code Intelligence": "{ }",
    "System Analytics": "▥",
    "Voice AI": "◍",
    "Chat History": "◴",
    "Collaborative AI": "⬡",
    "Swarm Intelligence": "✶",
    "Autonomous Loop": "⟳",
    "Planning Engine": "◱",
    "Recursive Reasoning": "∞",
    "Workflow Engine": "⧉",
    "Knowledge Sources": "◈",
}


NAV_STATUS = {
    "Command Center": "active",
    "Mission Control": "online",
    "Research Center": "online",
    "Code Intelligence": "online",
    "System Analytics": "online",
    "Voice AI": "idle",
    "Chat History": "idle",
    "Collaborative AI": "online",
    "Swarm Intelligence": "idle",
    "Autonomous Loop": "idle",
    "Planning Engine": "online",
    "Recursive Reasoning": "online",
    "Workflow Engine": "idle",
    "Knowledge Sources": "online",
}


STATUS_SYMBOLS = {
    "active": "●",
    "online": "●",
    "idle": "○",
    "warning": "▲",
}


def _key(label):

    return "nav_" + re.sub(
        r"[^a-z0-9]+",
        "_",
        label.lower()
    ).strip("_")


def _set_selected(label):

    st.session_state["helios_selected_module"] = label

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


def render_sidebar():

    query_params = getattr(
        st,
        "query_params",
        {}
    )

    query_module = query_params.get(
        "module"
    )

    if isinstance(
        query_module,
        list
    ):

        query_module = query_module[0] if query_module else None

    if query_module in NAV_ITEMS:

        st.session_state["helios_selected_module"] = query_module

    if "helios_selected_module" not in st.session_state:

        st.session_state["helios_selected_module"] = NAV_ITEMS[0]

    return st.session_state["helios_selected_module"]


def render_recovery_sidebar():

    query_params = getattr(
        st,
        "query_params",
        {}
    )

    nav_state = query_params.get(
        "nav",
        "open"
    )

    if isinstance(
        nav_state,
        list
    ):

        nav_state = nav_state[0] if nav_state else "open"

    nav_open = nav_state != "closed"

    selected = st.session_state.get(
        "helios_selected_module",
        NAV_ITEMS[0]
    )

    group_html = []

    for group_name, group_items in NAV_GROUPS.items():

        links = []

        for item in group_items:

            icon = NAV_ICONS.get(
                item,
                "•"
            )

            status = NAV_STATUS.get(
                item,
                "idle"
            )

            active = "active" if item == selected else ""
            href = f"?module={quote(item)}&nav={'open' if nav_open else 'closed'}"

            links.append(
                f"""
                <a class="helios-recovery-link {active} status-{status}" href="{href}" target="_self">
                    <span>{icon}</span>
                    <strong>{item}</strong>
                    <em>{status}</em>
                </a>
                """
            )

        group_html.append(
            f"""
            <section class="helios-recovery-group">
                <p>{group_name}</p>
                {''.join(links)}
            </section>
            """
        )

    toggle_href = (
        f"?module={quote(selected)}&nav={'closed' if nav_open else 'open'}"
    )

    st.markdown(
        f"""
        <style>
        .block-container{{
            padding-left:{'326px' if nav_open else '104px'} !important;
        }}
        div[data-testid="stBottomBlockContainer"]{{
            left:{'326px' if nav_open else '104px'} !important;
        }}
        @media (max-width:1180px){{
            div[data-testid="stBottomBlockContainer"]{{
                left:104px !important;
            }}
        }}
        @media (max-width:860px){{
            div[data-testid="stBottomBlockContainer"]{{
                left:14px !important;
            }}
        }}
        </style>
        <nav class="helios-recovery-sidebar {'is-open' if nav_open else 'is-collapsed'}">
            <div class="helios-recovery-brand">
                <span>H</span>
                <div>
                    <strong>HELIOS AI</strong>
                    <em>Control OS</em>
                </div>
                <a class="helios-recovery-toggle" href="{toggle_href}" target="_self" title="{'Collapse' if nav_open else 'Expand'} sidebar">
                    {'‹' if nav_open else '›'}
                </a>
            </div>
            <div class="helios-recovery-selected">
                <small>Current Module</small>
                <b>{selected}</b>
            </div>
            {''.join(group_html)}
        </nav>
        """,
        unsafe_allow_html=True
    )


def render_nav_toggle():

    render_recovery_sidebar()

    if "helios_nav_open" not in st.session_state:

        st.session_state["helios_nav_open"] = True

    nav_open = st.session_state["helios_nav_open"]
    focus_mode = st.session_state.get(
        "helios_focus_mode",
        False
    )
    render_open_nav = nav_open and not focus_mode

    sidebar_width = "292px" if render_open_nav else "72px"
    button_alignment = "flex-start" if render_open_nav else "center"
    button_padding = "0 12px" if render_open_nav else "0"
    sidebar_state_class = (
        "helios-sidebar-open"
        if render_open_nav
        else "helios-sidebar-collapsed"
    )

    st.markdown(
        f"""
        <style>
        div[data-testid="stSidebarHeader"],
        div[data-testid="stSidebarHeader"] *,
        section[data-testid="stSidebar"] header,
        section[data-testid="stSidebar"] header *,
        section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"],
        section[data-testid="stSidebar"] button[kind="header"],
        section[data-testid="stSidebar"] button[aria-label*="collapse" i],
        section[data-testid="stSidebar"] button[aria-label*="expand" i]{{
            display:none !important;
            visibility:hidden !important;
            pointer-events:none !important;
            width:0 !important;
            height:0 !important;
            min-height:0 !important;
            overflow:hidden !important;
        }}
        section[data-testid="stSidebar"]{{
            display:none !important;
            visibility:hidden !important;
            width:0 !important;
            min-width:0 !important;
            max-width:0 !important;
            overflow:hidden !important;
            border-right:1px solid rgba(148,163,184,0.18) !important;
            box-shadow:18px 0 44px rgba(0,0,0,0.30) !important;
        }}
        section[data-testid="stSidebar"] > div,
        section[data-testid="stSidebar"] [data-testid="stSidebarContent"]{{
            display:none !important;
            visibility:hidden !important;
            width:0 !important;
            min-width:0 !important;
            max-width:0 !important;
            overflow:hidden !important;
        }}
        section[data-testid="stSidebar"] .stButton button{{
            justify-content:{button_alignment} !important;
            padding:{button_padding} !important;
        }}
        .helios-sidebar-collapsed .stTextInput,
        .helios-sidebar-collapsed .helios-module-rail,
        .helios-sidebar-collapsed .helios-nav-group-label{{
            display:none !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    with st.sidebar:

        st.markdown(
            f"""
            <div class="helios-sidebar-shell {sidebar_state_class}">
                <div class="helios-sidebar-top">
                    <div class="helios-sidebar-wordmark">
                        <span>H</span>
                        <div>
                            <strong>HELIOS AI</strong>
                            <em>Control OS</em>
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(
            "‹" if render_open_nav else "›",
            key="helios_nav_toggle",
            help=None,
            use_container_width=True
        ):

            st.session_state["helios_nav_open"] = not nav_open

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

        if not render_open_nav:

            st.markdown(
                """
                <div class="helios-sidebar-shell helios-sidebar-collapsed">
                    <div class="helios-rail-divider"></div>
                </div>
                """,
                unsafe_allow_html=True
            )

            for item in NAV_ITEMS:

                icon = NAV_ICONS.get(
                    item,
                    "•"
                )

                status = NAV_STATUS.get(
                    item,
                    "idle"
                )

                selected = st.session_state.get(
                    "helios_selected_module",
                    NAV_ITEMS[0]
                )

                if item == selected:

                    st.markdown(
                        f"""
                        <div class="helios-compact-nav-selected status-{status}" title="{item}">
                            <span>{icon}</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                else:

                    if st.button(
                        icon,
                        key=_key(f"compact_{item}"),
                        help=item,
                        use_container_width=True
                    ):

                        _set_selected(item)

            return

        st.markdown(
            """
            <section class="helios-module-rail">
                <div class="helios-module-rail-head">
                    <strong>HELIOS Modules</strong>
                </div>
            </section>
            """,
            unsafe_allow_html=True
        )

        query = st.text_input(
            "Filter HELIOS modules",
            key="helios_module_filter",
            placeholder="Search modules...",
            label_visibility="collapsed"
        )

        selected = st.session_state.get(
            "helios_selected_module",
            NAV_ITEMS[0]
        )

        rendered_count = 0

        for group_name, group_items in NAV_GROUPS.items():

            visible_items = [
                item
                for item in group_items
                if (
                    not query
                    or query.lower() in item.lower()
                )
            ]

            if not visible_items:

                continue

            rendered_count += len(
                visible_items
            )

            st.markdown(
                f"""
                <div class="helios-nav-group-label">
                    <span>{group_name}</span>
                    <em>{len(visible_items)}</em>
                </div>
                """,
                unsafe_allow_html=True
            )

            for item in visible_items:

                icon = NAV_ICONS.get(
                    item,
                    "•"
                )

                status = NAV_STATUS.get(
                    item,
                    "idle"
                )

                status_symbol = STATUS_SYMBOLS.get(
                    status,
                    "○"
                )

                if item == selected:

                    st.markdown(
                        f"""
                        <div class="helios-inline-nav-selected status-{status}">
                            <span>{icon}</span>
                            <strong>{item}</strong>
                            <em>{status}</em>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                else:

                    if st.button(
                        f"{icon}  {item}",
                        key=_key(f"inline_{item}"),
                        help=None,
                        use_container_width=True
                    ):

                        _set_selected(item)

        if rendered_count == 0:

            st.markdown(
                """
                <div class="helios-empty-state helios-motion-card">
                    No matching HELIOS modules.
                </div>
                """,
                unsafe_allow_html=True
            )
