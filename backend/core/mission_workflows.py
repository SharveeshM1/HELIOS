import re

from pathlib import Path
from typing import Dict
from typing import List

from core.planning_engine import PlanningEngine
from core.code_workflow import run_code_execution_workflow
from core.research_grounding import build_grounded_research_artifact
from core.runtime_config import PROJECT_DIR
from core.swarm_engine import build_consensus
from core.source_library import search_sources
from core.source_library import source_stats
from core.task_engine import create_task
from core.task_engine import execute_task


MAX_FILE_SIGNALS = 8
SCAN_EXTENSIONS = {
    ".py",
    ".tsx",
    ".ts",
    ".js",
    ".jsx",
    ".css",
    ".md",
    ".json"
}
SKIP_DIRS = {
    ".git",
    ".next",
    ".pytest_cache",
    "__pycache__",
    "memory",
    "node_modules",
    "venv"
}
SKIP_FILES = {
    "package-lock.json"
}


def _terms(
    text: str
) -> List[str]:

    return sorted(
        {
            term
            for term in re.findall(
                r"[a-z0-9_]{3,}",
                str(text or "").lower()
            )
        }
    )


def _research_artifact(
    title: str
) -> Dict:

    terms = _terms(
        title
    )
    sources = search_sources(
        title,
        limit=5
    )

    evidence = [
        {
            "name": source.get("name"),
            "scope": source.get("scope"),
            "snippet": source.get("snippet"),
            "match_terms": source.get("match_terms", [])
        }
        for source in sources
    ]

    matched_terms = sorted(
        {
            term
            for item in evidence
            for term in item.get("match_terms", [])
        }
    )
    grounding = build_grounded_research_artifact(
        title,
        evidence,
        source_stats()
    )

    return {
        "kind": "research",
        "summary": (
            f"Mapped {len(evidence)} cited source signal(s) for this mission."
            if evidence
            else "No indexed source evidence matched yet. Add sources or broaden the mission query."
        ),
        "evidence": evidence,
        "citations": grounding["citations"],
        "claims": grounding["claims"],
        "grounded_answer": grounding["grounded_answer"],
        "coverage": {
            "query_terms": terms,
            "matched_terms": matched_terms,
            "unmatched_terms": [
                term
                for term in terms
                if term not in matched_terms
            ],
            "citation_count": len(
                grounding["citations"]
            ),
            "grounded": bool(
                grounding["citations"]
            ),
            **source_stats()
        }
    }


def _file_signal(
    path: Path,
    terms: List[str]
) -> Dict | None:

    try:

        content = path.read_text(
            encoding="utf-8",
            errors="ignore"
        )

    except Exception:

        return None

    lowered = content.lower()
    matched = [
        term
        for term in terms
        if term in lowered
        or term in path.name.lower()
    ]

    if terms and not matched:

        return None

    relative = path.relative_to(
        PROJECT_DIR
    )

    first_line = ""

    for line in content.splitlines():

        if line.strip():

            first_line = line.strip()[:180]
            break

    return {
        "path": str(relative),
        "extension": path.suffix,
        "matched_terms": matched,
        "line_count": len(
            content.splitlines()
        ),
        "snippet": first_line
    }


def _project_file_signals(
    title: str
) -> List[Dict]:

    terms = _terms(
        title
    )
    signals = []

    for path in PROJECT_DIR.rglob("*"):

        if not path.is_file():

            continue

        if path.name in SKIP_FILES:

            continue

        if path.suffix not in SCAN_EXTENSIONS:

            continue

        if any(
            part in SKIP_DIRS
            for part in path.parts
        ):

            continue

        signal = _file_signal(
            path,
            terms
        )

        if signal:

            signals.append(
                signal
            )

    signals.sort(
        key=lambda item: (
            len(item.get("matched_terms", [])),
            item.get("line_count", 0)
        ),
        reverse=True
    )

    return signals[:MAX_FILE_SIGNALS]


def _code_artifact(
    title: str
) -> Dict:

    file_signals = _project_file_signals(
        title
    )
    target_files = [
        signal["path"]
        for signal in file_signals
    ]
    workflow = run_code_execution_workflow(
        title,
        target_files=target_files
    )

    return {
        "kind": "code",
        "summary": (
            workflow.get(
                "summary"
            )
            or (
                f"Mapped {len(file_signals)} likely implementation files."
                if file_signals
                else "No matching implementation files found yet. Start by naming the target module or file."
            )
        ),
        "checks": [
            "Identify target files",
            "Apply bounded edits when requested",
            "Run verification through the execution ledger",
            "Prepare patch review"
        ],
        "target": title,
        "target_files": workflow.get(
            "target_files",
            target_files
        ),
        "file_signals": file_signals,
        "execution": workflow
    }


