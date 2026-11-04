"""Fixed Docker CLI calls. Model data is passed through stdin, never a host shell."""

import os
import selectors
import subprocess
import time


def docker(*args: str, timeout: float = 15) -> str:
    result = subprocess.run(
        ["docker", *args], capture_output=True,
        text=True, timeout=max(0.05, timeout), check=False,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip()[:2000] or f"Docker exited {result.returncode}")
    return result.stdout.strip()


def bounded_exec(args: list[str], request: bytes, timeout: float, limit: int = 524_288) -> bytes:
    """Bound the untrusted worker's host-side output, including protocol corruption."""
    process = subprocess.Popen(
        ["docker", *args], stdin=subprocess.PIPE,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    deadline = time.monotonic() + timeout
    output = bytearray()
    errors = bytearray()
    pending = memoryview(request)
    try:
        with selectors.DefaultSelector() as selector:
            for stream, events in [(process.stdin, selectors.EVENT_WRITE),
                                   (process.stdout, selectors.EVENT_READ),
                                   (process.stderr, selectors.EVENT_READ)]:
                os.set_blocking(stream.fileno(), False)
                selector.register(stream, events)
            while selector.get_map():
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError("Sandbox worker exceeded its host-side deadline")
                for key, _ in selector.select(min(remaining, 0.1)):
                    stream = key.fileobj
                    if stream is process.stdin:
                        try:
                            count = os.write(stream.fileno(), pending[:4096])
                            pending = pending[count:]
                        except BrokenPipeError:
                            pending = pending[:0]
                        if not pending:
                            selector.unregister(stream)
                            stream.close()
                    else:
                        data = os.read(stream.fileno(), 8192)
                        if not data:
                            selector.unregister(stream)
                            continue
                        (errors if stream is process.stderr else output).extend(data)
                        if len(output) + len(errors) > limit:
                            raise RuntimeError("Sandbox worker exceeded the host output bound")
            returncode = process.wait(timeout=max(0.05, deadline - time.monotonic()))
        if returncode:
            raise RuntimeError(f"Sandbox worker exited {returncode}: " + errors.decode(errors="replace")[:1000])
        return bytes(output)
    finally:
        if process.poll() is None:
            process.kill()
        process.wait(timeout=2)
        for stream in (process.stdin, process.stdout, process.stderr):
            if not stream.closed:
                stream.close()
