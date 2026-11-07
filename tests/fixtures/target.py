"""Trusted lifecycle for a synthetic service; no real benchmark data is loaded."""

from contextlib import contextmanager
import json
import secrets
import subprocess
import time
import uuid

from ctf_agent.docker import docker


@contextmanager
def synthetic_target(settings: dict):
    name = "ctf590-fixture-" + uuid.uuid4().hex[:12]
    network = name + "-net"
    expected = "ctf{" + secrets.token_hex(12) + "}"
    try:
        docker("network", "create", "--label", "ctf590.managed=true", network)
        docker("run", "--detach", "--pull", "never", "--name", name,
               "--label", "ctf590.managed=true", "--network", network, "--dns", "127.0.0.1",
               "--cap-drop", "ALL", "--security-opt", "no-new-privileges=true", "--read-only",
               "--memory", "64m", "--memory-swap", "64m", "--pids-limit", "32", "--cpus", "0.25",
               "--env", f"FIXTURE_FLAG={expected}", settings["target_image"])
        address = docker("inspect", "--format", "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}", name)
        deadline = time.monotonic() + 10
        while True:
            try:
                docker("exec", name, "python", "-I", "-c",
                       "import socket; socket.create_connection(('127.0.0.1',8000),1).close(); "
                       "socket.create_connection(('127.0.0.1',8001),1).close()", timeout=2)
                break
            except (RuntimeError, subprocess.TimeoutExpired):
                if time.monotonic() >= deadline:
                    raise RuntimeError("Synthetic target did not become ready")
                time.sleep(0.1)
        yield {"network": network, "address": address,
               "expected_flag": expected, "container": name,
               "endpoints": [{"address": address, "protocol": "tcp", "port": 8000}]}
    finally:
        errors = []
        for arguments in [("rm", "--force", name), ("network", "rm", network)]:
            try:
                docker(*arguments)
            except RuntimeError as error:
                if "No such" not in str(error):
                    errors.append(str(error))
            except subprocess.TimeoutExpired as error:
                errors.append(str(error))
        if errors:
            raise RuntimeError("Synthetic target cleanup incomplete: " + "; ".join(errors))
