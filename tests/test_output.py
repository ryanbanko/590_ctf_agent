"""Exercise the real bounded reader with fixed synthetic subprocesses, never model commands."""

import errno
from pathlib import Path
import subprocess
import sys
import threading
from unittest.mock import Mock

import pytest

from ctf_agent.agent import AttemptStopped
from ctf_agent.config import load_settings, validate_settings
from ctf_agent.docker import bounded_exec
from ctf_agent.tools import deliver_output, execute_tool


@pytest.fixture
def reader(monkeypatch, tmp_path):
    popen = subprocess.Popen
    calls = 0

    def run(script, *, limit=16384, retention=2_000_000, timeout=5, request=b""):
        nonlocal calls
        calls += 1
        def launch(args, **kwargs):
            assert args == ["docker", "synthetic"]
            return popen([sys.executable, "-I", "-c", script], **kwargs)
        monkeypatch.setattr("ctf_agent.docker.subprocess.Popen", launch)
        directory = tmp_path / "outputs" / str(calls)
        result = bounded_exec(["synthetic"], request, timeout, limit,
                              capture={"directory": directory, "limit": retention})
        return result, directory

    return run


@pytest.mark.parametrize("size", [0, 16383, 16384, 16385, 150000])
def test_overflow_preserves_prefix_middle_end_and_short_output_has_no_file(reader, size):
    result, directory = reader(f"import sys; sys.stdout.buffer.write(bytes(i % 127 for i in range({size})))")
    expected = bytes(i % 127 for i in range(size))
    assert result["exit_code"] == 0 and not result["timed_out"]
    assert result["output_bytes"] == size
    assert result["preview_bytes"] == min(size, 16384)
    if size <= 16384:
        assert not result["truncated"] and "capture" not in result and not directory.exists()
        assert result["stdout"].encode() == expected
    else:
        capture = result["capture"]
        assert result["truncated"] and capture["complete"] and not capture["limit_reached"]
        assert capture["bytes"] == size and capture["error"] is None
        assert (directory / "stdout.bin").read_bytes() == expected
        assert (directory / "stderr.bin").read_bytes() == b""
        assert f"{size - 16384} bytes omitted" in result["stdout"]
        assert result["stdout"].startswith(expected[:8192].decode())
        assert result["stdout"].endswith(expected[-8192:].decode())


def test_separate_streams_raw_invalid_utf8_and_nonzero_exit(reader):
    result, directory = reader("import sys; sys.stdout.buffer.write(b'\\xff'*40000); "
                               "sys.stderr.buffer.write(b'error-tail'*5000); sys.exit(7)")
    assert result["exit_code"] == 7 and result["capture"]["complete"]
    assert result["output_bytes"] == 90000 and result["preview_bytes"] == 16384
    assert "\ufffd" in result["stdout"] and "omitted" in result["stdout"]
    assert result["stderr"].endswith("error-tail")
    assert (directory / "stdout.bin").read_bytes() == b"\xff" * 40000
    assert (directory / "stderr.bin").read_bytes() == b"error-tail" * 5000


@pytest.mark.parametrize("retention", [0, 500, 30000])
def test_retention_limit_does_not_stop_draining_or_hide_late_diagnostic(reader, retention):
    result, directory = reader("import sys; sys.stdout.write('x'*90000+'-finished')", retention=retention)
    assert result["exit_code"] == 0 and result["stdout"].endswith("-finished")
    assert result["output_bytes"] == 90009 and result["capture"]["bytes"] == retention
    assert not result["capture"]["complete"] and result["capture"]["limit_reached"]
    if retention:
        assert (directory / "stdout.bin").read_bytes() == b"x" * retention
    else:
        assert not directory.exists() and not result["capture"]["files"]


def test_storage_failure_retains_result_and_drains(reader, monkeypatch):
    original = Path.open
    def no_space(path, *args, **kwargs):
        if path.name.endswith(".bin"):
            raise OSError(errno.ENOSPC, "synthetic storage failure")
        return original(path, *args, **kwargs)
    monkeypatch.setattr(Path, "open", no_space)
    result, _ = reader("print('x'*50000+'-done')")
    assert result["exit_code"] == 0 and result["stdout"].rstrip().endswith("-done")
    assert result["output_bytes"] == 50006 and not result["capture"]["complete"]
    assert result["capture"]["error"] == "No space left on device"


def test_background_output_and_timeout_capture_are_partial(reader):
    result, directory = reader("import os,time; os.write(1,b'x'*40000); time.sleep(30)", timeout=.4)
    assert result["timed_out"] and result["exit_code"] is None
    assert not result["capture"]["complete"] and not result["capture"]["limit_reached"]
    assert (directory / "stdout.bin").read_bytes() == b"x" * 40000


