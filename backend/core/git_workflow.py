import subprocess
import re
from typing import Dict
from typing import List

from core.runtime_config import PROJECT_DIR


BRANCH_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,119}$"
)
COMMIT_PATTERN = re.compile(
    r"^[0-9a-fA-F]{7,40}$"
)


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


def git_diff(
    staged: bool = False,
    path: str | None = None
) -> Dict:
    args = [
        "diff"
    ]
    if staged:
        args.append(
            "--staged"
        )
    if path:
        args.extend(
            [
                "--",
                str(
                    path
                )
            ]
        )
    result = _run_git(
        args
    )
    return {
        "status": "success"
        if result.returncode == 0
        else "failed",
        "staged": staged,
        "path": path,
        "diff": result.stdout[-120000:],
        "stderr": result.stderr.strip(),
        "return_code": result.returncode
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


def stage_files(
    paths: List[str],
    confirm: bool = False
) -> Dict:
    safe_paths = []
    for raw_path in paths[
        :50
    ]:
        candidate = (
            PROJECT_DIR / str(
                raw_path
            )
        ).resolve()
        try:
            relative = candidate.relative_to(
                PROJECT_DIR.resolve()
            )
        except ValueError:
            return {
                "status": "blocked",
                "reason": "A requested path is outside the project.",
                "git": git_status()
            }
        if ".git" in relative.parts:
            return {
                "status": "blocked",
                "reason": "The .git directory cannot be staged.",
                "git": git_status()
            }
        safe_paths.append(
            str(
                relative
            )
        )
    if not safe_paths:
        return {
            "status": "blocked",
            "reason": "At least one project path is required.",
            "git": git_status()
        }
    if not confirm:
        return {
            "status": "preview",
            "reason": "Set confirm=true to stage the selected paths.",
            "paths": safe_paths,
            "git": git_status()
        }
    result = _run_git(
        [
            "add",
            "--",
            *safe_paths
        ]
    )
    return {
        "status": "success"
        if result.returncode == 0
        else "failed",
        "paths": safe_paths,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "return_code": result.returncode,
        "git": git_status()
    }


def create_branch(
    name: str,
    confirm: bool = False
) -> Dict:
    branch = str(
        name
    ).strip()
    if not BRANCH_PATTERN.fullmatch(
        branch
    ) or ".." in branch or branch.endswith(
        "/"
    ):
        return {
            "status": "blocked",
            "reason": "Invalid git branch name.",
            "git": git_status()
        }
    if not confirm:
        return {
            "status": "preview",
            "reason": "Set confirm=true to create and switch branches.",
            "branch": branch,
            "git": git_status()
        }
    result = _run_git(
        [
            "switch",
            "-c",
            branch
        ]
    )
    return {
        "status": "success"
        if result.returncode == 0
        else "failed",
        "branch": branch,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "return_code": result.returncode,
        "git": git_status()
    }


def push_branch(
    branch: str,
    remote: str = "origin",
    confirm: bool = False
) -> Dict:
    clean_branch = str(
        branch
    ).strip()
    clean_remote = str(
        remote
    ).strip()
    if not BRANCH_PATTERN.fullmatch(
        clean_branch
    ) or not re.fullmatch(
        r"[A-Za-z0-9._-]{1,80}",
        clean_remote
    ):
        return {
            "status": "blocked",
            "reason": "Invalid branch or remote name.",
            "git": git_status()
        }
    if not confirm:
        return {
            "status": "preview",
            "reason": "Set confirm=true to push the branch.",
            "branch": clean_branch,
            "remote": clean_remote,
            "git": git_status()
        }
    result = _run_git(
        [
            "push",
            "-u",
            clean_remote,
            clean_branch
        ]
    )
    return {
        "status": "success"
        if result.returncode == 0
        else "failed",
        "branch": clean_branch,
        "remote": clean_remote,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "return_code": result.returncode,
        "git": git_status()
    }


def rollback_commit(
    commit: str,
    confirm: bool = False
) -> Dict:
    clean_commit = str(
        commit
    ).strip()
    if not COMMIT_PATTERN.fullmatch(
        clean_commit
    ):
        return {
            "status": "blocked",
            "reason": "Rollback requires a full or abbreviated commit hash.",
            "git": git_status()
        }
    if not confirm:
        return {
            "status": "preview",
            "reason": "Set confirm=true to create a revert commit.",
            "commit": clean_commit,
            "git": git_status()
        }
    result = _run_git(
        [
            "revert",
            "--no-edit",
            clean_commit
        ]
    )
    return {
        "status": "success"
        if result.returncode == 0
        else "failed",
        "commit": clean_commit,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "return_code": result.returncode,
        "git": git_status()
    }
