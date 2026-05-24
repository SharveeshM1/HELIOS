from datetime import datetime
import html
import json
import os
import re

import streamlit as st

from core.task_planner import build_execution_plan


AGENT_PROFILES = {
    "research": {
        "name": "Nova",
        "role": "evidence, source mapping, external intelligence",
        "load": "ready",
    },
    "code": {
        "name": "Vega",
        "role": "implementation, patch planning, verification",
        "load": "ready",
    },
    "analytics": {
        "name": "Orion",
        "role": "metrics, scaling, system diagnosis",
        "load": "stable",
    },
}


MISSION_MODES = [
    "Strategic Build",
    "Research Sprint",
    "Code Upgrade",
    "Autonomous Review",
]

MISSION_TEMPLATES = [
    {
        "name": "Build Feature",
        "mode": "Strategic Build",
        "priority": "High",
        "objective": "Build a polished HELIOS feature with scoped implementation, review, memory capture, and verification.",
    },
    {
        "name": "Debug System",
        "mode": "Code Upgrade",
        "priority": "High",
        "objective": "Diagnose a HELIOS issue, identify root cause, propose a clean fix, and verify the affected path.",
    },
    {
        "name": "Research Sprint",
        "mode": "Research Sprint",
        "priority": "Normal",
        "objective": "Research a topic, compare evidence, surface risks, and produce a concise decision brief.",
    },
    {
        "name": "Autonomous Review",
        "mode": "Autonomous Review",
        "priority": "Critical",
        "objective": "Review HELIOS mission readiness, find risks, run council critique, and prepare the next best action.",
    },
]

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

MISSION_ARCHIVE_FILE = os.path.join(
    BASE_DIR,
    "memory",
    "mission_archive.json"
)


def esc(value):
    return html.escape(
        str(value),
        quote=True
    )


def _slug(value):
    return re.sub(
        r"[^a-z0-9]+",
        "-",
        str(value).lower()
    ).strip("-")


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


def _summarize_goal(goal):
    goal = " ".join(
        str(goal).split()
    )

    if not goal:
        return "Design a high-impact HELIOS mission."

    if len(goal) <= 74:
        return goal

    return goal[:71].rstrip() + "..."


def _mission_defaults():
    return {
        "id": "HELIOS-MISSION-000",
        "title": "Future OS Upgrade",
        "objective": "Add a controlled futuristic mission layer without changing the existing UI foundation.",
        "mode": "Strategic Build",
        "priority": "High",
        "phase": 0,
        "created": "Standby",
        "steps": [
            {
                "phase": "Observe",
                "agent": "Orion",
                "objective": "Clarify mission intent and operating constraints.",
                "status": "active",
                "risk": "low",
            },
            {
                "phase": "Plan",
                "agent": "Nova",
                "objective": "Map knowledge, memory, and required context.",
                "status": "queued",
                "risk": "low",
            },
            {
                "phase": "Execute",
                "agent": "Vega",
                "objective": "Build scoped artifacts and verify behavior.",
                "status": "queued",
                "risk": "medium",
            },
            {
                "phase": "Reflect",
                "agent": "Orion",
                "objective": "Record outcome, risks, and next best action.",
                "status": "queued",
                "risk": "low",
            },
        ],
    }


def _load_mission_archive():
    if not os.path.exists(
        MISSION_ARCHIVE_FILE
    ):
        return []

    try:
        with open(
            MISSION_ARCHIVE_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(
                file
            )

    except Exception:
        return []

    if not isinstance(
        data,
        list
    ):
        return []

    return data


def _save_mission_archive(archive):
    os.makedirs(
        os.path.dirname(
            MISSION_ARCHIVE_FILE
        ),
        exist_ok=True
    )

    with open(
        MISSION_ARCHIVE_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            archive,
            file,
            indent=2
        )


def _archive_current_mission(mission):
    archive = _load_mission_archive()
    archived_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M"
    )

    snapshot = dict(
        mission
    )

    snapshot["archived_at"] = archived_at
    snapshot["archive_key"] = (
        f"{mission.get('id', 'HELIOS-MISSION')}-{datetime.now().strftime('%H%M%S')}"
    )

    archive = [
        item
        for item in archive
        if item.get("id") != snapshot.get("id")
    ]

    archive.insert(
        0,
        snapshot
    )

    _save_mission_archive(
        archive[:24]
    )

    return snapshot


def _risk_for_step(agent_key, priority):
    if priority == "Critical":
        return "high"

    if agent_key == "code":
        return "medium"

    return "low"


