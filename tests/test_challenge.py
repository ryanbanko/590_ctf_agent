"""Basic trusted-data and binary-staging checks; no benchmark answers or Docker."""

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
from copy import deepcopy

import pytest

from ctf_agent.challenge import contestant_files, load_challenge, public_task, stage_files
from ctf_agent.challenge import (MONGO_AMD64_IMAGE, MONGO_ARM64_IMAGE, check_target_services,
                                 challenge_target, target_compose)


def test_only_listed_files_and_public_fields_are_used(tmp_path, monkeypatch):
    (tmp_path / "files").mkdir()
    binary = b"\x7fELF\x00\xff\x80binary"
    (tmp_path / "files/program").write_bytes(binary)
    (tmp_path / "files/program").chmod(0o755)
    (tmp_path / "challenge.json").write_text('{"flag":"private-answer"}')
    challenge = SimpleNamespace(challenge_dir=tmp_path, files=["./files/program"],
                                name="fixture", category="pwn", description="Public description",
                                flag="private-answer", challenge={"private": "metadata"})
    files = contestant_files(challenge)
    task = json.loads(public_task(challenge, files, [{"address": "192.0.2.2", "port": 8000}]))
    assert set(task) == {"name", "category", "description", "files", "endpoints"}
    assert "private-answer" not in json.dumps(task) and task["files"] == ["files/program"]
    assert task["description"] == challenge.description
    calls = []
    def command(*args, **kwargs):
        assert 0 < kwargs['timeout'] <= 3
        calls.append(args)
        return ''
    monkeypatch.setattr('ctf_agent.challenge.docker', command)
    records = stage_files(files, "solver", 3)
    assert calls == [
        ('exec', '--user', '1000:1000', 'solver', 'mkdir', '-p', '--', '/workspace/files'),
        ('cp', str((tmp_path/'files/program').resolve()), 'solver:/workspace/files/program'),
        ('exec', '--user', '0:0', 'solver', 'chown', '1000:1000', '--', '/workspace/files/program')]
    assert records == [{"path": "files/program", "bytes": len(binary),
                        "sha256": hashlib.sha256(binary).hexdigest()}]


def test_private_paths_and_symlinks_are_rejected(tmp_path):
    (tmp_path / "link").symlink_to(tmp_path.parent)
    challenge = SimpleNamespace(challenge_dir=tmp_path)
    for name in ["../outside", "/absolute", "challenge.json", "../Dockerfile", "link/outside"]:
        challenge.files = [name]
        with pytest.raises(ValueError):
            contestant_files(challenge)
    (tmp_path / "public").write_text("public handout")
    challenge.files = ["public", "Dockerfile"]
    assert list(contestant_files(challenge)) == ["public"]


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


def test_runtime_compose_preserves_supplied_behavior_with_narrow_exceptions(tmp_path):
    source = tmp_path/'server.conf'
    source.write_text('server configuration')
    supplied = {'name': 'global', 'services': {'server': {
        'image': 'fixture', 'command': ['original-command'], 'dns': ['127.0.0.11'],
        'cap_add': ['CHOWN'], 'tmpfs': ['/scratch'], 'mem_limit': '64m', 'restart': 'on-failure',
        'networks': {'ctfnet': {'aliases': ['challenge.example']}, 'backend': None},
        'volumes': [{'type': 'bind', 'source': '/var/run/docker.sock', 'target': '/var/run/docker.sock'},
                    {'type': 'bind', 'source': str(source), 'target': '/etc/server.conf', 'read_only': True},
                    {'type': 'volume', 'source': 'data', 'target': '/data'}],
        'ports': [{'published': '8000', 'target': 8000}], 'build': '.', 'container_name': 'global'}},
        'networks': {'ctfnet': {'name': 'ctfnet', 'external': True}, 'backend': {'driver': 'bridge'}},
        'volumes': {'data': {'name': 'global-data'}}}
    original = deepcopy(supplied)
    runtime, changes = target_compose(supplied, tmp_path)
    assert supplied == original
    service = runtime['services']['server']
    assert service['volumes'] == original['services']['server']['volumes'][1:]
    assert not {'ports','build','container_name'} & service.keys()
    for key in ['command','dns','cap_add','tmpfs','mem_limit','restart','networks']:
        assert service[key] == original['services']['server'][key]
    assert not {'cap_drop','security_opt','logging'} & service.keys()
    assert {c['removed'] for c in changes} == {'ports','build','container_name','docker_socket'}
    assert not {'name','external','internal'} & runtime['networks']['ctfnet'].keys()
    assert 'name' not in runtime['volumes']['data']


