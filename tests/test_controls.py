"""Fixed synthetic integration checks, not a development pilot or scored run."""

from contextlib import ExitStack
from datetime import datetime, timezone
import json
from pathlib import Path
import shlex
import subprocess
import sys
import xml.etree.ElementTree as ET
import time
import uuid
import zipfile

import pytest

from ctf_agent.attempt import run_attempt
from ctf_agent.docker import docker
from ctf_agent.config import load_settings
from ctf_agent.launch import collect_provenance
from .fixtures.target import synthetic_target
from .fixtures.tracing import read_spans, save_spans

pytestmark = pytest.mark.docker


def python_command(source: str) -> dict:
    return {"command": "python -I -c " + shlex.quote(source)}


@pytest.mark.parametrize("attempt", [{"command_seconds": 30.0}], indirect=True)
def test_solver_utilities_and_executable_workspace(attempt, target):
    result = attempt["call_tool"]("run_command", python_command(f'''
import json, pathlib, shutil, subprocess
tools = ['bash', 'file', 'strings', 'readelf', 'objdump', 'xxd', 'curl', 'nc',
         'openssl', 'unzip', 'zip', 'gcc', 'make', 'gdb']
assert all(shutil.which(name) for name in tools)
shutil.copy('/bin/true', 'benign-true')
subprocess.run(['./benign-true'], check=True)
pathlib.Path('hello.c').write_text('int main(void) {{ return 0; }}\\n')
subprocess.run(['gcc', 'hello.c', '-o', 'hello'], check=True)
subprocess.run(['./hello'], check=True)
header = pathlib.Path('hello').read_bytes()[:20]
assert header[:5] == b'\\x7fELF\\x02' and int.from_bytes(header[18:20], 'little') == 62
subprocess.run(['zip', '-q', 'hello.zip', 'hello.c'], check=True)
assert subprocess.check_output(['unzip', '-p', 'hello.zip', 'hello.c']) == pathlib.Path('hello.c').read_bytes()
assert 'ELF 64-bit' in subprocess.check_output(['file', 'hello'], text=True)
assert 'ELF64' in subprocess.check_output(['readelf', '-h', 'hello'], text=True)
assert 'main' in subprocess.check_output(['objdump', '-t', 'hello'], text=True)
assert 'main' in subprocess.check_output(['strings', 'hello'], text=True)
assert '7f45 4c46' in subprocess.check_output(['xxd', '-l', '4', 'hello'], text=True)
assert 'OpenSSL' in subprocess.check_output(['openssl', 'version'], text=True)
assert 'Make' in subprocess.check_output(['make', '--version'], text=True)
assert 'elf64-x86-64' in subprocess.check_output(['gdb', '--batch', '-ex', 'info files', 'hello'], text=True)
reply = subprocess.check_output(['curl', '--noproxy', '*', '--fail', '--silent', '--show-error',
                                 '--max-time', '2', 'http://{target['address']}:8000/'])
assert 'flag' in json.loads(reply)
subprocess.run(['nc', '-z', '-w', '2', {target['address']!r}, '8000'], check=True)
subprocess.run(['bash', '-c', 'cat <<< bash-ok'], check=True, capture_output=True)
print(json.dumps({{'utilities': tools, 'amd64_execution': True,
                  'compiled_execution': True, 'archive_roundtrip': True, 'permitted_curl_and_nc': True}}))
'''))
    assert result["exit_code"] == 0, result
    assert json.loads(result["stdout"])["amd64_execution"]


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


