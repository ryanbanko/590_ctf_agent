"""Fast contract checks; no Docker or model calls."""

import json
import subprocess
import threading
from unittest.mock import patch

import pytest

from ctf_agent.config import CONFIG_PATH, load_settings, validate_settings

DEFAULTS = load_settings()
from ctf_agent.attempt import stop_attempt
from ctf_agent.sandbox import close_sandbox, make_sandbox
from ctf_agent.tools import validate_arguments
from tests.fixtures.target import synthetic_target
from tests.fixtures.tracing import attribute, read_spans


def test_configuration_rejects_invalid_limits(tmp_path):
    for value in [False, 0, -1, float("inf"), float("nan"), "10"]:
        with pytest.raises(ValueError):
            validate_settings(DEFAULTS | {"wall_seconds": value})
    for overrides in [{"max_tool_calls": True}, {"secret": "not-permitted"}]:
        with pytest.raises(ValueError):
            validate_settings(DEFAULTS | overrides)
    path = tmp_path / "config.toml"
    import re

    path.write_text(re.sub(r"(?m)^wall_seconds\s*=.*$", "wall_seconds = 4.0", CONFIG_PATH.read_text()))
    settings = load_settings(path)
    assert settings["wall_seconds"] == 4 and settings["solver_image"] == DEFAULTS["solver_image"]


def test_path_and_size_contracts():
    for path in ["", ".", "../x", "a/../../x", "/absolute", "nul\x00name"]:
        with pytest.raises(ValueError):
            validate_arguments("write_file", {"path": path, "content": "x"}, DEFAULTS)
    with pytest.raises(ValueError):
        validate_arguments("write_file", {"path": "x", "content": "é" * 40_000}, DEFAULTS)
    validate_arguments("write_file", {"path": "nested/script.py", "content": "print('✓')\n"}, DEFAULTS)


def test_command_timeout_and_argument_validation():
    for value in [True, 0, -1, float("nan"), DEFAULTS["command_seconds"] + 1]:
        with pytest.raises(ValueError):
            validate_arguments("run_command", {"command": "echo ok", "timeout_seconds": value}, DEFAULTS)
    for arguments in [{"command": "   "}, {"command": "x" * 20_000},
                      {"command": "echo ok", "extra": "x"}, []]:
        with pytest.raises(ValueError):
            validate_arguments("run_command", arguments, DEFAULTS)
    with pytest.raises(ValueError):
        validate_arguments("not_a_tool", {}, DEFAULTS)


def test_evaluator_uses_exact_equality_without_disclosing_expected(local_attempt, telemetry):
    expected = "ctf{synthetic-unit-test}"
    for candidate in [expected, "wrong", "prefix" + expected, expected + "\n"]:
        with local_attempt(expected_flag=expected) as run:
            result = run["call_tool"]("submit_flag", {"candidate": candidate})
            assert result == {"correct": candidate == expected}
            assert expected not in json.dumps(result)
        spans = read_spans(telemetry, run["result"]["trace_id"])
        root = next(span for span in spans if span.name == "attempt")
        assert expected not in root.to_json()


def test_native_trace_links_to_summary_without_trusted_state(local_attempt, telemetry):
    with local_attempt() as run:
        run["call_tool"]("submit_flag", {"candidate": "wrong"})
    summary = json.loads((run["directory"] / "summary.json").read_text())
    assert summary == run["result"] and summary["termination_reason"] == "completed_without_success"
    spans = read_spans(telemetry, summary["trace_id"])
    root = next(span for span in spans if span.name == "attempt")
    tool = next(span for span in spans if span.name == "submit_flag")
    assert tool.parent.span_id == root.context.span_id
    assert attribute(tool, "input") == {"candidate": "wrong"}
    assert attribute(tool, "output") == {"correct": False}
    assert attribute(root, "output")["tool_calls"] == 1
    serialized = "".join(span.to_json() for span in spans)
    assert "private-expected-answer" not in serialized and "expected_flag" not in serialized
    assert not (run["directory"] / "trace.jsonl").exists()