@pytest.mark.parametrize('architecture', ['arm64', 'aarch64', 'amd64', 'x86_64'])
def test_same_release_mongo_uses_native_arm_only_on_arm_engine(tmp_path, architecture):
    supplied = {'services': {'mongo': {'image': MONGO_AMD64_IMAGE,
        'environment': {'MONGO_INITDB_ROOT_USERNAME': 'fixture-user'},
        'command': ['mongod'], 'networks': {'backend': None}, 'restart': 'always'}}}
    original = deepcopy(supplied)
    runtime, changes = target_compose(supplied, tmp_path, architecture=architecture)
    service = runtime['services']['mongo']
    assert supplied == original
    for key in ['environment', 'command', 'networks', 'restart']:
        assert service[key] == original['services']['mongo'][key]
    if architecture in {'arm64', 'aarch64'}:
        assert service['image'] == MONGO_ARM64_IMAGE and service['platform'] == 'linux/arm64'
        assert changes[0]['original_image'] == MONGO_AMD64_IMAGE
        assert changes[0]['replacement_image'] == MONGO_ARM64_IMAGE and changes[0]['version'] == '7.0.9'
    else:
        assert service['image'] == MONGO_AMD64_IMAGE and 'platform' not in service and not changes


def test_other_mongo_releases_are_not_substituted(tmp_path):
    runtime, changes = target_compose({'services': {'mongo': {'image': 'mongo:7.0.10'}}},
                                    tmp_path, architecture='arm64')
    assert runtime['services']['mongo']['image'] == 'mongo:7.0.10' and not changes


@pytest.mark.parametrize('change', [
    {'Restarting': True}, {'Running': False, 'Status': 'exited', 'ExitCode': 1},
    {'OOMKilled': True}, {'Health': {'Status': 'unhealthy'}}, {'Health': {'Status': 'starting'}},
])
def test_target_readiness_rejects_failed_dependency_even_with_running_frontend(monkeypatch, change):
    good = {'Status': 'running', 'Running': True, 'Restarting': False, 'ExitCode': 0, 'OOMKilled': False}
    inspections = iter([{'State': good, 'RestartCount': 0},
                        {'State': good | change, 'RestartCount': 3, 'Config': {'Env': ['PRIVATE=synthetic-private']}}])
    monkeypatch.setattr('ctf_agent.challenge.docker', lambda *a, **k: json.dumps([next(inspections)]))
    target = {'containers': {'frontend': 'front-container', 'database': 'db-container'}}
    with pytest.raises(RuntimeError, match='database'):
        check_target_services(target, 'after_probes')
    states = target['service_checks']['after_probes']
    assert states['frontend']['running'] and states['database']['restart_count'] == 3
    assert 'synthetic-private' not in json.dumps(states)


def test_healthy_dependency_with_previous_restart_is_recorded_not_rejected(monkeypatch):
    state = {'Status': 'running', 'Running': True, 'Restarting': False, 'ExitCode': 0,
             'OOMKilled': False, 'Health': {'Status': 'healthy', 'Log': ['synthetic-private']}}
    monkeypatch.setattr('ctf_agent.challenge.docker', lambda *a, **k: json.dumps([{'State': state, 'RestartCount': 1}]))
    target = {'containers': {'database': 'container'}}
    check_target_services(target, 'startup')
    assert target['service_checks']['startup']['database']['restart_count'] == 1
    assert 'synthetic-private' not in json.dumps(target)


@pytest.mark.parametrize('change', [
    {'privileged': True}, {'network_mode': 'host'}, {'pid': 'host'}, {'use_api_socket': True},
    {'volumes': [{'type': 'bind', 'source': '/private-host', 'target': '/data', 'read_only': True}]},
    {'volumes': [{'type': 'bind', 'source': '.', 'target': '/data'}]},
])
def test_target_host_administration_and_persistent_host_state_rejected(tmp_path, change):
    with pytest.raises(ValueError):
        target_compose({'services': {'server': {'image':'fixture'} | change}}, tmp_path)


def test_external_storage_needs_reset_strategy(tmp_path):
    with pytest.raises(ValueError, match='fresh-state'):
        target_compose({'services': {}, 'volumes': {'data': {'external': True}}}, tmp_path)


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


def test_staging_uses_remaining_deadline(tmp_path, monkeypatch):
    source = tmp_path / 'public-file'
    source.write_bytes(b'public-data')
    monkeypatch.setattr('ctf_agent.challenge.docker', lambda *args, **kwargs: pytest.fail('Staged after deadline'))
    clock = iter([0, 4])
    monkeypatch.setattr('ctf_agent.challenge.time.monotonic', lambda: next(clock))
    with pytest.raises(TimeoutError, match='remaining attempt time'):
        stage_files({'public-file': source}, 'solver', 3)


@pytest.mark.parametrize('extra,expected', [([], 'configs/development.toml'),
                                          (['--experiment', 'custom.toml'], 'custom.toml')])
def test_prepare_cli_uses_selected_experiment(monkeypatch, extra, expected):
    from ctf_agent.__main__ import main

    calls = []
    monkeypatch.setattr('tests.check_readiness.check_readiness', lambda *args: calls.append(args))
    monkeypatch.setattr('sys.argv', ['ctf_agent', 'prepare-challenge', '--challenge', 'example', *extra])
    main()
    assert calls[0][0] == Path(expected) and calls[0][-1] == 'example'
