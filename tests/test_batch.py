"""Batch scheduling with simulated child records; no Docker, keys or model calls."""

import json
from pathlib import Path
import signal
from unittest.mock import MagicMock

import pytest

from ctf_agent.launch import launch_batch


@pytest.fixture
def batch_files(tmp_path):
    experiment = tmp_path / "settings.toml"
    experiment.write_bytes(Path("configs/development.toml").read_bytes())
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"development": ["dev-a", "dev-b"], "scored": ["held-out"]}))
    return {"experiment_path": experiment, "dataset_json": tmp_path / "unused-dataset.json",
            "manifest_path": manifest, "output_root": tmp_path / "batches"}


@pytest.fixture
def fake_children(monkeypatch):
    def configure(specifications):
        calls = []

        def start(command, *, start_new_session):
            assert start_new_session is True
            number = len(calls) + 1
            specification = specifications[number - 1]
            child = MagicMock()
            calls.append((command, child))
            child.__enter__.return_value = child
            child.__exit__.return_value = False
            child.wait.side_effect = ([KeyboardInterrupt(), 130] if specification.get("interrupt")
                                      else [specification.get("returncode", 0)])
            if not specification.get("missing_record"):
                output = Path(command[command.index("--output") + 1]) / f"challenge-{number}"
                output.mkdir(parents=True)
                result = {"run_id": f"run-{number}", "termination_reason": specification.get("outcome", "success"),
                          "verified_success": specification.get("outcome", "success") == "success",
                          "cleanup_errors": specification.get("cleanup_errors", []),
                          "cost_usd": specification.get("cost_usd", .001),
                          "usage_complete": specification.get("usage_complete", True)}
                report = {"challenge_id": command[command.index("--challenge") + 1], "result": result,
                          "evidence_complete": specification.get("evidence_complete", True),
                          "trace_url": f"https://example.invalid/traces/{number}"}
                (output / "run.json").write_text(json.dumps(report))
            return child

        monkeypatch.setattr("ctf_agent.launch.subprocess.Popen", start)
        return calls

    return configure


def test_batch_repeats_every_challenge_and_indexes_normal_failures(batch_files, fake_children):
    calls = fake_children([{}, {"outcome": "completed_without_success"}, {"outcome": "command_timeout"}, {}])
    directory = launch_batch(**batch_files, challenge_ids=["dev-a", "dev-b"], trials=2)
    index = json.loads((directory / "batch.json").read_text())
    assert index["status"] == "completed" and index["planned_attempts"] == 4
    assert [(r["challenge_id"], r["trial"]) for r in index["attempts"]] == [
        ("dev-a", 1), ("dev-b", 1), ("dev-a", 2), ("dev-b", 2)]
    assert [r["verified_success"] for r in index["attempts"]] == [True, False, False, True]
    assert len({r["run_id"] for r in index["attempts"]}) == 4
    assert len({r["record"] for r in index["attempts"]}) == 4
    assert all(r["status"] == "completed" and (directory / r["record"]).is_file() for r in index["attempts"])
    for command, child in calls:
        assert command[1:4] == ["-m", "ctf_agent", "run-challenge"]
        snapshot = Path(command[command.index("--experiment") + 1])
        assert snapshot == (directory / "experiment.toml").resolve()
        assert snapshot.read_bytes() == batch_files["experiment_path"].read_bytes()
        child.wait.assert_called_once()


@pytest.mark.parametrize("specification", [
    {"returncode": 1}, {"missing_record": True}, {"evidence_complete": False},
    {"cleanup_errors": ["synthetic cleanup failure"]}, {"outcome": "scope_violation"},
    {"outcome": "guard_failure"}, {"outcome": "infrastructure_error"},
    {"outcome": "response_source_error"}, {"outcome": "model_usage_missing"},
])
def test_batch_stops_and_retains_partial_index(batch_files, fake_children, specification):
    calls = fake_children([specification])
    with pytest.raises(RuntimeError, match="Batch stopped"):
        launch_batch(**batch_files, challenge_ids=["dev-a", "dev-b"], trials=1)
    index = json.loads(next(batch_files["output_root"].glob("*/batch.json")).read_text())
    assert index["status"] == "stopped" and len(calls) == len(index["attempts"]) == 1
    assert index["attempts"][0]["status"] == "stopped"


def test_batch_interrupt_forwards_signal_and_waits_for_child_records(batch_files, fake_children):
    calls = fake_children([{"interrupt": True}])
    with pytest.raises(KeyboardInterrupt):
        launch_batch(**batch_files, challenge_ids=["dev-a", "dev-b"], trials=1)
    index = json.loads(next(batch_files["output_root"].glob("*/batch.json")).read_text())
    assert index["status"] == "interrupted" and len(calls) == 1
    assert index["attempts"][0]["run_id"] == "run-1"
    calls[0][1].send_signal.assert_called_once_with(signal.SIGINT)
    assert calls[0][1].wait.call_count == 2


@pytest.mark.parametrize("ids,trials", [([], 1), (["dev-a", "dev-a"], 1), (["unknown"], 1),
                                      (["dev-a", "held-out"], 1), (["dev-a"], 0), (["dev-a"], True)])
def test_batch_invalid_plan_starts_nothing(batch_files, fake_children, ids, trials):
    calls = fake_children([])
    with pytest.raises(ValueError):
        launch_batch(**batch_files, challenge_ids=ids, trials=trials)
    assert not calls and not batch_files["output_root"].exists()


