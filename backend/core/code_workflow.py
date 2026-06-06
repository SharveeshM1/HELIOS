import re
import json
from pathlib import Path
from typing import Dict
from typing import List

from core.runtime_config import PROJECT_DIR
from core.tool_executor import execute_agent_tool
from api.ai_provider import generate_ai_response


BLOCKED_PARTS = {
    ".git",
    ".next",
    "__pycache__",
    "node_modules",
    "venv"
}


def _inside_project(
    path: Path
) -> bool:
    try:
        path.resolve().relative_to(
            PROJECT_DIR.resolve()
        )
        return True
    except ValueError:
        return False


def _safe_relative_path(
    raw_path: str
) -> str | None:
    candidate = Path(
        str(
            raw_path
        ).strip().strip("'\"")
    )

    if candidate.is_absolute():
        path = candidate
    else:
        path = PROJECT_DIR / candidate

    if not _inside_project(
        path
    ):
        return None

    if any(
        part in BLOCKED_PARTS
        for part in path.parts
    ):
        return None

    return str(
        path.relative_to(
            PROJECT_DIR
        )
    )


def _infer_file_operation(
    objective: str
) -> Dict | None:
    text = str(
        objective
    )

    create_match = re.search(
        r"(?:create|write)\s+(?:a\s+)?(?:file\s+)?(?:named|at|to)?\s*([A-Za-z0-9_./-]+\.[A-Za-z0-9]+)",
        text,
        flags=re.IGNORECASE
    )

    append_match = re.search(
        r"append\s+(?:to\s+)?(?:file\s+)?([A-Za-z0-9_./-]+\.[A-Za-z0-9]+)",
        text,
        flags=re.IGNORECASE
    )
    replace_match = re.search(
        r"replace\s+[\"'](.+?)[\"']\s+with\s+[\"'](.+?)[\"']\s+in\s+([A-Za-z0-9_./-]+\.[A-Za-z0-9]+)",
        text,
        flags=re.IGNORECASE
    )

    match = replace_match or append_match or create_match

    if not match:
        return None

    relative_path = _safe_relative_path(
        match.group(
            3
        )
        if replace_match
        else match.group(
            1
        )
    )

    if not relative_path:
        return {
            "status": "blocked",
            "reason": "Requested path is outside the project or inside a blocked directory."
        }

    if replace_match:
        return {
            "status": "ready",
            "tool": "replace_text",
            "path": relative_path,
            "old": replace_match.group(
                1
            ),
            "new": replace_match.group(
                2
            )
        }

    operation = "append_file" if append_match else "create_file"
    content = f"HELIOS code agent generated this file for:\n{objective}\n"

    return {
        "status": "ready",
        "tool": operation,
        "path": relative_path,
        "content": content
    }


def _verification_commands(
    objective: str,
    target_files: List[str]
) -> List[Dict]:
    lowered = str(
        objective
    ).lower()
    files_text = " ".join(
        target_files
    ).lower()

    commands = [
        {
            "label": "Git status",
            "command": "git status --short",
            "cwd": str(
                PROJECT_DIR
            )
        }
    ]

    should_run_tests = any(
        term in lowered
        for term in (
            "test",
            "verify",
            "fix",
            "bug",
            "failing"
        )
    )

    if should_run_tests and (
        "backend/" in files_text
        or "backend" in lowered
        or not target_files
    ):
        commands.append(
            {
                "label": "Backend tests",
                "command": "backend/venv/bin/python -m pytest backend",
                "cwd": str(
                    PROJECT_DIR
                )
            }
        )

    if should_run_tests and (
        "frontend/" in files_text
        or "frontend" in lowered
    ):
        commands.append(
            {
                "label": "Frontend build",
                "command": "npm run build",
                "cwd": str(
                    PROJECT_DIR / "frontend"
                )
            }
        )

    return commands


def _summarize_command_result(
    result
) -> Dict:
    text = str(
        result
    )
    return_code = None
    match = re.search(
        r"RETURN CODE:\s*(-?\d+)",
        text
    )

    if match:
        return_code = int(
            match.group(
                1
            )
        )

    return {
        "status": "passed"
        if return_code == 0
        else "failed"
        if return_code is not None
        else "unknown",
        "return_code": return_code,
        "output": text[-1600:]
    }