def _build_mission(goal, mode, priority):
    plan = build_execution_plan(
        goal
    )

    steps = [
        {
            "phase": "Observe",
            "agent": "Orion",
            "objective": "Capture the mission goal, context, constraints, and success signal.",
            "status": "active",
            "risk": "low",
        }
    ]

    for index, item in enumerate(plan, start=1):
        agent_key = item.get(
            "agent",
            "research"
        )

        profile = AGENT_PROFILES.get(
            agent_key,
            AGENT_PROFILES["research"]
        )

        steps.append(
            {
                "phase": f"Lane {index}",
                "agent": profile["name"],
                "objective": item.get(
                    "objective",
                    "General mission analysis"
                ),
                "status": "queued",
                "risk": _risk_for_step(
                    agent_key,
                    priority
                ),
            }
        )

    steps.append(
        {
            "phase": "Reflect",
            "agent": "Orion",
            "objective": "Package the final artifact, decision log, risks, and next best action.",
            "status": "queued",
            "risk": "low",
        }
    )

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M"
    )

    return {
        "id": f"HELIOS-MISSION-{datetime.now().strftime('%H%M%S')}",
        "title": _summarize_goal(
            goal
        ),
        "objective": str(goal).strip(),
        "mode": mode,
        "priority": priority,
        "phase": 0,
        "created": timestamp,
        "steps": steps,
    }


def _set_step_statuses(mission):
    phase = int(
        mission.get(
            "phase",
            0
        )
    )

    for index, step in enumerate(
        mission.get(
            "steps",
            []
        )
    ):
        if index < phase:
            step["status"] = "done"
        elif index == phase:
            step["status"] = "active"
        else:
            step["status"] = "queued"

    return mission


def _mission_metrics(mission):
    steps = mission.get(
        "steps",
        []
    )

    complete = len(
        [
            step
            for step in steps
            if step.get("status") == "done"
        ]
    )

    high_risk = len(
        [
            step
            for step in steps
            if step.get("risk") == "high"
        ]
    )

    agents = {
        step.get(
            "agent",
            "Orion"
        )
        for step in steps
    }

    progress = round(
        (complete / max(len(steps), 1)) * 100
    )

    return [
        ("Mission", mission.get("id", "HELIOS-MISSION")),
        ("Progress", f"{progress}%"),
        ("Agents", str(len(agents))),
        ("Risk", "High" if high_risk else "Managed"),
    ]


def _current_step(mission):
    steps = mission.get(
        "steps",
        []
    )

    if not steps:
        return {}

    index = min(
        int(mission.get("phase", 0)),
        len(steps) - 1
    )

    return steps[index]


def _mission_agent_names(mission):
    names = []

    for step in mission.get(
        "steps",
        []
    ):
        agent = step.get(
            "agent",
            "Orion"
        )

        if agent not in names:
            names.append(
                agent
            )

    return names


def _generate_council_review(mission):
    steps = mission.get(
        "steps",
        []
    )

    active_step = _current_step(
        mission
    )

    agents = _mission_agent_names(
        mission
    )

    high_risk = len(
        [
            step
            for step in steps
            if step.get("risk") == "high"
        ]
    )

    code_present = any(
        step.get("agent") == "Vega"
        for step in steps
    )

    research_present = any(
        step.get("agent") == "Nova"
        for step in steps
    )

    priority = mission.get(
        "priority",
        "High"
    )

    confidence = 86

    if high_risk:
        confidence -= 14

    if priority == "Critical":
        confidence -= 8

    if code_present and research_present:
        confidence += 4

    confidence = max(
        min(confidence, 94),
        58
    )

    opinions = [
        {
            "agent": "Orion",
            "stance": "mission architect",
            "signal": "Proceed through the active checkpoint before expanding scope.",
            "detail": f"Current focus: {active_step.get('objective', 'stabilize the mission path')}",
        },
        {
            "agent": "Nova",
            "stance": "knowledge scout",
            "signal": (
                "Evidence lane is present."
                if research_present
                else "Add a quick context scan before execution."
            ),
            "detail": "Attach assumptions, source needs, and memory hooks before final delivery.",
        },
        {
            "agent": "Vega",
            "stance": "build engineer",
            "signal": (
                "Implementation lane is ready."
                if code_present
                else "No code lane detected; keep this as planning and synthesis."
            ),
            "detail": "Keep changes scoped, verify imports, and avoid touching unrelated UI surfaces.",
        },
        {
            "agent": "Lyra",
            "stance": "voice operator",
            "signal": "Mission can be narrated into short checkpoints.",
            "detail": "Use voice later for hands-free status, recap, and next-action commands.",
        },
    ]

    verdict = (
        "Hold for risk review before execution."
        if high_risk
        else "Proceed with the active checkpoint."
    )

    return {
        "timestamp": datetime.now().strftime(
            "%Y-%m-%d %H:%M"
        ),
        "confidence": confidence,
        "verdict": verdict,
        "active_agent_count": len(agents),
        "opinions": opinions,
    }


def _generate_memory_timeline(mission):
    active_step = _current_step(
        mission
    )

    review = mission.get(
        "council_review",
        {}
    )

    complete_steps = len(
        [
            step
            for step in mission.get(
                "steps",
                []
            )
            if step.get("status") == "done"
        ]
    )

    total_steps = len(
        mission.get(
            "steps",
            []
        )
    )

    generated_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M"
    )

    review_signal = review.get(
        "verdict",
        "Council review has not been run yet."
    )

    confidence = review.get(
        "confidence",
        "pending"
    )

    return [
        {
            "kind": "intent",
            "label": "Mission Intent",
            "value": mission.get(
                "objective",
                "No objective captured."
            ),
            "time": mission.get(
                "created",
                "Standby"
            ),
        },
        {
            "kind": "checkpoint",
            "label": "Active Checkpoint",
            "value": active_step.get(
                "objective",
                "No active checkpoint."
            ),
            "time": generated_at,
        },
        {
            "kind": "decision",
            "label": "Council Signal",
            "value": f"{review_signal} Confidence: {confidence}.",
            "time": review.get(
                "timestamp",
                generated_at
            ),
        },
        {
            "kind": "progress",
            "label": "Progress Memory",
            "value": f"{complete_steps} of {total_steps} mission checkpoints completed.",
            "time": generated_at,
        },
    ]


