"""Basic trusted-data and binary-staging checks; no benchmark answers or Docker."""

import hashlib
import io
import json
from pathlib import Path
import tarfile
from types import SimpleNamespace

import pytest

from ctf_agent.challenge import contestant_files, load_challenge, public_task, stage_files


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
        assert args == ["cp", "--archive", "-", "solver:/workspace"] and timeout == 3
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


def test_scored_loading_is_rejected_before_private_files_are_opened(tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"development": ["development"], "scored": ["held-out"], "revision": None}))
    with pytest.raises(ValueError, match="development"):
        load_challenge(tmp_path / "missing-index.json", "held-out", manifest)
    with pytest.raises(ValueError, match="Pin"):
        load_challenge(tmp_path / "missing-index.json", "development", manifest)


def test_recorded_split_matches_metadata_only_selection():
    manifest = json.loads(Path("configs/ctftiny.json").read_text())
    index = json.loads(Path("evidence/ctftiny-readiness/index-metadata.json").read_text())
    ranked = sorted(index, key=lambda name: hashlib.sha256(("ctf590-v1:" + name).encode()).hexdigest())
    assert set(manifest["scored"]) == set(ranked[:10])
    assert set(manifest["development"]) == set(ranked[10:])
    assert manifest["readiness_challenge"] in manifest["development"]
