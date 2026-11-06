"""Untrusted solver-local commands and terminal sessions; no host execution."""

import base64
from collections import deque
from contextlib import ExitStack
import ctypes
import fcntl
import importlib.metadata
import json
import os
from pathlib import Path, PurePosixPath
import pty
import select
import selectors
import signal
import socket
import subprocess
import sys
import termios
import time
import uuid

SOCKET = '/tmp/ctf-worker.sock'
OUTPUT_DIRECTORY = Path('/workspace/.ctf-output')
FILE_LIMIT = 1_048_576


def descendants():
    """Include children reparented to this command's Linux subreaper."""
    parents = {}
    for entry in Path('/proc').iterdir():
        if entry.name.isdigit():
            try:
                fields = (entry / 'stat').read_text().rsplit(')', 1)[1].split()
                parents[int(entry.name)] = int(fields[1])
            except (FileNotFoundError, ProcessLookupError):
                pass
    found = {os.getpid()}
    while True:
        children = {pid for pid, parent in parents.items() if parent in found}
        if children <= found:
            return found - {os.getpid()}
        found |= children


def clean_children(process):
    """Freeze before killing, then reap adopted descendants, including setsid()."""
    deadline = time.monotonic() + 1.5
    while time.monotonic() < deadline:
        children = descendants()
        for pid in children:
            try:
                os.kill(pid, signal.SIGSTOP)
            except ProcessLookupError:
                pass
        for pid in descendants():
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        process.poll()
        while True:
            try:
                pid, _ = os.waitpid(-1, os.WNOHANG)
                if not pid:
                    break
            except ChildProcessError:
                break
        if not descendants():
            return True
        time.sleep(.01)
    return False