def _latest_verification(
    verification: List[Dict]
) -> Dict:
    latest = {}

    for check in verification:
        latest[
            check.get(
                "command",
                check.get(
                    "label",
                    "unknown"
                )
            )
        ] = check

    return latest


def _verification_summary(
    verification: List[Dict]
) -> Dict:
    latest = _latest_verification(
        verification
    )
    failed = [
        check
        for check in latest.values()
        if check.get(
            "status"
        )
        == "failed"
    ]
    passed = [
        check
        for check in latest.values()
        if check.get(
            "status"
        )
        == "passed"
    ]
    unknown = [
        check
        for check in latest.values()
        if check.get(
            "status"
        )
        == "unknown"
    ]

    return {
        "total": len(
            latest
        ),
        "passed": len(
            passed
        ),
        "failed": len(
            failed
        ),
        "unknown": len(
            unknown
        ),
        "failed_commands": [
            check.get(
                "command",
                check.get(
                    "label",
                    "unknown"
                )
            )
            for check in failed
        ]
    }


def _repair_next_actions(
    *,
    edits: List[Dict],
    verification: List[Dict],
    blockers: List[str],
    commit_ready: bool,
    target_files: List[str]
) -> List[str]:
    if commit_ready:
        return [
            "Review the patch.",
            "Stage the edited files.",
            "Commit after human approval."
        ]

    actions = []

    if blockers:
        actions.append(
            "Resolve safety blockers before applying more edits."
        )

    failed_commands = _verification_summary(
        verification
    ).get(
        "failed_commands",
        []
    )

    if failed_commands:
        actions.append(
            "Inspect failed verification commands: "
            + ", ".join(
                failed_commands[:3]
            )
            + "."
        )

    if not edits and not target_files:
        actions.append(
            "Provide a concrete target file or a precise edit request."
        )
    elif not edits:
        actions.append(
            "No edit was applied; rerun with explicit structured edits or a clearer objective."
        )

    if not actions:
        actions.append(
            "Review verification output before continuing."
        )

    return actions


def run_code_execution_workflow(
    objective: str,
    target_files: List[str] | None = None,
    verification_attempts: int = 2
) -> Dict:
    target_files = target_files or []
    edits = []
    verification = []
    blockers = []

    operation = _infer_file_operation(
        objective
    )

    if operation and operation.get(
        "status"
    ) == "blocked":
        blockers.append(
            operation.get(
                "reason"
            )
        )

    elif operation:
        try:
            if operation["tool"] == "replace_text":
                current = execute_agent_tool(
                    "code",
                    "read_file",
                    operation["path"]
                )

                if operation["old"] not in str(
                    current
                ):
                    raise ValueError(
                        "Replacement text was not found in the target file."
                    )

                updated = str(
                    current
                ).replace(
                    operation["old"],
                    operation["new"],
                    1
                )
                result = execute_agent_tool(
                    "code",
                    "create_file",
                    operation["path"],
                    updated
                )
            else:
                result = execute_agent_tool(
                    "code",
                    operation["tool"],
                    operation["path"],
                    operation["content"]
                )
            edits.append(
                {
                    "tool": operation["tool"],
                    "path": operation["path"],
                    "status": "applied",
                    "result": result
                }
            )
            if operation["path"] not in target_files:
                target_files.append(
                    operation["path"]
                )
        except Exception as error:
            edits.append(
                {
                    "tool": operation["tool"],
                    "path": operation["path"],
                    "status": "failed",
                    "error": str(
                        error
                    )
                }
            )

    max_attempts = max(
        1,
        min(
            int(
                verification_attempts
            ),
            3
        )
    )

    for command in _verification_commands(
        objective,
        target_files
    ):
        for attempt in range(
            1,
            max_attempts
            + 1
        ):
            try:
                result = execute_agent_tool(
                    "code",
                    "run_command",
                    command["command"],
                    command.get(
                        "cwd"
                    )
                )
                summary = {
                    **command,
                    "attempt": attempt,
                    **_summarize_command_result(
                        result
                    )
                }
                verification.append(
                    summary
                )

                if summary["status"] != "failed":
                    break

            except Exception as error:
                verification.append(
                    {
                        **command,
                        "attempt": attempt,
                        "status": "failed",
                        "error": str(
                            error
                        )
                    }
                )

    latest_checks = _latest_verification(
        verification
    )

    commit_ready = bool(
        edits
    ) and all(
        check.get(
            "status"
        )
        in {
            "passed",
            "unknown"
        }
        for check in latest_checks.values()
    ) and not blockers
    verification_health = _verification_summary(
        verification
    )

    return {
        "mode": "bounded_code_execution",
        "target_files": target_files,
        "edits": edits,
        "verification": verification,
        "verification_health": verification_health,
        "verification_attempts": max_attempts,
        "blockers": blockers,
        "commit_ready": commit_ready,
        "action_required": not commit_ready,
        "next_actions": _repair_next_actions(
            edits=edits,
            verification=verification,
            blockers=blockers,
            commit_ready=commit_ready,
            target_files=target_files
        ),
        "summary": (
            "Applied requested edit and captured verification."
            if edits
            else "Mapped code targets and captured verification signals."
        )
    }


