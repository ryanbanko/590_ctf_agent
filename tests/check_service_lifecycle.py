"""Explicit model-free development service diagnostic; no solving or submissions."""

import argparse
from collections import Counter
import json
from pathlib import Path
import shlex
import subprocess
import time
import uuid

from langfuse import Langfuse
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from ctf_agent.attempt import run_attempt
from ctf_agent.challenge import challenge_target, load_challenge, public_task
from ctf_agent.config import load_experiment
from ctf_agent.docker import docker
from tests.fixtures.tracing import read_spans


def snapshot(target):
    """Whitelist lifecycle state/process names; omit environment, argv and logs."""
    states = {}
    for name, container in target["containers"].items():
        info = json.loads(docker("inspect", container))[0]
        state = info["State"]
        row = {"status": state["Status"], "running": state["Running"],
               "restarting": state["Restarting"], "restart_count": info["RestartCount"],
               "exit_code": state["ExitCode"], "oom_killed": state["OOMKilled"],
               "health": state.get("Health", {}).get("Status"), "image": info["Image"]}
        if state["Running"]:
            names = docker("top", container, "-eo", "pid,comm").splitlines()[1:]
            row["process_names"] = dict(Counter(x.split(maxsplit=1)[1] for x in names))
        logs = subprocess.run(["docker", "logs", "--tail", "100", container],
                              capture_output=True, text=True, timeout=5)
        text = (logs.stdout + logs.stderr).lower()
        row["log_signatures"] = {word: text.count(word) for word in
            ["signal 11", "signal 6", "segmentation fault", "core dumped", "rosetta", "out of memory"]}
        states[name] = row
    return states


def probe_source(endpoint, action):
    # Fixed diagnostics authored here, never copied/evaluated from model traces.
    return f"""
import json,socket,time
result={{'action':{action!r},'connected':False,'received_bytes':0}}
started=time.monotonic()
try:
    with socket.create_connection(({endpoint['address']!r},{endpoint['port']}),2) as sock:
        result['connected']=True
        sock.settimeout(1)
        if {action!r} != 'connect_close':
            try:
                data=sock.recv(4096)
                result['received_bytes']+=len(data)
                result['initial_eof']=not data
            except socket.timeout:
                result['initial_read_timeout']=True
        if {action!r} == 'short_input':
            sock.sendall(b'hello\\n')
            try:
                data=sock.recv(4096)
                result['received_bytes']+=len(data)
                result['after_input_eof']=not data
            except socket.timeout:
                result['after_input_read_timeout']=True
except OSError as error:
    result['error_type']=type(error).__name__
    result['errno']=error.errno
result['seconds']=round(time.monotonic()-started,6)
print(json.dumps(result))
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--challenge", required=True, choices=["pwn-roppity", "pwn-baby-boi"])
    parser.add_argument("--output", type=Path, default=Path("runs/service-diagnostic"))
    args = parser.parse_args()
    manifest_path = Path("configs/ctftiny.json")
    manifest = json.loads(manifest_path.read_text())
    assert args.challenge in manifest["development"]
    challenge = load_challenge(Path("datasets/CTFTiny/ctftiny.json"), args.challenge, manifest_path)
    settings, _ = load_experiment()
    directory = args.output / (args.challenge + "-" + uuid.uuid4().hex[:12])
    directory.mkdir(parents=True, mode=0o700)
    report = {"challenge_id": args.challenge, "kind": "model_free_service_diagnostic",
              "model_calls": 0, "submissions": 0, "steps": []}
    exporter = InMemorySpanExporter()
    client = Langfuse(public_key="pk-lf-local-service-check", secret_key="sk-lf-local-service-check",
                      tracer_provider=TracerProvider(), span_exporter=exporter)
    try:
        with challenge_target(challenge, directory / "target") as target:
            report["target"] = target
            report["before"] = snapshot(target)
            task = public_task(challenge, {}, target["endpoints"])
            with run_attempt(settings, target["network"], target["endpoints"],
                             "unsubmitted-service-check-marker", directory, langfuse=client,
                             label=args.challenge, public_task=task,
                             mode="development-service-diagnostic") as run:
                report["solver"] = run["solver"]
                for action in ["connect_close", "read_close", "short_input"] * 3:
                    source = probe_source(target["endpoints"][0], action)
                    returned = run["call_tool"]("run_command", {
                        "command": "python -I -c " + shlex.quote(source), "timeout_seconds": 8})
                    step = {"number": len(report["steps"]) + 1, "action": action,
                            "exit_code": returned.get("exit_code"), "probe": json.loads(returned["stdout"])}
                    time.sleep(.3)
                    step["target"] = snapshot(target)
                    report["steps"].append(step)
                    print(json.dumps({"challenge": args.challenge, **step}), flush=True)
                    if any(not x["running"] for x in step["target"].values()):
                        break
                run["stop"]("service_diagnostic_complete")
            report["result"] = run["result"]
            report["observation_count"] = len(read_spans({"client": client, "exporter": exporter},
                                                        run["result"]["trace_id"]))
            report["after"] = snapshot(target)
    except BaseException as error:
        report["error_type"] = type(error).__name__
        raise
    finally:
        client.shutdown()
        (directory / "check.json").write_text(json.dumps(report, indent=2) + "\n")
        print("Diagnostic records:", directory, flush=True)


if __name__ == "__main__":
    main()
