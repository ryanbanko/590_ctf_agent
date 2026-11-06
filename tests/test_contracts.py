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
                        ("rm", "--force", "ctf590-test-solver"), ("rm", "--force", "ctf590-test-guard"),
                        ("network", "rm", "ctf590-test-egress")]
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
            with run_attempt(DEFAULTS, "test-network", "test-gateway", [], "private-answer", tmp_path,
                             langfuse=client):
                pytest.fail("Disabled tracing allowed an attempt")
    finally:
        client.shutdown()


def test_terminal_session_argument_contract():
    valid_id = 'a' * 32
    for arguments in [{'command': 'python -i', 'interactive': True},
                      {'session_id': valid_id, 'input': 'print(1)\n', 'wait_seconds': 0},
                      {'session_id': valid_id, 'close': True}]:
        validate_arguments('run_command', arguments, DEFAULTS)
    for arguments in [{'session_id': '../../escape'}, {'session_id': valid_id, 'command': 'echo wrong'},
                      {'command': 'cat', 'interactive': 'true'}, {'command': 'echo ok', 'wait_seconds': 1},
                      {'command': 'cat', 'interactive': True, 'timeout_seconds': 2},
                      {'session_id': valid_id, 'wait_seconds': float('nan')},
                      {'session_id': valid_id, 'input': 'x' * 20000}]:
        with pytest.raises(ValueError):
            validate_arguments('run_command', arguments, DEFAULTS)


def test_unconfirmed_command_cleanup_stops_attempt(local_attempt, monkeypatch):
    from ctf_agent.agent import AttemptStopped

    with local_attempt() as run:
        monkeypatch.setattr('ctf_agent.tools.invoke_worker', lambda *args, **kwargs:
                            {'timed_out': True, 'cleanup_confirmed': False})
        with pytest.raises(AttemptStopped, match='infrastructure_error'):
            run['call_tool']('run_command', {'command': 'sleep 10'})
    assert run['result']['termination_reason'] == 'infrastructure_error'


@pytest.fixture
def worker_module():
    import importlib.util
    from pathlib import Path

    spec = importlib.util.spec_from_file_location('solver_worker', Path('docker/worker.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_supervisor_setup_error_cleans_started_children(worker_module, monkeypatch, tmp_path):
    from unittest.mock import MagicMock, Mock

    process = MagicMock()
    process.stdout.fileno.return_value = 10
    process.stderr.fileno.return_value = 11
    library = MagicMock()
    library.prctl.return_value = 0
    cleanup = Mock(return_value=True)
    monkeypatch.setattr(worker_module.ctypes, 'CDLL', lambda *args, **kwargs: library)
    monkeypatch.setattr(worker_module.socket, 'socket', MagicMock())
    monkeypatch.setattr(worker_module.subprocess, 'Popen', lambda *args, **kwargs: process)
    monkeypatch.setattr(worker_module, 'clean_children', cleanup)
    monkeypatch.setattr(worker_module, 'OUTPUT_DIRECTORY', tmp_path / 'missing-output-directory')
    with pytest.raises(FileNotFoundError):
        worker_module.command_session(0, {'command': 'synthetic', 'lifetime_seconds': 1,
                                         'output_id': 'a' * 32, 'output_limit': 32})
    cleanup.assert_called_once_with(process)
    process.stdout.close.assert_called_once()
    process.stderr.close.assert_called_once()


@pytest.mark.parametrize('reply', [b'', b'invalid-json\n', b'{}\n'])
def test_bad_supervisor_reply_is_infrastructure_failure(worker_module, reply):
    from unittest.mock import MagicMock

    session = {'channel': MagicMock(), 'stream': MagicMock()}
    session['stream'].readline.return_value = reply
    with pytest.raises(RuntimeError):
        worker_module.read_session(session, 1)


def test_package_inventory_is_written_only_on_change(tmp_path, monkeypatch):
    from pathlib import Path
    from ctf_agent.sandbox import invoke_worker

    inventories = iter([{'example': '1'}, {'example': '1'}, {'example': '2'}])
    monkeypatch.setattr('ctf_agent.sandbox.bounded_exec', lambda *args, **kwargs:
                        json.dumps({'_packages': next(inventories), 'stdout': 'ok'}).encode())
    writes = []
    original = Path.write_text

    def record(path, content, *args, **kwargs):
        writes.append(json.loads(content))
        return original(path, content, *args, **kwargs)

    monkeypatch.setattr(Path, 'write_text', record)
    sandbox = {'solver': 'substituted-solver', 'directory': tmp_path}
    for _ in range(3):
        assert invoke_worker(sandbox, {'tool': 'inspect'}, 1) == {'stdout': 'ok'}
    assert writes == [{'example': '1'}, {'example': '2'}]
    assert json.loads((tmp_path / 'packages.json').read_text()) == {'example': '2'}


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
