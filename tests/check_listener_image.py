"""Model-free listener diagnostic: known development images, synthetic child only."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time
import uuid

from ctf_agent.docker import docker


IMAGES = {
    "roppity": ("sha256:e0fe9b2db871e1324ab71bc85d308783b6224fd62271d8ea4df3962aace4047c", "rop"),
    "baby-boi": ("sha256:e92afa986ce9c1fd01cdffb38cb46b8e66ffb802dab9382e912d33003144c665", "baby_boi"),
}
CLIENT_IMAGE = "python:3.13.2-slim-bookworm"
CHILD = """#!/bin/sh
ulimit -c 0
printf 'synthetic child pid=%s parent=%s\\n' "$$" "$PPID" >&2
case "$1" in
  normal) exit 0 ;;
  signal) kill -SEGV $$ ;;
  delayed) sleep 1; kill -SEGV $$ ;;
esac
"""
CLIENT = """import json, socket, time
rows = []
for i in range(20):
    row = {'connection': i + 1}
    try:
        with socket.create_connection(('listener', 8000), 2) as sock:
            row['connected'] = True
            sock.settimeout(3)
            row['eof'] = not sock.recv(1)
    except OSError as error:
        row.update(error=type(error).__name__, errno=error.errno)
    rows.append(row)
    if not row.get('connected'):
        break
    time.sleep(0.15)
print(json.dumps(rows))
"""


def check_case(image, user, network, source, mode, init, switch_user, debug, nofork_exec):
    name = "ctf590-listener-" + uuid.uuid4().hex[:10]
    client = name + "-client"
    row = {"child_mode": mode, "init": init, "switch_user": switch_user,
           "debug": debug, "nofork_exec": nofork_exec}
    listener = "TCP-LISTEN:8000,reuseaddr,fork" + (",su=" + user if switch_user else "")
    try:
        docker("create", "--name", name, "--pull", "never", "--platform", "linux/amd64",
               "--network", network, "--network-alias", "listener",
               *(["--init"] if init else []), "--entrypoint", "socat", image,
               *(["-d", "-d"] if debug else []),
               "-T60", listener, "EXEC:/bin/sh /synthetic-child.sh " + mode
               + (",nofork" if nofork_exec else ""))
        docker("cp", str(source.resolve()), name + ":/synthetic-child.sh")
        docker("start", name)
        time.sleep(0.3)
        docker("create", "--name", client, "--pull", "never", "--network", network,
               CLIENT_IMAGE, "python", "-I", "-c", CLIENT)
        row["connections"] = json.loads(docker("start", "-a", client, timeout=40))
        time.sleep(0.3)
        info = json.loads(docker("inspect", name))[0]
        row["end"] = {key: info["State"][key] for key in ("Status", "Running", "ExitCode", "OOMKilled")}
        if info["State"]["Running"]:
            row["processes"] = docker("top", name, "-eo", "pid,ppid,comm").splitlines()
        logs = subprocess.run(["docker", "logs", name], capture_output=True, text=True, timeout=5, check=True)
        row["synthetic_logs"] = (logs.stdout + logs.stderr).splitlines()
        return row
    finally:
        docker("rm", "-f", client, name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", choices=IMAGES, required=True)
    parser.add_argument("--mode", choices=["normal", "signal", "delayed"], default="signal")
    parser.add_argument("--init", action="store_true")
    parser.add_argument("--without-user-switch", action="store_true")
    parser.add_argument("--debug", action="store_true", help="Verbose logs from the synthetic service only")
    parser.add_argument("--nofork-exec", action="store_true", help="Test EXEC without the intermediate relay process")
    parser.add_argument("--output", type=Path, default=Path("runs/listener-image-diagnostic"))
    args = parser.parse_args()
    image, user = IMAGES[args.image]
    directory = args.output / (args.image + "-" + uuid.uuid4().hex[:10])
    directory.mkdir(parents=True)
    source = directory / "synthetic-child.sh"
    source.write_text(CHILD)
    source.chmod(0o644)
    network = "ctf590-listener-net-" + uuid.uuid4().hex[:10]
    report = {"kind": "known_listener_synthetic_child", "image_id": image,
              "label": args.image, "model_calls": 0, "challenge_program_executed": False,
              "helper_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    try:
        report["version"] = docker("run", "--rm", "--pull", "never", "--network", "none",
            "--platform", "linux/amd64", "--entrypoint", "socat", image, "-V").splitlines()[:3]
        report["client_image_id"] = docker("image", "inspect", CLIENT_IMAGE, "--format", "{{.Id}}")
        docker("network", "create", "--internal", network)
        report["case"] = check_case(image, user, network, source, args.mode,
                                    args.init, not args.without_user_switch, args.debug, args.nofork_exec)
    except BaseException as error:
        report["error_type"] = type(error).__name__
        raise
    finally:
        cleanup = subprocess.run(["docker", "network", "rm", network], capture_output=True, text=True)
        report["network_cleanup"] = cleanup.returncode == 0 or "not found" in cleanup.stderr
        (directory / "check.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2), flush=True)
        print("Diagnostic records: " + str(directory), flush=True)


if __name__ == "__main__":
    main()
