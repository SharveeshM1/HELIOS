import subprocess
from typing import Dict
from typing import List

from core.runtime_config import PROJECT_DIR


def _run_git(
    args: List[str]
) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            "git",
            *args
        ],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        check=False
    )


def git_status() -> Dict:
    result = _run_git(
        [
            "status",
            "--short"
        ]
    )
    lines = [
        line
        for line in result.stdout.splitlines()
        if line.strip()
    ]
    staged = [
        line
        for line in lines
        if line[:2].strip()
        and not line.startswith("??")
        and line[0] != " "
    ]
    unstaged = [
        line
        for line in lines
        if line.startswith(" ")
        or line.startswith("??")
    ]

    return {
        "clean": not lines,
        "changed": lines,
        "staged": staged,
        "unstaged": unstaged,
        "return_code": result.returncode,
        "stderr": result.stderr.strip()
    }


def commit_staged_changes(
    message: str,
    confirm: bool = False
) -> Dict:
    clean_message = str(
        message
    ).strip()

    status = git_status()

    if not clean_message:
        return {
            "status": "blocked",
            "reason": "Commit message is required.",
            "git": status
        }

    if not status["staged"]:
        return {
            "status": "blocked",
            "reason": "No staged files. Stage exact files first, then commit.",
            "git": status
        }

    if not confirm:
        return {
            "status": "preview",
            "reason": "Set confirm=true to commit staged files.",
            "message": clean_message,
            "git": status
        }

    result = _run_git(
        [
            "commit",
            "-m",
            clean_message
        ]
    )

    return {
        "status": "success"
        if result.returncode == 0
        else "failed",
        "message": clean_message,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "return_code": result.returncode,
        "git": git_status()
    }