@pytest.mark.parametrize("attempt", [{"command_seconds": 30.0}], indirect=True)
def test_solver_python_libraries_and_network_deadline(attempt, target):
    result = attempt["call_tool"]("run_command", python_command(f'''
import importlib.metadata, json, socket, time
import numpy as np
import requests
from Crypto.Cipher import AES
from PIL import Image
from pwn import ELF, context, p32, u32, remote
from sympy import Symbol, solve

context.log_level = 'error'
assert ELF('/bin/true', checksec=False).arch == 'amd64'
assert u32(p32(12345)) == 12345
x = Symbol('x')
assert solve(x + 2 - 5, x) == [3]
assert np.dot([1, 2], [3, 4]) == 11
cipher = AES.new(b'0123456789abcdef', AES.MODE_ECB)
block = b'benign-test-data'
assert cipher.decrypt(cipher.encrypt(block)) == block
Image.new('RGB', (2, 3), 'blue').save('benign.png')
with Image.open('benign.png') as image:
 assert image.size == (2, 3)
with requests.Session() as session:
 session.trust_env = False
 reply = session.get('http://{target['address']}:8000/', timeout=(1, 1))
 assert reply.status_code == 200 and 'flag' in reply.json()
with remote({target['address']!r}, 8000, timeout=1) as connection:
 connection.send(b'GET / HTTP/1.0\\r\\n\\r\\n')
 assert b'HTTP/1.1 200 OK' in connection.recvall(timeout=1)
# This fixture waits for an HTTP request: reading first deliberately stalls.
started = time.monotonic()
with socket.create_connection(({target['address']!r}, 8000), timeout=.2) as connection:
 try:
  connection.recv(1)
  raise AssertionError('Expected an internal read timeout')
 except socket.timeout:
  pass
assert time.monotonic() - started < 2
print(json.dumps({{'packages': {{name: importlib.metadata.version(name) for name in
 ['pwntools', 'sympy', 'numpy', 'pycryptodome', 'requests', 'Pillow']}},
 'internal_read_timeout': True, 'elapsed_seconds': time.monotonic() - started}}))
'''))
    assert result["exit_code"] == 0 and not result["timed_out"], result
    assert json.loads(result["stdout"])["internal_read_timeout"]
    assert attempt["result"]["termination_reason"] is None


@pytest.mark.parametrize("attempt", [{"command_seconds": 120, "memory_mb": 1024}], indirect=True)
def test_runtime_pip_install_and_writable_home(attempt, tmp_path):
    from ctf_agent.challenge import stage_files

    wheel = tmp_path / 'ctf_image_probe-0.0.0-py3-none-any.whl'
    metadata = 'ctf_image_probe-0.0.0.dist-info/'
    files = {
        'ctf_image_probe.py': 'VALUE = 590\n',
        metadata + 'METADATA': 'Metadata-Version: 2.1\nName: ctf-image-probe\nVersion: 0.0.0\n',
        metadata + 'WHEEL': 'Wheel-Version: 1.0\nRoot-Is-Purelib: true\nTag: py3-none-any\n',
    }
    files[metadata + 'RECORD'] = ''.join(f'{name},,\n' for name in [*files, metadata + 'RECORD'])
    with zipfile.ZipFile(wheel, 'w') as archive:
        for name, content in files.items():
            archive.writestr(name, content)
    stage_files({wheel.name: wheel}, attempt['solver'], attempt['remaining_seconds']())
    probe = attempt["call_tool"]("run_command", python_command(
        "import os,pathlib,sys,importlib.util; "
        "assert sys.prefix!=sys.base_prefix and os.access(sys.prefix,os.W_OK); "
        "assert importlib.util.find_spec('ctf_image_probe') is None; home=pathlib.Path.home(); "
        "(home/'home-marker').write_text('writable'); "
        "(home/'space-probe').write_bytes(b'x'*(80*1024*1024)); (home/'space-probe').unlink()"))
    assert probe["exit_code"] == 0, probe
    result = attempt["call_tool"]("run_command", {
        "command": f"python -m pip install --quiet --no-index --no-deps {wheel.name} && "
                   "python -I -c 'import ctf_image_probe; print(ctf_image_probe.VALUE)'"})
    assert result["exit_code"] == 0 and not result["timed_out"], result
    assert result["stdout"].strip() == '590'
    assert 'ctf-image-probe' not in json.loads((attempt['directory'] / 'packages-initial.json').read_text())
    before = docker('inspect', '--format', '{{.State.StartedAt}}', attempt['solver'])
    result = attempt['call_tool']('run_command', {'command': 'sleep 10', 'timeout_seconds': .4})
    assert result['timed_out'] and result['solver_restarted'], result
    assert docker('inspect', '--format', '{{.State.StartedAt}}', attempt['solver']) != before
    assert attempt['call_tool']('run_command', python_command(
        "import ctf_image_probe,pathlib; assert (pathlib.Path.home()/'home-marker').exists(); "
        "print(ctf_image_probe.VALUE)"))['stdout'].strip() == '590'



