"""Three explicit tools. Definitions and real implementations live together."""

import json
import math
from pathlib import PurePosixPath
import time
import uuid

from .docker import bounded_exec, docker
from .sandbox import restart_solver


TOOL_DEFINITIONS = [
    {
        "name": "run_command",
        "description": (
            "Run a command with /bin/sh starting in the isolated solver's /workspace. "
            "Use bash explicitly for Bash syntax. Each call starts a new shell without an "
            "interactive terminal or cross-call input. Keep stateful read/compute/respond "
            "interactions in one script using the same connection. A command timeout restarts "
            "the solver, ending all processes/connections while preserving files/packages; "
            "no automatic retries. Use shorter internal network deadlines. Returns stdout, "
            "stderr, exit code and timeout/truncation metadata; ordinary nonzero exits are "
            "diagnostic results. Large output has marked beginning/end excerpts and capture "
            "metadata: solver_path entries locate retained files; complete, limit_reached, "
            "error and delivery_error describe capture/retrieval limits."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "command": {"type": "string"},
                "timeout_seconds": {"type": "number", "exclusiveMinimum": 0,
                                    "description": "Command seconds to allow; omission uses the configured maximum, clipped to remaining attempt time. Recovery/output delivery also use remaining attempt time."},
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


COPY_OUTPUT = """
import json, os, sys
directory = os.open('/workspace', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
try:
    for part in ('.command-output', sys.argv[1]):
        try:
            os.mkdir(part, mode=0o700, dir_fd=directory)
        except FileExistsError:
            pass
        child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
        os.close(directory)
        directory = child
    descriptor = os.open(sys.argv[2], os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_NONBLOCK,
                         0o600, dir_fd=directory)
    written = 0
    with os.fdopen(descriptor, 'wb') as output:
        while True:
            chunk = sys.stdin.buffer.read(8192)
            if not chunk:
                break
            output.write(chunk)
            written += len(chunk)
    if written != int(sys.argv[3]):
        raise ValueError('Incomplete output delivery')
finally:
    os.close(directory)
print(json.dumps({'bytes_written': written}))
"""


def deliver_output(returned: dict, sandbox: dict, capture_directory):
    """Copy only controller-generated artifacts; never restart for file delivery."""
    capture = returned["capture"]
    deadline = time.monotonic() + 5
    for stream, record in capture["files"].items():
        remaining = min(deadline - time.monotonic(), sandbox["remaining"]())
        if remaining <= 0 or sandbox["stopping"].is_set():
            capture["delivery_error"] = "Delivery budget exhausted or solver stopping"
            return
        try:
            with (capture_directory / f"{stream}.bin").open("rb") as source:
                delivered = bounded_exec(["exec", "--interactive", "--user", "1000:1000",
                    "--workdir", "/workspace", sandbox["solver"], "python", "-I", "-c", COPY_OUTPUT,
                    capture_directory.name, f"{stream}.bin", str(record["bytes"])],
                    source, remaining, 4096)
            if delivered["timed_out"]:
                capture["delivery_error"] = "Output delivery timed out"
                sandbox["observation"].create_event(name="output_delivery_timeout", metadata={"command_result": returned})
                # A timed-out Docker exec can outlive its client. Stop rather than
                # leave a writer running or reset unrelated solver processes.
                sandbox["stop"]("infrastructure_error")
                return
            sandbox["remaining"]()
            if sandbox["stopping"].is_set():
                capture["delivery_error"] = "Solver stopping"
                return
            if (delivered["exit_code"] != 0 or delivered["truncated"]
                    or json.loads(delivered["stdout"]) != {"bytes_written": record["bytes"]}):
                capture["delivery_error"] = "Output writer failed or returned an incomplete acknowledgement"
                return
            record["solver_path"] = f"/workspace/.command-output/{capture_directory.name}/{stream}.bin"
        except (OSError, ValueError) as error:
            capture["delivery_error"] = f"Output delivery failed ({type(error).__name__})"
            return


def execute_tool(name: str, arguments: dict, settings: dict, sandbox: dict,
                 seconds_left: float) -> dict:
    """Use standard Docker exec; only trusted controller code can restart it."""
    command = (["/bin/sh", "-c", arguments["command"]] if name == "run_command"
               else ["python", "-I", "-c", WRITE_FILE])
    request = b"" if name == "run_command" else json.dumps(arguments).encode()
    capture_directory = sandbox["directory"] / "outputs" / uuid.uuid4().hex[:12]
    capture_options = ({"capture": {"directory": capture_directory,
        "limit": min(settings["max_capture_bytes"],
                     settings["max_attempt_capture_bytes"] - sandbox["captured_output_bytes"])}}
        if name == "run_command" else {})
    returned = bounded_exec(["exec", "--interactive", "--user", "1000:1000", "--workdir", "/workspace",
                             sandbox["solver"], *command], request,
                            min(arguments.get("timeout_seconds", settings["command_seconds"]), seconds_left),
                            settings["max_output_bytes"], **capture_options)
    if "capture" in returned:
        sandbox["captured_output_bytes"] += returned["capture"]["bytes"]
        for stream, record in returned["capture"]["files"].items():
            record["artifact"] = f"outputs/{capture_directory.name}/{stream}.bin"
        sandbox["observation"].create_event(name="command_output_captured", metadata=returned["capture"])
    if returned["timed_out"]:
        sandbox["observation"].create_event(name="command_timeout", metadata={"partial_output": returned})
        restart_solver(sandbox)
        returned.update(solver_restarted=True, process_state_reset=True)
        if name == "write_file":
            return returned
    elif returned["exit_code"] != 0:
        if docker("inspect", "--format", "{{.State.Running}}", sandbox["solver"],
                  timeout=min(3, sandbox["remaining"]())) != "true":
            raise RuntimeError("Solver stopped during command execution")
    if name == "write_file":
        if returned["exit_code"] != 0 or returned["truncated"]:
            raise RuntimeError("File writer did not return a complete observation")
        return json.loads(returned["stdout"])
    if "capture" in returned:
        deliver_output(returned, sandbox, capture_directory)
    return returned
