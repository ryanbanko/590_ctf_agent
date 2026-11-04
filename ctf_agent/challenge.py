"""Trusted nyuctf loading and contestant-file staging; no model or target shell."""

from contextlib import contextmanager
import hashlib
import ipaddress
import io
import json
from pathlib import Path, PurePosixPath
import shlex
import subprocess
import tarfile
import uuid

from .docker import bounded_exec, docker


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
    if endpoints and getattr(challenge, "server_name", None):
        description = description.replace(challenge.server_name, endpoints[0]["address"])
    task = {"name": challenge.name, "category": challenge.category,
            "description": description, "files": list(files), "endpoints": endpoints}
    return json.dumps(task, ensure_ascii=True)


def stage_files(files: dict[str, Path], solver: str, workspace_bytes: int, timeout: float) -> list[dict]:
    """Stream a validated tar to Python in the solver as its unprivileged user.

    Run once before model/tool execution. No host directory is mounted, and no
    additional model tool is exposed. Return names/sizes/hashes, never contents.
    """
    total = sum(path.stat().st_size for path in files.values())
    if total > workspace_bytes:
        raise ValueError("Contestant files exceed the solver workspace limit")
    records = []
    directories = set()
    with io.BytesIO() as data:
        with tarfile.open(fileobj=data, mode="w") as archive:
            for name, source in files.items():
                for parent in reversed(PurePosixPath(name).parents):
                    if str(parent) != "." and str(parent) not in directories:
                        entry = tarfile.TarInfo(str(parent))
                        entry.type, entry.mode = tarfile.DIRTYPE, 0o700
                        entry.uid = entry.gid = 1000
                        archive.addfile(entry)
                        directories.add(str(parent))
                content = source.read_bytes()
                entry = tarfile.TarInfo(name)
                entry.size, entry.mode = len(content), 0o700 if source.stat().st_mode & 0o111 else 0o600
                entry.uid = entry.gid = 1000
                archive.addfile(entry, io.BytesIO(content))
                records.append({"path": name, "bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()})
        if records:
            # Docker cp refuses a read-only container root even for writable tmpfs.
            # Python's standard data filter also rejects archive traversal/links.
            extract = ("import sys,tarfile; "
                       "tarfile.open(fileobj=sys.stdin.buffer,mode='r|').extractall(path='.',filter='data')")
            bounded_exec(["exec", "--interactive", "--user", "1000:1000", "--workdir", "/workspace",
                          solver, "python", "-I", "-c", extract], data.getvalue(), timeout)
    return records


def target_compose(supplied: dict, network: str) -> dict:
    """Keep supplied image services/aliases, removing host ports and socket mounts."""
    services = {}
    for name, original in supplied["services"].items():
        if original.get("privileged"):
            raise ValueError("Privileged target setup is unsupported under the current isolation controls")
        if (original.keys() - {"image", "networks", "ports", "volumes", "command", "entrypoint", "environment",
                               "depends_on", "expose", "platform", "user", "working_dir", "hostname", "healthcheck",
                               "build", "privileged", "restart"}
                or not original.get("image")
                or any(mount.get("target") != "/var/run/docker.sock" for mount in original.get("volumes", []))):
            raise ValueError("Unsupported target arrangement; review its Compose setup")
        service = {key: value for key, value in original.items()
                   if key not in {"ports", "volumes", "build", "privileged", "restart"}}
        service.setdefault("networks", {"ctfnet": {}})
        service.update(pull_policy="never",
                   labels={"ctf590.managed": "true"},
                   cap_drop=["ALL"], cap_add=["CHOWN", "SETUID", "SETGID"],
                   security_opt=["no-new-privileges:true"], dns=["127.0.0.1"],
                   mem_limit="256m", memswap_limit="256m", cpus=0.5, pids_limit=64,
                   tmpfs=["/tmp:rw,noexec,nosuid,nodev,size=16m"],
                   logging={"driver": "json-file", "options": {"max-size": "1m", "max-file": "1"}})
        services[name] = service
    networks = {"ctfnet": {"name": network, "external": True}}
    for service in services.values():
        for name in service["networks"]:
            if name != "ctfnet":
                networks[name] = {"internal": True, "enable_ipv6": False,
                                  "labels": {"ctf590.managed": "true"},
                                  "driver_opts": {"com.docker.network.bridge.gateway_mode_ipv4": "isolated"}}
    return {"services": services, "networks": networks}


@contextmanager
def challenge_target(challenge, directory: Path):
    """Own a fresh network and any supplied Compose services for one challenge.

    Every entry creates new containers and a fresh isolated network. All target
    operations are trusted setup, never tools available to the model.
    """
    name = "ctf590-target-" + uuid.uuid4().hex[:12]
    network = name + "-net"
    directory.mkdir(parents=True, exist_ok=True)
    compose_path = directory / "compose.json"
    compose = ("compose", "--project-name", name, "-f", str(compose_path.resolve()))
    target = {"network": network, "container": None, "containers": {}, "images": {}, "volumes": [],
              "endpoints": [], "cleanup_errors": []}
    runtime = None
    if challenge.container:
        supplied_path = next((challenge.challenge_dir / filename for filename in
                              ("docker-compose.yml", "docker-compose.yaml")
                              if (challenge.challenge_dir / filename).is_file()), None)
        if supplied_path is None:
            raise ValueError("Service-backed challenge is missing its Compose file")
        supplied = json.loads(docker("compose", "-f", str(supplied_path), "config", "--format", "json"))
        runtime = target_compose(supplied, network)
        for service_name, service in runtime["services"].items():
            reference = service["image"]
            try:
                info = json.loads(docker("image", "inspect", reference))[0]
            except RuntimeError as error:
                if "No such image" not in str(error):
                    raise
                docker("pull", "--platform", service.get("platform", "linux/amd64"), reference, timeout=300)
                info = json.loads(docker("image", "inspect", reference))[0]
            # Use the resolved local ID throughout this attempt; tags cannot move mid-run.
            service["image"] = info["Id"]
            service["platform"] = "linux/" + info["Architecture"]
            target["images"][service_name] = info["Id"]
        compose_path.write_text(json.dumps(runtime, indent=2) + "\n")
    network_created = False
    try:
        docker("network", "create", "--internal", "--ipv6=false", "--label", "ctf590.managed=true",
               "--opt", "com.docker.network.bridge.gateway_mode_ipv4=isolated", network)
        network_created = True
        inspected = json.loads(docker("network", "inspect", network))[0]
        subnet = ipaddress.IPv4Network(inspected["IPAM"]["Config"][0]["Subnet"])
        target["gateway"] = str(subnet.broadcast_address - 1)
        if runtime is not None:
            docker(*compose, "up", "--detach", "--force-recreate", "--no-build", "--pull", "never", timeout=30)
            for service_name, service in runtime["services"].items():
                container = docker(*compose, "ps", "--all", "--quiet", service_name)
                target["containers"][service_name] = container
                info = json.loads(docker("inspect", container))[0]
                target["volumes"].extend(mount["Name"] for mount in info["Mounts"] if mount["Type"] == "volume")
                if not info["State"]["Running"]:
                    raise RuntimeError(f"Target service {service_name} exited during startup")
                aliases = (service["networks"].get("ctfnet") or {}).get("aliases", [])
                if challenge.server_name in [service_name, *aliases]:
                    address = info["NetworkSettings"]["Networks"][network]["IPAddress"]
                    target.update(address=address, container=container, image_id=info["Image"],
                        endpoints=[{"address": address, "protocol": "udp" if challenge.challenge.get("proto") == "udp" else "tcp",
                                    "port": int(challenge.port or challenge.challenge.get("port"))}])
            if not target["endpoints"]:
                raise ValueError("No Compose service matches the challenge connection metadata")
        yield target
    finally:
        if runtime is not None:
            try:
                docker(*compose, "down", "--volumes", "--remove-orphans", "--timeout", "2", timeout=15)
                for volume in target["volumes"]:
                    if docker("volume", "ls", "--filter", f"name=^{volume}$", "--format", "{{.Name}}"):
                        target["cleanup_errors"].append("Target volume removal failed")
            except (RuntimeError, subprocess.TimeoutExpired) as error:
                target["cleanup_errors"].append(type(error).__name__ + ": target removal failed")
        if network_created:
            try:
                docker("network", "rm", network, timeout=5)
            except (RuntimeError, subprocess.TimeoutExpired) as error:
                target["cleanup_errors"].append(type(error).__name__ + ": network removal failed")
        (directory / "target.json").write_text(json.dumps(target, indent=2) + "\n")
        if target["cleanup_errors"]:
            raise RuntimeError("Target cleanup incomplete; see target.json")