@pytest.mark.parametrize("fault", ["mid_write", "close"])
def test_storage_write_or_close_failure_keeps_command_result_and_truthful_record(reader, monkeypatch, fault):
    original = Path.open
    def partial_storage(path, *args, **kwargs):
        handle = original(path, *args, **kwargs)
        if path.name != "stdout.bin" or args != ("xb",):
            return handle
        proxy = Mock(wraps=handle)
        written_once = False
        def write(data):
            nonlocal written_once
            if written_once:
                raise OSError(errno.ENOSPC, "synthetic mid-write failure")
            written_once = True
            return handle.write(data[:3])
        if fault == "mid_write":
            proxy.write.side_effect = write
        else:
            def close():
                handle.close()
                raise OSError(errno.EIO, "synthetic close failure")
            proxy.close.side_effect = close
        return proxy
    monkeypatch.setattr(Path, "open", partial_storage)
    result, directory = reader("print('x'*50000+'-done')")
    assert result["exit_code"] == 0 and result["stdout"].rstrip().endswith("-done")
    expected = b"xxx" if fault == "mid_write" else b"x"*50000+b"-done\n"
    assert result["capture"]["bytes"] == len(expected) and not result["capture"]["complete"]
    assert result["capture"]["files"]["stdout"]["bytes"] == len(expected)
    assert result["capture"]["error"]
    assert (directory / "stdout.bin").read_bytes() == expected


def test_trusted_input_file_streams_without_loading_it(reader, tmp_path):
    source = tmp_path / "input"
    source.write_bytes(b"binary\x00\xff" * 10000)
    with source.open("rb") as handle:
        result, directory = reader("import sys; sys.stdout.buffer.write(sys.stdin.buffer.read())", request=handle)
    assert result["capture"]["complete"]
    assert (directory / "stdout.bin").read_bytes() == source.read_bytes()


def test_capture_limits_are_explicit_positive_integer_settings():
    settings = load_settings()
    for field in ("max_capture_bytes", "max_attempt_capture_bytes"):
        for value in (0, -1, True, 1.5):
            with pytest.raises(ValueError):
                validate_settings(settings | {field: value})


def test_attempt_retention_budget_counts_actual_bytes_across_commands(tmp_path, monkeypatch):
    limits = []
    def command(*args, capture):
        limits.append(capture["limit"])
        return {"exit_code": 0, "timed_out": False, "capture": {"bytes": min(20, capture["limit"]), "files": {}}}
    monkeypatch.setattr("ctf_agent.tools.bounded_exec", command)
    monkeypatch.setattr("ctf_agent.tools.deliver_output", lambda *args: None)
    sandbox = {"directory": tmp_path, "captured_output_bytes": 0, "solver": "synthetic", "observation": Mock()}
    settings = load_settings() | {"max_capture_bytes": 20, "max_attempt_capture_bytes": 30}
    for _ in range(3):
        execute_tool("run_command", {"command": "synthetic"}, settings, sandbox, 5)
    assert limits == [20, 10, 0] and sandbox["captured_output_bytes"] == 30


@pytest.mark.parametrize("condition", ["stopping", "deadline", "failure", "timeout", "late_stop"])
def test_output_delivery_respects_terminal_state_and_never_restarts(tmp_path, monkeypatch, condition):
    directory = tmp_path / "capture"
    directory.mkdir()
    (directory / "stdout.bin").write_bytes(b"saved")
    returned = {"exit_code": 7, "capture": {"complete": True, "files": {"stdout": {"bytes": 5}}}}
    sandbox = {"remaining": lambda: 1, "stopping": threading.Event(), "solver": "synthetic",
               "observation": Mock(), "stop": Mock()}
    if condition == "stopping":
        sandbox["stopping"].set()
    elif condition == "deadline":
        def expired():
            raise AttemptStopped("wall_limit")
        sandbox["remaining"] = expired
    executor = Mock(return_value={"timed_out": condition == "timeout", "exit_code": 1,
                                  "truncated": False, "stdout": ""})
    if condition == "late_stop":
        def finish_after_stop(*args):
            sandbox["stopping"].set()
            def stopped():
                raise AttemptStopped("scope_violation")
            sandbox["remaining"] = stopped
            return {"timed_out": False, "exit_code": 0, "truncated": False,
                    "stdout": '{"bytes_written":5}'}
        executor.side_effect = finish_after_stop
    monkeypatch.setattr("ctf_agent.tools.bounded_exec", executor)
    monkeypatch.setattr("ctf_agent.tools.restart_solver", lambda *a: pytest.fail("Delivery restarted solver"))
    if condition in {"deadline", "late_stop"}:
        with pytest.raises(AttemptStopped, match="wall_limit" if condition == "deadline" else "scope_violation"):
            deliver_output(returned, sandbox, directory)
    else:
        deliver_output(returned, sandbox, directory)
        assert "delivery_error" in returned["capture"]
    assert "solver_path" not in returned["capture"]["files"]["stdout"]
    assert returned["exit_code"] == 7 and (directory / "stdout.bin").read_bytes() == b"saved"
    assert executor.call_count == (condition in {"failure", "timeout", "late_stop"})
    assert sandbox["stop"].call_count == (condition == "timeout")
