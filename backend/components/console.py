import time

import streamlit as st

from components.ui import (
    esc,
    render_section_header
)


def render_console(events=None):

    events = events or []

    if not events:

        events = [
            {
                "time": time.strftime("%H:%M:%S"),
                "label": "RUN",
                "message": "Task router idle. Send a request to start the live ledger.",
                "status": "IDLE",
                "actor": "Orion",
                "module": "Command Center"
            }
        ]

    visible_events = list(
        reversed(
            events[-10:]
        )
    )

    console_rows = "".join(
        f"""
        <div class="helios-terminal-row status-{esc(str(item.get("status", "OK")).lower())}">
            <span>{esc(item.get("time", "--:--:--"))}</span>
            <strong>{esc(item.get("label", "RUN"))}</strong>
            <p>{esc(item.get("message", ""))}</p>
            <small>{esc(item.get("actor", "Orion"))} • {esc(item.get("module", "Command Center"))}</small>
            <em>{esc(item.get("status", "OK"))}</em>
        </div>
        """
        for item in visible_events
    )

    last_status = visible_events[0].get(
        "status",
        "IDLE"
    )

    render_section_header(
        "Execution Log",
        "Live run ledger from real HELIOS stages."
    )

    st.markdown(
        f"""
        <div class="helios-terminal helios-motion-card helios-execution-log">
            <div class="helios-terminal-top">
                <div>
                    <span></span>
                    <strong>{esc(last_status)}</strong>
                </div>
                <small>stream://helios</small>
            </div>
            <div class="helios-terminal-grid">
                {console_rows}
            </div>
            <details class="helios-log-drawer">
                <summary>Run ledger details</summary>
                <div>
                    {console_rows}
                </div>
            </details>
        </div>
        """,
        unsafe_allow_html=True
    )
