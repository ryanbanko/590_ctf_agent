"""Trusted CTFTiny loading and contestant-file staging; no model or target shell."""

import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import subprocess
import tarfile

from .docker import bounded_exec


def load_challenge(dataset_json: Path, challenge_id: str, manifest_path: Path):
    """Load development data only; the returned package object stays trusted."""
    manifest = json.loads(manifest_path.read_text())
    if challenge_id not in manifest["development"] or challenge_id in manifest["scored"]:
        raise ValueError("Readiness checks may load only a development challenge")
    if not manifest["revision"]:
        raise ValueError("Pin the CTFTiny checkout revision before loading a challenge")
    root = dataset_json.resolve().parent
    revision = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                              capture_output=True, text=True, check=True).stdout.strip()
    index = json.loads(dataset_json.read_text())
    digest = hashlib.sha256(json.dumps(index, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if revision != manifest["revision"] or digest != manifest["index_sha256"]:
        raise ValueError("CTFTiny revision or index differs from the recorded selection")
    if (len(manifest["scored"]) != 10 or set(manifest["scored"]) & set(manifest["development"])
            or set(manifest["scored"]) | set(manifest["development"]) != set(index)):
        raise ValueError("Expected ten scored challenges and a disjoint development remainder")
    # Import only for real loading; pure file/public-data checks need no package.
    from nyuctf.challenge import CTFChallenge
    from nyuctf.dataset import CTFDataset

    dataset = CTFDataset(dataset_json=dataset_json)
    return CTFChallenge(dataset.get(challenge_id), dataset.basedir)


def contestant_files(challenge) -> dict[str, Path]:
    """Resolve only listed regular contestant files, without following symlinks."""
    root = challenge.challenge_dir.resolve()
    files = {}
    for name in challenge.files:
        path = PurePosixPath(name)
        if (not path.parts or path.is_absolute() or ".." in path.parts or "\x00" in name
                or path.name in {"challenge.json", "docker-compose.yml", "docker-compose.yaml", "Dockerfile"}):
            raise ValueError("Invalid contestant-file path")
        source = root
        for part in path.parts:
            source = source / part
            if source.is_symlink():
                raise ValueError("Contestant files must not use symlinks")
        if not source.is_file() or str(path) in files:
            raise ValueError("Contestant files must be unique regular files")
        files[str(path)] = source
    return files


def public_task(challenge, files: dict[str, Path], endpoints: list[dict]) -> str:
    """Whitelist public fields; never serialize the package's private metadata."""
    task = {"name": challenge.name, "category": challenge.category,
            "description": challenge.description, "files": list(files), "endpoints": endpoints}
    return json.dumps(task, ensure_ascii=True)


def stage_files(files: dict[str, Path], solver: str, workspace_bytes: int, timeout: float) -> list[dict]:
    """Copy bytes with Docker's standard tar input, owned by the solver user.

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
            bounded_exec(["cp", "--archive", "-", f"{solver}:/workspace"], data.getvalue(), timeout)
    return records
