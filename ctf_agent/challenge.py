"""Trusted nyuctf loading and contestant-file staging; no model or target shell."""

from contextlib import contextmanager
from copy import deepcopy
import hashlib
import json
from pathlib import Path, PurePosixPath
import shlex
import subprocess
import time
import uuid

from .docker import docker


# MongoDB 7.0.9-jammy siblings in the same official release index. The supplied
# AMD64 build requires AVX unavailable under this project's ARM Docker emulation.
MONGO_AMD64_IMAGE = "mongo:latest@sha256:7b88befc893008d7139ce3276c093b3efd435023af8bb76a9d79fa90be1eaeb6"
MONGO_ARM64_IMAGE = "mongo@sha256:8ff69162926750978451697274dc3c93eac609894b9cff7ed977e76e6bcabcbe"


def load_challenge(dataset_json: Path, challenge_id: str, manifest_path: Path):
    """Load an indexed challenge through nyuctf; its package object stays trusted."""
    manifest = json.loads(manifest_path.read_text())
    if challenge_id not in manifest["development"] + manifest["scored"]:
        raise ValueError("Choose a challenge ID from the recorded dataset index")
    if not manifest["revision"]:
        raise ValueError("Pin the dataset checkout revision before loading a challenge")
    root = dataset_json.resolve().parent
    revision = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                              capture_output=True, text=True, check=True).stdout.strip()
    index = json.loads(dataset_json.read_text())
    digest = hashlib.sha256(json.dumps(index, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if revision != manifest["revision"] or digest != manifest["index_sha256"]:
        raise ValueError("Dataset revision or index differs from the recorded selection")
    changed = subprocess.run(["git", "-C", str(root), "status", "--porcelain"],
                             capture_output=True, text=True, check=True).stdout
    if changed:
        raise ValueError("Dataset checkout must be clean")
    if (len(manifest["scored"]) != 10 or set(manifest["scored"]) & set(manifest["development"])
            or set(manifest["scored"]) | set(manifest["development"]) != set(index)):
        raise ValueError("Expected ten scored challenges and a disjoint development remainder")
    # Import only for real loading; pure file/public-data checks need no package.
    from nyuctf.challenge import CTFChallenge
    from nyuctf.dataset import CTFDataset

    dataset = CTFDataset(dataset_json=dataset_json)
    if not (dataset.basedir / dataset.get(challenge_id)["path"] / "challenge.json").is_file():
        raise ValueError(
            f"Challenge {challenge_id!r} is not downloaded. Complete the full dataset setup in README.md. "
            f"For an existing sparse checkout, run: git -C {shlex.quote(str(root))} sparse-checkout disable")
    return CTFChallenge(dataset.get(challenge_id), dataset.basedir)


def contestant_files(challenge) -> dict[str, Path]:
    """Resolve only listed regular contestant files, without following symlinks."""
    root = challenge.challenge_dir.resolve()
    files = {}
    for name in challenge.files:
        path = PurePosixPath(name)
        if (not path.parts or path.is_absolute() or ".." in path.parts or "\x00" in name
                or path.name in {"challenge.json", "docker-compose.yml", "docker-compose.yaml"}):
            raise ValueError("Invalid contestant-file path")
        source = root
        for part in path.parts:
            source = source / part
            if source.is_symlink():
                raise ValueError("Contestant files must not use symlinks")
        # Course controls retain target build files even when listed as handouts.
        if path.name == "Dockerfile":
            continue
        if not source.is_file() or str(path) in files:
            raise ValueError("Contestant files must be unique regular files")
        files[str(path)] = source
    return files


def public_task(challenge, files: dict[str, Path], endpoints: list[dict]) -> str:
    """Whitelist public fields; never serialize the package's private metadata."""
    description = challenge.description
    if any(str(PurePosixPath(name)) not in files for name in challenge.files):
        description += "\nTarget build files are retained by the trusted controller, outside the solver."
    task = {"name": challenge.name, "category": challenge.category,
            "description": description, "files": list(files), "endpoints": endpoints}
    return json.dumps(task, ensure_ascii=True)


def stage_files(files: dict[str, Path], solver: str, timeout: float) -> list[dict]:
    """Copy only validated handouts before agent execution, using ordinary Docker."""
    deadline = time.monotonic() + timeout
    records = []

    def remaining():
        seconds = deadline - time.monotonic()
        if seconds <= 0:
            raise TimeoutError("Contestant-file staging exceeded the remaining attempt time")
        return seconds

    for name, source in files.items():
        destination = "/workspace/" + name
        docker("exec", "--user", "1000:1000", solver, "mkdir", "-p", "--",
               str(PurePosixPath(destination).parent), timeout=remaining())
        docker("cp", str(source.resolve()), f"{solver}:{destination}", timeout=remaining())
        # Docker cp normally creates root-owned files. This is trusted setup,
        # before any model action, not a root execution tool.
        docker("exec", "--user", "0:0", solver, "chown", "1000:1000", "--", destination,
               timeout=remaining())
        with source.open("rb") as handle:
            digest = hashlib.file_digest(handle, "sha256").hexdigest()
        remaining()
        records.append({"path": name, "bytes": source.stat().st_size, "sha256": digest})
    return records


def target_compose(supplied: dict, root: Path, *, architecture: str = "") -> tuple[dict, list]:
    """Preserve supplied services; scope resources and exclude host administration."""
    runtime = deepcopy(supplied)
    adjustments = []
    runtime.pop("name", None)
    for name, service in runtime["services"].items():
        if architecture in {"arm64", "aarch64"} and service["image"] == MONGO_AMD64_IMAGE:
            service.update(image=MONGO_ARM64_IMAGE, platform="linux/arm64")
            adjustments.append({"service": name, "original_image": MONGO_AMD64_IMAGE,
                                "replacement_image": MONGO_ARM64_IMAGE, "platform": "linux/arm64",
                                "version": "7.0.9", "reason": "same-release native MongoDB; AMD64 build needs AVX"})
        if (service.get("privileged") or service.get("network_mode") == "host" or service.get("devices")
                or service.get("use_api_socket")
                or any(service.get(key) == "host" for key in ("pid", "ipc", "uts", "userns_mode"))):
            raise ValueError(f"Service {name}: host-administrative access needs a separately isolated engine")
        if service.get("network_mode") or service.get("volumes_from"):
            raise ValueError(f"Service {name}: shared target namespaces/storage need explicit review")
        for key in ("ports", "build", "container_name"):
            if key in service:
                service.pop(key)
                adjustments.append({"service": name, "removed": key})
        mounts = []
        for mount in service.get("volumes", []):
            if (PurePosixPath(mount.get("source", "")).name == "docker.sock"
                    or mount["target"] == "/var/run/docker.sock"):
                adjustments.append({"service": name, "removed": "docker_socket", "reason": "shared trusted daemon"})
                continue
            if mount.get("type") == "bind":
                source = Path(mount["source"]).resolve()
                if not mount.get("read_only") or not source.is_relative_to(root.resolve()):
                    raise ValueError("Target binds must be read-only challenge files; writable binds need a fresh-state strategy")
            mounts.append(mount)
        if "volumes" in service:
            service["volumes"] = mounts
        service.setdefault("labels", {})["ctf590.managed"] = "true"
    for section in ("configs", "secrets"):
        for item in runtime.get(section, {}).values():
            if item.get("external") or not Path(item.get("file", "")).resolve().is_relative_to(root.resolve()):
                raise ValueError("Target config/secret files must come from the challenge directory")
    for section in ("networks", "volumes"):
        for item in runtime.get(section, {}).values():
            if section == "volumes" and (item.get("external") or item.get("driver_opts")):
                raise ValueError("External/custom target storage needs an explicit fresh-state strategy")
            if section == "networks" and item.get("driver", "bridge") != "bridge":
                raise ValueError("Target networking must use ordinary project-local bridges")
            # The supplied global ctfnet becomes a fresh Compose-owned network.
            item.pop("external", None)
            item.pop("name", None)
            item.setdefault("labels", {})["ctf590.managed"] = "true"
    return runtime, adjustments


def snapshot_target_services(target: dict, phase: str, *, best_effort: bool = False) -> dict:
    """Whitelist service state; final diagnostics share a three-second allowance."""
    states = {}
    target.setdefault("service_checks", {})[phase] = states
    deadline = time.monotonic() + 3 if best_effort else None
    for name, container in target["containers"].items():
        try:
            timeout = deadline - time.monotonic() if deadline is not None else 15
            if timeout <= 0:
                raise TimeoutError("Target diagnostic allowance exhausted")
            info = json.loads(docker("inspect", container, timeout=timeout))[0]
            state = info["State"]
            states[name] = {"status": state["Status"], "running": state["Running"],
                           "restarting": state["Restarting"], "restart_count": info["RestartCount"],
                           "exit_code": state["ExitCode"], "oom_killed": state["OOMKilled"],
                           "health": state.get("Health", {}).get("Status"),
                           "networks": {network: {"address": details.get("IPAddress"),
                                                  "network_id": details.get("NetworkID")}
                                        for network, details in info.get("NetworkSettings", {}).get("Networks", {}).items()}}
        except Exception as error:
            if not best_effort:
                raise
            missing = isinstance(error, RuntimeError) and any(
                marker in str(error) for marker in ("No such container", "No such object"))
            states[name] = {"status": "missing" if missing else "unavailable",
                            "error_type": type(error).__name__}
    return states


def check_target_services(target: dict, phase: str) -> None:
    """Record safe dependency state and reject failures, not just a closed port."""
    states = snapshot_target_services(target, phase)
    failed = [name for name, state in states.items() if not state["running"]
              or state["restarting"] or state["oom_killed"] or state["health"] not in {None, "healthy"}]
    if failed:
        raise RuntimeError(f"Target services not ready ({phase}): {', '.join(failed)}; see target.json service_checks")


@contextmanager
def challenge_target(challenge, directory: Path):
    """Use supplied Compose semantics with fresh project-owned networks/storage."""
    name = "ctf590-target-" + uuid.uuid4().hex[:12]
    directory.mkdir(parents=True, exist_ok=True)
    compose_path = directory / "compose.json"
    compose = ("compose", "--project-name", name, "-f", str(compose_path.resolve()))
    target = {"project": name, "network": None, "container": None, "containers": {},
              "images": {}, "volumes": [], "endpoints": [], "adjustments": [], "cleanup_errors": []}
    runtime = None
    try:
        if challenge.container:
            supplied_path = next((challenge.challenge_dir / filename for filename in
                                  ("docker-compose.yml", "docker-compose.yaml")
                                  if (challenge.challenge_dir / filename).is_file()), None)
            if supplied_path is None:
                raise ValueError("Service-backed challenge is missing its Compose file")
            supplied = json.loads(docker("compose", "-f", str(supplied_path), "config", "--format", "json"))
            runtime, target["adjustments"] = target_compose(
                supplied, challenge.challenge_dir, architecture=docker("info", "--format", "{{.Architecture}}"))
            for service_name, service in runtime["services"].items():
                reference = service["image"]
                try:
                    info = json.loads(docker("image", "inspect", reference))[0]
                except RuntimeError as error:
                    if "No such image" not in str(error):
                        raise
                    docker("pull", "--platform", service.get("platform", "linux/amd64"), reference, timeout=300)
                    info = json.loads(docker("image", "inspect", reference))[0]
                service["image"] = info["Id"]
                service["platform"] = "linux/" + info["Architecture"]
                target["images"][service_name] = info["Id"]
            compose_path.write_text(json.dumps(runtime, indent=2) + "\n")
            try:
                docker(*compose, "up", "--wait", "--wait-timeout", "20", "--force-recreate",
                       "--no-build", "--pull", "never", timeout=30)
            except (RuntimeError, subprocess.TimeoutExpired):
                # Capture dependency failures before Compose cleanup removes them.
                for service_name in runtime["services"]:
                    container = docker(*compose, "ps", "--all", "--quiet", service_name)
                    if container:
                        target["containers"][service_name] = container
                check_target_services(target, "startup_failed")
                raise
            for service_name, service in runtime["services"].items():
                container = docker(*compose, "ps", "--all", "--quiet", service_name)
                target["containers"][service_name] = container
                info = json.loads(docker("inspect", container))[0]
                target["volumes"].extend(m["Name"] for m in info["Mounts"] if m["Type"] == "volume")
                for key, network in service.get("networks", {"default": {}}).items():
                    aliases = (network or {}).get("aliases", [])
                    if challenge.server_name in [service_name, *aliases]:
                        actual = name + "_" + key
                        address = info["NetworkSettings"]["Networks"][actual]["IPAddress"]
                        target.update(network=actual, address=address, container=container, image_id=info["Image"],
                            endpoints=[{"address": address, "protocol": "udp" if challenge.challenge.get("proto") == "udp" else "tcp",
                                        "port": int(challenge.port or challenge.challenge.get("port"))}])
                        break
            if not target["endpoints"]:
                raise ValueError("No Compose service matches the challenge connection metadata")
            check_target_services(target, "startup")
        else:
            target["network"] = name + "-net"
            docker("network", "create", "--label", "ctf590.managed=true", target["network"])
        yield target
    finally:
        try:
            snapshot_target_services(target, "before_cleanup", best_effort=True)
        except Exception as error:
            target["diagnostic_error"] = {"phase": "before_cleanup", "error_type": type(error).__name__}
        finally:
            try:
                if compose_path.exists():
                    docker(*compose, "down", "--volumes", "--remove-orphans", "--timeout", "2", timeout=15)
                    for volume in target["volumes"]:
                        if docker("volume", "ls", "--filter", f"name=^{volume}$", "--format", "{{.Name}}"):
                            target["cleanup_errors"].append("Target volume removal failed")
                elif target["network"]:
                    docker("network", "rm", target["network"], timeout=5)
            except (RuntimeError, subprocess.TimeoutExpired) as error:
                target["cleanup_errors"].append(type(error).__name__ + ": target cleanup failed")
            (directory / "target.json").write_text(json.dumps(target, indent=2) + "\n")
            if target["cleanup_errors"]:
                raise RuntimeError("Target cleanup incomplete; see target.json")