def _generate_risk_radar(mission):
    steps = mission.get(
        "steps",
        []
    )

    review = mission.get(
        "council_review"
    )

    timeline = mission.get(
        "memory_timeline"
    )

    high_risk = len(
        [
            step
            for step in steps
            if step.get("risk") == "high"
        ]
    )

    medium_risk = len(
        [
            step
            for step in steps
            if step.get("risk") == "medium"
        ]
    )

    has_code = any(
        step.get("agent") == "Vega"
        for step in steps
    )

    has_research = any(
        step.get("agent") == "Nova"
        for step in steps
    )

    findings = []

    if not str(
        mission.get(
            "objective",
            ""
        )
    ).strip():
        findings.append(
            ("Objective", "high", "Mission objective is empty.")
        )

    if high_risk:
        findings.append(
            ("Risk", "high", f"{high_risk} high-risk checkpoint needs review.")
        )

    if medium_risk:
        findings.append(
            ("Build Risk", "medium", f"{medium_risk} implementation-sensitive checkpoint detected.")
        )

    if has_code and not review:
        findings.append(
            ("Review", "medium", "Code lane exists without a council review.")
        )

    if not has_research:
        findings.append(
            ("Context", "medium", "No Nova research lane is assigned yet.")
        )

    if not timeline:
        findings.append(
            ("Memory", "low", "Mission memory has not been captured.")
        )

    if not findings:
        findings.append(
            ("Clearance", "low", "Mission looks stable for the next checkpoint.")
        )

    score = 100
    score -= high_risk * 24
    score -= medium_risk * 12

    if not review:
        score -= 10

    if not timeline:
        score -= 6

    score = max(
        score,
        28
    )

    level = "stable"

    if score < 55 or high_risk:
        level = "critical"
    elif score < 78 or medium_risk:
        level = "watch"

    return {
        "score": score,
        "level": level,
        "findings": findings[:4],
    }


def _generate_next_actions(mission):
    actions = []

    review = mission.get(
        "council_review"
    )

    timeline = mission.get(
        "memory_timeline"
    )

    steps = mission.get(
        "steps",
        []
    )

    complete_steps = len(
        [
            step
            for step in steps
            if step.get("status") == "done"
        ]
    )

    if not review:
        actions.append(
            {
                "label": "Review",
                "key": "review",
                "detail": "Ask agents for a pass.",
            }
        )

    if not timeline:
        actions.append(
            {
                "label": "Capture",
                "key": "memory",
                "detail": "Save mission state.",
            }
        )

    if complete_steps < len(steps):
        actions.append(
            {
                "label": "Advance",
                "key": "advance",
                "detail": "Move one step.",
            }
        )

    actions.append(
        {
            "label": "Save",
            "key": "archive",
            "detail": "Archive locally.",
        }
    )

    if complete_steps >= len(steps):
        actions.insert(
            0,
            {
                "label": "Complete mission",
                "key": "complete",
                "detail": "Seal the mission and prepare it for archive.",
            }
        )

    return actions[:4]


def _apply_template(template):
    st.session_state["helios_mission_control"] = _build_mission(
        template.get(
            "objective",
            ""
        ),
        template.get(
            "mode",
            MISSION_MODES[0]
        ),
        template.get(
            "priority",
            "High"
        )
    )

    st.session_state["helios_mission_action_notice"] = (
        f"Template loaded: {template.get('name', 'Mission')}."
    )


def _render_mission_bridge(mission):
    metrics_html = "".join(
        f"""
        <div>
            <span>{esc(label)}</span>
            <strong>{esc(value)}</strong>
        </div>
        """
        for label, value in _mission_metrics(
            mission
        )
    )

    st.markdown(
        f"""
        <section class="helios-mission-control-hero helios-motion-card">
            <div class="helios-mission-control-copy">
                <span>Mission Control</span>
                <h1>{esc(mission.get("title", "Future OS Upgrade"))}</h1>
                <p>{esc(mission.get("objective", ""))}</p>
            </div>
            <div class="helios-mission-control-lattice" aria-hidden="true">
                <span></span>
                <span></span>
                <span></span>
                <span></span>
            </div>
            <div class="helios-mission-control-metrics">
                {metrics_html}
            </div>
        </section>
        """,
        unsafe_allow_html=True
    )