def _planning_artifact(
    title: str
) -> Dict:

    plan = PlanningEngine().create_plan(
        title
    )

    return {
        "kind": "planning",
        "summary": f"Converted mission into {len(plan['tasks'])} routed execution step(s).",
        "steps": [
            f"{item['agent'].title()} priority {item['priority']}: {item['objective'][:90]}"
            for item in plan["tasks"]
        ],
        "target": title,
        "plan": plan
    }


def _analytics_artifact(
    title: str
) -> Dict:

    files = _project_file_signals(
        title
    )
    stats = source_stats()

    return {
        "kind": "analytics",
        "summary": "Captured project and knowledge signals for analysis.",
        "signals": {
            "matching_files": len(files),
            "indexed_sources": stats.get("indexed_sources", 0),
            "pending_sources": stats.get("pending_sources", 0),
            "total_content_chars": stats.get("total_content_chars", 0)
        },
        "file_signals": files,
        "target": title
    }


def _knowledge_artifact(
    title: str
) -> Dict:

    sources = search_sources(
        title,
        limit=8
    )

    return {
        "kind": "knowledge",
        "summary": f"Found {len(sources)} indexed knowledge item(s) for this mission.",
        "sources": sources,
        "coverage": source_stats(),
        "target": title
    }


def _voice_artifact(
    title: str
) -> Dict:

    return {
        "kind": "voice",
        "summary": "Prepared the voice mission path and required checks.",
        "checks": [
            "Confirm microphone recorder availability",
            "Capture transcript",
            "Route transcript through active module",
            "Persist spoken turn in chat memory"
        ],
        "target": title
    }


def _swarm_artifact(
    title: str
) -> Dict:

    plan = PlanningEngine().create_plan(
        title
    )
    synthetic_results = [
        {
            "agent": f"{item['agent'].title()} Agent",
            "output": item["objective"],
            "status": "completed",
            "duration": 0
        }
        for item in plan["tasks"]
    ]
    consensus = build_consensus(
        synthetic_results
    )

    return {
        "kind": "swarm",
        "summary": f"Prepared {len(plan['tasks'])} agent assignment(s) for coordinated execution.",
        "assignments": plan["tasks"],
        "debate": consensus["debate"],
        "consensus": consensus,
        "target": title
    }


def _default_artifact(
    title: str,
    module: str
) -> Dict:

    return {
        "kind": module or "mission",
        "summary": f"Prepared {module or 'mission'} workflow from current project context.",
        "steps": [
            "Inspect mission state",
            "Route to active module",
            "Capture output",
            "Await review"
        ],
        "file_signals": _project_file_signals(
            title
        ),
        "target": title
    }


def run_mission_workflow(
    mission: Dict
) -> Dict:

    title = str(
        mission.get(
            "title",
            "Untitled mission"
        )
    )
    module = str(
        mission.get(
            "module",
            "planning"
        )
    )
    agent = str(
        mission.get(
            "agent",
            "Orion"
        )
    )

    if module == "research":

        artifact = _research_artifact(
            title
        )

    elif module == "code":

        artifact = _code_artifact(
            title
        )

    elif module == "analytics":

        artifact = _analytics_artifact(
            title
        )

    elif module == "knowledge":

        artifact = _knowledge_artifact(
            title
        )

    elif module == "voice":

        artifact = _voice_artifact(
            title
        )

    elif module in {
        "swarm",
        "collab"
    }:

        artifact = _swarm_artifact(
            title
        )

    elif module in {
        "planning",
        "workflow",
        "loop",
        "reasoning"
    }:

        artifact = _planning_artifact(
            title
        )

    else:

        artifact = _default_artifact(
            title,
            module
        )

    task = create_task(
        title,
        artifact.get(
            "summary",
            "Mission workflow prepared."
        ),
        agent,
        priority="high"
    )
    executed = execute_task(
        task,
        execution_callback=lambda: artifact
    )

    return {
        "artifact": artifact,
        "task": {
            "id": executed.get("id"),
            "title": executed.get("title"),
            "agent": executed.get("agent"),
            "status": executed.get("status"),
            "progress": executed.get("progress"),
            "logs": executed.get("logs", [])[-6:],
            "result": executed.get("result")
        }
    }
