import hashlib
import hmac
import json
import logging
import os
import re
import subprocess
import sys
from pathlib import Path

from tools import TOOL_REGISTRY


logger = logging.getLogger("helios-plugins")

PLUGIN_NAME_PATTERN = re.compile(
    r"^[a-zA-Z][a-zA-Z0-9_]{0,63}\.py$"
)
PLUGIN_TOOL_NAMES: set[str] = set()
PLUGIN_RUNNER_TIMEOUT_SECONDS = 30


def plugin_directory() -> Path:
    return Path(
        __file__
    ).resolve().parents[1] / "plugins"


def validate_plugin_name(
    name: str
) -> str:
    safe_name = str(
        name or ""
    ).strip()
    if not safe_name.endswith(
        ".py"
    ):
        safe_name += ".py"
    if not PLUGIN_NAME_PATTERN.fullmatch(
        safe_name
    ):
        raise ValueError(
            "Plugin name must be a simple Python filename."
        )
    if safe_name == "__init__.py":
        raise ValueError(
            "The plugin package initializer cannot be replaced."
        )
    return safe_name


def save_plugin_code(
    name: str,
    code: str,
    *,
    version: str = "1.0.0",
    description: str = "",
    dependencies: list[str] | None = None
) -> Path:
    safe_name = validate_plugin_name(
        name
    )
    safe_code = str(
        code or ""
    )
    if not safe_code.strip():
        raise ValueError(
            "Plugin code is required."
        )
    dependency_list = [
        str(
            dependency
        ).strip()
        for dependency in dependencies
        or []
        if str(
            dependency
        ).strip()
    ]
    if dependency_list:
        raise ValueError(
            "Plugins must be dependency-isolated and cannot declare runtime dependencies."
        )
    path = plugin_directory()
    path.mkdir(
        parents=True,
        exist_ok=True
    )
    file_path = path / safe_name
    file_path.write_text(
        safe_code,
        encoding="utf-8"
    )
    digest = hashlib.sha256(
        safe_code.encode(
            "utf-8"
        )
    ).hexdigest()
    signing_key = os.getenv(
        "HELIOS_PLUGIN_SIGNING_KEY",
        ""
    ).strip()
    signature = (
        hmac.new(
            signing_key.encode(
                "utf-8"
            ),
            digest.encode(
                "ascii"
            ),
            hashlib.sha256
        ).hexdigest()
        if signing_key
        else digest
    )
    manifest = {
        "name": file_path.stem,
        "filename": file_path.name,
        "version": str(
            version or "1.0.0"
        )[
            :40
        ],
        "description": str(
            description or ""
        )[
            :500
        ],
        "dependencies": [],
        "isolation": "subprocess-no-runtime-dependencies",
        "digest": digest,
        "signature": signature,
        "signature_type": "hmac-sha256"
        if signing_key
        else "sha256-integrity"
    }
    file_path.with_suffix(
        ".plugin.json"
    ).write_text(
        json.dumps(
            manifest,
            indent=2
        ),
        encoding="utf-8"
    )
    return file_path


def plugin_manifest(
    file: Path
) -> dict:
    manifest_path = file.with_suffix(
        ".plugin.json"
    )
    if not manifest_path.exists():
        return {
            "name": file.stem,
            "filename": file.name,
            "version": "unversioned",
            "description": "",
            "dependencies": [],
            "isolation": "legacy",
            "verified": False
        }
    try:
        manifest = json.loads(
            manifest_path.read_text(
                encoding="utf-8"
            )
        )
    except Exception:
        manifest = {}
    digest = hashlib.sha256(
        file.read_bytes()
    ).hexdigest()
    signing_key = os.getenv(
        "HELIOS_PLUGIN_SIGNING_KEY",
        ""
    ).strip()
    expected = (
        hmac.new(
            signing_key.encode(
                "utf-8"
            ),
            digest.encode(
                "ascii"
            ),
            hashlib.sha256
        ).hexdigest()
        if signing_key
        else digest
    )
    return {
        **manifest,
        "name": manifest.get(
            "name",
            file.stem
        ),
        "filename": file.name,
        "verified": hmac.compare_digest(
            str(
                manifest.get(
                    "signature",
                    ""
                )
            ),
            expected
        )
    }