def run_structured_code_repair(
    objective: str,
    edits: List[Dict],
    verification_commands: List[str] | None = None,
    verification_attempts: int = 2
) -> Dict:
    """Apply explicit bounded edits and verify them without allowing arbitrary paths."""
    applied = []
    blockers = []
    target_files = []

    for edit in edits[:20]:
        relative_path = _safe_relative_path(
            edit.get(
                "path",
                ""
            )
        )
        if not relative_path:
            blockers.append(
                "An edit path was outside the project or inside a blocked directory."
            )
            continue

        operation = edit.get(
            "operation",
            "replace"
        )
        try:
            current = ""
            if operation != "create":
                current = str(
                    execute_agent_tool(
                        "code",
                        "read_file",
                        relative_path
                    )
                )

            if operation == "replace":
                old = str(
                    edit.get(
                        "old",
                        ""
                    )
                )
                if not old or old not in current:
                    raise ValueError(
                        "Expected replacement text was not found."
                    )
                updated = current.replace(
                    old,
                    str(
                        edit.get(
                            "new",
                            ""
                        )
                    ),
                    1
                )
            elif operation == "append":
                updated = current + str(
                    edit.get(
                        "content",
                        ""
                    )
                )
            elif operation == "create":
                updated = str(
                    edit.get(
                        "content",
                        ""
                    )
                )
            else:
                raise ValueError(
                    f"Unsupported edit operation: {operation}"
                )

            result = execute_agent_tool(
                "code",
                "create_file",
                relative_path,
                updated
            )
            applied.append(
                {
                    "path": relative_path,
                    "operation": operation,
                    "status": "applied",
                    "result": result
                }
            )
            target_files.append(
                relative_path
            )
        except Exception as error:
            applied.append(
                {
                    "path": relative_path,
                    "operation": operation,
                    "status": "failed",
                    "error": str(
                        error
                    )
                }
            )

    commands = [
        {
            "label": command,
            "command": command,
            "cwd": str(
                PROJECT_DIR
            )
        }
        for command in (
            verification_commands or []
        )[:10]
    ] or _verification_commands(
        objective,
        target_files
    )
    verification = []
    max_attempts = max(
        1,
        min(
            int(
                verification_attempts
            ),
            3
        )
    )
    for command in commands:
        for attempt in range(
            1,
            max_attempts + 1
        ):
            result = execute_agent_tool(
                "code",
                "run_command",
                command["command"],
                command.get(
                    "cwd"
                )
            )
            summary = {
                **command,
                "attempt": attempt,
                **_summarize_command_result(
                    result
                )
            }
            verification.append(
                summary
            )
            if summary["status"] != "failed":
                break

    latest = _latest_verification(
        verification
    )
    commit_ready = bool(
        applied
    ) and not blockers and all(
        item.get(
            "status"
        )
        == "passed"
        for item in latest.values()
    )
    return {
        "mode": "structured_code_repair",
        "objective": objective,
        "target_files": target_files,
        "edits": applied,
        "verification": verification,
        "verification_health": _verification_summary(
            verification
        ),
        "blockers": blockers,
        "commit_ready": commit_ready,
        "action_required": not commit_ready,
        "next_actions": _repair_next_actions(
            edits=applied,
            verification=verification,
            blockers=blockers,
            commit_ready=commit_ready,
            target_files=target_files
        )
    }


