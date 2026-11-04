"""Basic trusted-data and binary-staging checks; no benchmark answers or Docker."""

import hashlib
import io
import json
from pathlib import Path
import tarfile
from types import SimpleNamespace
from copy import deepcopy

import pytest

from ctf_agent.challenge import contestant_files, load_challenge, public_task, stage_files
from ctf_agent.challenge import challenge_target, target_compose


def test_only_listed_files_and_public_fields_are_used(tmp_path, monkeypatch):
    (tmp_path / "files").mkdir()
    binary = b"\x7fELF\x00\xff\x80binary"
    (tmp_path / "files/program").write_bytes(binary)
    (tmp_path / "files/program").chmod(0o755)
    (tmp_path / "challenge.json").write_text('{"flag":"private-answer"}')
    challenge = SimpleNamespace(challenge_dir=tmp_path, files=["files/program"],
                                name="fixture", category="pwn", description="Public description",
                                flag="private-answer", challenge={"private": "metadata"})
    files = contestant_files(challenge)
    task = json.loads(public_task(challenge, files, [{"address": "192.0.2.2", "port": 8000}]))
    assert set(task) == {"name", "category", "description", "files", "endpoints"}
    assert "private-answer" not in json.dumps(task) and task["files"] == ["files/program"]
    transferred = []

    def copy(args, data, timeout):
        assert args[:10] == ["exec", "--interactive", "--user", "1000:1000", "--workdir", "/workspace",
                             "solver", "python", "-I", "-c"] and timeout == 3
        assert "filter='data'" in args[10]
        with tarfile.open(fileobj=io.BytesIO(data)) as archive:
            assert archive.getnames() == ["files", "files/program"]
            assert archive.extractfile("files/program").read() == binary
            assert all(item.uid == item.gid == 1000 for item in archive.getmembers())
            assert archive.getmember("files/program").mode == 0o700
        transferred.append(True)

    monkeypatch.setattr("ctf_agent.challenge.bounded_exec", copy)
    records = stage_files(files, "solver", 1024, 3)
    assert transferred and records == [{"path": "files/program", "bytes": len(binary),
                                       "sha256": hashlib.sha256(binary).hexdigest()}]
    with pytest.raises(ValueError, match="workspace limit"):
        stage_files(files, "solver", 1, 3)


def test_private_paths_and_symlinks_are_rejected(tmp_path):
    (tmp_path / "link").symlink_to(tmp_path.parent)
    challenge = SimpleNamespace(challenge_dir=tmp_path)
    for name in ["../outside", "/absolute", "challenge.json", "Dockerfile", "link/outside"]:
        challenge.files = [name]
        with pytest.raises(ValueError):
            contestant_files(challenge)


def test_unknown_loading_is_rejected_and_both_splits_require_pinned_data(tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"development": ["development"], "scored": ["held-out"], "revision": None}))
    with pytest.raises(ValueError, match="challenge ID"):
        load_challenge(tmp_path / "missing-index.json", "unknown", manifest)
    with pytest.raises(ValueError, match="Pin"):
        load_challenge(tmp_path / "missing-index.json", "held-out", manifest)
    with pytest.raises(ValueError, match="Pin"):
        load_challenge(tmp_path / "missing-index.json", "development", manifest)


def test_recorded_split_matches_metadata_only_selection():
    manifest = json.loads(Path("configs/ctftiny.json").read_text())
    index = json.loads(Path("evidence/ctftiny-readiness/index-metadata.json").read_text())
    ranked = sorted(index, key=lambda name: hashlib.sha256(("ctf590-v1:" + name).encode()).hexdigest())
    assert set(manifest["scored"]) == set(ranked[:10])
    assert len(manifest["scored"]) == 10
    assert set(manifest["development"]) == set(ranked[10:])
    assert "pwn-baby-boi" in manifest["development"]


