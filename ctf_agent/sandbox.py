"""Procedural lifecycle for the solver and its trusted network guard."""

import ipaddress
import json
import subprocess
import threading
import time

from .docker import bounded_exec, docker


def validate_endpoints(endpoints: list[dict]):
    for endpoint in endpoints:
        ipaddress.IPv4Address(endpoint["address"])
        if endpoint["protocol"] not in {"tcp", "udp"}:
            raise ValueError("Endpoint protocol must be tcp or udp")
        if type(endpoint["port"]) is not int or not 1 <= endpoint["port"] <= 65535:
            raise ValueError("Endpoint port must be an integer from 1 to 65535")


def make_sandbox(run_id: str, observation, stop):
    return {
        "solver": f"ctf590-{run_id}-solver", "guard": f"ctf590-{run_id}-guard",
        "observation": observation, "stop": stop, "ready": threading.Event(),
        "closing": threading.Event(), "monitor": None, "log_process": None,
    }


def monitor_guard(sandbox: dict):
    process = sandbox["log_process"]
    try:
        for line in process.stdout:
            if sandbox["closing"].is_set():
                break
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                sandbox["stop"]("guard_failure")
                return
            kind = event.pop("event", "guard_diagnostic")
            sandbox["observation"].create_event(name=kind, metadata=event)
            if kind == "guard_ready":
                sandbox["ready"].set()
            elif kind == "network_denied":
                sandbox["stop"]("scope_violation")
            elif kind == "guard_failed":
                sandbox["stop"]("guard_failure")
    except (OSError, ValueError):
        if not sandbox["closing"].is_set():
            sandbox["stop"]("guard_failure")
    finally:
        if not sandbox["closing"].is_set():
            sandbox["stop"]("guard_failure")


def start_sandbox(sandbox: dict, settings: dict, network: str, gateway: str,
                  endpoints: list[dict], remaining):
    validate_endpoints(endpoints)
    policy = json.dumps({"gateway": gateway, "endpoints": endpoints})
    docker(
        "run", "--detach", "--pull", "never", "--name", sandbox["guard"],
        "--label", "ctf590.managed=true", "--network", network,
        "--dns", "127.0.0.1", "--cap-drop", "ALL", "--cap-add", "NET_ADMIN",
        "--cap-add", "NET_RAW", "--cap-add", "SETUID", "--cap-add", "SETGID",
        "--security-opt", "no-new-privileges=true",
        "--read-only", "--tmpfs", "/tmp:rw,noexec,nosuid,nodev,size=8m",
        "--memory", "128m", "--memory-swap", "128m", "--pids-limit", "16",
        "--cpus", "0.25", "--log-opt", "max-size=1m", "--log-opt", "max-file=1",
        "--env", f"GUARD_POLICY={policy}", settings["guard_image"],
        timeout=min(15, remaining()),
    )
    process = subprocess.Popen(
        ["docker", "logs", "--follow", sandbox["guard"]],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        text=True, bufsize=1,
    )
    sandbox["log_process"] = process
    sandbox["monitor"] = threading.Thread(target=monitor_guard, args=(sandbox,), daemon=True)
    sandbox["monitor"].start()
    startup_deadline = time.monotonic() + min(10, remaining())
    while not sandbox["ready"].wait(0.05):
        remaining()
        if time.monotonic() >= startup_deadline:
            raise RuntimeError("Network guard did not become ready; solver was not started")
    remaining()
    memory = f'{settings["memory_mb"]}m'
    docker(
        "run", "--detach", "--pull", "never", "--platform", "linux/amd64", "--name", sandbox["solver"],
        "--label", "ctf590.managed=true", "--network", f'container:{sandbox["guard"]}',
        "--user", "1000:1000", "--cap-drop", "ALL",
        "--security-opt", "no-new-privileges=true", "--read-only",
        "--tmpfs", f'/workspace:rw,exec,nosuid,nodev,size={settings["workspace_mb"]}m,uid=1000,gid=1000,mode=700',
        "--tmpfs", "/tmp:rw,nosuid,nodev,size=16m,uid=1000,gid=1000,mode=700",
        "--memory", memory, "--memory-swap", memory,
        "--pids-limit", str(settings["pids"]), "--cpus", str(settings["cpus"]),
        "--log-opt", "max-size=1m", "--log-opt", "max-file=1", settings["solver_image"],
        timeout=min(15, remaining()),
    )
    remaining()
    sandbox["observation"].create_event(name="sandbox_ready", metadata={
        "solver": sandbox["solver"], "guard": sandbox["guard"], "endpoints": endpoints})


def stop_solver(sandbox: dict) -> bool:
    try:
        docker("kill", sandbox["solver"], timeout=3)
    except (RuntimeError, subprocess.TimeoutExpired) as error:
        # Repeated stopping and setup failure can leave no running solver.
        if isinstance(error, RuntimeError) and ("No such container" in str(error)
                                               or "is not running" in str(error)):
            return True
        sandbox["observation"].create_event(name="solver_stop_failed", level="ERROR",
            metadata={"exception": type(error).__name__, "message": str(error)[:2000]})
        return False
    return True


def audit_network(sandbox: dict, timeout: float):
    raw = docker("exec", sandbox["guard"], "nft", "-j", "list", "counter", "inet", "ctf", "denied",
                 timeout=min(3, timeout))
    counters = json.loads(raw)["nftables"]
    denied = sum(item.get("counter", {}).get("packets", 0) for item in counters)
    if denied:
        sandbox["observation"].create_event(name="network_denial_counter", metadata={"packets": denied})
        sandbox["stop"]("scope_violation")


def invoke_worker(sandbox: dict, request: dict, timeout: float):
    raw = bounded_exec(
        ["exec", "--interactive", "--user", "1000:1000", "--workdir", "/workspace",
         sandbox["solver"], "python", "-I", "/opt/ctf/worker.py"],
        json.dumps(request).encode(), timeout,
    )
    result = json.loads(raw)
    if not isinstance(result, dict):
        raise RuntimeError("Sandbox worker returned an invalid result")
    return result


def close_sandbox(sandbox: dict) -> list[str]:
    """Remove only resources belonging to this attempt, preserving guard output."""
    errors = []
    for name in (sandbox["solver"], sandbox["guard"]):
        try:
            docker("rm", "--force", name, timeout=5)
        except RuntimeError as error:
            if "No such container" not in str(error):
                errors.append(f"{name}: {error}")
        except subprocess.TimeoutExpired:
            errors.append(f"Timed out removing {name}")
    sandbox["closing"].set()
    process = sandbox["log_process"]
    if process is not None:
        if process.poll() is None:
            process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=2)
        # The monitor can still be completing a bounded three-second solver kill.
        sandbox["monitor"].join(timeout=4)
        process.stdout.close()
    sandbox["observation"].create_event(name="sandbox_cleanup", metadata={"errors": errors})
    return errors
