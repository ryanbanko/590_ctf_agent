"""Non-secret settings for a single bounded attempt."""

from pathlib import Path
import math
import tomllib


DEFAULTS = {
    "solver_image": "ctf590-solver:m1",
    "guard_image": "ctf590-guard:m1",
    "target_image": "ctf590-fixture:m1",
    "wall_seconds": 60.0,
    "max_tool_calls": 20,
    "max_model_turns": 20,
    "command_seconds": 10.0,
    "max_command_bytes": 16_384,
    "max_output_bytes": 16_384,
    "max_write_bytes": 65_536,
    "memory_mb": 256,
    "workspace_mb": 64,
    "pids": 64,
    "cpus": 1.0,
}


def validate_settings(settings: dict) -> None:
    if settings.keys() != DEFAULTS.keys():
        raise ValueError("Settings must contain exactly the documented configuration keys")
    for name, value in settings.items():
        if name.endswith("_image"):
            if not isinstance(value, str) or not value or value.startswith("-"):
                raise ValueError(f"{name} must be an image reference")
        elif name in {"wall_seconds", "command_seconds", "cpus"}:
            if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be finite and positive")
        elif type(value) is not int or value <= 0:
            raise ValueError(f"{name} must be a positive integer")
    if settings["max_output_bytes"] > 65_536 or settings["max_write_bytes"] > 1_048_576:
        raise ValueError("Output/write limits exceed the initial implementation's bounds")


def load_settings(path: Path) -> dict:
    with path.open("rb") as handle:
        values = tomllib.load(handle)
    settings = DEFAULTS | values
    validate_settings(settings)
    return settings