def _render_futuristic_control_deck(mission):
    current_step = _current_step(
        mission
    )

    used_agents = _mission_agent_names(
        mission
    )

    radar_nodes = [
        ("Orion", "Strategy", "top"),
        ("Nova", "Research", "left"),
        ("Vega", "Code", "right"),
        ("Lyra", "Voice", "bottom"),
    ]

    radar_html = "".join(
        f"""
        <article class="deck-node-{esc(position)} {'active' if name in used_agents else ''} {'current' if name == current_step.get("agent", "Orion") else ''}">
            <span>{esc(role)}</span>
            <strong>{esc(name)}</strong>
        </article>
        """
        for name, role, position in radar_nodes
    )

    memory_items = mission.get(
        "memory_timeline"
    ) or _generate_memory_timeline(
        mission
    )

    memory_html = "".join(
        f"""
        <article>
            <span>{esc(item.get("label", ""))}</span>
            <strong>{esc(item.get("value", ""))}</strong>
        </article>
        """
        for item in memory_items[:3]
    )

    risk = _generate_risk_radar(
        mission
    )

    complete_steps = len(
        [
            step
            for step in mission.get(
                "steps",
                []
            )
            if step.get("status") == "done"
        ]
    )

    pulse_items = [
        ("Backend", "Online"),
        ("Mission", mission.get("mode", "Strategic Build")),
        ("Stability", f"{risk.get('score', 0)}%"),
        ("Progress", f"{complete_steps}/{len(mission.get('steps', []))}"),
    ]

    pulse_html = "".join(
        f"""
        <div>
            <span>{esc(label)}</span>
            <strong>{esc(value)}</strong>
            <i></i>
        </div>
        """
        for label, value in pulse_items
    )

    st.markdown(
        f"""
        <section class="helios-futuristic-deck helios-motion-card">
            <div class="helios-mission-section-head">
                <div>
                    <span>Futuristic Control Deck</span>
                    <strong>New HELIOS surfaces added cleanly to this page</strong>
                </div>
                <em>4 features</em>
            </div>
            <div class="helios-futuristic-deck-grid">
                <article class="helios-deck-card helios-deck-mission">
                    <span>Mission Control Mode</span>
                    <strong>{esc(mission.get("title", "Active mission"))}</strong>
                    <p>{esc(mission.get("objective", ""))}</p>
                    <em>{esc(current_step.get("phase", "Observe"))} / {esc(current_step.get("agent", "Orion"))}</em>
                </article>
                <article class="helios-deck-card helios-deck-radar">
                    <span>Live Agent Radar</span>
                    <strong>{esc(current_step.get("agent", "Orion"))} active</strong>
                    <div class="helios-deck-radar-map">
                        <div>
                            <b>HELIOS</b>
                            <small>core</small>
                        </div>
                        {radar_html}
                    </div>
                </article>
                <article class="helios-deck-card helios-deck-memory">
                    <span>Memory Timeline</span>
                    <strong>{esc(len(memory_items))} mission memory points</strong>
                    <div class="helios-deck-memory-list">
                        {memory_html}
                    </div>
                </article>
                <article class="helios-deck-card helios-deck-pulse">
                    <span>AI System Pulse</span>
                    <strong>{esc(risk.get("level", "stable")).title()} / {esc(risk.get("score", 0))}% stable</strong>
                    <div class="helios-deck-pulse-grid">
                        {pulse_html}
                    </div>
                </article>
            </div>
        </section>
        """,
        unsafe_allow_html=True
    )


def _render_mission_templates():
    templates_html = "".join(
        f"""
        <article>
            <span>{esc(item.get("mode", ""))}</span>
            <strong>{esc(item.get("name", ""))}</strong>
            <p>{esc(item.get("objective", ""))}</p>
            <em>{esc(item.get("priority", "High"))}</em>
        </article>
        """
        for item in MISSION_TEMPLATES
    )

    st.markdown(
        f"""
        <section class="helios-mission-templates helios-motion-card">
            <div class="helios-mission-section-head">
                <div>
                    <span>Mission Templates</span>
                    <strong>Start from a ready-made mission pattern</strong>
                </div>
                <em>{esc(len(MISSION_TEMPLATES))} templates</em>
            </div>
            <div class="helios-mission-template-grid">
                {templates_html}
            </div>
        </section>
        """,
        unsafe_allow_html=True
    )

    template_cols = st.columns(
        len(MISSION_TEMPLATES),
        gap="small"
    )

    for index, item in enumerate(
        MISSION_TEMPLATES
    ):
        with template_cols[index]:
            if st.button(
                item.get(
                    "name",
                    "Use template"
                ),
                key=f"helios_template_{_slug(item.get('name', index))}",
                use_container_width=True
            ):
                _apply_template(
                    item
                )
                _rerun()


