"""Execute HELIOS plugins outside the API server process."""

import importlib.util
import json
import sys
from pathlib import Path


def _load_registry(plugin_path: Path) -> dict:
    spec = importlib.util.spec_from_file_location(
        f"helios_plugin_runner_{plugin_path.stem}",
        plugin_path
    )
    if spec is None or spec.loader is None:
        raise ValueError("Plugin could not be loaded.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    register_plugin = getattr(module, "register_plugin", None)
    if not callable(register_plugin):
        raise ValueError("register_plugin(registry) is required.")
    registry: dict = {}
    register_plugin(registry)
    if not all(isinstance(name, str) and callable(tool) for name, tool in registry.items()):
        raise ValueError("Plugins may only register named callable tools.")
    return registry


def main() -> int:
    if len(sys.argv) < 3:
        raise ValueError("Usage: plugin_runner.py <discover|invoke> <plugin-path> [tool-name]")
    mode = sys.argv[1]
    plugin_path = Path(sys.argv[2]).resolve()
    registry = _load_registry(plugin_path)
    if mode == "discover":
        payload = {"tools": sorted(registry)}
    elif mode == "invoke":
        if len(sys.argv) < 4:
            raise ValueError("Tool name is required.")
        tool_name = sys.argv[3]
        if tool_name not in registry:
            raise ValueError(f"Plugin tool not found: {tool_name}")
        request = json.loads(sys.stdin.read() or "{}")
        payload = {
            "result": registry[tool_name](
                *request.get("args", []),
                **request.get("kwargs", {})
            )
        }
    else:
        raise ValueError(f"Unsupported plugin runner mode: {mode}")
    sys.stdout.write(json.dumps(payload))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        sys.stderr.write(str(error))
        raise SystemExit(1)