def command_session(descriptor, request):
    # A separate subreaper per command keeps detached children attributable even
    # when another terminal session is running. No additional capability needed.
    if ctypes.CDLL(None, use_errno=True).prctl(36, 1, 0, 0, 0) != 0:
        raise OSError(ctypes.get_errno(), 'Cannot establish command subreaper')
    with ExitStack() as resources:
        control = resources.enter_context(socket.socket(fileno=descriptor))
        stream = resources.enter_context(control.makefile('rb'))
        interactive = request.get('interactive', False)
        if interactive:
            master, slave = pty.openpty()
            resources.callback(os.close, master)
            try:
                process = subprocess.Popen(['/bin/sh', '-c', request['command']], cwd='/workspace',
                    stdin=slave, stdout=slave, stderr=slave, start_new_session=True,
                    preexec_fn=lambda: fcntl.ioctl(0, termios.TIOCSCTTY, 0))
            finally:
                os.close(slave)
            pipes = {master: 'stdout'}
        else:
            process = subprocess.Popen(['/bin/sh', '-c', request['command']], cwd='/workspace',
                stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                start_new_session=True)
            resources.callback(process.stdout.close)
            resources.callback(process.stderr.close)
            pipes = {process.stdout.fileno(): 'stdout', process.stderr.fileno(): 'stderr'}
        resources.callback(clean_children, process)
        deadline = time.monotonic() + request['lifetime_seconds']
        output_id = request['output_id']
        output = resources.enter_context((OUTPUT_DIRECTORY / (output_id + '.log')).open('xb', buffering=0))
        total = pending_bytes = saved = 0
        head, tail = [], deque()
        head_size = tail_size = 0
        half = request['output_limit'] // 2
        pending = None
        finished = timed_out = closed = False
        cleanup_confirmed = True
        exit_code = None
        with selectors.DefaultSelector() as selector:
            selector.register(control, selectors.EVENT_READ, 'control')
            for fd, name in pipes.items():
                selector.register(fd, selectors.EVENT_READ, name)
            while True:
                now = time.monotonic()
                if not finished and (process.poll() is not None or now >= deadline or closed):
                    timed_out = now >= deadline and process.poll() is None and not closed
                    exit_code = process.poll()
                    cleanup_confirmed = clean_children(process)
                    if exit_code is None:
                        exit_code = process.poll()
                    finished = True
                for key, _ in selector.select(.02):
                    if key.data == 'control':
                        line = stream.readline(8_388_609)
                        if not line:
                            return
                        pending = json.loads(line)
                        pending['until'] = time.monotonic() + pending['wait_seconds']
                        pending['input_bytes_sent'] = 0
                        closed = pending.get('close', False)
                        if pending.get('input') and not finished:
                            data = pending['input'].encode()
                            os.set_blocking(master, False)
                            # Bounded writes: a program that is not reading must not
                            # block the supervisor and defeat its execution deadline.
                            while data:
                                try:
                                    count = os.write(master, data)
                                except BlockingIOError:
                                    pending['input_error'] = 'Program is not reading; remaining input was not sent'
                                    break
                                except OSError:
                                    pending['input_error'] = 'Terminal is not accepting input; remaining input was not sent'
                                    break
                                pending['input_bytes_sent'] += count
                                data = data[count:]
                    else:
                        try:
                            data = os.read(key.fd, 8192)
                        except OSError:
                            data = b''  # A PTY reports EIO when its last slave closes.
                        if not data:
                            selector.unregister(key.fd)
                            continue
                        total += len(data)
                        pending_bytes += len(data)
                        kept = data[:max(0, FILE_LIMIT - saved)]
                        output.write(kept)
                        saved += len(kept)
                        take = min(len(data), half - head_size)
                        if take:
                            head.append((key.data, data[:take]))
                            head_size += take
                        if data[take:]:
                            tail.append((key.data, data[take:]))
                            tail_size += len(data) - take
                            while tail_size > request['output_limit'] - half:
                                name, chunk = tail.popleft()
                                discard = min(len(chunk), tail_size - (request['output_limit'] - half))
                                tail_size -= discard
                                if discard < len(chunk):
                                    tail.appendleft((name, chunk[discard:]))
                drained = len(selector.get_map()) == 1
                if ((finished and (drained or not cleanup_confirmed))
                        or (pending and not finished and time.monotonic() >= pending['until'])):
                    chunks = head + list(tail)
                    result = {'stdout': b''.join(chunk for name, chunk in chunks if name == 'stdout').decode(errors='replace'),
                              'stderr': b''.join(chunk for name, chunk in chunks if name == 'stderr').decode(errors='replace'),
                              'exit_code': exit_code, 'timed_out': timed_out, 'closed': closed,
                              'running': not finished, 'cleanup_confirmed': cleanup_confirmed,
                              'truncated': pending_bytes > request['output_limit'], 'output_bytes': pending_bytes,
                              'total_output_bytes': total, 'output_file_truncated': total > FILE_LIMIT,
                              'input_bytes_sent': pending.get('input_bytes_sent', 0) if pending else 0,
                              'output_file': str(OUTPUT_DIRECTORY / (output_id + '.log')),
                              '_output_id': output_id}
                    if pending and 'input_error' in pending:
                        result['input_error'] = pending['input_error']
                    control.sendall(json.dumps(result, ensure_ascii=True).encode() + b'\n')
                    pending = None
                    head, tail = [], deque()
                    head_size = tail_size = pending_bytes = 0
                    if finished:
                        break


def write_file(request):
    path = PurePosixPath(request['path'])
    if path.is_absolute() or not path.parts or '..' in path.parts:
        raise ValueError("Use a nonempty path relative to /workspace without '..'")
    content = request['content'].encode('utf-8')
    if len(content) > request['write_limit']:
        raise ValueError('File content exceeds the write limit')
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
        descriptor = os.open(path.parts[-1], os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW | os.O_NONBLOCK,
                             0o600, dir_fd=directory)
        with os.fdopen(descriptor, 'wb') as handle:
            handle.write(content)
    finally:
        os.close(directory)
    return {'path': str(path), 'bytes_written': len(content)}


def packages():
    paths = ['/workspace/.venv/lib/python3.13/site-packages', '/usr/local/lib/python3.13/site-packages']
    versions = {}
    for distribution in importlib.metadata.distributions(path=paths):
        name = distribution.metadata.get('Name')
        if name:
            versions.setdefault(name, distribution.version)
    return dict(sorted(versions.items()))


def read_session(session, timeout):
    """Receive one bounded reply; release a finished supervisor immediately."""
    try:
        session['channel'].settimeout(timeout)
        raw = session['stream'].readline(524289)
        if not raw or len(raw) > 524288 or not raw.endswith(b'\n'):
            raise RuntimeError('Command supervisor stopped without a complete result')
        result = json.loads(raw)
        if not isinstance(result, dict) or type(result.get('running')) is not bool:
            raise RuntimeError('Invalid command supervisor result')
        if not result['running']:
            session['process'].wait(timeout=2)
            session['stream'].close()
            session['channel'].close()
            session['result'] = result
        return result
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        raise RuntimeError('Command supervisor communication failed') from error