def _render_mission_timeline(mission):
    steps = mission.get(
        "steps",
        []
    )

    steps_html = "".join(
        f"""
        <article class="mission-step-{esc(step.get("status", "queued"))} risk-{esc(step.get("risk", "low"))}">
            <div>
                <span>{esc(step.get("phase", ""))}</span>
                <strong>{esc(step.get("agent", ""))}</strong>
            </div>
            <p>{esc(step.get("objective", ""))}</p>
            <em>{esc(step.get("status", "queued"))}</em>
        </article>
        """
        for step in steps
    )

    st.markdown(
        f"""
        <section class="helios-mission-timeline helios-motion-card">
            <div class="helios-mission-section-head">
                <div>
                    <span>Execution Timeline</span>
                    <strong>Observe -> Plan -> Execute -> Reflect</strong>
                </div>
                <em>{esc(mission.get("mode", "Strategic Build"))}</em>
            </div>
            <div class="helios-mission-step-grid">
                {steps_html}
            </div>
        </section>
        """,
        unsafe_allow_html=True
    )


def _render_visual_agent_network(mission):
    used_agents = _mission_agent_names(
        mission
    )

    current_agent = _current_step(
        mission
    ).get(
        "agent",
        "Orion"
    )

    nodes = [
        ("Orion", "Architecture", "top"),
        ("Nova", "Knowledge", "left"),
        ("Vega", "Build", "right"),
        ("Lyra", "Voice", "bottom"),
    ]

    nodes_html = "".join(
        f"""
        <article class="node-{esc(position)} {'active' if name in used_agents else ''} {'current' if name == current_agent else ''}">
            <span>{esc(role)}</span>
            <strong>{esc(name)}</strong>
        </article>
        """
        for name, role, position in nodes
    )

    st.markdown(
        f"""
        <section class="helios-agent-network helios-motion-card">
            <div class="helios-mission-section-head">
                <div>
                    <span>Visual Agent Network</span>
                    <strong>Mission routing map with active specialist signals</strong>
                </div>
                <em>{esc(current_agent)} active</em>
            </div>
            <div class="helios-agent-network-map">
                <div class="helios-agent-network-core">
                    <span>Mission Core</span>
                    <strong>{esc(mission.get("mode", "Strategic Build"))}</strong>
                </div>
                {nodes_html}
            </div>
        </section>
        """,
        unsafe_allow_html=True
    )


def _render_agent_council(mission):
    used_agents = _mission_agent_names(
        mission
    )

    council = [
        ("Orion", "mission architect", "keeps scope, checkpoints, and final synthesis aligned"),
        ("Nova", "knowledge scout", "finds context gaps, source needs, and memory hooks"),
        ("Vega", "build engineer", "turns the mission into implementation-ready work"),
        ("Lyra", "voice operator", "keeps hands-free command paths available"),
    ]

    council_html = "".join(
        f"""
        <article class="{'active' if name in used_agents else ''}">
            <span>{esc(role)}</span>
            <strong>{esc(name)}</strong>
            <p>{esc(detail)}</p>
        </article>
        """
        for name, role, detail in council
    )

    st.markdown(
        f"""
        <section class="helios-mission-council helios-motion-card">
            <div class="helios-mission-section-head">
                <div>
                    <span>Agent Council</span>
                    <strong>Specialists assigned without changing the base workspace</strong>
                </div>
                <em>{esc(len(used_agents))} active</em>
            </div>
            <div class="helios-mission-council-grid">
                {council_html}
            </div>
        </section>
        """,
        unsafe_allow_html=True
    )


def _render_council_review(mission):
    review = mission.get(
        "council_review"
    )

    if not review:
        st.markdown(
            """
            <section class="helios-mission-review helios-motion-card">
                <div class="helios-mission-section-head">
                    <div>
                        <span>Review</span>
                        <strong>No review yet.</strong>
                    </div>
                    <em>standby</em>
                </div>
                <div class="helios-mission-review-empty">
                    <strong>Standby.</strong>
                    <p>Run council when you need another pass.</p>
                </div>
            </section>
            """,
            unsafe_allow_html=True
        )

        return

    opinions_html = "".join(
        f"""
        <article>
            <span>{esc(item.get("stance", ""))}</span>
            <strong>{esc(item.get("agent", ""))}</strong>
            <b>{esc(item.get("signal", ""))}</b>
            <p>{esc(item.get("detail", ""))}</p>
        </article>
        """
        for item in review.get(
            "opinions",
            []
        )
    )

    st.markdown(
        f"""
        <section class="helios-mission-review helios-motion-card">
            <div class="helios-mission-section-head">
                <div>
                    <span>Council Review</span>
                    <strong>{esc(review.get("verdict", "Proceed with the active checkpoint."))}</strong>
                </div>
                <em>{esc(review.get("confidence", 0))}% confidence</em>
            </div>
            <div class="helios-mission-review-meta">
                <div>
                    <span>Reviewed</span>
                    <strong>{esc(review.get("timestamp", ""))}</strong>
                </div>
                <div>
                    <span>Agents</span>
                    <strong>{esc(review.get("active_agent_count", 0))} active lanes</strong>
                </div>
            </div>
            <div class="helios-mission-review-grid">
                {opinions_html}
            </div>
        </section>
        """,
        unsafe_allow_html=True
    )


