"""Synthetic Docker proof of blocked access, corrective feedback and bounded recovery."""

import json
import time

import pytest

from ctf_agent.agent import AttemptStopped, run_agent
from ctf_agent.docker import docker
from .fixtures.responses import tool_response
from .fixtures.tracing import attribute, read_spans
from .test_controls import python_command

pytestmark = pytest.mark.docker


def connection_counter(target):
    # Fixed fixture-only listener and trusted counter query; never run trace/model code.
    source = """
import select, socket
listeners = []
for port in (8002, 8003):
    s = socket.socket(); s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', port)); s.listen(); listeners.append(s)
seen = 0
while True:
    for listener in select.select(listeners, [], [])[0]:
        client, _ = listener.accept()
        if listener is listeners[0]:
            seen += 1
        else:
            client.sendall(str(seen).encode())
        client.close()
"""
    docker('exec', '--detach', target['container'], 'python', '-I', '-c', source)
    def received():
        return int(docker('exec', target['container'], 'python', '-I', '-c',
            "import socket; s=socket.create_connection(('127.0.0.1',8003),1); print(s.recv(32).decode())"))
    deadline = time.monotonic() + 3
    while True:
        try:
            assert received() == 0
            return received
        except RuntimeError:
            if time.monotonic() >= deadline:
                raise
            time.sleep(.05)


def test_blocked_connection_is_recoverable_without_reaching_live_listener(attempt, target, telemetry):
    received = connection_counter(target)
    attempt['call_tool']('write_file', {'path': 'kept', 'content': 'persistent'})
    started = docker('inspect', '--format', '{{.State.StartedAt}}', target['container'])
    before = attempt['remaining_seconds']()
    command = python_command(
        "import socket,subprocess,pathlib,os; "
        "child=subprocess.Popen(['sleep','29'],start_new_session=True,stdin=subprocess.DEVNULL,"
        "stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); "
        "pathlib.Path('old-child.pid').write_text(str(child.pid)); os.write(1,b'x'*90000); "
        f"socket.create_connection(({target['address']!r},8002),10); "
        "pathlib.Path('forbidden-reached').write_text('bad')")
    result = attempt['call_tool']('run_command', command)
    assert result['error']['kind'] == 'scope_denied'
    assert result['solver_restarted'] and result['process_state_reset'] and result['scope_recoveries_used'] == 1
    assert result['allowed_endpoints'] == target['endpoints']
    assert result['interrupted'] and not result['timed_out'] and result['exit_code'] is None
    assert attempt['result']['termination_reason'] is None
    assert attempt['result']['tool_calls'] == 2 and attempt['remaining_seconds']() < before
    assert received() == 0
    assert docker('inspect', '--format', '{{.State.StartedAt}}', target['container']) == started
    capture = result['capture']
    assert not capture['complete'] and capture['bytes'] == 90000
    output_path = capture['files']['stdout']['solver_path']
    proof = attempt['call_tool']('run_command', python_command(
        "from pathlib import Path; import urllib.request; "
        "assert Path('kept').read_text()=='persistent', 'workspace file changed'; "
        "assert not Path('forbidden-reached').exists(), 'forbidden connection marker appeared'; "
        "pid=int(Path('old-child.pid').read_text()); p=Path(f'/proc/{pid}/cmdline'); "
        "assert not p.exists() or b'sleep\\x0029\\x00' not in p.read_bytes(), 'old sleep 29 child survived'; "
        f"assert Path({output_path!r}).read_bytes()==b'x'*90000, 'captured bytes changed'; "
        f"assert urllib.request.urlopen('http://{target['address']}:8000/',timeout=2).status==200, 'permitted HTTP failed'; "
        "print('permitted-work-ok')"))
    assert proof['exit_code'] == 0 and proof['stdout'].strip() == 'permitted-work-ok'
    assert received() == 0
    spans = read_spans(telemetry, attempt['result']['trace_id'])
    recovered = [s for s in spans if s.name == 'scope_recovered']
    assert len(recovered) == 1 and attribute(recovered[0], 'metadata.recovery') == 1


def test_model_history_receives_denial_and_second_incident_is_terminal(attempt, target, telemetry):
    # Fixed scripted responder; checks feedback delivery without a paid model.
    def respond(*, messages, tools, timeout_seconds):
        if messages[-1]['role'] == 'user':
            return tool_response('run_command', python_command(
                f"import socket; socket.create_connection(({target['address']!r},8001),10)"), 'first-denial')
        feedback = json.loads(messages[-1]['content'])
        assert feedback['error']['kind'] == 'scope_denied'
        assert feedback['scope_recoveries_used'] == 1 and feedback['allowed_endpoints'] == target['endpoints']
        return tool_response('run_command', python_command(
            f"import socket; socket.create_connection(({target['address']!r},8001),10)"), 'second-denial')
    # The attempt fixture has no responder; this wrapper drives its bounded tools
    # through the real public loop and records the scripted model-independent input.
    histories = []
    def recorded(**kwargs):
        histories.append(kwargs['messages'])
        return respond(**kwargs, timeout_seconds=attempt['remaining_seconds']())
    assert run_agent('synthetic permitted endpoint', recorded, attempt['call_tool']) == 'scope_violation'
    assert len(histories) == 2 and attempt['result']['termination_reason'] == 'scope_violation'
    assert attempt['result']['tool_calls'] == 2
    spans = read_spans(telemetry, attempt['result']['trace_id'])
    assert sum(s.name == 'scope_recovered' for s in spans) == 1


def test_denial_between_commands_remains_terminal(attempt, target):
    source = f"import time,socket; time.sleep(2); socket.create_connection(({target['address']!r},8001),3)"
    result = attempt['call_tool']('run_command', python_command(
        f"import subprocess; subprocess.Popen(['python','-I','-c',{source!r}],start_new_session=True,"
        "stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); print('background')"))
    assert result['exit_code'] == 0 and result['stdout'].strip() == 'background'
    deadline = time.monotonic() + 6
    while attempt['result']['termination_reason'] is None:
        assert time.monotonic() < deadline
        time.sleep(.05)
    assert attempt['result']['termination_reason'] == 'scope_violation'


def test_failed_scope_restart_is_terminal_and_never_returns_recovery(attempt, target, monkeypatch):
    def failed(*args, **kwargs):
        raise RuntimeError('synthetic scope restart failure')
    monkeypatch.setattr('ctf_agent.sandbox.restart_solver', failed)
    with pytest.raises(AttemptStopped, match='infrastructure_error'):
        attempt['call_tool']('run_command', python_command(
            f"import socket; socket.create_connection(({target['address']!r},8001),10)"))
    assert attempt['result']['termination_reason'] == 'infrastructure_error'