def test_fixture_cleanup_attempts_network_removal_after_container_failure():
    for failure in [RuntimeError("synthetic removal failure"), subprocess.TimeoutExpired("docker rm", 1)]:
        def fake_docker(*args, **_kwargs):
            if args[:2] == ("network", "inspect"):
                return json.dumps([{"IPAM": {"Config": [{"Subnet": "192.0.2.0/24"}]}}])
            if args[0] == "inspect":
                return "192.0.2.2"
            if args[0] == "rm":
                raise failure
            return ""

        with patch("tests.fixtures.target.docker", side_effect=fake_docker) as command:
            with pytest.raises(RuntimeError, match="cleanup incomplete"):
                with synthetic_target(DEFAULTS):
                    pass
            assert any(call.args[:2] == ("network", "rm") for call in command.call_args_list)


@pytest.mark.parametrize("failure,reason", [
    (RuntimeError("daemon unavailable"), "infrastructure_error"),
    (subprocess.TimeoutExpired("docker kill", 3), "infrastructure_error"),
    (RuntimeError("No such container: test-solver"), "success"),
    (RuntimeError("container test-solver is not running"), "success"),
], ids=["daemon-error", "kill-timeout", "missing", "already-stopped"])
def test_solver_stopping_reports_failures_and_preserves_cleanup(telemetry, monkeypatch, failure, reason):
    commands = []

    def fake_docker(*args, **kwargs):
        commands.append(args)
        if args[0] == "kill":
            raise failure
        return ""

    monkeypatch.setattr("ctf_agent.sandbox.docker", fake_docker)
    with telemetry["client"].start_as_current_observation(name="stop-check") as observation:
        sandbox = make_sandbox("test", observation, None)
        state = {"lock": threading.Lock(), "result": {"termination_reason": None},
                 "sandbox": sandbox, "observation": observation}
        stop_attempt(state, "success")
        assert state["result"]["termination_reason"] == reason
        assert close_sandbox(sandbox) == []
    assert commands == [("kill", "ctf590-test-solver"),
                        ("rm", "--force", "ctf590-test-solver"), ("rm", "--force", "ctf590-test-guard")]
    spans = read_spans(telemetry, observation.trace_id)
    stopping = next(span for span in spans if span.name == "attempt_stopping")
    assert attribute(stopping, "metadata.reason") == "success"
    failures = [span for span in spans if span.name == "solver_stop_failed"]
    assert len(failures) == (1 if reason == "infrastructure_error" else 0)
    assert any(span.name == "sandbox_cleanup" for span in spans)


def test_sdk_export_failure_does_not_skip_stopping_cleanup_or_summary(local_attempt, telemetry, monkeypatch):
    from opentelemetry.sdk.trace.export import SpanExportResult
    from ctf_agent.agent import run_agent

    monkeypatch.setattr(telemetry["exporter"], "export", lambda spans: SpanExportResult.FAILURE)
    with local_attempt(lambda **kwargs: {"role": "assistant", "content": "Done"}) as run:
        assert run_agent("public", run["respond"], run["call_tool"]) == "completed_without_success"
    assert run["result"]["termination_reason"] == "completed_without_success"
    assert not run["result"]["cleanup_errors"]
    assert json.loads((run["directory"] / "summary.json").read_text()) == run["result"]
    assert read_spans(telemetry, run["result"]["trace_id"]) == []


def test_disabled_tracing_cannot_start_solver(tmp_path, monkeypatch):
    from langfuse import Langfuse
    from ctf_agent.attempt import run_attempt

    monkeypatch.setattr("ctf_agent.attempt.docker", lambda *args, **kwargs: pytest.fail("Docker must not start"))
    client = Langfuse(public_key="pk-lf-disabled-check", secret_key="sk-lf-disabled-check", tracing_enabled=False)
    try:
        with pytest.raises(RuntimeError, match="active Langfuse"):
            with run_attempt(DEFAULTS, "test-network", [], "private-answer", tmp_path,
                             langfuse=client):
                pytest.fail("Disabled tracing allowed an attempt")
    finally:
        client.shutdown()


