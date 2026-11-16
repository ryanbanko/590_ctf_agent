"""Manual HTB setup and human-relayed verification; all functions run on the host."""

from contextlib import contextmanager
import ipaddress
import json
import os
from pathlib import Path, PurePosixPath
import select
import shutil
import stat
import subprocess
import sys
from types import SimpleNamespace
import uuid
import zipfile

from .agent import AttemptStopped
from .challenge import contestant_files
from .docker import docker
from .sandbox import validate_endpoints


MAX_FILES = 10_000
MAX_BYTES = 512 * 1024 * 1024
PRIVATE_NAMES = {"challenge.json", "Dockerfile", "docker-compose.yml", "docker-compose.yaml",
                 "compose.yml", "compose.yaml", ".git", ".aws", ".codex", ".ssh", ".env", "docker.sock",
                 ".DS_Store", "__MACOSX"}


def handout_path(name: str) -> PurePosixPath:
    path = PurePosixPath(name)
    if (not path.parts or path.is_absolute() or ".." in path.parts
            or "\\" in name or ":" in name or "\x00" in name or len(name.encode()) > 4096):
        raise ValueError("Handout paths must be relative, without traversal or special separators")
    return path


def withheld(path: PurePosixPath) -> bool:
    return any(part in PRIVATE_NAMES or part.startswith(".env.") or part.endswith(".ovpn")
               for part in path.parts)


def import_handouts(source: Path, destination: Path) -> tuple[list[str], list[str]]:
    """Copy bounded regular files or extract a ZIP; never execute handout content."""
    names, omitted, seen = [], [], set()
    total = 0

    def copy_file(name, mode, size, open_source):
        nonlocal total
        path = handout_path(name)
        normalized = str(path)
        if normalized in seen:
            raise ValueError("Duplicate handout path")
        seen.add(normalized)
        if len(seen) > MAX_FILES or size < 0 or total + size > MAX_BYTES:
            raise ValueError("Handouts exceed 10,000 files or 512 MiB; select a smaller folder")
        total += size
        if withheld(path):
            omitted.append(normalized)
            return
        target = destination / normalized
        target.parent.mkdir(parents=True, exist_ok=True)
        copied = 0
        with open_source() as incoming, target.open("xb") as outgoing:
            while chunk := incoming.read(1024 * 1024):
                copied += len(chunk)
                if copied > size:
                    raise ValueError("Handout size changed or exceeded its declared size")
                outgoing.write(chunk)
        if copied != size:
            raise ValueError("Handout size changed during import")
        target.chmod(0o644 | (mode & 0o111))
        names.append(normalized)

    if source.is_symlink():
        raise ValueError("Select a regular ZIP or folder, not a symlink")
    if source.is_dir():
        for item in sorted(source.rglob("*")):
            info = item.lstat()
            if stat.S_ISLNK(info.st_mode):
                raise ValueError("Handouts must not contain symlinks")
            if stat.S_ISDIR(info.st_mode):
                continue
            if not stat.S_ISREG(info.st_mode):
                raise ValueError("Handouts must contain only regular files and directories")
            copy_file(item.relative_to(source).as_posix(), info.st_mode, info.st_size,
                      lambda item=item: item.open("rb"))
    elif source.is_file() and zipfile.is_zipfile(source):
        try:
            with zipfile.ZipFile(source) as archive:
                if len(archive.infolist()) > MAX_FILES:
                    raise ValueError("ZIP exceeds 10,000 entries")
                for entry in archive.infolist():
                    handout_path(entry.filename)
                    mode = entry.external_attr >> 16
                    kind = stat.S_IFMT(mode)
                    if kind not in {0, stat.S_IFREG, stat.S_IFDIR}:
                        raise ValueError("ZIP must not contain symlinks or special files")
                    if entry.is_dir():
                        continue
                    copy_file(entry.filename, mode, entry.file_size,
                              lambda entry=entry: archive.open(entry, pwd=b"hackthebox"))
        except (NotImplementedError, RuntimeError, zipfile.BadZipFile) as error:
            raise ValueError("Cannot read this ZIP. Extract it locally and select the folder instead.") from error
    else:
        raise ValueError("Select a downloaded ZIP or extracted folder")
    return sorted(names), sorted(omitted)


def load_manual_task(path: Path) -> tuple[dict, dict[str, Path]]:
    """Validate the saved public task and resolve only its listed contestant files."""
    if path.stat().st_size > 131_072:
        raise ValueError("task.json exceeds 128 KiB")
    task = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(task, dict) or task.keys() != {"name", "category", "description", "files", "endpoints"}:
        raise ValueError("Task must have name, category, description, files and endpoints")
    for key, maximum in (("name", 200), ("category", 64), ("description", 65_536)):
        if not isinstance(task[key], str) or not task[key].strip() or len(task[key].encode()) > maximum:
            raise ValueError(f"Task {key} must be nonempty text within {maximum} bytes")
    if not isinstance(task["files"], list) or len(task["files"]) > MAX_FILES:
        raise ValueError("Task files must be a list of at most 10,000 relative paths")
    for name in task["files"]:
        if not isinstance(name, str) or withheld(handout_path(name)):
            raise ValueError("Task lists a private/build/credential file")
    if (not isinstance(task["endpoints"], list) or len(task["endpoints"]) > 32
            or any(not isinstance(item, dict) or item.keys() != {"address", "protocol", "port"}
                   or not isinstance(item["address"], str)
                   for item in task["endpoints"])):
        raise ValueError("Task endpoints must list address, protocol and port (at most 32)")
    validate_endpoints(task["endpoints"])
    # Reuse the CTFTiny file boundary, without constructing a private dataset object.
    root = path.resolve().parent / "files"
    if root.is_symlink():
        raise ValueError("The handout folder must not be a symlink")
    files = contestant_files(SimpleNamespace(challenge_dir=root, files=task["files"]))
    if sum(item.stat().st_size for item in files.values()) > MAX_BYTES:
        raise ValueError("Task files exceed 512 MiB")
    task["files"] = list(files)
    return task, files


