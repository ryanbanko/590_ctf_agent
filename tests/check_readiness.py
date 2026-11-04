"""Zero-model CTFTiny preparation check, using the real SDK with local transport."""

import json
from pathlib import Path
import shlex
import time
import uuid

from langfuse import Langfuse
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from ctf_agent.agent import AttemptStopped
from ctf_agent.attempt import run_attempt
from ctf_agent.challenge import challenge_target, contestant_files, load_challenge, public_task, stage_files
from ctf_agent.config import load_settings
from ctf_agent.docker import docker
from ctf_agent.launch import collect_provenance
from .fixtures.tracing import read_spans, save_spans


def run_python(run: dict, source: str) -> dict:
    returned = run["call_tool"]("run_command", {"command": "python -I -c " + shlex.quote(source)})
    if returned.get("exit_code") != 0:
        raise RuntimeError("Readiness solver probe failed; see tool observation")
    return json.loads(returned["stdout"])


def check_readiness(config_path: Path, dataset_json: Path, manifest_path: Path, output_root: Path,
                    challenge_id: str = "pwn-baby-boi"):
    manifest = json.loads(manifest_path.read_text())
    challenge = load_challenge(dataset_json, challenge_id, manifest_path)
    files = contestant_files(challenge)
    settings = load_settings(config_path)
    directory = output_root / ("ctftiny-readiness-" + uuid.uuid4().hex[:12])
    directory.mkdir(parents=True, mode=0o700)
    report = {"mode": "ctftiny-readiness", "challenge_id": challenge_id, "passed": False,
              "model_calls": 0, "cost_usd": 0.0, "cycles": [], "checks": {}}
    started = time.monotonic()
    exporter = InMemorySpanExporter()
    client = Langfuse(public_key="pk-lf-ctf590-readiness", secret_key="sk-lf-local-readiness",
                      tracer_provider=TracerProvider(), span_exporter=exporter)
    telemetry = {"client": client, "exporter": exporter}
    try:
        report["dataset"] = {"revision": manifest["revision"], "index_sha256": manifest["index_sha256"]}
        private_marker = directory / "host-only-marker"
        private_marker.write_text("trusted readiness storage\n")
        for cycle_number in (1, 2):
            cycle_dir = directory / f"cycle-{cycle_number}"
            with challenge_target(challenge, cycle_dir) as target:
                report["provenance"] = collect_provenance(settings, target_images=target["images"])
                task = public_task(challenge, files, target["endpoints"])
                (cycle_dir / "public-task.json").write_text(task + "\n")
                cycle = {"number": cycle_number, "target": target, "checks": {}}
                report["cycles"].append(cycle)
                with run_attempt(settings, target["network"], target["gateway"], target["endpoints"],
                                 challenge.flag, cycle_dir, langfuse=client, label=challenge_id,
                                 public_task=task, mode="ctftiny-readiness") as run:
                    records = stage_files(files, run["solver"], settings["workspace_mb"] * 1024 * 1024, 5)
                    cycle["files"] = records
                    observed = run_python(run,
                        "import hashlib,json,os,pathlib; root=pathlib.Path('/workspace'); "
                        "print(json.dumps({'files':{str(p.relative_to(root)):{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),"
                        "'uid':p.stat().st_uid,'gid':p.stat().st_gid} for p in root.rglob('*') if p.is_file()},"
                        "'uid':os.getuid(),'status':pathlib.Path('/proc/self/status').read_text(),"
                        "'credential_names':list(set(os.environ)&{'LITELLM_TOKEN','LANGFUSE_SECRET_KEY','LANGFUSE_PUBLIC_KEY','LANGFUSE_BASE_URL'}),"
                        "'docker_socket':pathlib.Path('/var/run/docker.sock').exists(),"
                        f"'host_marker':pathlib.Path({str(private_marker.resolve())!r}).exists()}}))")
                    expected_files = {row["path"]: {"sha256": row["sha256"], "uid": 1000, "gid": 1000}
                                      for row in records}
                    solver = json.loads(docker("inspect", run["solver"]))[0]
                    target_info = [json.loads(docker("inspect", container))[0] for container in target["containers"].values()]
                    network = json.loads(docker("network", "inspect", target["network"]))[0]
                    cycle["checks"].update(
                        exact_public_files=observed["files"] == expected_files,
                        nonroot_no_capabilities=(observed["uid"] == 1000 and "CapEff:\t0000000000000000" in observed["status"]),
                        private_boundary=not observed["credential_names"] and not observed["docker_socket"] and not observed["host_marker"],
                        solver_no_host_mounts=not solver["HostConfig"]["Binds"] and all(m["Type"] == "tmpfs" for m in solver["Mounts"]),
                        target_no_mounts_or_published_ports=all(not info["HostConfig"]["Binds"] and not info["HostConfig"]["PortBindings"]
                            and all(mount["Type"] == "tmpfs" for mount in info["Mounts"]) for info in target_info),
                        isolated_network=network["Internal"] and network["Options"].get("com.docker.network.bridge.gateway_mode_ipv4") == "isolated")
                    for endpoint in target["endpoints"]:
                        connection = run_python(run,
                            "import json,socket,time; deadline=time.monotonic()+7\n"
                            "while True:\n"
                            " try:\n"
                            f"  socket.create_connection(({endpoint['address']!r},{endpoint['port']}),1).close()\n"
                            "  print(json.dumps({'connected':True})); break\n"
                            " except OSError:\n"
                            "  if time.monotonic()>=deadline: raise\n"
                            "  time.sleep(.1)\n")
                        cycle["checks"]["target_responds"] = connection["connected"]
                    if cycle_number == 2:
                        try:
                            run["call_tool"]("run_command", {"command": "python -I -c " + shlex.quote(
                                "import socket; socket.create_connection(('198.51.100.1',443),2)")})
                        except AttemptStopped:
                            pass
                        cycle["checks"]["denial_stops_solver"] = (run["result"]["termination_reason"] == "scope_violation"
                            and docker("inspect", "--format", "{{.State.Running}}", run["solver"]) == "false")
                    else:
                        run["stop"]("readiness_complete")
                cycle["result"] = run["result"]
                spans = read_spans(telemetry, run["result"]["trace_id"])
                cycle["checks"]["expected_answer_absent"] = all(challenge.flag not in span.to_json() for span in spans)
                cycle["checks"]["zero_model_calls"] = run["result"]["model_calls"] == run["result"]["scripted_turns"] == 0
                cycle["checks"]["solver_cleanup"] = not run["result"]["cleanup_errors"]
                if cycle_number == 2:
                    cycle["checks"]["independent_denial_record"] = any(span.name == "network_denied" for span in spans)
            cycle["checks"]["target_cleanup"] = not target["cleanup_errors"]
        first, second = report["cycles"]
        report["checks"]["fresh_reset"] = ((not challenge.container or first["target"]["containers"] != second["target"]["containers"])
            and first["target"]["network"] != second["target"]["network"]
            and first["result"]["run_id"] != second["result"]["run_id"]
            and first["files"] == second["files"])
        report["checks"]["cleanup_verified"] = not docker(
            "ps", "--all", "--filter", "label=ctf590.managed=true", "--format", "{{.Names}}") and not docker(
            "network", "ls", "--filter", "label=ctf590.managed=true", "--format", "{{.Name}}")
        report["passed"] = all(report["checks"].values()) and all(
            all(cycle["checks"].values()) for cycle in report["cycles"])
    except BaseException as error:
        report["error_type"] = type(error).__name__
        raise
    finally:
        try:
            # Include failed setup attempts, even when the context never yielded.
            for summary_path in directory.glob("cycle-*/*/summary.json"):
                summary = json.loads(summary_path.read_text())
                save_spans(telemetry, summary_path.parent, summary["trace_id"])
        finally:
            client.shutdown()
            report["total_seconds"] = round(time.monotonic() - started, 6)
            (directory / "check.json").write_text(json.dumps(report, indent=2) + "\n")
            print(f"Evidence: {directory}", flush=True)
    if not report["passed"]:
        raise RuntimeError("CTFTiny readiness failed; see check.json")
    print("CTFTiny readiness verified; no model requests or challenge solving.")
    return directory
