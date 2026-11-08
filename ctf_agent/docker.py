"""Fixed Docker CLI calls. Model data never runs in a host shell."""

from collections import deque
import os
import selectors
import subprocess
import time
from typing import BinaryIO


def docker(*args: str, timeout: float = 15) -> str:
    result = subprocess.run(
        ["docker", *args], capture_output=True,
        text=True, timeout=max(0.05, timeout), check=False,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip()[:2000] or f"Docker exited {result.returncode}")
    return result.stdout.strip()


def bounded_exec(args: list[str], request: bytes | BinaryIO, timeout: float, limit: int,
                 *, capture: dict | None = None) -> dict:
    """Drain Docker output with bounded head/tail memory; timeout needs solver reset.

    Killing the local Docker client does not kill its remote command. The caller
    must reset or stop the solver before executing another action after timeout.
    Optional capture spills raw streams before preview eviction, up to its byte
    limit. A trusted input file can be streamed directly to Docker without loading
    it into memory. Capture/storage errors do not stop draining the command.
    """
    process = subprocess.Popen(["docker", *args], stdin=subprocess.PIPE if isinstance(request, bytes) else request,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    deadline = time.monotonic() + timeout
    pending = memoryview(request) if isinstance(request, bytes) else memoryview(b"")
    head, tail = [], deque()
    head_size = tail_size = total = 0
    stream_bytes = {"stdout": 0, "stderr": 0}
    half = limit // 2
    timed_out = False
    recorded = None
    handles = {}

    def retain(name, data):
        if recorded["error"] is not None:
            return
        take = min(len(data), capture["limit"] - recorded["bytes"])
        if take < len(data):
            recorded["limit_reached"] = True
        if not take:
            return
        try:
            if not handles:
                capture["directory"].parent.mkdir(mode=0o700, exist_ok=True)
                capture["directory"].mkdir(mode=0o700)
                for stream in stream_bytes:
                    handles[stream] = (capture["directory"] / f"{stream}.bin").open("xb", buffering=0)
                    recorded["files"][stream] = {"bytes": 0}
            pending_output = memoryview(data)[:take]
            while pending_output:
                written = handles[name].write(pending_output)
                if not written:
                    raise OSError("Output storage made no progress")
                recorded["files"][name]["bytes"] += written
                recorded["bytes"] += written
                pending_output = pending_output[written:]
        except OSError as error:
            # Keep host paths out of the model-facing observation.
            recorded["error"] = os.strerror(error.errno) if error.errno else "Output storage failed"

    try:
        with selectors.DefaultSelector() as selector:
            for stream, event, name in [(process.stdout, selectors.EVENT_READ, 'stdout'),
                                        (process.stderr, selectors.EVENT_READ, 'stderr')]:
                os.set_blocking(stream.fileno(), False)
                selector.register(stream, event, name)
            if process.stdin is not None:
                os.set_blocking(process.stdin.fileno(), False)
                selector.register(process.stdin, selectors.EVENT_WRITE, 'input')
            # Also wait for process completion when output closes before exit.
            while selector.get_map() or process.poll() is None:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    timed_out = True
                    break
                for key, _ in selector.select(min(remaining, 0.05)):
                    if key.data == 'input':
                        try:
                            pending = pending[os.write(key.fd, pending[:4096]):] if pending else pending
                        except BrokenPipeError:
                            pending = pending[:0]
                        if not pending:
                            selector.unregister(key.fileobj)
                            key.fileobj.close()
                        continue
                    data = os.read(key.fd, 8192)
                    if not data:
                        selector.unregister(key.fileobj)
                        continue
                    total += len(data)
                    stream_bytes[key.data] += len(data)
                    if capture is not None and total > limit:
                        if recorded is None:
                            recorded = {"bytes": 0, "files": {}, "limit_reached": False, "error": None}
                            for name, chunk in head + list(tail):
                                retain(name, chunk)
                        retain(key.data, data)
                    take = min(len(data), half - head_size)
                    if take:
                        head.append((key.data, data[:take]))
                        head_size += take
                    if data[take:]:
                        tail.append((key.data, data[take:]))
                        tail_size += len(data) - take
                        while tail_size > limit - half:
                            name, chunk = tail.popleft()
                            discard = min(len(chunk), tail_size - (limit - half))
                            tail_size -= discard
                            if discard < len(chunk):
                                tail.appendleft((name, chunk[discard:]))
        output = {}
        for name, count in stream_bytes.items():
            prefix = b''.join(c for n, c in head if n == name)
            suffix = b''.join(c for n, c in tail if n == name)
            omitted = count - len(prefix) - len(suffix)
            if omitted:
                output[name] = (prefix.decode(errors='replace')
                                + f'\n[... {omitted} bytes omitted ...]\n'
                                + suffix.decode(errors='replace'))
            else:
                output[name] = (prefix + suffix).decode(errors='replace')
        output.update(exit_code=None if timed_out else process.returncode, timed_out=timed_out,
                      truncated=total > limit, output_bytes=total,
                      preview_bytes=head_size + tail_size)
        if recorded is not None:
            recorded["complete"] = not timed_out and recorded["error"] is None and recorded["bytes"] == total
            output["capture"] = recorded
        return output
    finally:
        if process.poll() is None:
            process.kill()
        process.wait(timeout=2)
        for handle in handles.values():
            try:
                handle.close()
            except OSError as error:
                recorded["error"] = os.strerror(error.errno) if error.errno else "Output storage failed"
                recorded["complete"] = False
        for stream in (process.stdin, process.stdout, process.stderr):
            if stream is not None:
                stream.close()