def test_dirty_dataset_is_rejected_before_challenge_loading(tmp_path, monkeypatch):
    index = {"development": {}}
    dataset = tmp_path / "ctftiny.json"
    dataset.write_text(json.dumps(index))
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"development": ["development"], "scored": [], "revision": "pinned",
        "index_sha256": hashlib.sha256(json.dumps(index, sort_keys=True, separators=(",", ":")).encode()).hexdigest()}))
    outputs = iter(["pinned\n", " M ctftiny/pwn/task/challenge.json\n"])
    monkeypatch.setattr("ctf_agent.challenge.subprocess.run", lambda *a, **k: SimpleNamespace(stdout=next(outputs)))
    with pytest.raises(ValueError, match="clean"):
        load_challenge(dataset, "development", manifest)


def test_runtime_compose_removes_socket_and_host_ports_without_changing_supplied_data():
    supplied = {"services": {"game-server": {"image": "llmctf/task:latest",
        "volumes": [{"source": "/var/run/docker.sock", "target": "/var/run/docker.sock"}],
        "ports": [{"published": "8000", "target": 8000}],
        "networks": {"ctfnet": {"aliases": ["challenge.example"]}}}}}
    original = deepcopy(supplied)
    runtime = target_compose(supplied, "fresh-internal-network")
    service = runtime["services"]["game-server"]
    assert supplied == original
    assert not {"volumes", "ports"} & service.keys()
    assert service["image"] == "llmctf/task:latest"
    assert service["networks"] == original["services"]["game-server"]["networks"]
    assert runtime["networks"]["ctfnet"] == {"name": "fresh-internal-network", "external": True}
    assert "read_only" not in service and service["cap_drop"] == ["ALL"]
    for change in [{"build": "."}, {"privileged": True}, {"volumes": [{"target": "/private-host"}]}]:
        with pytest.raises(ValueError, match="Unsupported"):
            target_compose({"services": {"game-server": original["services"]["game-server"] | change}},
                           "network")


def test_target_start_failure_still_removes_compose_resources_and_network(tmp_path, monkeypatch):
    (tmp_path / "docker-compose.yml").write_text("services: {}\n")
    calls = []

    def fake_docker(*args, **kwargs):
        calls.append(args)
        if args[-3:] == ("config", "--format", "json"):
            return json.dumps({"services": {"game-server": {"image": "llmctf/task:latest"}}})
        if args[:2] == ("network", "inspect"):
            return json.dumps([{"IPAM": {"Config": [{"Subnet": "192.0.2.0/24"}]}}])
        if args[:2] == ("image", "inspect"):
            return json.dumps([{"Id": "sha256:abc", "Architecture": "amd64"}])
        if "up" in args:
            raise RuntimeError("synthetic target startup failure")
        return ""

    monkeypatch.setattr("ctf_agent.challenge.docker", fake_docker)
    challenge = SimpleNamespace(name="baby_boi", port=8000, container=True, challenge_dir=tmp_path)
    with pytest.raises(RuntimeError, match="startup failure"):
        with challenge_target(challenge, tmp_path / "evidence"):
            pytest.fail("Failed target was yielded")
    assert any("down" in args for args in calls)
    assert any(args[:2] == ("network", "rm") for args in calls)
    assert json.loads((tmp_path / "evidence/target.json").read_text())["cleanup_errors"] == []


def test_package_loader_accepts_evaluation_id_without_a_separate_runner(tmp_path, monkeypatch):
    entry = {"year": "2026", "event": "fixture", "category": "misc", "challenge": "fixture", "path": "selected"}
    index = {f"evaluation-{i}": entry for i in range(10)} | {"development": entry}
    (tmp_path / "selected").mkdir()
    (tmp_path / "selected/challenge.json").write_text(json.dumps({"name": "fixture", "category": "misc",
        "description": "Public fixture", "flag": "ctf{private-fixture}", "files": [], "compose": False}))
    dataset = tmp_path / "ctftiny.json"
    dataset.write_text(json.dumps(index))
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"development": ["development"], "scored": [f"evaluation-{i}" for i in range(10)],
        "revision": "pinned", "index_sha256": hashlib.sha256(json.dumps(index, sort_keys=True, separators=(",", ":")).encode()).hexdigest()}))
    outputs = iter(["pinned\n", ""])
    monkeypatch.setattr("ctf_agent.challenge.subprocess.run", lambda *a, **k: SimpleNamespace(stdout=next(outputs)))
    challenge = load_challenge(dataset, "evaluation-0", manifest)
    assert challenge.name == "fixture" and challenge.files == [] and not challenge.container
