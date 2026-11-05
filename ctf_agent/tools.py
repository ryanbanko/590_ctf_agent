"""Three explicit tools. Definitions and real implementations live together."""

import math
from pathlib import PurePosixPath

from .sandbox import invoke_worker


TOOL_DEFINITIONS = [
    {
        "name": "run_command",
        "description": (
            "Run a command with /bin/sh starting in the isolated solver's /workspace. "
            "Use bash explicitly for Bash syntax. Each call starts a new process; files "
            "persist between calls, but network connections do not automatically persist. "
            "Set connection and read deadlines shorter than timeout_seconds (or its "
            "default) so network errors return before the command limit. A command "
            "timeout ends the attempt."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "command": {"type": "string"},
                "timeout_seconds": {"type": "number", "exclusiveMinimum": 0,
                                    "description": "Seconds to allow; omission uses the configured maximum."},
            },
            "required": ["command"],
            "additionalProperties": False,
        },
    },
    {
        "name": "write_file",
        "description": "Write UTF-8 text to a workspace-relative file. Symlink traversal is rejected.",
        "parameters": {
            "type": "object",
            "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
            "required": ["path", "content"],
            "additionalProperties": False,
        },
    },
    {
        "name": "submit_flag",
        "description": "Submit a candidate to trusted verification. Success ends the attempt.",
        "parameters": {
            "type": "object",
            "properties": {"candidate": {"type": "string"}},
            "required": ["candidate"],
            "additionalProperties": False,
        },
    },
]
TOOLS_BY_NAME = {tool["name"]: tool for tool in TOOL_DEFINITIONS}


def validate_arguments(name: str, arguments: dict, settings: dict):
    if name not in TOOLS_BY_NAME:
        raise ValueError("Unknown tool")
    if not isinstance(arguments, dict):
        raise ValueError("Tool arguments must be an object")
    schema = TOOLS_BY_NAME[name]["parameters"]
    if not set(schema["required"]) <= arguments.keys() or arguments.keys() - schema["properties"].keys():
        raise ValueError("Missing or unexpected tool argument")
    for key, value in arguments.items():
        if key == "timeout_seconds":
            if (type(value) not in (int, float) or not math.isfinite(value)
                    or not 0 < value <= settings["command_seconds"]):
                raise ValueError(
                    "timeout_seconds must be a finite number greater than 0 "
                    f"and at most {settings['command_seconds']:g} seconds")
        elif not isinstance(value, str):
            raise ValueError(f"{key} must be a string")
    if name == "run_command":
        command = arguments["command"]
        if not command.strip() or "\x00" in command or len(command.encode()) > settings["max_command_bytes"]:
            raise ValueError("Command is empty, contains NUL, or exceeds the byte limit")
    elif name == "write_file":
        path = arguments["path"]
        parsed = PurePosixPath(path)
        if (not parsed.parts or parsed.is_absolute() or ".." in parsed.parts
                or "\x00" in path or len(path.encode()) > 4096):
            raise ValueError("Use a nonempty workspace-relative path without '..'")
        if len(arguments["content"].encode()) > settings["max_write_bytes"]:
            raise ValueError("File content exceeds the write limit")
    elif not arguments["candidate"] or len(arguments["candidate"].encode()) > 4096:
        raise ValueError("Candidate must contain 1 to 4096 bytes")


def execute_tool(name: str, arguments: dict, settings: dict, sandbox: dict,
                 seconds_left: float) -> dict:
    """Execute a validated command/file action; verification stays in the runner."""
    request = {"tool": name, **arguments}
    request["output_limit"] = settings["max_output_bytes"]
    request["write_limit"] = settings["max_write_bytes"]
    request["timeout_seconds"] = min(arguments.get("timeout_seconds", settings["command_seconds"]), seconds_left)
    return invoke_worker(sandbox, request, timeout=min(seconds_left, request["timeout_seconds"] + 2))