def _extract_json_object(
    text: str
) -> Dict:
    raw = str(
        text
    ).strip()
    fenced = re.search(
        r"```(?:json)?\s*(\{.*\})\s*```",
        raw,
        flags=re.DOTALL
    )
    candidate = fenced.group(
        1
    ) if fenced else raw[
        raw.find(
            "{"
        ):
        raw.rfind(
            "}"
        )
        + 1
    ]
    parsed = json.loads(
        candidate
    )
    if not isinstance(
        parsed,
        dict
    ):
        raise ValueError(
            "Code repair planner did not return an object."
        )
    return parsed


def run_general_code_repair(
    objective: str,
    target_files: List[str],
    verification_commands: List[str] | None = None,
    repair_attempts: int = 2
) -> Dict:
    safe_files = [
        path
        for raw_path in target_files[:12]
        if (
            path := _safe_relative_path(
                raw_path
            )
        )
    ]
    if not safe_files:
        return {
            "mode": "general_code_repair",
            "status": "blocked",
            "blockers": [
                "At least one safe project target file is required."
            ],
            "attempts": [],
            "commit_ready": False,
            "action_required": True,
            "next_actions": [
                "Select at least one safe project file before running automatic repair."
            ]
        }

    file_context = {}
    for path in safe_files:
        try:
            file_context[path] = str(
                execute_agent_tool(
                    "code",
                    "read_file",
                    path
                )
            )[:16000]
        except Exception as error:
            file_context[path] = f"[READ ERROR] {error}"

    attempts = []
    failure_context = ""
    max_attempts = max(
        1,
        min(
            int(
                repair_attempts
            ),
            3
        )
    )
    for attempt in range(
        1,
        max_attempts + 1
    ):
        prompt = f"""
You are the HELIOS code repair planner.
Return JSON only with an "edits" array.
Allowed operations: replace, append, create.
For replace, include path, old, and new. Use exact existing text.
Only edit these files: {safe_files}
Keep changes minimal and directly related to the objective.

Objective:
{objective}

Files:
{json.dumps(file_context, ensure_ascii=False)}

Previous verification failures:
{failure_context or "None"}
"""
        try:
            proposal = _extract_json_object(
                generate_ai_response(
                    prompt
                )
            )
            repair = run_structured_code_repair(
                objective,
                proposal.get(
                    "edits",
                    []
                ),
                verification_commands,
                verification_attempts=1
            )
            attempts.append(
                {
                    "attempt": attempt,
                    "proposal": proposal,
                    "repair": repair
                }
            )
            if repair.get(
                "commit_ready"
            ):
                return {
                    "mode": "general_code_repair",
                    "status": "completed",
                    "attempts": attempts,
                    "commit_ready": True,
                    "target_files": safe_files,
                    "action_required": False,
                    "next_actions": _repair_next_actions(
                        edits=repair.get(
                            "edits",
                            []
                        ),
                        verification=repair.get(
                            "verification",
                            []
                        ),
                        blockers=repair.get(
                            "blockers",
                            []
                        ),
                        commit_ready=True,
                        target_files=safe_files
                    )
                }
            failure_context = "\n".join(
                str(
                    check.get(
                        "output",
                        check.get(
                            "error",
                            ""
                        )
                    )
                )[-2000:]
                for check in repair.get(
                    "verification",
                    []
                )
                if check.get(
                    "status"
                )
                == "failed"
            )
        except Exception as error:
            attempts.append(
                {
                    "attempt": attempt,
                    "status": "failed",
                    "error": str(
                        error
                    )
                }
            )
            failure_context = str(
                error
            )

    return {
        "mode": "general_code_repair",
        "status": "failed",
        "attempts": attempts,
        "commit_ready": False,
        "target_files": safe_files,
        "action_required": True,
        "next_actions": [
            "Review the final repair attempt and failed verification output.",
            "Provide a narrower objective or explicit structured edit if automatic repair cannot converge."
        ]
    }
