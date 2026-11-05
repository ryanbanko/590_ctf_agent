"""Three explicit tools. Definitions and real implementations live together."""

import math
from pathlib import PurePosixPath

from .sandbox import invoke_worker


TOOL_DEFINITIONS = [
    {
        "name": "run_command",
        "description": (
            "Run a command with /bin/sh starting in the isolated solver's /workspace. "
            "Use python -m pip install for missing dependencies; external internet is "
            "permitted only for pip installation, never answer/write-up lookup. "
            "Use interactive=true to start a terminal session; later calls supply "
            "session_id and optional input (include a newline to submit a line), or "
            "close=true. wait_seconds controls how long an interactive call waits for "
            "output, not session lifetime; sessions end at the attempt deadline. "
            "Ordinary commands finish or reach timeout_seconds; a timeout cleans up "
            "that command and permits recovery. Use shorter internal network deadlines. "
            "Files persist; ordinary commands start new shells. Use bash explicitly "
            "for Bash syntax. Large output returns a beginning/end excerpt and file "
            "path; inspect additional sections with a command."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "command": {"type": "string"},
                "interactive": {"type": "boolean"},
                "session_id": {"type": "string"},
                "input": {"type": "string"},
                "close": {"type": "boolean"},
                "wait_seconds": {"type": "number", "minimum": 0, "maximum": 5,
                                 "description": "Interactive wait, default 0.5 seconds."},
                "timeout_seconds": {"type": "number", "exclusiveMinimum": 0,
                                    "description": "Seconds to allow; omission uses the configured maximum."},
            },
            "required": [],
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
        if key in {"interactive", "close"}:
            if type(value) is not bool:
                raise ValueError(f"{key} must be a boolean")
        elif key == "wait_seconds":
            if type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= 5:
                raise ValueError("wait_seconds must be between 0 and 5")
        elif key == "timeout_seconds":
            if (type(value) not in (int, float) or not math.isfinite(value)
                    or not 0 < value <= settings["command_seconds"]):
                raise ValueError(
                    "timeout_seconds must be a finite number greater than 0 "
                    f"and at most {settings['command_seconds']:g} seconds")
        elif not isinstance(value, str):
            raise ValueError(f"{key} must be a string")
    if name == "run_command":
        if "session_id" in arguments:
            identifier = arguments["session_id"]
            if (len(identifier) != 32 or any(c not in "0123456789abcdef" for c in identifier)
                    or arguments.keys() & {"command", "interactive", "timeout_seconds"}):
                raise ValueError("Use a returned session_id without command, interactive, or timeout_seconds")
        else:
            command = arguments.get("command", "")
            if not command.strip() or "\x00" in command or len(command.encode()) > settings["max_command_bytes"]:
                raise ValueError("Command is empty, contains NUL, or exceeds the byte limit")
            if arguments.keys() & {"input", "close"}:
                raise ValueError("input and close require session_id")
            if not arguments.get("interactive") and "wait_seconds" in arguments:
                raise ValueError("wait_seconds requires an interactive command or session_id")
            if arguments.get("interactive") and "timeout_seconds" in arguments:
                raise ValueError("Interactive sessions use the attempt deadline; set wait_seconds instead")
        if len(arguments.get("input", "").encode()) > settings["max_command_bytes"]:
            raise ValueError("Session input exceeds the command byte limit")
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
    interactive = arguments.get("interactive", False) or "session_id" in arguments
    request["lifetime_seconds"] = seconds_left if interactive else request["timeout_seconds"]
    request["wait_seconds"] = arguments.get("wait_seconds", 0.5) if interactive else request["timeout_seconds"] + 2
    return invoke_worker(sandbox, request, timeout=min(seconds_left, request["wait_seconds"] + 4))
