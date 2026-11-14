"""Verify a listener-only image update using synthetic children, never task code."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time
import uuid

from ctf_agent.docker import docker
from tests.check_listener_image import CHILD, CLIENT_IMAGE, IMAGES, check_case


IO_CHILD = """#!/bin/sh
ulimit -c 0
IFS= read -r mode
case "$mode" in
  echo) IFS= read -r line; printf 'reply:%s\\n' "$line" ;;
  stream) exec /bin/cat ;;
  idle) exec /bin/sleep 90 ;;
esac
"""
IO_CLIENT = """import json, socket, time
def connect():
    return socket.create_connection(('listener', 8000), 3)
def echo():
    with connect() as sock:
        sock.settimeout(3)
        sock.sendall(b'echo\\nsynthetic-input\\n')
        with sock.makefile('rb') as reader:
            assert reader.readline() == b'reply:synthetic-input\\n'
rows = []
for _ in range(20):
    echo()
rows.append({'check': 'normal_io', 'exchanges': 20, 'passed': True})
with connect() as sock:
    sock.settimeout(3)
    sock.sendall(b'stream\\nsynthetic-stream\\n')
    with sock.makefile('rb') as reader:
        assert reader.readline() == b'synthetic-stream\\n'
        sock.shutdown(socket.SHUT_WR)
        assert reader.read(1) == b''
echo()
rows.append({'check': 'peer_disconnect_and_reconnect', 'passed': True})
with connect() as sock:
    sock.settimeout(75)
    sock.sendall(b'idle\\n')
    started = time.monotonic()
    assert sock.recv(1) == b''
    elapsed = time.monotonic() - started
    assert 55 <= elapsed <= 70, elapsed
rows.append({'check': 'inactivity_timeout', 'seconds': elapsed, 'passed': True})
echo()
rows.append({'check': 'reconnect_after_timeout', 'passed': True})
print(json.dumps(rows))
"""


def check_io(image, user, network, source):
    name = "ctf590-listener-update-" + uuid.uuid4().hex[:10]
    client = name + "-client"
    try:
        docker("create", "--name", name, "--pull", "never", "--platform", "linux/amd64",
               "--network", network, "--network-alias", "listener", "--entrypoint", "socat",
               image, "-T60", "TCP-LISTEN:8000,reuseaddr,fork,su=" + user,
               "EXEC:/bin/sh /synthetic-child.sh")
        docker("cp", str(source.resolve()), name + ":/synthetic-child.sh")
        docker("start", name)
        time.sleep(0.3)
        docker("create", "--name", client, "--pull", "never", "--network", network,
               CLIENT_IMAGE, "python", "-I", "-c", IO_CLIENT)
        checks = json.loads(docker("start", "-a", client, timeout=95))
        time.sleep(1)
        state = json.loads(docker("inspect", name))[0]["State"]
        assert state["Running"] and not state["OOMKilled"]
        processes = docker("top", name, "-eo", "pid,ppid,comm").splitlines()
        # No per-connection child should remain after completed exchanges/timeouts.
        assert len(processes) == 2, processes
        return {"checks": checks, "listener_running": True, "processes": processes}
    finally:
        docker("rm", "-f", client, name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", choices=IMAGES, required=True)
    parser.add_argument("--output", type=Path, default=Path("runs/listener-update"))
    args = parser.parse_args()
    original, user = IMAGES[args.image]
    image = "ctf590-target-" + args.image + ":socat-1.7.3.3"
    directory = args.output / (args.image + "-" + uuid.uuid4().hex[:10])
    directory.mkdir(parents=True)
    source = directory / "synthetic-child.sh"
    network = "ctf590-listener-update-net-" + uuid.uuid4().hex[:10]
    report = {"kind": "fixed_listener_validation", "label": args.image,
              "original_image_id": original, "image_reference": image,
              "image_id": docker("image", "inspect", image, "--format", "{{.Id}}"),
              "model_calls": 0, "challenge_program_executed": False,
              "helper_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "reproduction_helper_sha256": hashlib.sha256(Path("tests/check_listener_image.py").read_bytes()).hexdigest(),
              "cases": []}
    try:
        docker("network", "create", "--internal", network)
        source.write_text(CHILD)
        source.chmod(0o644)
        for mode in ("normal", "signal"):
            row = check_case(image, user, network, source, mode, False, True, False, False)
            report["cases"].append(row)
            assert row["end"]["Running"] and len(row["connections"]) == 20
            assert all(x.get("connected") and x.get("eof") for x in row["connections"])
            print(args.image + ": " + mode + " survived 20/20", flush=True)
        source.write_text(IO_CHILD)
        report["io_timeout"] = check_io(image, user, network, source)
        report["passed"] = True
    except BaseException as error:
        report["error_type"] = type(error).__name__
        raise
    finally:
        cleanup = subprocess.run(["docker", "network", "rm", network], capture_output=True, text=True)
        report["network_cleanup"] = cleanup.returncode == 0 or "not found" in cleanup.stderr
        (directory / "check.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({"label": args.image, "passed": report.get("passed", False),
                          "network_cleanup": report["network_cleanup"],
                          "io_timeout": report.get("io_timeout")}), flush=True)
        print("Diagnostic records: " + str(directory), flush=True)


if __name__ == "__main__":
    main()