def test_complete_configuration_has_one_model_call_limit(tmp_path):
    from ctf_agent.config import load_experiment

    attempt, model = load_experiment()
    assert model['max_requests'] == attempt['max_model_turns']
    path = tmp_path / 'incomplete.toml'
    path.write_text('[attempt]\nwall_seconds=60\n[model]\n')
    with pytest.raises(ValueError, match='Attempt settings'):
        load_experiment(path)
    path.write_text(CONFIG_PATH.read_text().replace('[model]', '[model]\nmax_requests=7'))
    with pytest.raises(ValueError, match='max_requests is derived'):
        load_experiment(path)


def test_failed_restart_stops_attempt(local_attempt, monkeypatch, telemetry):
    from ctf_agent.agent import AttemptStopped

    monkeypatch.setattr('ctf_agent.tools.bounded_exec', lambda *args, **kwargs:
                        {'timed_out': True, 'stdout': 'partial', 'stderr': '', 'exit_code': None})
    def failed(*args):
        raise RuntimeError('synthetic restart failure')
    monkeypatch.setattr('ctf_agent.tools.restart_solver', failed)
    with local_attempt() as run:
        with pytest.raises(AttemptStopped, match='infrastructure_error'):
            run['call_tool']('run_command', {'command': 'sleep 10'})
    assert run['result']['termination_reason'] == 'infrastructure_error'
    spans = read_spans(telemetry, run['result']['trace_id'])
    event = next(span for span in spans if span.name == 'command_timeout')
    assert attribute(event, 'metadata.partial_output')['stdout'] == 'partial'


@pytest.mark.parametrize('reason', ['wall_limit', 'scope_violation', 'guard_failure', 'user_cancel'])
def test_terminal_stop_wins_during_restart(telemetry, monkeypatch, reason):
    from ctf_agent.agent import AttemptStopped
    from ctf_agent.sandbox import restart_solver, stop_solver

    calls = []
    with telemetry['client'].start_as_current_observation(name='restart-race') as observation:
        sandbox = make_sandbox('race', observation, None)
        terminal = threading.Event()
        stopper = []
        def remaining():
            if terminal.is_set():
                raise AttemptStopped(reason)
            return 5
        sandbox['remaining'] = remaining
        def command(*args, **kwargs):
            calls.append(args)
            if args[0] == 'restart':
                terminal.set()
                thread = threading.Thread(target=stop_solver, args=(sandbox,))
                stopper.append(thread)
                thread.start()
                assert sandbox['stopping'].wait(1)
            return ''
        monkeypatch.setattr('ctf_agent.sandbox.docker', command)
        monkeypatch.setattr('ctf_agent.sandbox.audit_network', lambda *args: None)
        with pytest.raises(AttemptStopped, match=reason):
            restart_solver(sandbox)
        stopper[0].join(timeout=1)
        assert not stopper[0].is_alive()
    assert [call[0] for call in calls] == ['restart', 'kill']
    assert sandbox['restarts'] == 0


def test_terminal_stop_prevents_restart(telemetry, monkeypatch):
    from ctf_agent.sandbox import restart_solver
    with telemetry['client'].start_as_current_observation(name='stopped-restart') as observation:
        sandbox = make_sandbox('stopped', observation, None)
        sandbox['remaining'] = lambda: 5
        sandbox['stopping'].set()
        monkeypatch.setattr('ctf_agent.sandbox.docker', lambda *a, **k: pytest.fail('Restarted after stop'))
        with pytest.raises(RuntimeError, match='stopping'):
            restart_solver(sandbox)
