"""Passive target records must not disclose trusted data or interfere with cleanup."""

import json
from types import SimpleNamespace

import pytest

from ctf_agent.challenge import challenge_target, snapshot_target_services


@pytest.mark.parametrize("status,oom,networks", [
    ("running", False, {"bridge": {"IPAddress": "192.0.2.2", "NetworkID": "network-id",
                                   "Aliases": ["private-alias"]}}),
    ("exited", False, {}), ("exited", True, {}), ("running", False, {}),
])
def test_snapshot_records_distinct_target_failures_and_network_loss(monkeypatch, status, oom, networks):
    info = {"State": {"Status": status, "Running": status == "running", "Restarting": False,
                      "ExitCode": 137 if oom else 0, "OOMKilled": oom,
                      "Health": {"Status": "healthy", "Log": ["private-health-log"]}},
            "RestartCount": 2, "NetworkSettings": {"Networks": networks},
            "Config": {"Env": ["PRIVATE=private-environment"], "Cmd": ["private-command"]}}
    def inspect(*args, **kwargs):
        assert 0 < kwargs["timeout"] <= 3
        return json.dumps([info])
    monkeypatch.setattr("ctf_agent.challenge.docker", inspect)
    target = {"containers": {"server": "container"}}
    row = snapshot_target_services(target, "before_cleanup", best_effort=True)["server"]
    assert row["status"] == status and row["oom_killed"] == oom
    assert row["running"] == (status == "running") and row["restart_count"] == 2
    assert row["exit_code"] == (137 if oom else 0)
    assert row["networks"] == ({"bridge": {"address": "192.0.2.2", "network_id": "network-id"}}
                                if networks else {})
    assert "private-" not in json.dumps(target)


@pytest.mark.parametrize("error,status", [
    (RuntimeError("No such object: private-container"), "missing"),
    (RuntimeError("private-daemon-error"), "unavailable"),
    (TimeoutError("private-timeout"), "unavailable"),
    (ValueError("private-invalid-json"), "unavailable"),
])
def test_failed_inspection_is_sanitized_and_does_not_hide_other_services(monkeypatch, error, status):
    good = {"State": {"Status": "running", "Running": True, "Restarting": False,
                      "ExitCode": 0, "OOMKilled": False}, "RestartCount": 0}
    def inspect(*args, **kwargs):
        if args[1] == "failed":
            raise error
        return json.dumps([good])
    monkeypatch.setattr("ctf_agent.challenge.docker", inspect)
    target = {"containers": {"first": "failed", "second": "working"}}
    states = snapshot_target_services(target, "before_cleanup", best_effort=True)
    assert states["first"] == {"status": status, "error_type": type(error).__name__}
    assert states["second"]["running"]
    assert "private-" not in json.dumps(target)


def test_final_snapshots_share_one_bounded_allowance(monkeypatch):
    clock = iter([0, 0, 4])
    monkeypatch.setattr("ctf_agent.challenge.time.monotonic", lambda: next(clock))
    calls = []
    def inspect(*args, **kwargs):
        calls.append(kwargs["timeout"])
        raise TimeoutError("inspect timed out")
    monkeypatch.setattr("ctf_agent.challenge.docker", inspect)
    target = {"containers": {"one": "first", "two": "second"}}
    states = snapshot_target_services(target, "before_cleanup", best_effort=True)
    assert calls == [3]
    assert all(row["error_type"] == "TimeoutError" for row in states.values())


@pytest.mark.parametrize("body_fails,cleanup_fails", [(False, False), (True, False), (False, True)])
def test_diagnostic_error_preserves_outcome_exception_and_cleanup(tmp_path, monkeypatch,
                                                               body_fails, cleanup_fails):
    calls = []
    def command(*args, **kwargs):
        calls.append(args)
        if args[:2] == ("network", "rm") and cleanup_fails:
            raise RuntimeError("cleanup failure")
        return ""
    def snapshot(*args, **kwargs):
        calls.append(("snapshot",))
        raise RuntimeError("private diagnostic detail")
    monkeypatch.setattr("ctf_agent.challenge.docker", command)
    monkeypatch.setattr("ctf_agent.challenge.snapshot_target_services", snapshot)
    def run():
        with challenge_target(SimpleNamespace(container=False), tmp_path / "record") as target:
            target["outcome_marker"] = "original-result"
            if body_fails:
                raise ValueError("original body error")
    if body_fails:
        with pytest.raises(ValueError, match="original body error"):
            run()
    elif cleanup_fails:
        with pytest.raises(RuntimeError, match="Target cleanup incomplete"):
            run()
    else:
        run()
    record = json.loads((tmp_path / "record/target.json").read_text())
    assert record["outcome_marker"] == "original-result"
    assert record["diagnostic_error"] == {"phase": "before_cleanup", "error_type": "RuntimeError"}
    assert bool(record["cleanup_errors"]) == cleanup_fails
    assert calls[-2][0] == "snapshot" and calls[-1][:2] == ("network", "rm")
    assert "private diagnostic detail" not in json.dumps(record)
