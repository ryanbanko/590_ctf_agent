"""Three explicit tools. Definitions and real implementations live together."""

import json
import math
from pathlib import PurePosixPath

from .docker import bounded_exec, docker
from .sandbox import restart_solver


TOOL_DEFINITIONS = [
    {
        "name": "run_command",
        "description": (
            "Run a command with /bin/sh starting in the isolated solver's /workspace. "
            "Use python -m pip install for missing dependencies; external internet is "
            "permitted only for pip installation, never answer/write-up lookup. "
            "Commands finish or reach timeout_seconds; a timeout restarts the solver, "
            "ending ALL its processes and connections while preserving files and pip installs. "
            "Use shorter internal network deadlines. Each command starts a new shell; "
            "cross-call terminal sessions are unavailable. Use bash explicitly for Bash syntax. "
            "Large output returns a bounded beginning/end excerpt; redirect output to "
            "a workspace file yourself if you need to inspect omitted sections."
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


# Runs once per write inside the solver. Values arrive as stdin data, not code.
WRITE_FILE = """
import json, os, stat, sys
from pathlib import PurePosixPath
request = json.load(sys.stdin)
try:
    path = PurePosixPath(request['path'])
    content = request['content'].encode()
    directory = os.open('/workspace', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in path.parts[:-1]:
            try:
                os.mkdir(part, mode=0o700, dir_fd=directory)
            except FileExistsError:
                pass
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
            os.close(directory)
            directory = child
        descriptor = os.open(path.parts[-1], os.O_WRONLY | os.O_CREAT | os.O_NOFOLLOW | os.O_NONBLOCK,
                             0o600, dir_fd=directory)
        with os.fdopen(descriptor, 'wb') as handle:
            if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):
                raise ValueError('Use a regular file')
            handle.truncate(0)
            handle.write(content)
    finally:
        os.close(directory)
    result = {'path': str(path), 'bytes_written': len(content)}
except (OSError, ValueError) as error:
    result = {'error': {'kind': 'tool_error', 'message': str(error)}}
print(json.dumps(result))
"""


def execute_tool(name: str, arguments: dict, settings: dict, sandbox: dict,
                 seconds_left: float) -> dict:
    """Use standard Docker exec; only trusted controller code can restart it."""
    command = (["/bin/sh", "-c", arguments["command"]] if name == "run_command"
               else ["python", "-I", "-c", WRITE_FILE])
    request = b"" if name == "run_command" else json.dumps(arguments).encode()
    returned = bounded_exec(["exec", "--interactive", "--user", "1000:1000", "--workdir", "/workspace",
                             sandbox["solver"], *command], request,
                            min(arguments.get("timeout_seconds", settings["command_seconds"]), seconds_left),
                            settings["max_output_bytes"])
    if returned["timed_out"]:
        sandbox["observation"].create_event(name="command_timeout", metadata={"partial_output": returned})
        restart_solver(sandbox)
        returned.update(solver_restarted=True, process_state_reset=True)
        return returned
    if returned["exit_code"] != 0:
        if docker("inspect", "--format", "{{.State.Running}}", sandbox["solver"],
                  timeout=min(3, sandbox["remaining"]())) != "true":
            raise RuntimeError("Solver stopped during command execution")
    if name == "write_file":
        if returned["exit_code"] != 0 or returned["truncated"]:
            raise RuntimeError("File writer did not return a complete observation")
        return json.loads(returned["stdout"])
    return returned