def _render_memory_timeline(mission):
    timeline = mission.get(
        "memory_timeline"
    )

    if not timeline:
        timeline = _generate_memory_timeline(
            mission
        )

    memory_html = "".join(
        f"""
        <article class="memory-kind-{esc(item.get("kind", "intent"))}">
            <span>{esc(item.get("label", ""))}</span>
            <strong>{esc(item.get("value", ""))}</strong>
            <em>{esc(item.get("time", ""))}</em>
        </article>
        """
        for item in timeline
    )

    st.markdown(
        f"""
        <section class="helios-mission-memory helios-motion-card">
            <div class="helios-mission-section-head">
                <div>
                    <span>Memory Timeline</span>
                    <strong>Inspectable mission memory before anything is saved permanently</strong>
                </div>
                <em>{esc(len(timeline))} memories</em>
            </div>
            <div class="helios-mission-memory-rail">
                {memory_html}
            </div>
        </section>
        """,
        unsafe_allow_html=True
    )


def _generate_replay_events(mission):
    events = [
        {
            "label": "Mission created",
            "detail": mission.get(
                "objective",
                "Mission objective captured."
            ),
            "time": mission.get(
                "created",
                "Standby"
            ),
        }
    ]

    steps = mission.get(
        "steps",
        []
    )

    for index, step in enumerate(
        steps
    ):
        if step.get("status") in {
            "done",
            "active",
        }:
            events.append(
                {
                    "label": f"{step.get('phase', 'Step')} checkpoint",
                    "detail": f"{step.get('agent', 'Orion')}: {step.get('objective', '')}",
                    "time": step.get(
                        "status",
                        "queued"
                    ),
                }
            )

    review = mission.get(
        "council_review"
    )

    if review:
        events.append(
            {
                "label": "Council review",
                "detail": review.get(
                    "verdict",
                    "Council reviewed the mission."
                ),
                "time": review.get(
                    "timestamp",
                    ""
                ),
            }
        )

    memory_timeline = mission.get(
        "memory_timeline"
    )

    if memory_timeline:
        events.append(
            {
                "label": "Memory captured",
                "detail": f"{len(memory_timeline)} mission memory nodes captured.",
                "time": memory_timeline[-1].get(
                    "time",
                    ""
                ),
            }
        )

    if mission.get(
        "archived_at"
    ):
        events.append(
            {
                "label": "Mission archived",
                "detail": "Persistent mission snapshot was saved locally.",
                "time": mission.get(
                    "archived_at",
                    ""
                ),
            }
        )

    return events[-6:]


def _render_mission_replay(mission):
    events = _generate_replay_events(
        mission
    )

    events_html = "".join(
        f"""
        <article>
            <span>{esc(item.get("label", ""))}</span>
            <strong>{esc(item.get("detail", ""))}</strong>
            <em>{esc(item.get("time", ""))}</em>
        </article>
        """
        for item in events
    )

    st.markdown(
        f"""
        <section class="helios-mission-replay helios-motion-card">
            <div class="helios-mission-section-head">
                <div>
                    <span>Mission Replay</span>
                    <strong>Compact visual run history for the current mission</strong>
                </div>
                <em>{esc(len(events))} events</em>
            </div>
            <div class="helios-mission-replay-track">
                {events_html}
            </div>
        </section>
        """,
        unsafe_allow_html=True
    )


def _render_risk_radar(mission):
    radar = _generate_risk_radar(
        mission
    )

    findings_html = "".join(
        f"""
        <article class="risk-tone-{esc(tone)}">
            <span>{esc(label)}</span>
            <strong>{esc(detail)}</strong>
            <em>{esc(tone)}</em>
        </article>
        """
        for label, tone, detail in radar.get(
            "findings",
            []
        )
    )

    st.markdown(
        f"""
        <section class="helios-risk-radar helios-motion-card risk-level-{esc(radar.get("level", "stable"))}">
            <div class="helios-mission-section-head">
                <div>
                    <span>Risk</span>
                    <strong>{esc(radar.get("level", "stable")).title()}</strong>
                </div>
                <em>{esc(radar.get("score", 0))}% stable</em>
            </div>
            <div class="helios-risk-radar-grid">
                {findings_html}
            </div>
        </section>
        """,
        unsafe_allow_html=True
    )


def _perform_next_action(action_key):
    if action_key == "review":
        _run_council_review()
        return "Council review generated."

    if action_key == "memory":
        _capture_memory_timeline()
        return "Mission memory captured."

    if action_key == "advance":
        _advance_mission()
        return "Mission checkpoint advanced."

    if action_key == "complete":
        _complete_mission()
        return "Mission marked complete."

    if action_key == "archive":
        mission = st.session_state.get(
            "helios_mission_control",
            _mission_defaults()
        )
        archived = _archive_current_mission(
            mission
        )
        st.session_state["helios_mission_archive_notice"] = (
            f"Saved {archived.get('title', 'mission')} to archive."
        )
        return st.session_state["helios_mission_archive_notice"]

    return "No action performed."


