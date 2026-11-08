"""State and race checks for recovery of a confirmed firewall drop; no network/model calls."""

import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from ctf_agent.agent import AttemptStopped
from ctf_agent.config import load_settings, validate_settings
from ctf_agent.sandbox import audit_network, make_sandbox, monitor_guard, recover_scope_denial
from ctf_agent.tools import scope_feedback


@pytest.fixture
def scope(monkeypatch):
    state = {'reason': None, 'packets': 0, 'commands': []}
    sandbox = make_sandbox('synthetic', Mock(), None)
    def stop(reason):
        state['reason'] = state['reason'] or reason
        sandbox['stopping'].set()
    def remaining():
        if state['reason']:
            raise AttemptStopped(state['reason'])
        return 5
    sandbox.update(stop=stop, remaining=remaining, scope_limit=1, scope_phase='command')
    def command(*args, **kwargs):
        state['commands'].append(args)
        if args[0] == 'exec':
            return json.dumps({'nftables': [{'counter': {'name': 'denied', 'packets': state['packets']}}]})
        return 'true' if args[0] == 'inspect' else ''
    monkeypatch.setattr('ctf_agent.sandbox.docker', command)
    return sandbox, state


def test_one_command_many_packets_recovers_then_delayed_log_is_ignored_and_new_incident_stops(scope):
    sandbox, state = scope
    state['packets'] = 2
    audit_network(sandbox, 5)
    state['packets'] = 4
    audit_network(sandbox, 5)
    assert sandbox['scope_incidents'] == 1 and state['reason'] is None
    recover_scope_denial(sandbox)
    assert sandbox['scope_recoveries'] == sandbox['restarts'] == 1
    assert sandbox['denied_acknowledged'] == 4 and not sandbox['scope_pending'].is_set()
    def delayed_lines():
        yield json.dumps({'event': 'network_denied', 'packet': 'delayed old drop'})
        sandbox['closing'].set()  # End the synthetic stream without simulating guard loss.
    sandbox['log_process'] = SimpleNamespace(stdout=delayed_lines())
    monitor_guard(sandbox)
    assert state['reason'] is None and sandbox['scope_incidents'] == 1
    state['packets'] = 5
    audit_network(sandbox, 5)
    assert state['reason'] == 'scope_violation' and sandbox['scope_incidents'] == 2
    assert sandbox['scope_recoveries'] == 1


@pytest.mark.parametrize('condition', ['strict', 'idle'])
def test_strict_or_unattributed_denial_is_terminal(scope, condition):
    sandbox, state = scope
    if condition == 'strict':
        sandbox['scope_limit'] = 0
    else:
        sandbox['scope_phase'] = 'idle'
    state['packets'] = 1
    audit_network(sandbox, 5)
    with pytest.raises(AttemptStopped, match='scope_violation'):
        recover_scope_denial(sandbox)
    assert sandbox['scope_recoveries'] == sandbox['restarts'] == 0


@pytest.mark.parametrize('raw', ['not-json', '{"nftables":[]}',
    '{"nftables":[{"counter":{"name":"denied","packets":true}}]}'])
def test_unknown_counter_is_guard_failure(scope, monkeypatch, raw):
    sandbox, state = scope
    monkeypatch.setattr('ctf_agent.sandbox.docker', lambda *args, **kwargs: raw)
    with pytest.raises(RuntimeError, match='counter unavailable'):
        audit_network(sandbox, 5)
    assert state['reason'] == 'guard_failure' and sandbox['scope_recoveries'] == 0


def test_counter_rewind_is_terminal_without_acknowledging(scope):
    sandbox, state = scope
    state['packets'] = 3
    audit_network(sandbox, 5)
    state['packets'] = 2
    with pytest.raises(RuntimeError, match='counter unavailable'):
        recover_scope_denial(sandbox)
    assert state['reason'] == 'guard_failure' and sandbox['denied_acknowledged'] == 0


@pytest.mark.parametrize('reason', ['wall_limit', 'guard_failure', 'user_cancel', 'scope_violation'])
def test_terminal_reason_wins_during_scope_restart(scope, monkeypatch, reason):
    sandbox, state = scope
    state['packets'] = 1
    audit_network(sandbox, 5)
    def restart(*args, **kwargs):
        sandbox['stop'](reason)
        sandbox['remaining']()
    monkeypatch.setattr('ctf_agent.sandbox.restart_solver', restart)
    with pytest.raises(AttemptStopped, match=reason):
        recover_scope_denial(sandbox)
    assert state['reason'] == reason
    assert sandbox['scope_recoveries'] == 0 and sandbox['denied_acknowledged'] == 0


def test_recovery_allowance_setting_is_only_zero_or_one():
    settings = load_settings()
    for value in (0, 1):
        validate_settings(settings | {'max_scope_recoveries': value})
    for value in (True, -1, 2, 1.5):
        with pytest.raises(ValueError, match='max_scope_recoveries'):
            validate_settings(settings | {'max_scope_recoveries': value})


@pytest.mark.parametrize('state', ['new', 'delivered', 'failed'])
def test_scope_feedback_preserves_capture_delivery_state_without_retry(tmp_path, monkeypatch, state):
    capture = {'files': {'stdout': {'artifact': 'outputs/command/stdout.bin', 'bytes': 5}}}
    if state == 'delivered':
        capture['files']['stdout']['solver_path'] = '/workspace/.command-output/command/stdout.bin'
    elif state == 'failed':
        capture['delivery_error'] = 'prior delivery failure'
    returned = {'capture': capture}
    sandbox = {'directory': tmp_path, 'endpoints': [], 'scope_recoveries': 1}
    monkeypatch.setattr('ctf_agent.tools.recover_scope_denial', lambda sandbox: None)
    delivery = Mock()
    monkeypatch.setattr('ctf_agent.tools.deliver_output', delivery)
    feedback = scope_feedback(returned, sandbox)
    assert feedback['error']['kind'] == 'scope_denied' and feedback['scope_recoveries_used'] == 1
    assert delivery.call_count == (state == 'new')
    if state == 'delivered':
        assert feedback['capture']['files']['stdout']['solver_path'].endswith('stdout.bin')
    elif state == 'failed':
        assert feedback['capture']['delivery_error'] == 'prior delivery failure'
