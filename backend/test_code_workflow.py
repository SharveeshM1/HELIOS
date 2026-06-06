from core import code_workflow


def test_code_workflow_applies_clear_create_file_request(
    tmp_path,
    monkeypatch
):
    calls = []

    def fake_execute_agent_tool(
        agent,
        tool,
        *args,
        **kwargs
    ):
        calls.append(
            {
                "agent": agent,
                "tool": tool,
                "args": args,
                "kwargs": kwargs
            }
        )

        if tool == "run_command":
            return """
STDOUT:
clean

STDERR:

RETURN CODE:
0
"""

        return f"{tool} ok"

    monkeypatch.setattr(
        code_workflow,
        "PROJECT_DIR",
        tmp_path
    )
    monkeypatch.setattr(
        code_workflow,
        "execute_agent_tool",
        fake_execute_agent_tool
    )

    result = code_workflow.run_code_execution_workflow(
        "Create file named backend/generated_agent_note.txt"
    )

    assert result["edits"][0]["tool"] == "create_file"
    assert result["edits"][0]["path"] == "backend/generated_agent_note.txt"
    assert result["verification"][0]["status"] == "passed"
    assert result["commit_ready"] is True
    assert result["action_required"] is False
    assert result["verification_health"]["passed"] == 1
    assert calls[0]["agent"] == "code"
    assert calls[0]["tool"] == "create_file"


def test_code_workflow_blocks_paths_outside_project(
    tmp_path,
    monkeypatch
):
    calls = []

    monkeypatch.setattr(
        code_workflow,
        "PROJECT_DIR",
        tmp_path
    )
    monkeypatch.setattr(
        code_workflow,
        "execute_agent_tool",
        lambda *args, **kwargs: calls.append(
            args
        )
    )

    result = code_workflow.run_code_execution_workflow(
        "Create file named ../../outside.py"
    )

    assert result["blockers"]
    assert result["edits"] == []
    assert result["action_required"] is True
    assert result["next_actions"]
    assert calls
    assert calls[0][1] == "run_command"


def test_code_workflow_adds_verification_for_explicit_test_request(
    tmp_path,
    monkeypatch
):
    commands = []

    def fake_execute_agent_tool(
        agent,
        tool,
        command,
        cwd=None
    ):
        commands.append(
            command
        )

        return """
STDOUT:
ok

STDERR:

RETURN CODE:
0
"""

    monkeypatch.setattr(
        code_workflow,
        "PROJECT_DIR",
        tmp_path
    )
    monkeypatch.setattr(
        code_workflow,
        "execute_agent_tool",
        fake_execute_agent_tool
    )

    result = code_workflow.run_code_execution_workflow(
        "Fix backend tests",
        target_files=[
            "backend/main.py"
        ]
    )

    assert "git status --short" in commands
    assert "backend/venv/bin/python -m pytest backend" in commands
    assert all(
        item["status"] == "passed"
        for item in result["verification"]
    )


def test_code_workflow_replaces_exact_text(
    tmp_path,
    monkeypatch
):
    files = {
        "backend/example.py": "value = 'old'\n"
    }

    def fake_execute_agent_tool(
        agent,
        tool,
        *args,
        **kwargs
    ):
        if tool == "read_file":
            return files[args[0]]

        if tool == "create_file":
            files[args[0]] = args[1]
            return "updated"

        return """
RETURN CODE:
0
"""

    monkeypatch.setattr(
        code_workflow,
        "PROJECT_DIR",
        tmp_path
    )
    monkeypatch.setattr(
        code_workflow,
        "execute_agent_tool",
        fake_execute_agent_tool
    )

    result = code_workflow.run_code_execution_workflow(
        "Replace \"old\" with \"new\" in backend/example.py"
    )

    assert "new" in files["backend/example.py"]
    assert result["edits"][0]["tool"] == "replace_text"


def test_code_workflow_retries_failed_verification(
    tmp_path,
    monkeypatch
):
    attempts = []

    def fake_execute_agent_tool(
        agent,
        tool,
        command,
        cwd=None
    ):
        attempts.append(
            command
        )

        return f"""
RETURN CODE:
{1 if len(attempts) == 1 else 0}
"""

    monkeypatch.setattr(
        code_workflow,
        "PROJECT_DIR",
        tmp_path
    )
    monkeypatch.setattr(
        code_workflow,
        "execute_agent_tool",
        fake_execute_agent_tool
    )

    result = code_workflow.run_code_execution_workflow(
        "Verify backend tests",
        target_files=[
            "backend/main.py"
        ],
        verification_attempts=2
    )

    assert len(
        result["verification"]
    ) >= 2
    assert result["verification"][0]["status"] == "failed"


def test_structured_code_repair_applies_multiple_edits(
    tmp_path,
    monkeypatch
):
    files = {
        "backend/example.py": "value = 'old'\n"
    }

    def fake_execute_agent_tool(
        agent,
        tool,
        *args,
        **kwargs
    ):
        if tool == "read_file":
            return files[args[0]]
        if tool == "create_file":
            files[args[0]] = args[1]
            return "updated"
        return "RETURN CODE: 0"

    monkeypatch.setattr(
        code_workflow,
        "PROJECT_DIR",
        tmp_path
    )
    monkeypatch.setattr(
        code_workflow,
        "execute_agent_tool",
        fake_execute_agent_tool
    )

    result = code_workflow.run_structured_code_repair(
        "Repair example",
        [
            {
                "path": "backend/example.py",
                "operation": "replace",
                "old": "old",
                "new": "new"
            },
            {
                "path": "backend/new.py",
                "operation": "create",
                "content": "ready = True\n"
            }
        ],
        [
            "git status --short"
        ]
    )

    assert len(
        result["edits"]
    ) == 2
    assert result["commit_ready"] is True
    assert "new" in files["backend/example.py"]


def test_general_code_repair_uses_model_proposal(
    tmp_path,
    monkeypatch
):
    files = {
        "backend/example.py": "value = 'old'\n"
    }

    def fake_execute_agent_tool(
        agent,
        tool,
        *args,
        **kwargs
    ):
        if tool == "read_file":
            return files[args[0]]
        if tool == "create_file":
            files[args[0]] = args[1]
            return "updated"
        return "RETURN CODE: 0"

    monkeypatch.setattr(
        code_workflow,
        "PROJECT_DIR",
        tmp_path
    )
    monkeypatch.setattr(
        code_workflow,
        "execute_agent_tool",
        fake_execute_agent_tool
    )
    monkeypatch.setattr(
        code_workflow,
        "generate_ai_response",
        lambda prompt: """
        {
          "edits": [
            {
              "path": "backend/example.py",
              "operation": "replace",
              "old": "old",
              "new": "new"
            }
          ]
        }
        """
    )

    result = code_workflow.run_general_code_repair(
        "Fix example",
        [
            "backend/example.py"
        ],
        [
            "git status --short"
        ]
    )

    assert result["status"] == "completed"
    assert result["commit_ready"] is True
    assert "new" in files["backend/example.py"]