def _render_next_actions(mission):
    actions = _generate_next_actions(
        mission
    )

    actions_html = "".join(
        f"""
        <article>
            <span>{esc(item.get("label", ""))}</span>
            <strong>{esc(item.get("detail", ""))}</strong>
        </article>
        """
        for item in actions
    )

    st.markdown(
        f"""
        <section class="helios-next-actions helios-motion-card">
            <div class="helios-mission-section-head">
                <div>
                    <span>Next</span>
                    <strong>Pick an action</strong>
                </div>
                <em>{esc(len(actions))} options</em>
            </div>
            <div class="helios-next-action-grid">
                {actions_html}
            </div>
        </section>
        """,
        unsafe_allow_html=True
    )

    action_cols = st.columns(
        len(actions),
        gap="small"
    )

    for index, item in enumerate(
        actions
    ):
        with action_cols[index]:
            if st.button(
                item.get(
                    "label",
                    "Run action"
                ),
                key=f"helios_next_action_{_slug(item.get('key', index))}",
                use_container_width=True
            ):
                st.session_state["helios_mission_action_notice"] = (
                    _perform_next_action(
                        item.get(
                            "key",
                            ""
                        )
                    )
                )
                _rerun()

    notice = st.session_state.get(
        "helios_mission_action_notice"
    )

    if notice:
        st.markdown(
            f"""
            <div class="helios-mission-action-notice">
                {esc(notice)}
            </div>
            """,
            unsafe_allow_html=True
        )


def _render_mission_archive():
    archive = _load_mission_archive()

    archive_cards = archive[:4]

    if archive_cards:
        cards_html = "".join(
            f"""
            <article>
                <span>{esc(item.get("archived_at", "Saved"))}</span>
                <strong>{esc(item.get("title", "Untitled mission"))}</strong>
                <p>{esc(item.get("objective", ""))}</p>
                <em>{esc(item.get("priority", "High"))}</em>
            </article>
            """
            for item in archive_cards
        )
    else:
        cards_html = """
        <article>
            <span>Archive</span>
            <strong>No saved missions yet.</strong>
            <p>Use Save mission to persist the current Mission Control state.</p>
            <em>empty</em>
        </article>
        """

    st.markdown(
        f"""
        <section class="helios-mission-archive helios-motion-card">
            <div class="helios-mission-section-head">
                <div>
                    <span>Persistent Mission Archive</span>
                    <strong>Local mission snapshots stored separately from chat memory</strong>
                </div>
                <em>{esc(len(archive))} saved</em>
            </div>
            <div class="helios-mission-archive-grid">
                {cards_html}
            </div>
        </section>
        """,
        unsafe_allow_html=True
    )

    if archive:
        options = [
            f"{item.get('title', 'Untitled mission')} | {item.get('archived_at', 'Saved')}"
            for item in archive[:12]
        ]

        selected = st.selectbox(
            "Load archived mission",
            options,
            key="helios_mission_archive_select",
            label_visibility="collapsed"
        )

        load_cols = st.columns(
            [
                1,
                1,
            ],
            gap="small"
        )

        with load_cols[0]:
            if st.button(
                "Load archived mission",
                key="helios_mission_archive_load",
                use_container_width=True
            ):
                selected_index = options.index(
                    selected
                )
                st.session_state["helios_mission_control"] = archive[
                    selected_index
                ]
                st.session_state["helios_mission_action_notice"] = (
                    "Archived mission loaded."
                )
                _rerun()

        with load_cols[1]:
            if st.button(
                "Save current mission",
                key="helios_mission_archive_save_secondary",
                use_container_width=True
            ):
                _perform_next_action(
                    "archive"
                )
                _rerun()


def _render_artifact_panel(mission):
    current_step = mission.get(
        "steps",
        [{}]
    )[
        min(
            int(mission.get("phase", 0)),
            max(len(mission.get("steps", [])) - 1, 0)
        )
    ]

    artifact_lines = [
        ("Objective", mission.get("objective", "")),
        ("Current agent", current_step.get("agent", "Orion")),
        ("Current checkpoint", current_step.get("objective", "")),
        ("Completion signal", "Every step is done, risks are visible, and an artifact is ready."),
    ]

    artifact_html = "".join(
        f"""
        <div>
            <span>{esc(label)}</span>
            <strong>{esc(value)}</strong>
        </div>
        """
        for label, value in artifact_lines
    )

    st.markdown(
        f"""
        <section class="helios-mission-artifact helios-motion-card">
            <div class="helios-mission-section-head">
                <div>
                    <span>Artifact Studio</span>
                    <strong>Mission brief stays separate from normal chat output</strong>
                </div>
                <em>{esc(mission.get("priority", "High"))}</em>
            </div>
            <div class="helios-mission-artifact-grid">
                {artifact_html}
            </div>
        </section>
        """,
        unsafe_allow_html=True
    )


def _advance_mission():
    mission = st.session_state.get(
        "helios_mission_control",
        _mission_defaults()
    )

    last_index = max(
        len(mission.get("steps", [])) - 1,
        0
    )

    mission["phase"] = min(
        int(mission.get("phase", 0)) + 1,
        last_index
    )

    st.session_state["helios_mission_control"] = _set_step_statuses(
        mission
    )


def _complete_mission():
    mission = st.session_state.get(
        "helios_mission_control",
        _mission_defaults()
    )

    mission["phase"] = len(
        mission.get(
            "steps",
            []
        )
    )

    for step in mission.get(
        "steps",
        []
    ):
        step["status"] = "done"

    st.session_state["helios_mission_control"] = mission