@pytest.mark.parametrize("attempt", [{"max_output_bytes": 32_768}], indirect=True)
def test_larger_output_retains_observed_size_and_remains_bounded(attempt):
    result = attempt["call_tool"]("run_command", python_command(
        "import sys; print('x' * 17000); print('diagnostic-marker', file=sys.stderr); sys.exit(7)"))
    assert result["exit_code"] == 7 and not result["truncated"], result
    assert len(result["stdout"]) == 17_001 and "diagnostic-marker" in result["stderr"]
    result = attempt["call_tool"]("run_command", python_command("print('x' * 40000)"))
    assert result["truncated"] and result["output_bytes"] > 32_768
    assert len(result["stdout"].encode()) + len(result["stderr"].encode()) <= 32_768


def test_filesystem_credentials_privileges_output(attempt: dict, target: dict, settings):
    container = json.loads(docker("inspect", attempt["solver"]))[0]
    host = container["HostConfig"]
    assert not host["ReadonlyRootfs"] and host["CapDrop"] == ["ALL"]
    assert {cap.removeprefix("CAP_") for cap in host["CapAdd"]} == {"CHOWN"} and host["Init"]
    assert host["Memory"] == settings["memory_mb"] * 1024 * 1024
    assert host["MemorySwap"] == host["Memory"]
    assert host["PidsLimit"] == settings["pids"]
    assert host["NanoCpus"] == int(settings["cpus"] * 1_000_000_000)
    assert not host["Binds"] and not container["Mounts"]
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
    assert "CapBnd:\t0000000000000001" in info["status"]
    assert "NoNewPrivs:\t1" in info["status"]
    assert not info["docker_socket"] and not info["target_source"] and not info["challenge_json"]
    assert not {"FIXTURE_FLAG", "LITELLM_TOKEN", "LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY",
                "LANGFUSE_BASE_URL"} & info["env"].keys()
    assert target["expected_flag"] not in json.dumps(info)
    result = attempt["call_tool"]("run_command", {"command": "echo forbidden > /opt/controller-private"})
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
        "import subprocess,time,pathlib; child=subprocess.Popen(['sleep','30'], start_new_session=True); "
        "pathlib.Path('detached.pid').write_text(str(child.pid)); time.sleep(30)")
    result = attempt["call_tool"]("run_command", command | {"timeout_seconds": 0.4})
    assert result["timed_out"] and result["solver_restarted"]
    assert attempt["result"]["termination_reason"] is None
    proof = attempt["call_tool"]("run_command", python_command(
        "from pathlib import Path; pid=int(Path('detached.pid').read_text()); "
        "p=Path(f'/proc/{pid}/cmdline'); assert not p.exists() or b'sleep' not in p.read_bytes(); print('recovered')"))
    assert proof["exit_code"] == 0 and proof["stdout"].strip() == "recovered", proof
    running = docker("inspect", "--format", "{{.State.Running}}", attempt["solver"])
    assert running == "true"


@pytest.mark.parametrize("attempt", [{"max_tool_calls": 1}], indirect=True)
def test_tool_limit(attempt: dict):
    attempt["call_tool"]("run_command", {"command": "echo first"})
    with pytest.raises(RuntimeError):
        attempt["call_tool"]("run_command", {"command": "echo second"})
    assert attempt["result"]["termination_reason"] == "tool_limit" and attempt["result"]["tool_calls"] == 1


def test_command_timeout_closed_output(attempt: dict):
    result = attempt["call_tool"]("run_command", {
        "command": "exec >/dev/null 2>&1; sleep 30", "timeout_seconds": 0.4})
    assert result["timed_out"] and result["solver_restarted"]
    assert attempt["result"]["termination_reason"] is None
    assert attempt["call_tool"]("run_command", {"command": "echo recovered"})["stdout"].strip() == "recovered"


