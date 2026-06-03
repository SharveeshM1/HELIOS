from types import SimpleNamespace

from core import git_workflow


def test_git_commit_preview_requires_staged_files(
    monkeypatch
):
    monkeypatch.setattr(
        git_workflow,
        "_run_git",
        lambda args: SimpleNamespace(
            stdout=" M backend/main.py\n",
            stderr="",
            returncode=0
        )
    )

    result = git_workflow.commit_staged_changes(
        "Test commit",
        confirm=False
    )

    assert result["status"] == "blocked"
    assert "No staged files" in result["reason"]


def test_git_commit_preview_blocks_without_confirmation(
    monkeypatch
):
    monkeypatch.setattr(
        git_workflow,
        "_run_git",
        lambda args: SimpleNamespace(
            stdout="M  backend/main.py\n",
            stderr="",
            returncode=0
        )
    )

    result = git_workflow.commit_staged_changes(
        "Test commit",
        confirm=False
    )

    assert result["status"] == "preview"
    assert result["git"]["staged"]


def test_git_commit_runs_when_confirmed(
    monkeypatch
):
    calls = []

    def fake_git(
        args
    ):
        calls.append(
            args
        )

        if args[0] == "commit":
            return SimpleNamespace(
                stdout="[main abc123] Test commit",
                stderr="",
                returncode=0
            )

        return SimpleNamespace(
            stdout="M  backend/main.py\n",
            stderr="",
            returncode=0
        )

    monkeypatch.setattr(
        git_workflow,
        "_run_git",
        fake_git
    )

    result = git_workflow.commit_staged_changes(
        "Test commit",
        confirm=True
    )

    assert result["status"] == "success"
    assert [
        "commit",
        "-m",
        "Test commit"
    ] in calls
