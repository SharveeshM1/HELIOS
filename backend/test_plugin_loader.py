import pytest

from core import plugin_loader


def test_plugin_name_rejects_path_traversal():
    with pytest.raises(
        ValueError,
        match="simple Python filename"
    ):
        plugin_loader.validate_plugin_name(
            "../escape.py"
        )


def test_plugin_loader_requires_explicit_registration(
    tmp_path,
    monkeypatch
):
    monkeypatch.setattr(
        plugin_loader,
        "PLUGIN_TOOL_NAMES",
        set()
    )
    registry = plugin_loader.TOOL_REGISTRY
    original = dict(
        registry
    )
    try:
        (
            tmp_path / "implicit.py"
        ).write_text(
            "def accidental_tool():\n    return 'no'\n",
            encoding="utf-8"
        )

        assert plugin_loader.load_plugins(
            tmp_path
        ) == 0
        assert "accidental_tool" not in registry
    finally:
        registry.clear()
        registry.update(
            original
        )