def setup_manual_task(output_root: Path, *, ask=input) -> Path:
    """Prepare once, without Docker, credentials, model calls or HTB authentication."""
    name = ask("Challenge name: ").strip()
    category = ask("Category: ").strip()
    print("Paste the description. Finish with a line containing only a period (.).")
    lines = []
    while (line := ask("")) != ".":
        lines.append(line)
    source = ask("Path to downloaded ZIP or extracted folder (blank for no files): ").strip()
    endpoints = []
    while address := ask("Assigned target IPv4 address (blank when done): ").strip():
        port = int(ask("Target port: "))
        protocol = ask("Protocol [tcp]: ").strip().lower() or "tcp"
        endpoints.append({"address": str(ipaddress.IPv4Address(address)), "protocol": protocol, "port": port})
    validate_endpoints(endpoints)
    if len(endpoints) > 32:
        raise ValueError("At most 32 assigned endpoints are supported")
    directory = output_root / ("task-" + uuid.uuid4().hex[:12])
    if source and directory.resolve().is_relative_to(Path(source).expanduser().resolve()):
        raise ValueError("Choose a handout folder separate from the task output directory")
    directory.mkdir(parents=True, exist_ok=False, mode=0o700)
    try:
        (directory / "files").mkdir()
        files, omitted = import_handouts(Path(source).expanduser(), directory / "files") if source else ([], [])
        task = {"name": name, "category": category, "description": "\n".join(lines),
                "files": files, "endpoints": endpoints}
        path = directory / "task.json"
        path.write_text(json.dumps(task, indent=2) + "\n", encoding="utf-8")
        load_manual_task(path)
        print(json.dumps(task, indent=2, ensure_ascii=True))
        if omitted:
            print("Withheld private/build/credential paths: " + json.dumps(omitted))
        (directory / "import.json").write_text(json.dumps({"withheld_files": omitted}, indent=2) + "\n")
        if ask("Save this task and its listed files? [y/N]: ").strip().lower() not in {"y", "yes"}:
            raise KeyboardInterrupt("Task setup cancelled")
    except BaseException:
        shutil.rmtree(directory)
        raise
    print(f"Saved task: {path}")
    print("No agent has run. Review it, then use run-manual --task with this path.")
    return path


def terminal_line(prompt: str, remaining, *, stream=None) -> str:
    """Read a terminal/pipe line without allowing input to outlive the attempt."""
    stream = sys.stdin if stream is None else stream
    print(prompt, end="", flush=True)
    data = bytearray()
    while True:
        seconds = remaining()
        ready, _, _ = select.select([stream], [], [], min(0.2, seconds))
        if not ready:
            continue
        value = os.read(stream.fileno(), 1)
        if not value:
            raise EOFError("Manual verdict input closed")
        if value == b"\n":
            remaining()
            return data.decode("utf-8").strip()
        data.extend(value)
        if len(data) > 4096:
            raise RuntimeError("Manual verdict input exceeds 4096 bytes")


def manual_verdict(label: str, candidate: str, remaining) -> dict:
    print("\nChallenge: " + json.dumps(label, ensure_ascii=True))
    print("Candidate (copy the value inside the JSON quotes): " + json.dumps(candidate, ensure_ascii=True))
    print("Submit this exact candidate on HTB. Enter n only if HTB explicitly rejects it.")
    while True:
        answer = terminal_line("HTB accepted? [y/n/cancel/error]: ", remaining).lower()
        if answer in {"y", "yes", "n", "no"}:
            return {"correct": answer in {"y", "yes"}}
        if answer in {"c", "cancel"}:
            raise AttemptStopped("user_cancel")
        if answer in {"e", "error"}:
            raise AttemptStopped("verification_unavailable")
        print("Enter y for accepted, n for rejected, cancel to stop, or error if HTB could not verify.")


@contextmanager
def manual_network(endpoints: list[dict], directory: Path):
    """Own only a local bridge; the operator owns the remote HTB instance."""
    validate_endpoints(endpoints)
    directory.mkdir(parents=True, exist_ok=False, mode=0o700)
    name = "ctf590-htb-" + uuid.uuid4().hex[:12]
    target = {"kind": "htb-external", "network": name, "endpoints": endpoints,
              "images": {}, "cleanup_errors": [], "remote_lifecycle": "operator-managed"}
    docker("network", "create", "--label", "ctf590.managed=true", name, timeout=10)
    try:
        yield target
    finally:
        try:
            docker("network", "rm", name, timeout=5)
        except (RuntimeError, subprocess.TimeoutExpired) as error:
            target["cleanup_errors"].append(type(error).__name__ + ": local bridge cleanup failed")
        (directory / "target.json").write_text(json.dumps(target, indent=2) + "\n")
        if target["cleanup_errors"]:
            raise RuntimeError("Local bridge cleanup incomplete; see target.json")