def serve():
    OUTPUT_DIRECTORY.mkdir(mode=0o700, exist_ok=True)
    sessions = {}
    with socket.socket(socket.AF_UNIX) as listener:
        listener.bind(SOCKET)
        listener.listen(4)
        listener.settimeout(.1)
        while True:
            # Finished commands send their final reply without waiting for a
            # poll. Reap while idle; retain only their bounded result in memory.
            for session in sessions.values():
                if session['result'] is None and (session['process'].poll() is not None
                        or select.select([session['channel']], [], [], 0)[0]):
                    result = read_session(session, 3)
                    if result['running'] or result.get('cleanup_confirmed') is not True:
                        raise RuntimeError('Unconfirmed background command cleanup')
            try:
                connection, _ = listener.accept()
            except socket.timeout:
                continue
            with connection:
                connection.settimeout(130)
                started = time.monotonic()
                try:
                    request = json.loads(connection.makefile('rb').readline(8_388_609))
                    if request['tool'] == 'run_command':
                        session_id = request.get('session_id')
                        if not session_id:
                            session_id = uuid.uuid4().hex
                            request['output_id'] = session_id
                            parent, child = socket.socketpair()
                            process = subprocess.Popen([sys.executable, '-I', __file__, '--session',
                                str(child.fileno()), json.dumps(request)], pass_fds=(child.fileno(),))
                            child.close()
                            sessions[session_id] = {'process': process, 'channel': parent,
                                                    'stream': parent.makefile('rb'), 'result': None}
                        if session_id not in sessions:
                            raise ValueError('Unknown or finished session_id')
                        session = sessions[session_id]
                        result = session['result']
                        if result is None:
                            # A final reply may race with this input. Read it even
                            # if the supervisor has already closed its socket.
                            send_failed = False
                            try:
                                session['channel'].sendall(json.dumps({'input': request.get('input', ''),
                                    'close': request.get('close', False), 'wait_seconds': request['wait_seconds']}).encode() + b'\n')
                            except OSError:
                                send_failed = True
                            result = read_session(session, request['wait_seconds'] + 3)
                            if send_failed and result['running']:
                                raise RuntimeError('Session input delivery failed')
                        if request.get('input') and not result['running'] and result['input_bytes_sent'] == 0:
                            result['input_error'] = 'Session has exited; input was not sent'
                        if result['running']:
                            result['session_id'] = session_id
                        else:
                            del sessions[session_id]
                    elif request['tool'] == 'write_file':
                        result = write_file(request)
                    elif request['tool'] == 'artifact':
                        identifier = request['output_id']
                        if len(identifier) != 32 or any(c not in '0123456789abcdef' for c in identifier):
                            raise ValueError('Invalid output identifier')
                        descriptor = os.open(OUTPUT_DIRECTORY / (identifier + '.log'), os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
                        with os.fdopen(descriptor, 'rb') as handle:
                            result = {'data': base64.b64encode(handle.read(FILE_LIMIT)).decode()}
                    elif request['tool'] == 'inspect':
                        result = {}
                    else:
                        raise ValueError('Unknown worker tool')
                    if request['tool'] != 'artifact':
                        result['_packages'] = packages()
                except (ValueError, OSError) as error:
                    result = {'error': {'kind': 'tool_error', 'message': str(error)}}
                except Exception as error:
                    result = {'_worker_error': type(error).__name__}
                result['duration_seconds'] = round(time.monotonic() - started, 6)
                connection.sendall(json.dumps(result, ensure_ascii=True).encode() + b'\n')


def main():
    if sys.argv[1:] == ['--serve']:
        serve()
    elif sys.argv[1:2] == ['--session']:
        command_session(int(sys.argv[2]), json.loads(sys.argv[3]))
    else:
        request = sys.stdin.buffer.read(8_388_609)
        if len(request) > 8_388_608:
            raise ValueError('Worker request exceeds its bound')
        with socket.socket(socket.AF_UNIX) as connection:
            connection.connect(SOCKET)
            connection.sendall(request + b'\n')
            with connection.makefile('rb') as stream:
                sys.stdout.buffer.write(stream.readline(2_097_153))


if __name__ == '__main__':
    main()
