"""Host-only, bounded message queue for optional human guidance during one run."""

from datetime import datetime, timezone
import fcntl
from itertools import islice
import json
import os
from pathlib import Path
import shlex
import tempfile
import time
import uuid

from .agent import AttemptStopped


PREFACE = "Human guidance: Consider this alongside the evidence gathered so far."
MAX_MESSAGE_BYTES = 4096
MAX_MESSAGES = 64
MAX_RECORD_BYTES = 32768


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def atomic_json(path, value):
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=".pending-", delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(json.dumps(value, ensure_ascii=False) + "\n")
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def read_json(path):
    # Never follow a message symlink or read an unbounded/non-regular file.
    import stat

    with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK), "rb") as handle:
        if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):
            raise ValueError("Guidance records must be regular files")
        raw = handle.read(MAX_RECORD_BYTES + 1)
    if len(raw) > MAX_RECORD_BYTES:
        raise ValueError("Guidance record exceeds its size limit")
    return json.loads(raw)


def message_files(directory):
    # A normal empty turn is just one directory listing, with no file reads.
    with os.scandir(directory / "messages") as entries:
        entries = list(islice(entries, MAX_MESSAGES + 2))
    paths = [Path(entry.path) for entry in entries if entry.name.endswith(".json")]
    if len(entries) > MAX_MESSAGES + 1 or len(paths) > MAX_MESSAGES:
        raise ValueError("Guidance queue exceeds its message limit")
    return sorted(paths)


def validate_message(message):
    if not isinstance(message, str) or not message.strip():
        raise ValueError("Guidance must be nonempty text")
    if len(message.encode("utf-8")) > MAX_MESSAGE_BYTES:
        raise ValueError(f"Guidance is limited to {MAX_MESSAGE_BYTES} UTF-8 bytes")


def start_guidance(run_directory, run_id):
    directory = run_directory / "guidance"
    directory.mkdir(mode=0o700)
    (directory / "messages").mkdir(mode=0o700)
    info = {"run_id": run_id, "pid": os.getpid(), "status": "running"}
    (directory / "queue.lock").touch(mode=0o600)
    atomic_json(directory / "state.json", info)
    command = ("uv run --frozen python -m ctf_agent guide --run "
               + shlex.quote(str(run_directory.resolve())) + ' --message "YOUR MESSAGE"')
    print(f"Guidance enabled for run {run_id}.\n{command}", flush=True)
    return {"directory": directory, "info": info, "seen": set(), "pending": [],
            "disabled": False, "errors": 0}


def queue_guidance(run_directory, message):
    validate_message(message)
    directory = run_directory / "guidance"
    if not (directory / "queue.lock").is_file():
        raise ValueError("This run has no guidance inbox; start it with --allow-guidance")
    # Only senders lock: serialize publication/order/cap without blocking the solver.
    with (directory / "queue.lock").open("r") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        info = read_json(directory / "state.json")
        if info["status"] != "running":
            raise ValueError("This guidance inbox is closed")
        try:
            os.kill(info["pid"], 0)
        except ProcessLookupError:
            raise ValueError("The guidance process is no longer running") from None
        if len(message_files(directory)) >= MAX_MESSAGES:
            raise ValueError(f"At most {MAX_MESSAGES} guidance messages are allowed per run")
        message_id = f"{time.time_ns():020d}-{uuid.uuid4().hex}"
        row = {"id": message_id, "run_id": info["run_id"], "queued_at": timestamp(), "text": message}
        atomic_json(directory / "messages" / (message_id + ".json"), row)
    return row


def guidance_error(state, error, observation):
    state["disabled"] = True
    state["errors"] += 1
    print(f"Guidance disabled after {type(error).__name__}; solve continues. "
          "Check the inbox and its records.", flush=True)
    try:
        atomic_json(state["directory"] / "state.json", state["info"] | {"status": "disabled"})
    except (OSError, ValueError):
        pass
    # Guidance telemetry must not turn an optional inbox failure into a solve failure.
    try:
        observation.create_event(name="human_guidance_error", level="WARNING",
                                 metadata={"exception": type(error).__name__})
    except Exception:
        pass


def receive_guidance(state, observation, remaining):
    if state["disabled"]:
        return []
    messages = []
    try:
        for path in message_files(state["directory"]):
            remaining()
            if path.stem in state["seen"]:
                continue
            row = read_json(path)
            if (set(row) != {"id", "run_id", "queued_at", "text"}
                    or row["id"] != path.stem or row["run_id"] != state["info"]["run_id"]
                    or not isinstance(row["queued_at"], str)):
                raise ValueError("Invalid guidance record")
            validate_message(row["text"])
            observation.create_event(name="human_guidance_queued", input=row)
            state["seen"].add(row["id"])
            state["pending"].append(row)
            messages.append({"role": "user", "content": PREFACE + "\n\n" + row["text"]})
    except AttemptStopped:
        raise
    except Exception as error:
        guidance_error(state, error, observation)
    return messages


def dispatch_guidance(state, observation, request_number, sent_at):
    """Record inclusion in a request attempt, never claim provider acceptance."""
    rows, state["pending"] = state["pending"], []
    for row in rows:
        receipt = {"id": row["id"], "status": "included_in_request",
                   "timestamp": sent_at, "request": request_number}
        try:
            with (state["directory"] / "events.jsonl").open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(receipt) + "\n")
            observation.create_event(name="human_guidance_delivered", input=row, metadata=receipt)
            print(f'Guidance {row["id"]}: included in request {request_number}.', flush=True)
        except Exception as error:
            guidance_error(state, error, observation)
    return len(rows)


def close_guidance(state, reason, observation):
    try:
        atomic_json(state["directory"] / "state.json", state["info"] | {"status": "closed", "reason": reason})
    except (OSError, ValueError) as error:
        guidance_error(state, error, observation)


def guidance_status(run_directory):
    directory = run_directory / "guidance"
    info = read_json(directory / "state.json")
    receipts = {}
    path = directory / "events.jsonl"
    if path.exists():
        # At most MAX_MESSAGES small receipts are written by the controller.
        for line in path.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            receipts[row["id"]] = row
    rows = []
    for path in message_files(directory):
        message = read_json(path)
        pending = "queued" if info["status"] == "running" else "undelivered"
        rows.append(message | receipts.get(message["id"], {"status": pending}))
    return {"run": info, "messages": rows}