def _run_council_review():
    mission = st.session_state.get(
        "helios_mission_control",
        _mission_defaults()
    )

    mission["council_review"] = _generate_council_review(
        mission
    )

    st.session_state["helios_mission_control"] = mission


def _capture_memory_timeline():
    mission = st.session_state.get(
        "helios_mission_control",
        _mission_defaults()
    )

    mission["memory_timeline"] = _generate_memory_timeline(
        mission
    )

    st.session_state["helios_mission_control"] = mission


def render_mission_control():
    if "helios_mission_control" not in st.session_state:
        st.session_state["helios_mission_control"] = _mission_defaults()

    mission = _set_step_statuses(
        st.session_state["helios_mission_control"]
    )

    _render_mission_bridge(
        mission
    )

    _render_mission_templates()

    with st.form(
        "helios_mission_control_form",
        clear_on_submit=False
    ):
        st.markdown(
            """
            <section class="helios-mission-input-head helios-motion-card">
                <div>
                    <span>Mission Builder</span>
                    <strong>Describe a goal and HELIOS will stage it into agent lanes.</strong>
                </div>
            </section>
            """,
            unsafe_allow_html=True
        )

        goal = st.text_area(
            "Mission objective",
            value=mission.get(
                "objective",
                ""
            ),
            height=112,
            placeholder="Example: Build a memory timeline and agent council without touching the current command center.",
            key="helios_mission_goal_input"
        )

        control_cols = st.columns(
            [
                1,
                1,
                0.82
            ],
            gap="small"
        )

        with control_cols[0]:
            mode = st.selectbox(
                "Mission mode",
                MISSION_MODES,
                index=MISSION_MODES.index(
                    mission.get(
                        "mode",
                        MISSION_MODES[0]
                    )
                    if mission.get(
                        "mode",
                        MISSION_MODES[0]
                    )
                    in MISSION_MODES
                    else MISSION_MODES[0]
                ),
            )

        with control_cols[1]:
            priority = st.selectbox(
                "Priority",
                [
                    "Normal",
                    "High",
                    "Critical",
                ],
                index=[
                    "Normal",
                    "High",
                    "Critical",
                ].index(
                    mission.get(
                        "priority",
                        "High"
                    )
                    if mission.get(
                        "priority",
                        "High"
                    )
                    in {
                        "Normal",
                        "High",
                        "Critical",
                    }
                    else "High"
                ),
            )

        with control_cols[2]:
            submitted = st.form_submit_button(
                "Generate mission",
                use_container_width=True
            )

    if submitted:
        st.session_state["helios_mission_control"] = _build_mission(
            goal,
            mode,
            priority
        )

        _rerun()

    action_cols = st.columns(
        [
            1,
            1,
            1,
            1,
            1,
            1,
        ],
        gap="small"
    )

    with action_cols[0]:
        if st.button(
            "Advance checkpoint",
            key="helios_mission_advance",
            use_container_width=True
        ):
            _advance_mission()
            _rerun()

    with action_cols[1]:
        if st.button(
            "Run council review",
            key="helios_mission_council_review",
            use_container_width=True
        ):
            _run_council_review()
            _rerun()

    with action_cols[2]:
        if st.button(
            "Capture memory",
            key="helios_mission_capture_memory",
            use_container_width=True
        ):
            _capture_memory_timeline()
            _rerun()

    with action_cols[3]:
        if st.button(
            "Save mission",
            key="helios_mission_archive_save",
            use_container_width=True
        ):
            _perform_next_action(
                "archive"
            )
            _rerun()

    with action_cols[4]:
        if st.button(
            "Complete mission",
            key="helios_mission_complete",
            use_container_width=True
        ):
            _complete_mission()
            _rerun()

    with action_cols[5]:
        if st.button(
            "Reset mission",
            key="helios_mission_reset",
            use_container_width=True
        ):
            st.session_state["helios_mission_control"] = _mission_defaults()
            _rerun()

    mission = st.session_state.get(
        "helios_mission_control",
        _mission_defaults()
    )

    _render_futuristic_control_deck(
        mission
    )

    _render_mission_timeline(
        mission
    )

    network_cols = st.columns(
        [
            1,
            1,
        ],
        gap="small"
    )

    with network_cols[0]:
        _render_visual_agent_network(
            mission
        )

    with network_cols[1]:
        _render_mission_replay(
            mission
        )

    insight_cols = st.columns(
        [
            0.92,
            1.08
        ],
        gap="small"
    )

    with insight_cols[0]:
        _render_risk_radar(
            mission
        )

    with insight_cols[1]:
        _render_next_actions(
            mission
        )

    _render_council_review(
        mission
    )

    _render_memory_timeline(
        mission
    )

    lower_cols = st.columns(
        [
            1.08,
            0.92
        ],
        gap="small"
    )

    with lower_cols[0]:
        _render_agent_council(
            mission
        )

    with lower_cols[1]:
        _render_artifact_panel(
            mission
        )

    _render_mission_archive()
