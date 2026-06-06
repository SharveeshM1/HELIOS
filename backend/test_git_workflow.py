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


def test_git_diff_returns_patch_text(
    monkeypatch
):
    monkeypatch.setattr(
        git_workflow,
        "_run_git",
        lambda args: SimpleNamespace(
            stdout="-old\n+new\n",
            stderr="",
            returncode=0
        )
    )

    result = git_workflow.git_diff(
        staged=True,
        path="backend/main.py"
    )

    assert result["status"] == "success"
    assert "+new" in result["diff"]


def test_git_stage_runs_only_after_confirmation(
    monkeypatch
):
    calls = []

    def fake_git(
        args
    ):
        calls.append(
            args
        )
        return SimpleNamespace(
            stdout="",
            stderr="",
            returncode=0
        )

    monkeypatch.setattr(
        git_workflow,
        "_run_git",
        fake_git
    )

    preview = git_workflow.stage_files(
        [
            "backend/main.py"
        ],
        confirm=False
    )
    confirmed = git_workflow.stage_files(
        [
            "backend/main.py"
        ],
        confirm=True
    )

    assert preview["status"] == "preview"
    assert confirmed["status"] == "success"
    assert [
        "add",
        "--",
        "backend/main.py"
    ] in calls


def test_git_branch_push_and_rollback_are_validated(
    monkeypatch
):
    calls = []

    def fake_git(
        args
    ):
        calls.append(
            args
        )
        return SimpleNamespace(
            stdout="",
            stderr="",
            returncode=0
        )

    monkeypatch.setattr(
        git_workflow,
        "_run_git",
        fake_git
    )

    assert git_workflow.create_branch(
        "../bad",
        confirm=True
    )["status"] == "blocked"
    assert git_workflow.rollback_commit(
        "not-a-sha",
        confirm=True
    )["status"] == "blocked"
    assert git_workflow.create_branch(
        "feature/phase-one",
        confirm=True
    )["status"] == "success"
    assert git_workflow.push_branch(
        "feature/phase-one",
        confirm=True
    )["status"] == "success"
    assert git_workflow.rollback_commit(
        "abc1234",
        confirm=True
    )["status"] == "success"

    assert [
        "switch",
        "-c",
        "feature/phase-one"
    ] in calls
    assert [
        "push",
        "-u",
        "origin",
        "feature/phase-one"
    ] in calls
    assert [
        "revert",
        "--no-edit",
        "abc1234"
    ] in calls
