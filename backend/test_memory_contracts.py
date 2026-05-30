import json

from pathlib import Path

from core import memory


def test_memory_paths_are_backend_scoped():

    memory_path = Path(
        memory.MEMORY_FILE
    )

    assert memory_path.name == "chat_history.json"
    assert memory_path.parent.name == "memory"
    assert memory_path.parent.parent.name == "backend"


def test_corrupt_memory_recovers_valid_backup(
    tmp_path,
    monkeypatch
):

    memory_file = tmp_path / "chat_history.json"
    backup_file = tmp_path / "chat_history.backup.json"
    valid_item = {
        "timestamp": "2026-05-30 10:00:00",
        "user": "How does HELIOS remember code reviews?",
        "assistant": "It stores concise project memory."
    }

    memory_file.write_text(
        "{broken",
        encoding="utf-8"
    )
    backup_file.write_text(
        json.dumps(
            [
                valid_item,
                {
                    "bad": "record"
                }
            ]
        ),
        encoding="utf-8"
    )

    monkeypatch.setattr(
        memory,
        "MEMORY_FILE",
        str(
            memory_file
        )
    )
    monkeypatch.setattr(
        memory,
        "BACKUP_FILE",
        str(
            backup_file
        )
    )

    assert memory.load_memory() == [
        valid_item
    ]


def test_memory_search_ranks_token_matches():

    history = [
        {
            "timestamp": "2026-05-30 10:00:00",
            "user": "Plan a dashboard refresh",
            "assistant": "Use analytics panels."
        },
        {
            "timestamp": "2026-05-30 10:01:00",
            "user": "Improve memory retrieval and source search",
            "assistant": "Rank memory by repeated retrieval terms."
        }
    ]

    results = memory.search_memory(
        history,
        "memory retrieval"
    )

    assert results[0]["user"].startswith(
        "Improve memory"
    )