def list_plugin_catalog() -> list[dict]:
    path = plugin_directory()
    if not path.exists():
        return []
    return [
        plugin_manifest(
            file
        )
        for file in sorted(
            path.glob(
                "*.py"
            )
        )
        if file.name != "__init__.py"
    ]


def uninstall_plugin(
    name: str
) -> str:
    safe_name = validate_plugin_name(
        name
    )
    file_path = plugin_directory() / safe_name
    if not file_path.exists():
        raise ValueError(
            "Plugin not found."
        )
    file_path.unlink()
    manifest_path = file_path.with_suffix(
        ".plugin.json"
    )
    if manifest_path.exists():
        manifest_path.unlink()
    load_plugins()
    return safe_name


def load_plugins(
    plugins_dir: str | Path | None = None
) -> int:
    """Load plugins that explicitly register tools into TOOL_REGISTRY."""
    path = Path(
        plugins_dir
    ) if plugins_dir else plugin_directory()
    if not path.exists():
        logger.warning(
            "Plugin directory %s does not exist.",
            path
        )
        return 0

    for tool_name in PLUGIN_TOOL_NAMES:
        TOOL_REGISTRY.pop(
            tool_name,
            None
        )
    PLUGIN_TOOL_NAMES.clear()

    count = 0
    for file in sorted(
        path.glob(
            "*.py"
        )
    ):
        if file.name == "__init__.py":
            continue
        manifest = plugin_manifest(
            file
        )
        if not manifest.get(
            "verified",
            False
        ):
            logger.warning(
                "Skipped plugin %s: signature or integrity verification failed.",
                file.name
            )
            continue

        try:
            before = dict(
                TOOL_REGISTRY
            )
            registered = set(
                _discover_plugin_tools(
                    file
                )
            )
            overridden = sorted(
                name
                for name in registered
                if name in before
            )
            if overridden:
                raise ValueError(
                    "Plugins cannot replace built-in tools: "
                    + ", ".join(
                        overridden
                    )
                )
            for tool_name in registered:
                TOOL_REGISTRY[tool_name] = _isolated_plugin_tool(
                    file,
                    tool_name
                )
            PLUGIN_TOOL_NAMES.update(
                registered
            )
            logger.info(
                "Loaded plugin %s with %s tool(s).",
                file.name,
                len(
                    registered
                )
            )
            count += 1
        except Exception:
            logger.exception(
                "Failed to load plugin %s.",
                file.name
            )

    return count


def _plugin_environment() -> dict[str, str]:
    allowed = {
        "PATH",
        "PYTHONPATH",
        "LANG",
        "LC_ALL",
        "TMPDIR"
    }
    return {
        key: value
        for key, value in os.environ.items()
        if key in allowed
    }


def _run_plugin(
    file: Path,
    mode: str,
    *,
    tool_name: str | None = None,
    payload: dict | None = None
) -> dict:
    command = [
        sys.executable,
        str(Path(__file__).with_name("plugin_runner.py")),
        mode,
        str(file)
    ]
    if tool_name:
        command.append(tool_name)
    result = subprocess.run(
        command,
        input=json.dumps(payload or {}),
        text=True,
        capture_output=True,
        timeout=PLUGIN_RUNNER_TIMEOUT_SECONDS,
        cwd=str(plugin_directory()),
        env=_plugin_environment(),
        check=False
    )
    if result.returncode != 0:
        raise RuntimeError(
            result.stderr.strip()
            or f"Plugin runner exited with {result.returncode}."
        )
    return json.loads(
        result.stdout
        or "{}"
    )


def _discover_plugin_tools(file: Path) -> list[str]:
    tools = _run_plugin(
        file,
        "discover"
    ).get(
        "tools",
        []
    )
    if not isinstance(tools, list) or not all(isinstance(name, str) for name in tools):
        raise ValueError("Plugin discovery returned invalid tool names.")
    return tools


def _isolated_plugin_tool(file: Path, tool_name: str):
    def execute(*args, **kwargs):
        return _run_plugin(
            file,
            "invoke",
            tool_name=tool_name,
            payload={
                "args": args,
                "kwargs": kwargs
            }
        ).get("result")

    execute.__name__ = tool_name
    return execute
