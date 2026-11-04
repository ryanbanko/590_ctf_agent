"""Fixed synthetic integration checks, not a development pilot or scored run."""

from contextlib import ExitStack
import json
from pathlib import Path
import shlex
import time
import uuid

import pytest

from ctf_agent.attempt import run_attempt
from ctf_agent.docker import docker
from .fixtures.target import synthetic_target
from .fixtures.tracing import read_spans, save_spans

pytestmark = pytest.mark.docker


def python_command(source: str) -> dict:
    return {"command": "python -I -c " + shlex.quote(source)}


def test_files_tools_evaluator_success(attempt: dict, target: dict):
    result = attempt["call_tool"]("write_file", {"path": "scripts/check.py", "content": "print('observation: 5')\n"})
    assert result["bytes_written"] == 24, result
    result = attempt["call_tool"]("run_command", {"command": "python scripts/check.py"})
    assert result["stdout"].strip() == "observation: 5", result
    result = attempt["call_tool"]("run_command", {"command": "exit 7"})
    assert result["exit_code"] == 7, result
    assert attempt["call_tool"]("submit_flag", {"candidate": "wrong-synthetic-candidate"}) == {"correct": False}
    url = f'http://{target["address"]}:8000/'
    result = attempt["call_tool"]("run_command", python_command(
        f"import urllib.request; print(urllib.request.urlopen({url!r},timeout=2).read().decode())"))
    candidate = json.loads(result["stdout"])["flag"]
    assert candidate == target["expected_flag"]
    assert attempt["call_tool"]("submit_flag", {"candidate": candidate}) == {"correct": True}
    before = attempt["result"]["tool_calls"]
    with pytest.raises(RuntimeError):
        attempt["call_tool"]("run_command", {"command": "echo should-not-run"})
    assert attempt["result"]["tool_calls"] == before


def test_filesystem_credentials_privileges_output(attempt: dict, target: dict, settings):
    container = json.loads(docker("inspect", attempt["solver"]))[0]
    host = container["HostConfig"]
    assert host["ReadonlyRootfs"] and host["CapDrop"] == ["ALL"]
    assert host["Memory"] == settings["memory_mb"] * 1024 * 1024
    assert host["MemorySwap"] == host["Memory"]
    assert host["PidsLimit"] == settings["pids"]
    assert host["NanoCpus"] == int(settings["cpus"] * 1_000_000_000)
    assert not host["Binds"] and all(mount["Type"] == "tmpfs" for mount in container["Mounts"])
    for arguments in [{"path": "../../escape", "content": "x"},
                      {"path": "/tmp/escape", "content": "x"},
                      {"path": "too-big", "content": "x" * (settings["max_write_bytes"] + 1)}]:
        assert "error" in attempt["call_tool"]("write_file", arguments)
    assert "error" in attempt["call_tool"]("run_command", {"command": "echo no", "unexpected": True})
    attempt["call_tool"]("run_command", {"command": "ln -s /tmp escape; ln -s /tmp/final escape-file"})
    assert "error" in attempt["call_tool"]("write_file", {"path": "escape/file", "content": "x"})
    assert "error" in attempt["call_tool"]("write_file", {"path": "escape-file", "content": "x"})
    result = attempt["call_tool"]("run_command", python_command(
        "import os,pathlib,json; print(json.dumps({'uid':os.getuid(),"
        "'status':pathlib.Path('/proc/self/status').read_text(),"
        "'env':dict(os.environ),'docker_socket':pathlib.Path('/var/run/docker.sock').exists(),"
        "'target_source':pathlib.Path('/opt/fixture/service.py').exists(),"
        "'challenge_json':bool(list(pathlib.Path('/workspace').rglob('challenge.json')))}))"))
    info = json.loads(result["stdout"])
    assert info["uid"] == 1000
    assert "CapEff:\t0000000000000000" in info["status"]
    assert "CapBnd:\t0000000000000000" in info["status"]
    assert "NoNewPrivs:\t1" in info["status"]
    assert not info["docker_socket"] and not info["target_source"] and not info["challenge_json"]
    assert not {"FIXTURE_FLAG", "LITELLM_TOKEN", "LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY",
                "LANGFUSE_BASE_URL"} & info["env"].keys()
    assert target["expected_flag"] not in json.dumps(info)
    result = attempt["call_tool"]("run_command", {"command": "echo forbidden > /opt/ctf/worker.py"})
    assert result["exit_code"] != 0
    marker = attempt["directory"] / "host-only-marker"
    marker.write_text("host-private", encoding="utf-8")
    result = attempt["call_tool"]("run_command", python_command(
        f"from pathlib import Path; print(Path({str(marker.resolve())!r}).exists())"))
    assert result["stdout"].strip() == "False"
    result = attempt["call_tool"]("run_command", python_command("print('x' * 100000)"))
    assert result["truncated"] and len(result["stdout"].encode()) <= settings["max_output_bytes"]


def check_denial(attempt: dict, command: str, telemetry):
    try:
        attempt["call_tool"]("run_command", {"command": command})
    except RuntimeError:
        pass
    assert attempt["result"]["termination_reason"] == "scope_violation", attempt["result"]["termination_reason"]
    spans = read_spans(telemetry, attempt["result"]["trace_id"])
    assert any(span.name in {"network_denied", "network_denial_counter"} for span in spans)


