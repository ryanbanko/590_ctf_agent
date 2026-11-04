"""Untrusted-side helper. The host bounds its output independently."""

import json
import os
from pathlib import PurePosixPath
import selectors
import signal
import subprocess
import sys
import time


def run_command(request):
    process = subprocess.Popen(
        ["/bin/sh", "-c", request["command"]], cwd="/workspace",
        stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        start_new_session=True,
    )
    outputs = {"stdout": bytearray(), "stderr": bytearray()}
    total = 0
    remaining_space = request["output_limit"]
    deadline = time.monotonic() + request["timeout_seconds"]
    timed_out = False
    with selectors.DefaultSelector() as selector:
        selector.register(process.stdout, selectors.EVENT_READ, "stdout")
        selector.register(process.stderr, selectors.EVENT_READ, "stderr")
        while selector.get_map():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                timed_out = True
                break
            for key, _ in selector.select(min(remaining, 0.1)):
                data = os.read(key.fileobj.fileno(), 8192)
                if not data:
                    selector.unregister(key.fileobj)
                    continue
                total += len(data)
                kept = data[:remaining_space]
                outputs[key.data].extend(kept)
                remaining_space -= len(kept)
    if not timed_out:
        try:
            process.wait(timeout=max(0.01, deadline - time.monotonic()))
        except subprocess.TimeoutExpired:
            timed_out = True
    if timed_out:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait(timeout=1)
    process.stdout.close()
    process.stderr.close()
    return {
        "stdout": outputs["stdout"].decode(errors="replace"),
        "stderr": outputs["stderr"].decode(errors="replace"),
        "exit_code": process.returncode,
        "timed_out": timed_out,
        "truncated": total > request["output_limit"],
        "output_bytes": total,
    }


def write_file(request):
    path = PurePosixPath(request["path"])
    if path.is_absolute() or not path.parts or ".." in path.parts:
        raise ValueError("Use a nonempty path relative to /workspace without '..'")
    content = request["content"].encode("utf-8")
    if len(content) > request["write_limit"]:
        raise ValueError("File content exceeds the write limit")
    directory = os.open("/workspace", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in path.parts[:-1]:
            try:
                os.mkdir(part, mode=0o700, dir_fd=directory)
            except FileExistsError:
                pass
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
            os.close(directory)
            directory = child
        descriptor = os.open(
            path.parts[-1], os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW | os.O_NONBLOCK,
            0o600, dir_fd=directory,
        )
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
    finally:
        os.close(directory)
    return {"path": str(path), "bytes_written": len(content)}


def main():
    request = json.load(sys.stdin)
    started = time.monotonic()
    try:
        if request["tool"] == "run_command":
            result = run_command(request)
        elif request["tool"] == "write_file":
            result = write_file(request)
        else:
            raise ValueError("Unknown worker tool")
    except (ValueError, OSError) as error:
        result = {"error": {"kind": "tool_error", "message": str(error)}}
    result["duration_seconds"] = round(time.monotonic() - started, 6)
    print(json.dumps(result, ensure_ascii=True), flush=True)


if __name__ == "__main__":
    main()
