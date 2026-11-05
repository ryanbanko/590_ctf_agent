"""Real launch flow with SDK transports and Docker substituted."""

from contextlib import contextmanager
import json
from pathlib import Path
from types import SimpleNamespace

import httpx2
from langfuse.openai import OpenAI
import pytest

from ctf_agent.config import DEFAULTS, load_experiment
from ctf_agent.launch import run_challenge
from ctf_agent.agent import MODEL_SETTINGS, make_responder
from ctf_agent.launch import read_model_trace
from .fixtures.tracing import read_spans
from .test_model import sdk_response


@pytest.mark.parametrize("invalid", [float("nan"), -1, True])
def test_invalid_model_cap_is_rejected_before_launch(tmp_path, invalid):
    path = tmp_path / "experiment.toml"
    text = "nan" if type(invalid) is float else "true" if invalid is True else "-1"
    path.write_text(f"[attempt]\n[model]\nrequest_seconds = {text}\n")
    with pytest.raises(ValueError):
        load_experiment(path)


@pytest.mark.parametrize("split", ["development", "scored"])
def test_shared_run_flow_keeps_answer_private_and_verifies_observed_candidate(
        tmp_path, monkeypatch, local_attempt, telemetry, split):
    task_dir = tmp_path / "contestant"
    task_dir.mkdir()
    (task_dir / "program").write_bytes(b"public binary fixture")
    expected = "ctf{observed-fixture-candidate}"
    challenge = SimpleNamespace(name="baby_boi", category="pwn", description="Connect to original.example:8000",
        server_name="original.example", files=["program"], challenge_dir=task_dir, flag=expected)
    monkeypatch.setattr("ctf_agent.launch.load_challenge", lambda *args: challenge)
    monkeypatch.setattr("ctf_agent.launch.collect_provenance", lambda settings, **kwargs: {"config": settings})
    staged = []

    def stage(files, *args):
        staged.extend(files)
        return [{"path": name} for name in files]

    monkeypatch.setattr("ctf_agent.launch.stage_files", stage)

    @contextmanager
    def target(*args):
        yield {"network": "test-network", "gateway": "192.0.2.254", "cleanup_errors": [], "images": {},
               "endpoints": [{"address": "192.0.2.1", "protocol": "tcp", "port": 8000}]}

    monkeypatch.setattr("ctf_agent.launch.challenge_target", target)
    monkeypatch.setattr("ctf_agent.tools.invoke_worker", lambda *args, **kwargs:
                        {"stdout": expected, "stderr": "", "exit_code": 0})
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"revision": "pinned", "index_sha256": "index-hash",
                                   "scored": ["pwn-baby-boi"] if split == "scored" else []}))
    requests = []

    def handle(request):
        data = json.loads(request.content)
        requests.append(data)
        if len(requests) == 1:
            assert expected not in request.content.decode()
            assert "original.example" not in request.content.decode()
            assert "192.0.2.1" in request.content.decode()
            output = [{"type": "function_call", "call_id": "read", "name": "run_command", "arguments": '{"command":"read-public-interface"}'}]
        else:
            assert expected in data["input"][-1]["output"]
            output = [{"type": "function_call", "call_id": "submit", "name": "submit_flag", "arguments": json.dumps({"candidate": expected})}]
        return httpx2.Response(200, json=sdk_response(output))

    with OpenAI(api_key="dummy", max_retries=0,
                http_client=httpx2.Client(transport=httpx2.MockTransport(handle))) as client:
        respond, usage = make_responder(client, langfuse_public_key="pk-lf-ctf590-local")
        directory = tmp_path / "run"
        report = run_challenge(DEFAULTS, tmp_path / "index.json", manifest, "pwn-baby-boi", directory,
            langfuse=telemetry["client"], respond=respond, model_usage=usage, export_trace=None)
    assert staged == ["program"]
    assert report["result"]["verified_success"] and report["result"]["mode"] == split
    assert report["result"]["model_calls"] == report["result"]["tool_calls"] == 2
    assert not report["result"]["scripted_turns"]
    assert json.loads((directory / "run.json").read_text())["result"]["verified_success"]
    spans = read_spans(telemetry, report["result"]["trace_id"])
    root = next(span for span in spans if span.name == "attempt")
    assert expected not in root.to_json()
    assert len([span for span in spans if span.name == "model-response"]) == 2


def test_pinned_cli_exports_complete_failure_trace(tmp_path, monkeypatch):
    rows = [{"id": "root", "name": "attempt", "type": "SPAN", "traceId": "trace", "endTime": "done"},
            {"id": "error", "name": "model-response", "type": "GENERATION", "traceId": "trace", "endTime": "done"},
            {"id": "cleanup", "name": "sandbox_cleanup", "type": "EVENT", "traceId": "trace", "endTime": "done"}]
    commands = []

    def cli(command, **kwargs):
        commands.append(command)
        return SimpleNamespace(returncode=0, stdout=json.dumps({"body": {"data": rows}}))

    monkeypatch.setenv("LANGFUSE_BASE_URL", "https://example.invalid")
    monkeypatch.setattr("ctf_agent.launch.subprocess.run", cli)
    assert read_model_trace("trace", 1, 0, tmp_path) == rows
    assert "@langfuse/cli@1.3.1" in commands[0]
    assert "--from-start-time" in commands[0] and "--to-start-time" in commands[0]
    assert (tmp_path / "cli-observations.json").is_file()
