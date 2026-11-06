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
mounts = [line for line in pathlib.Path('/proc/mounts').read_text().splitlines()
          if line.split()[1] in ['/workspace', '/tmp']]
workspace_options = next(line.split()[3].split(',') for line in mounts if line.split()[1] == '/workspace')
assert 'noexec' not in workspace_options
assert {{'nosuid', 'nodev'}} <= set(workspace_options)
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
print(json.dumps({{'utilities': tools, 'mounts': mounts, 'amd64_execution': True,
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


@pytest.mark.parametrize("attempt", [{"command_seconds": 120, "memory_mb": 1024, "workspace_mb": 512}], indirect=True)
def test_runtime_pip_install_and_writable_home(attempt):
    probe = attempt["call_tool"]("run_command", python_command(
        "import os,pathlib,sys,importlib.util; "
        "assert sys.prefix=='/workspace/.venv'; assert importlib.util.find_spec('humanfriendly') is None; "
        "home=pathlib.Path.home(); assert str(home)=='/workspace'; "
        "(home/'home-marker').write_text('writable'); "
        "assert os.environ['TMPDIR']=='/workspace'; "
        "(home/'space-probe').write_bytes(b'x'*(80*1024*1024)); (home/'space-probe').unlink()"))
    assert probe["exit_code"] == 0, probe
    result = attempt["call_tool"]("run_command", {
        "command": "python -m pip install --quiet --retries 0 --timeout 10 humanfriendly==10.0 && "
                   "python -c 'import humanfriendly; print(humanfriendly.format_size(1000))'"})
    assert result["exit_code"] == 0 and not result["timed_out"], result
    assert "1 KB" in result["stdout"]
    packages = json.loads((attempt["directory"] / "packages.json").read_text())
    assert packages["humanfriendly"] == "10.0"


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
        "import subprocess,time,pathlib; child=subprocess.Popen(['sleep','30'], start_new_session=True); "
        "pathlib.Path('detached.pid').write_text(str(child.pid)); time.sleep(30)")
    result = attempt["call_tool"]("run_command", command | {"timeout_seconds": 0.4})
    assert result["timed_out"] and result["cleanup_confirmed"]
    assert attempt["result"]["termination_reason"] is None
    proof = attempt["call_tool"]("run_command", python_command(
        "from pathlib import Path; pid=int(Path('detached.pid').read_text()); "
        "assert not Path(f'/proc/{pid}').exists(); print('recovered')"))
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
    assert result["timed_out"] and result["cleanup_confirmed"]
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


def test_interactive_terminal_and_independent_command(attempt):
    result = attempt['call_tool']('run_command', {
        'command': "python -u -c \"import os; assert os.isatty(0); print(input('Name? ')); print(input('Again? '))\"",
        'interactive': True})
    assert result['running'] and 'Name?' in result['stdout'], result
    session = result['session_id']
    result = attempt['call_tool']('run_command', {'session_id': session, 'input': 'first\n'})
    assert result['running'] and 'Again?' in result['stdout'], result
    assert attempt['call_tool']('run_command', {'command': 'echo independent'})['stdout'].strip() == 'independent'
    result = attempt['call_tool']('run_command', {'session_id': session, 'input': 'second\n'})
    assert not result['running'] and result['exit_code'] == 0 and 'second' in result['stdout'], result
    assert result['cleanup_confirmed']
    result = attempt['call_tool']('run_command', {'session_id': session})
    assert result['error']['kind'] == 'tool_error'
    result = attempt['call_tool']('run_command', {'command': 'sleep 30', 'interactive': True, 'wait_seconds': 0})
    result = attempt['call_tool']('run_command', {'session_id': result['session_id'], 'close': True})
    assert result['closed'] and not result['running'] and result['cleanup_confirmed'], result


def test_output_excerpt_file_and_late_diagnostic(attempt):
    result = attempt['call_tool']('run_command', python_command("print('start-'+'x'*100000+'-end-diagnostic')"))
    assert result['truncated'] and result['stdout'].startswith('start-')
    assert result['stdout'].rstrip().endswith('-end-diagnostic')
    captured = (attempt['directory'] / result['recorded_output']).read_text()
    assert captured.startswith('start-') and captured.rstrip().endswith('-end-diagnostic')
    assert not result['output_file_truncated'] and len(captured) == result['total_output_bytes']
    readback = attempt['call_tool']('run_command', {'command': 'tail -c 32 ' + result['output_file']})
    assert readback['exit_code'] == 0 and readback['stdout'].rstrip().endswith('-end-diagnostic')
    result = attempt['call_tool']('run_command', python_command("print('x'*1100000+'-last-line')"))
    assert result['output_file_truncated'] and result['stdout'].rstrip().endswith('-last-line')
    assert (attempt['directory'] / result['recorded_output']).stat().st_size == 1_048_576


def test_fresh_python_environment(attempt):
    result = attempt['call_tool']('run_command', python_command(
        "import pathlib,importlib.util; assert importlib.util.find_spec('humanfriendly') is None; "
        "assert not pathlib.Path('/workspace/home-marker').exists(); "
        "assert importlib.util.find_spec('sympy') is not None"))
    assert result['exit_code'] == 0, result


@pytest.mark.parametrize('attempt', [{'wall_seconds': 8}], indirect=True)
def test_attempt_deadline_stops_unpolled_session(attempt):
    result = attempt['call_tool']('run_command', {'command': 'sleep 30', 'interactive': True})
    assert result['running']
    deadline = time.monotonic() + 9
    while attempt['result']['termination_reason'] is None:
        assert time.monotonic() < deadline
        time.sleep(.05)
    assert attempt['result']['termination_reason'] == 'wall_limit'
    # Stop reason is set just before the bounded Docker kill finishes.
    while docker('inspect', '--format', '{{.State.Running}}', attempt['solver']) != 'false':
        assert time.monotonic() < deadline
        time.sleep(.05)


def test_finished_session_is_reaped_without_polling(attempt):
    result = attempt['call_tool']('run_command', {
        'command': 'sleep .3; printf finished', 'interactive': True, 'wait_seconds': 0})
    session = result['session_id']
    # A fixed in-solver probe observes process lifetime without polling the
    # command tool, which used to keep the finished supervisor alive.
    source = '''import pathlib,time
end=time.monotonic()+4
while True:
 children=[p for p in pathlib.Path('/proc').iterdir() if p.name.isdigit()
           and p.name not in ('1',str(__import__('os').getpid()))]
 supervisors=[]
 for p in children:
  try:
   fields=(p/'stat').read_text().rsplit(')',1)[1].split()
   if fields[1]=='1': supervisors.append(p.name)
  except FileNotFoundError: pass
 if not supervisors: break
 assert time.monotonic()<end, supervisors
 time.sleep(.05)
'''
    docker('exec', attempt['solver'], '/usr/local/bin/python', '-I', '-c', source, timeout=5)
    result = attempt['call_tool']('run_command', {'session_id': session})
    assert not result['running'] and result['stdout'] == 'finished' and result['cleanup_confirmed'], result


def test_terminal_partial_input_reports_progress(attempt):
    result = attempt['call_tool']('run_command', {
        'command': 'stty -icanon -echo; printf ready; sleep 30', 'interactive': True})
    session = result['session_id']
    for _ in range(4):
        result = attempt['call_tool']('run_command', {'session_id': session, 'input': 'x' * 16384})
        sent = result['input_bytes_sent']
        assert 0 <= sent <= 16384
        if result.get('input_error'):
            assert sent < 16384, result
            break
    else:
        pytest.fail('The non-reading terminal did not exercise partial input')
    result = attempt['call_tool']('run_command', {'session_id': session, 'close': True})
    assert result['cleanup_confirmed'] and not result['running']


def test_zero_wait_polls_preserve_final_output(attempt):
    result = attempt['call_tool']('run_command', {
        'command': "python -u -c \"print('begin-'+'x'*300000+'-final-marker',end='')\"",
        'interactive': True, 'wait_seconds': 0})
    output_file = result['recorded_output']
    session = result.get('session_id')
    for _ in range(8):
        if not result['running']:
            break
        result = attempt['call_tool']('run_command', {'session_id': session, 'wait_seconds': 0})
    assert not result['running'] and result['cleanup_confirmed'], result
    captured = (attempt['directory'] / output_file).read_text()
    assert captured == 'begin-' + 'x' * 300000 + '-final-marker'
    assert result['total_output_bytes'] == len(captured)


def test_supervisor_loss_stops_attempt(attempt):
    from ctf_agent.agent import AttemptStopped

    result = attempt['call_tool']('run_command', {'command': 'sleep 30', 'interactive': True})
    identifier = result['session_id']
    source = '''import json,os,pathlib,signal,sys
for path in pathlib.Path('/proc').iterdir():
 if not path.name.isdigit(): continue
 try: args=(path/'cmdline').read_bytes().split(b'\\0')
 except FileNotFoundError: continue
 if b'--session' in args and json.loads(args[-2])['output_id']==sys.argv[1]:
  os.kill(int(path.name),signal.SIGKILL); break
else: raise AssertionError('Supervisor missing before injection')
'''
    docker('exec', attempt['solver'], '/usr/local/bin/python', '-I', '-c', source, identifier)
    with pytest.raises(AttemptStopped, match='infrastructure_error'):
        attempt['call_tool']('run_command', {'session_id': identifier})
    assert docker('inspect', '--format', '{{.State.Running}}', attempt['solver']) == 'false'