def test_command_timeout_detached_child(attempt: dict):
    # The child creates a new session, escaping ordinary process-group cleanup.
    command = python_command(
        "import subprocess,time; subprocess.Popen(['sleep','30'], start_new_session=True); time.sleep(30)")
    result = attempt["call_tool"]("run_command", command | {"timeout_seconds": 0.4})
    assert result["timed_out"] and attempt["result"]["termination_reason"] == "command_timeout"
    running = docker("inspect", "--format", "{{.State.Running}}", attempt["solver"])
    assert running == "false"


@pytest.mark.parametrize("attempt", [{"max_tool_calls": 1}], indirect=True)
def test_tool_limit(attempt: dict):
    attempt["call_tool"]("run_command", {"command": "echo first"})
    with pytest.raises(RuntimeError):
        attempt["call_tool"]("run_command", {"command": "echo second"})
    assert attempt["result"]["termination_reason"] == "tool_limit" and attempt["result"]["tool_calls"] == 1


def test_command_timeout_closed_output(attempt: dict):
    result = attempt["call_tool"]("run_command", {
        "command": "exec >/dev/null 2>&1; sleep 30", "timeout_seconds": 0.4})
    assert result["timed_out"] and attempt["result"]["termination_reason"] == "command_timeout"


@pytest.mark.parametrize("attempt", [{"wall_seconds": 3, "command_seconds": 30}], indirect=True)
def test_wall_limit(attempt: dict):
    with pytest.raises(RuntimeError):
        attempt["call_tool"]("run_command", python_command("import time; time.sleep(30)"))
    assert attempt["result"]["termination_reason"] == "wall_limit", attempt["result"]["termination_reason"]


def test_guard_loss(attempt: dict):
    docker("kill", attempt["guard"])
    deadline = time.monotonic() + 3
    while time.monotonic() < deadline:
        running = docker("inspect", "--format", "{{.State.Running}}", attempt["solver"])
        if attempt["result"]["termination_reason"] == "guard_failure" and running == "false":
            return
        time.sleep(0.02)
    raise AssertionError("Loss of guard did not stop the solver within three seconds")


def test_worker_loss(attempt: dict):
    docker("kill", attempt["solver"])
    with pytest.raises(RuntimeError):
        attempt["call_tool"]("run_command", {"command": "echo should-not-run"})
    assert attempt["result"]["termination_reason"] == "infrastructure_error"


def test_ipv6_no_external_route(attempt: dict):
    result = attempt["call_tool"]("run_command", python_command(
        "import socket; s=socket.socket(socket.AF_INET6); s.settimeout(1); "
        "s.connect(('2001:db8::1',443))"))
    assert result["exit_code"] != 0 and "Network is unreachable" in result["stderr"], result


@pytest.mark.parametrize("destination", [
    "unapproved_live_port", "internet_ip", "host_address", "embedded_dns",
    "external_dns", "unrelated_container",
])
def test_network_scope(attempt, target, settings, destination, telemetry):
    with ExitStack() as stack:
        if destination == "unapproved_live_port":
            address, port = target["address"], 8001
        elif destination == "internet_ip":
            address, port = "198.51.100.1", 443
        elif destination == "host_address":
            bridge = json.loads(docker("network", "inspect", "bridge"))[0]
            address, port = bridge["IPAM"]["Config"][0]["Gateway"], 443
        elif destination == "unrelated_container":
            other = stack.enter_context(synthetic_target(settings))
            address, port = other["address"], 8000
        else:
            address, port = ("127.0.0.11" if destination == "embedded_dns" else "192.0.2.53"), 53
        if destination.endswith("dns"):
            source = ("import socket,time; s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM); "
                      f"s.sendto(b'blocked-probe',({address!r},{port})); time.sleep(2)")
        else:
            source = f"import socket; socket.create_connection(({address!r},{port}),2)"
        check_denial(attempt, python_command(source)["command"], telemetry)


def test_interruption_cleanup(settings, target, output_root, record_property, telemetry):
    record_property("check_name", "interruption_cleanup")
    with pytest.raises(KeyboardInterrupt):
        with run_attempt(settings, target["network"], target["gateway"], target["endpoints"],
                         target["expected_flag"], output_root, langfuse=telemetry["client"], label="interruption_cleanup") as attempt:
            record_property("run_id", attempt["run_id"])
            raise KeyboardInterrupt("synthetic interruption")
    save_spans(telemetry, attempt["directory"], attempt["result"]["trace_id"])
    assert attempt["result"]["termination_reason"] == "user_cancel"
    assert not attempt["result"]["cleanup_errors"]


def test_setup_failure_cleanup(settings, target, output_root, record_property, telemetry):
    record_property("check_name", "setup_failure_cleanup")
    before = set(output_root.glob("*/summary.json"))
    invalid = settings | {"solver_image": "ctf590-missing:" + uuid.uuid4().hex}
    with pytest.raises(RuntimeError):
        with run_attempt(invalid, target["network"], target["gateway"], target["endpoints"],
                         target["expected_flag"], output_root, langfuse=telemetry["client"], label="setup_failure_cleanup"):
            pytest.fail("Started solver with a nonexistent image")
    created = set(output_root.glob("*/summary.json")) - before
    assert len(created) == 1
    path = created.pop()
    summary = json.loads(path.read_text())
    save_spans(telemetry, path.parent, summary["trace_id"])
    record_property("run_id", summary["run_id"])
    assert summary["termination_reason"] == "infrastructure_error"
    assert summary["tool_calls"] == 0 and not summary["cleanup_errors"]