@pytest.mark.parametrize("attempt", [{"wall_seconds": 8, "command_seconds": 30}], indirect=True)
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


def test_solver_loss(attempt: dict):
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
    "unapproved_live_port", "internet_ip", "host_address",
    "external_dns", "unrelated_container", "curl_internet",
])
def test_network_scope(attempt, target, settings, destination, telemetry):
    if destination == "curl_internet":
        check_denial(attempt, "curl --noproxy '*' --connect-timeout 2 https://198.51.100.1/", telemetry)
        return
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
        with run_attempt(settings, target["network"], target["endpoints"],
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
        with run_attempt(invalid, target["network"], target["endpoints"],
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


def self_check(config_path: Path, output_root: Path) -> Path:
    suite_dir = output_root / ("self-check-" + uuid.uuid4().hex[:12])
    suite_dir.mkdir(parents=True, mode=0o700)
    suite = {"mode": "synthetic-controls", "time_utc": datetime.now(timezone.utc).isoformat(),
             "checks": [], "passed": False, "model_calls": 0, "cost_usd": 0.0}
    started = time.monotonic()
    try:
        suite["provenance"] = collect_provenance(load_settings(config_path))
        report_path = suite_dir / "pytest.xml"
        result = subprocess.run([
            sys.executable, "-m", "pytest", "tests", "-m", "docker", "-q", "-x",
            "--disable-plugin-autoload", "--ctf-config", str(config_path.resolve()),
            "--ctf-output", str(suite_dir.resolve()), "--junitxml", str(report_path.resolve()),
        ], check=False)
        if report_path.exists():
            for case in ET.parse(report_path).iter("testcase"):
                properties = {p.attrib["name"]: p.attrib["value"] for p in case.findall("properties/property")}
                suite["checks"].append({
                    "name": properties.get("check_name", case.attrib["name"]),
                    "run_id": properties.get("run_id"),
                    "passed": not any(case.find(tag) is not None for tag in ("error", "failure", "skipped")),
                })
        containers = docker("ps", "--all", "--filter", "label=ctf590.managed=true", "--format", "{{.Names}}")
        networks = docker("network", "ls", "--filter", "label=ctf590.managed=true", "--format", "{{.Name}}")
        suite["cleanup_verified"] = not containers and not networks
        suite["pytest_exit_code"] = result.returncode
        suite["passed"] = (result.returncode == 0 and bool(suite["checks"])
                           and all(check["passed"] for check in suite["checks"]) and suite["cleanup_verified"])
    except BaseException as error:
        suite["error"] = {"type": type(error).__name__, "message": str(error)[:2000]}
        raise
    finally:
        suite["total_seconds"] = round(time.monotonic() - started, 6)
        (suite_dir / "suite.json").write_text(json.dumps(suite, indent=2) + "\n")
        print(f"Evidence: {suite_dir}", flush=True)
    if not suite["passed"]:
        raise RuntimeError(f"Controls checks failed; see {suite_dir}")
    return suite_dir


def test_output_excerpt_and_late_diagnostic(attempt):
    result = attempt['call_tool']('run_command', python_command("print('start-'+'x'*1100000+'-end-diagnostic')"))
    assert result['truncated'] and result['stdout'].startswith('start-')
    assert result['stdout'].rstrip().endswith('-end-diagnostic')
    assert result['output_bytes'] == 1100022
    assert not {'output_file', 'recorded_output', 'session_id'} & result.keys()
    assert not (attempt['directory'] / 'outputs').exists()


def test_fresh_python_environment(attempt):
    result = attempt['call_tool']('run_command', python_command(
        "import pathlib,importlib.util; assert importlib.util.find_spec('ctf_image_probe') is None; "
        "assert not (pathlib.Path.home()/'home-marker').exists(); "
        "assert importlib.util.find_spec('sympy') is not None"))
    assert result['exit_code'] == 0, result


@pytest.mark.parametrize('attempt', [{'wall_seconds': 8}], indirect=True)
def test_attempt_deadline_stops_background_process(attempt):
    result = attempt['call_tool']('run_command', {
        'command': 'sleep 30 </dev/null >/dev/null 2>&1 & echo background-started'})
    assert result['exit_code'] == 0
    deadline = time.monotonic() + 9
    while attempt['result']['termination_reason'] is None:
        assert time.monotonic() < deadline
        time.sleep(.05)
    assert attempt['result']['termination_reason'] == 'wall_limit'
    while docker('inspect', '--format', '{{.State.Running}}', attempt['solver']) != 'false':
        assert time.monotonic() < deadline
        time.sleep(.05)


def test_standard_copy_preserves_handouts_and_ownership(attempt, tmp_path):
    import hashlib
    from ctf_agent.challenge import stage_files

    path = tmp_path / 'handout'
    path.write_bytes(b'#!/bin/sh\nprintf copied-handout')
    path.chmod(0o755)
    records = stage_files({'nested/handout': path}, attempt['solver'], attempt['remaining_seconds']())
    assert records[0]['sha256'] == hashlib.sha256(path.read_bytes()).hexdigest()
    result = attempt['call_tool']('run_command', python_command(
        "import pathlib,subprocess; p=pathlib.Path('nested/handout'); "
        "assert p.stat().st_uid==p.stat().st_gid==1000; "
        "assert p.stat().st_mode & 0o111; "
        "assert subprocess.check_output(['./nested/handout'])==b'copied-handout'; "
        "p.write_text('editable'); print('copied')"))
    assert result['exit_code'] == 0 and result['stdout'].strip() == 'copied', result


def test_restart_resets_all_processes_and_preserves_files(attempt, target, telemetry):
    from .fixtures.tracing import attribute

    attempt['call_tool']('write_file', {'path': 'kept', 'content': 'persistent'})
    result = attempt['call_tool']('run_command', python_command(
        "import subprocess; subprocess.Popen(['sleep','29'],stdin=subprocess.DEVNULL,"
        "stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)"))
    assert result['exit_code'] == 0
    target_started = docker('inspect', '--format', '{{.State.StartedAt}}', target['container'])
    before = attempt['result']['tool_calls']
    run_id = attempt['run_id']
    result = attempt['call_tool']('run_command', {'command': 'echo before-timeout; sleep 30', 'timeout_seconds': .4})
    assert result['timed_out'] and result['solver_restarted'] and result['process_state_reset']
    assert result['stdout'].strip() == 'before-timeout'
    assert attempt['run_id'] == run_id and attempt['result']['tool_calls'] == before + 1
    assert docker('inspect', '--format', '{{.State.StartedAt}}', target['container']) == target_started
    result = attempt['call_tool']('run_command', python_command(
        "import pathlib; assert pathlib.Path('kept').read_text()=='persistent'; "
        "assert not any(b'sleep\\x0029' in p.read_bytes() for p in pathlib.Path('/proc').glob('[0-9]*/cmdline') "
        "if p.exists()); print('recovered')"))
    assert result['exit_code'] == 0 and result['stdout'].strip() == 'recovered', result
    attempt['stop']('synthetic_complete')
    spans = read_spans(telemetry, attempt['result']['trace_id'])
    assert any(span.name == 'solver_restarted' for span in spans)
    tools = [span for span in spans if span.name == 'run_command']
    assert attribute(tools[-1], 'output') == result


def test_compose_dns_backend_scope_and_fresh_volume(settings, output_root, telemetry, record_property):
    from types import SimpleNamespace
    from ctf_agent.challenge import challenge_target

    record_property('check_name', 'compose_dns_backend_scope_and_fresh_volume')
    tmp_path = (output_root / ('compose-source-' + uuid.uuid4().hex[:12])).resolve()
    tmp_path.mkdir(parents=True)
    # Synthetic front end exercises the supplied private backend relationship.
    front = '''import http.server,json,pathlib,urllib.request
class Handler(http.server.BaseHTTPRequestHandler):
 def do_GET(self):
  with urllib.request.urlopen('http://backend:8000',timeout=1) as response:
   backend=json.load(response)
  marker=pathlib.Path('/state/visited')
  body=json.dumps({'backend':backend['flag'],'fresh':not marker.exists()}).encode()
  marker.write_text('visited')
  self.send_response(200); self.end_headers(); self.wfile.write(body)
http.server.HTTPServer(('0.0.0.0',8000),Handler).serve_forever()
'''
    expected = 'ctf{synthetic-backend-fixture}'
    supplied = {'services': {
        'frontend': {'image': settings['target_image'], 'user':'0:0', 'command':['python','-I','-c',front],
                     'depends_on':['backend'], 'networks':{'ctfnet':{'aliases':['challenge.test']},'backend':{}},
                     'volumes':[{'type':'volume','source':'state','target':'/state'}]},
        'backend': {'image':settings['target_image'],'environment':{'FIXTURE_FLAG':expected},'networks':{'backend':{}}}},
        'networks':{'ctfnet':{'external':True},'backend':{}}, 'volumes':{'state':{}}}
    (tmp_path/'docker-compose.yml').write_text(json.dumps(supplied))
    challenge = SimpleNamespace(container=True,challenge_dir=tmp_path,server_name='challenge.test',port=8000,challenge={})
    cycles=[]
    for cycle in (1,2):
        with challenge_target(challenge, output_root/f'compose-cycle-{uuid.uuid4().hex[:12]}') as target:
            assert len(target['containers'])==2 and len(target['volumes'])==1
            assert not target['adjustments']
            with run_attempt(settings,target['network'],target['endpoints'],expected,output_root,
                             langfuse=telemetry['client'],label='compose_standard_networks') as run:
                record_property('run_id',run['run_id'])
                source = '''import json,time,urllib.request
end=time.monotonic()+5
while True:
 try:
  with urllib.request.urlopen('http://challenge.test:8000',timeout=1) as response: print(response.read().decode())
  break
 except OSError:
  if time.monotonic()>end: raise
  time.sleep(.1)
'''
                returned=run['call_tool']('run_command',python_command(source))
                assert returned['exit_code']==0,returned
                observed=json.loads(returned['stdout'])
                assert observed=={'backend':expected,'fresh':True}
                returned=run['call_tool']('run_command',python_command(source))
                assert json.loads(returned['stdout'])['fresh'] is False
                guard=json.loads(docker('inspect',run['guard']))[0]
                assert list(guard['NetworkSettings']['Networks'])==[target['network']]
                info=json.loads(docker('inspect',target['containers']['backend']))[0]
                address=next(iter(info['NetworkSettings']['Networks'].values()))['IPAddress']
                check_denial(run,python_command(f"import socket; socket.create_connection(({address!r},8000),1)")['command'],telemetry)
            save_spans(telemetry,run['directory'],run['result']['trace_id'])
            cycles.append(target)
        assert not target['cleanup_errors']
    assert cycles[0]['volumes']!=cycles[1]['volumes']
    assert cycles[0]['network']!=cycles[1]['network']


@pytest.mark.parametrize('phase', ['startup', 'after_probes'])
def test_target_state_checks_detect_failed_dependency(settings, output_root, phase):
    from types import SimpleNamespace
    from ctf_agent.challenge import challenge_target, check_target_services

    source = output_root / ('dependency-source-' + uuid.uuid4().hex[:12])
    source.mkdir(parents=True)
    service = {'image': settings['target_image'], 'command': ['sleep', '300'], 'networks': {'ctfnet': {}}}
    database = dict(service)
    if phase == 'startup':
        database['healthcheck'] = {'test': ['CMD', 'false'], 'interval': '100ms', 'timeout': '1s', 'retries': 1}
    (source / 'docker-compose.yml').write_text(json.dumps({
        'services': {'frontend': service, 'database': database}, 'networks': {'ctfnet': {}}}))
    challenge = SimpleNamespace(container=True, challenge_dir=source, server_name='frontend', port=8000, challenge={})
    with pytest.raises(RuntimeError, match='database'):
        with challenge_target(challenge, source / 'runtime') as target:
            assert phase == 'after_probes'
            assert all(s['running'] for s in target['service_checks']['startup'].values())
            docker('kill', target['containers']['database'])
            check_target_services(target, 'after_probes')
    target = json.loads((source / 'runtime/target.json').read_text())
    states = target['service_checks']['startup_failed' if phase == 'startup' else 'after_probes']
    assert states['frontend']['running']
    assert states['database']['health'] == 'unhealthy' if phase == 'startup' else not states['database']['running']
    assert not target['cleanup_errors']


# Supplied toolkit capabilities and privilege boundary.
def test_supplied_sudo_cannot_elevate(attempt):
    assert attempt['call_tool']('run_command', {'command': 'command -v sudo'})['stdout'].strip()
    result = attempt['call_tool']('run_command', {'command': 'sudo -n id'})
    assert result['exit_code'] != 0 and 'uid=0' not in result['stdout'], result
    assert attempt['call_tool']('run_command', {'command': 'id -u'})['stdout'].strip() == '1000'


def test_sage_arithmetic_and_linear_algebra(attempt):
    result = attempt['call_tool']('run_command', {
        'command': 'sage -c "assert list(factor(360)) == [(2,3),(3,2),(5,1)]; '
                   'assert matrix(QQ,[[1,2],[3,4]]).det() == -2; print(\'sage-ok\')"'})
    assert result['exit_code'] == 0 and 'sage-ok' in result['stdout'], result


def test_multilib_compilation_and_execution(attempt):
    result = attempt['call_tool']('run_command', python_command('''
import pathlib, subprocess
pathlib.Path('benign32.c').write_text('int main(void){return 0;}')
subprocess.run(['gcc','-m32','-o','benign32','benign32.c'],check=True)
assert pathlib.Path('benign32').read_bytes()[:5]==b'\\x7fELF\\x01'
subprocess.run(['./benign32'],check=True)
print('multilib-ok')
'''))
    assert result['exit_code'] == 0 and result['stdout'].strip() == 'multilib-ok', result


def test_radare2_binary_analysis(attempt):
    result = attempt['call_tool']('run_command', python_command('''
import json, pathlib, subprocess
pathlib.Path('benign.c').write_text('int choose(int x){return x==7?42:0;} int main(void){return 0;}')
subprocess.run(['gcc','-O0','-o','benign','benign.c'],check=True)
output=subprocess.check_output(['radare2','-2','-q','-c','aaa;aflj','benign'],text=True)
functions=json.loads(output)
assert any(f['name']=='main' or f['name'].endswith('.main') for f in functions)
print(json.dumps({'function_count':len(functions),'main_found':True}))
'''))
    assert result['exit_code'] == 0, result
    assert json.loads(result['stdout'])['main_found']


def test_angr_symbolic_function(attempt):
    result = attempt['call_tool']('run_command', python_command('''
import angr, claripy, json, pathlib, subprocess
pathlib.Path('benign.c').write_text('int choose(int x){return x==7?42:0;} int main(void){return 0;}')
subprocess.run(['gcc','-O0','-fno-pie','-no-pie','-o','benign','benign.c'],check=True)
project=angr.Project('benign',auto_load_libs=False)
value=claripy.BVS('value',32)
state=project.factory.call_state(project.loader.find_symbol('choose').rebased_addr,value,
    ret_addr=0xdeadbeef,prototype='int choose(int)',
    add_options={angr.options.ZERO_FILL_UNCONSTRAINED_REGISTERS,
                 angr.options.ZERO_FILL_UNCONSTRAINED_MEMORY})
simulation=project.factory.simgr(state)
simulation.explore(find=lambda s: s.addr==0xdeadbeef and
    s.solver.satisfiable(extra_constraints=[s.regs.eax==42]))
assert simulation.found
found=simulation.found[0]; found.solver.add(found.regs.eax==42)
assert found.solver.eval(value)==7
print(json.dumps({'angr':angr.__version__,'symbolic_result':7}))
'''))
    assert result['exit_code'] == 0, result
    assert json.loads(result['stdout'])['symbolic_result'] == 7
