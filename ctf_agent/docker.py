"""Fixed Docker CLI calls. Model data never runs in a host shell."""

from collections import deque
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


def bounded_exec(args: list[str], request: bytes, timeout: float, limit: int) -> dict:
    """Drain Docker output with bounded head/tail memory; timeout needs solver reset.

    Killing the local Docker client does not kill its remote command. The caller
    must reset or stop the solver before executing another action after timeout.
    """
    process = subprocess.Popen(["docker", *args], stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    deadline = time.monotonic() + timeout
    pending = memoryview(request)
    head, tail = [], deque()
    head_size = tail_size = total = 0
    half = limit // 2
    timed_out = False
    try:
        with selectors.DefaultSelector() as selector:
            for stream, event, name in [(process.stdin, selectors.EVENT_WRITE, 'input'),
                                        (process.stdout, selectors.EVENT_READ, 'stdout'),
                                        (process.stderr, selectors.EVENT_READ, 'stderr')]:
                os.set_blocking(stream.fileno(), False)
                selector.register(stream, event, name)
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
        chunks = head + list(tail)
        return {'stdout': b''.join(c for n, c in chunks if n == 'stdout').decode(errors='replace'),
                'stderr': b''.join(c for n, c in chunks if n == 'stderr').decode(errors='replace'),
                'exit_code': None if timed_out else process.returncode,
                'timed_out': timed_out, 'truncated': total > limit, 'output_bytes': total}
    finally:
        if process.poll() is None:
            process.kill()
        process.wait(timeout=2)
        for stream in (process.stdin, process.stdout, process.stderr):
            stream.close()
