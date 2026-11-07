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
        "closing": threading.Event(), "stopping": threading.Event(),
        "lifecycle": threading.RLock(), "restarts": 0, "monitor": None, "log_process": None,
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


def start_sandbox(sandbox: dict, settings: dict, network: str,
                  endpoints: list[dict], remaining):
    validate_endpoints(endpoints)
    policy = json.dumps({"endpoints": endpoints})
    docker(
        "run", "--detach", "--pull", "never", "--name", sandbox["guard"],
        "--label", "ctf590.managed=true", "--network", network,
        "--cap-drop", "ALL", "--cap-add", "NET_ADMIN",
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
    sandbox["remaining"] = remaining
    with sandbox["lifecycle"]:
        remaining()
        docker(
            "run", "--detach", "--init", "--pull", "never", "--platform", "linux/amd64", "--name", sandbox["solver"],
            "--label", "ctf590.managed=true", "--network", f'container:{sandbox["guard"]}',
            "--user", "1000:1000", "--workdir", "/workspace", "--cap-drop", "ALL", "--cap-add", "CHOWN",
            "--security-opt", "no-new-privileges=true",
            "--memory", memory, "--memory-swap", memory,
            "--pids-limit", str(settings["pids"]), "--cpus", str(settings["cpus"]),
            "--log-opt", "max-size=1m", "--log-opt", "max-file=1",
            "--entrypoint", "/bin/sleep", settings["solver_image"], "infinity",
            timeout=min(15, remaining()),
        )
        remaining()
    snapshot_packages(sandbox, 'initial', min(5, remaining()))
    remaining()
    sandbox["observation"].create_event(name="sandbox_ready", metadata={
        "solver": sandbox["solver"], "guard": sandbox["guard"], "endpoints": endpoints})


def stop_solver(sandbox: dict) -> bool:
    # Set before waiting: a concurrent recovery cannot hide a terminal stop.
    sandbox["stopping"].set()
    with sandbox["lifecycle"]:
        try:
            docker("kill", sandbox["solver"], timeout=3)
        except (RuntimeError, subprocess.TimeoutExpired) as error:
            if isinstance(error, RuntimeError) and ("No such container" in str(error)
                                                   or "is not running" in str(error)):
                return True
            sandbox["observation"].create_event(name="solver_stop_failed", level="ERROR",
                metadata={"exception": type(error).__name__, "message": str(error)[:2000]})
            return False
    return True


def restart_solver(sandbox: dict):
    """Reset all solver processes; terminal stop always takes precedence."""
    with sandbox["lifecycle"]:
        remaining = sandbox["remaining"]
        remaining()
        if sandbox["stopping"].is_set():
            raise RuntimeError("Solver is stopping; recovery refused")
        audit_network(sandbox, remaining())
        remaining()
        sandbox["observation"].create_event(name="solver_restarting", metadata={"reason": "command_timeout"})
        docker("restart", "--signal", "SIGKILL", sandbox["solver"], timeout=min(5, remaining()))
        remaining()
        if sandbox["stopping"].is_set():
            raise RuntimeError("Solver stopped during recovery")
        if docker("inspect", "--format", "{{.State.Running}}", sandbox["solver"],
                  timeout=min(3, remaining())) != "true":
            raise RuntimeError("Solver did not recover")
        audit_network(sandbox, remaining())
        remaining()
        sandbox["restarts"] += 1
        sandbox["observation"].create_event(name="solver_restarted", metadata={"restart": sandbox["restarts"]})


def snapshot_packages(sandbox: dict, phase: str, timeout: float):
    """Best-effort, bounded image/final inventory; no per-tool scans or RPC."""
    try:
        result = bounded_exec(["exec", sandbox["solver"], "python", "-I", "-c",
            "import importlib.metadata as m,json; print(json.dumps({d.metadata['Name']:d.version for d in m.distributions()}))"],
            b"", timeout, 65_536)
        if result["timed_out"] or result["truncated"] or result["exit_code"] != 0:
            raise RuntimeError("Package inventory unavailable or incomplete")
        packages = json.loads(result["stdout"])
        (sandbox["directory"] / f"packages-{phase}.json").write_text(json.dumps(packages, indent=2) + "\n")
        sandbox["observation"].create_event(name="package_inventory", metadata={"phase": phase, "available": True})
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as error:
        sandbox["observation"].create_event(name="package_inventory", metadata={
            "phase": phase, "available": False, "exception": type(error).__name__})


def audit_network(sandbox: dict, timeout: float):
    raw = docker("exec", sandbox["guard"], "nft", "-j", "list", "counter", "inet", "ctf", "denied",
                 timeout=min(3, timeout))
    counters = json.loads(raw)["nftables"]
    denied = sum(item.get("counter", {}).get("packets", 0) for item in counters)
    if denied:
        sandbox["observation"].create_event(name="network_denial_counter", metadata={"packets": denied})
        sandbox["stop"]("scope_violation")


def close_sandbox(sandbox: dict) -> list[str]:
    """Remove only resources belonging to this attempt, preserving guard output."""
    sandbox["stopping"].set()
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
