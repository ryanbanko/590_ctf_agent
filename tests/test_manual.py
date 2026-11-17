"""Manual workflow using synthetic handouts, local SDK spans and substituted Docker."""

from contextlib import contextmanager
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import time
from types import SimpleNamespace
import zipfile

import httpx2
from langfuse.openai import OpenAI
import pytest

from ctf_agent.agent import AttemptStopped, SYSTEM_PROMPT
from ctf_agent.agent import make_responder
from ctf_agent.config import load_experiment
from ctf_agent.launch import (MANUAL_HTB_PROMPT_PREFACE, read_model_trace,
                              run_manual_challenge)
from ctf_agent.manual import (import_handouts, load_manual_task, manual_network, manual_verdict,
                              setup_manual_task, terminal_line)
from .fixtures.responses import tool_response
from .fixtures.tracing import attribute, read_spans
from .test_model import sdk_response


def saved_task(tmp_path):
    (tmp_path / "files").mkdir(exist_ok=True)
    (tmp_path / "files/handout").write_bytes(b"synthetic public data")
    task = {"name": "synthetic HTB", "category": "misc", "description": "Synthetic integration check",
            "files": ["handout"], "endpoints": []}
    path = tmp_path / "task.json"
    path.write_text(json.dumps(task))
    return path


@pytest.mark.parametrize("archive", [False, True])
def test_setup_imports_reusable_files_and_records_withheld_paths(tmp_path, archive):
    source = tmp_path / "download"
    source.mkdir()
    (source / "program").write_bytes(b"\x7fELF\xfffixture")
    (source / "program").chmod(0o755)
    (source / "Dockerfile").write_text("host-only build data")
    if archive:
        path = tmp_path / "download.zip"
        with zipfile.ZipFile(path, "w") as zipped:
            for item in source.iterdir():
                zipped.write(item, item.name)
        source = path
    answers = iter(["example", "reversing", "Public description", ".", str(source),
                    "192.0.2.10", "31337", "", "", "y"])
    path = setup_manual_task(tmp_path / "saved", ask=lambda _: next(answers))
    task, files = load_manual_task(path)
    assert task["files"] == ["program"]
    assert task["endpoints"] == [{"address": "192.0.2.10", "port": 31337, "protocol": "tcp"}]
    assert files["program"].read_bytes() == b"\x7fELF\xfffixture"
    assert files["program"].stat().st_mode & 0o111
    assert json.loads((path.parent / "import.json").read_text())["withheld_files"] == ["Dockerfile"]
    assert not (path.parent / "files/Dockerfile").exists()


@pytest.mark.parametrize("name", ["../escape", "/absolute", "folder/../../escape", "a\\b", "C:/file"])
def test_zip_traversal_is_rejected(tmp_path, name):
    source = tmp_path / "download.zip"
    with zipfile.ZipFile(source, "w") as archive:
        archive.writestr(name, "public")
    with pytest.raises(ValueError, match="paths"):
        import_handouts(source, tmp_path / "out")
    assert not (tmp_path / "escape").exists()


@pytest.mark.parametrize("kind", ["symlink", "duplicate", "limit"])
def test_unsafe_archives_fail_instead_of_silently_importing(tmp_path, monkeypatch, kind):
    source = tmp_path / "download.zip"
    with zipfile.ZipFile(source, "w") as archive:
        if kind == "symlink":
            info = zipfile.ZipInfo("link")
            info.external_attr = (stat.S_IFLNK | 0o777) << 16
            archive.writestr(info, "outside")
        else:
            archive.writestr("a", "public")
            if kind == "duplicate":
                archive.writestr("./a", "duplicate")
    if kind == "limit":
        monkeypatch.setattr("ctf_agent.manual.MAX_BYTES", 2)
    with pytest.raises(ValueError):
        import_handouts(source, tmp_path / "out")


def test_folder_symlinks_and_cancelled_setup_are_rejected(tmp_path):
    source = tmp_path / "download"
    source.mkdir()
    (source / "link").symlink_to(tmp_path)
    with pytest.raises(ValueError, match="symlinks"):
        import_handouts(source, tmp_path / "out")
    answers = iter(["example", "misc", "Public", ".", "", "", "n"])
    with pytest.raises(KeyboardInterrupt):
        setup_manual_task(tmp_path / "saved", ask=lambda _: next(answers))
    assert not list((tmp_path / "saved").iterdir())


def test_htb_password_protected_zip_uses_standard_library(tmp_path):
    if not shutil.which("zip"):
        pytest.skip("zip is needed only to create this synthetic encrypted test archive")
    (tmp_path / "handout").write_bytes(b"synthetic encrypted fixture")
    subprocess.run(["zip", "-q", "-P", "hackthebox", "download.zip", "handout"],
                   cwd=tmp_path, check=True)
    names, _ = import_handouts(tmp_path / "download.zip", tmp_path / "out")
    assert names == ["handout"]
    assert (tmp_path / "out/handout").read_bytes() == b"synthetic encrypted fixture"


@pytest.mark.parametrize("field,value", [
    ("flag", "private"), ("files", ["../outside"]), ("files", [".env"]),
    ("files", ["handout", "./handout"]), ("endpoints", [{"address": "host.example", "port": 80, "protocol": "tcp"}]),
    ("endpoints", [{"address": "192.0.2.1", "port": True, "protocol": "tcp"}]),
])
def test_saved_task_rejects_private_fields_invalid_paths_and_endpoints(tmp_path, field, value):
    path = saved_task(tmp_path)
    task = json.loads(path.read_text())
    task[field] = value
    path.write_text(json.dumps(task))
    with pytest.raises(ValueError):
        load_manual_task(path)


def test_terminal_input_handles_partial_pipe_and_does_not_outlive_deadline():
    read_fd, write_fd = os.pipe()
    try:
        with os.fdopen(read_fd, "rb", buffering=0) as stream:
            os.write(write_fd, b"y")  # Data without a newline must not block readline forever.
            deadline = time.monotonic() + 0.05
            def remaining():
                seconds = deadline - time.monotonic()
                if seconds <= 0:
                    raise AttemptStopped("wall_limit")
                return seconds
            with pytest.raises(AttemptStopped, match="wall_limit"):
                terminal_line("", remaining, stream=stream)
            os.write(write_fd, b"n\n")
            assert terminal_line("", lambda: 1, stream=stream) == "n"
        read_fd = None
    finally:
        os.close(write_fd)
        if read_fd is not None:
            # fdopen closes on exceptional paths as well.
            try:
                os.close(read_fd)
            except OSError:
                pass


@pytest.mark.parametrize("answer,expected", [("y", True), ("n", False), ("yes", True), ("no", False)])
def test_manual_verdict_reprompts_then_returns_actual_verdict(monkeypatch, answer, expected):
    answers = iter(["maybe", answer])
    monkeypatch.setattr("ctf_agent.manual.terminal_line", lambda *a: next(answers))
    assert manual_verdict("example", "candidate", lambda: 1) == {"correct": expected}


def test_remote_network_owns_only_its_local_bridge(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr("ctf_agent.manual.docker", lambda *a, **k: calls.append(a))
    with manual_network([], tmp_path / "target") as target:
        assert target["images"] == {} and target["remote_lifecycle"] == "operator-managed"
    assert calls == [("network", "create", "--label", "ctf590.managed=true", target["network"]),
                     ("network", "rm", target["network"])]


def test_remote_network_cleanup_failure_is_recorded(tmp_path, monkeypatch):
    def command(*args, **kwargs):
        if args[:2] == ("network", "rm"):
            raise subprocess.TimeoutExpired("synthetic bridge cleanup", 5)
    monkeypatch.setattr("ctf_agent.manual.docker", command)
    with pytest.raises(RuntimeError, match="cleanup incomplete"):
        with manual_network([], tmp_path / "target"):
            pass
    record = json.loads((tmp_path / "target/target.json").read_text())
    assert record["cleanup_errors"] == ["TimeoutExpired: local bridge cleanup failed"]


@pytest.mark.parametrize("ending", ["accepted", "cancel", "error", "eof", "interrupt", "late", "invalid"])
def test_shared_runner_preserves_manual_submission_verdicts_and_terminal_stops(
        tmp_path, monkeypatch, local_attempt, telemetry, settings, model_settings, ending):
    path = saved_task(tmp_path)
    monkeypatch.setattr(telemetry["client"], "get_trace_url", lambda **kw: "https://local.invalid/trace")
    monkeypatch.setattr("ctf_agent.launch.collect_provenance", lambda *a, **k: {})
    monkeypatch.setattr("ctf_agent.launch.stage_files", lambda *a: [{"path": "handout"}])
    @contextmanager
    def network(*args):
        yield {"network": "substitute", "endpoints": [], "images": {}, "cleanup_errors": []}
    monkeypatch.setattr("ctf_agent.manual.manual_network", network)
    answers = iter(["n", "y"] if ending == "accepted" else [ending])
    def read(*args):
        answer = next(answers)
        if answer == "eof":
            raise EOFError()
        if answer == "interrupt":
            raise KeyboardInterrupt()
        return answer
    monkeypatch.setattr("ctf_agent.manual.terminal_line", read)
    calls = []
    def respond(**kwargs):
        calls.append(kwargs)
        return tool_response("submit_flag", {"candidate": "synthetic-candidate"}, str(len(calls)))
    verifier = None
    if ending == "late":
        def verifier(candidate, remaining):
            time.sleep(remaining() + 0.02)
            return {"correct": True}
    elif ending == "invalid":
        verifier = lambda *a: {"correct": "yes"}
    configured = settings | ({"wall_seconds": 0.1} if ending == "late" else {})
    report = run_manual_challenge(configured, path, tmp_path / "run", langfuse=telemetry["client"],
        respond=respond, model_usage={"model_settings": model_settings}, verify_candidate=verifier,
        export_trace=None)
    result = report["result"]
    expected = {"accepted": "success", "cancel": "user_cancel", "error": "verification_unavailable",
                "eof": "user_cancel", "interrupt": "user_cancel", "late": "wall_limit",
                "invalid": "infrastructure_error"}[ending]
    assert result["termination_reason"] == expected
    assert result["verified_success"] is (ending == "accepted")
    assert len(calls) == (2 if ending == "accepted" else 1)
    rows = [json.loads(line) for line in next((tmp_path / "run").glob("*/submissions.jsonl")).read_text().splitlines()]
    assert [row["status"] for row in rows] == (["pending", "rejected", "pending", "accepted"]
                                                if ending == "accepted" else ["pending", expected])
    assert all(row["source"] == "htb-human-relay" and row["challenge_id"] == "synthetic HTB" for row in rows)
    assert report["local_answer_key"] is False and "dataset" not in report
    spans = read_spans(telemetry, result["trace_id"])
    root = next(span for span in spans if span.name == "attempt")
    assert "synthetic-candidate" not in root.to_json()
    tools = [span for span in spans if span.name == "submit_flag"]
    assert all(span.parent.span_id == root.context.span_id for span in tools)
    assert all(attribute(span, "metadata.verification_source") == "htb-human-relay" for span in tools)
    assert attribute(tools[-1], "output") == ({"correct": True} if ending == "accepted"
        else {"error": {"kind": expected}} if ending != "invalid"
        else {"error": {"kind": expected, "message": "Verification did not return an accepted/rejected verdict"}})


def test_competition_config_preserves_every_other_setting():
    baseline, model = load_experiment()
    manual, manual_model = load_experiment(Path("configs/htb-manual.toml"))
    assert manual == baseline | {"wall_seconds": 900.0, "max_model_turns": 60}
    assert manual_model == model | {"max_requests": 60}


def test_manual_model_flow_exports_real_sdk_spans_without_hosted_access(
        tmp_path, monkeypatch, local_attempt, telemetry, settings, model_settings):
    path = saved_task(tmp_path)
    monkeypatch.setattr(telemetry["client"], "get_trace_url", lambda **kw: "https://local.invalid/trace")
    def close(sandbox):
        sandbox["observation"].create_event(name="sandbox_cleanup")
        return []
    monkeypatch.setattr("ctf_agent.attempt.close_sandbox", close)
    monkeypatch.setattr("ctf_agent.launch.collect_provenance", lambda *a, **k: {})
    monkeypatch.setattr("ctf_agent.launch.stage_files", lambda *a: [{"path": "handout", "sha256": "fixture-hash"}])
    @contextmanager
    def network(*args):
        yield {"network": "substitute", "endpoints": [], "images": {}, "cleanup_errors": []}
    monkeypatch.setattr("ctf_agent.manual.manual_network", network)
    requests = []
    def handle(request):
        requests.append(json.loads(request.content))
        assert "expected_flag" not in request.content.decode()
        return httpx2.Response(200, json=sdk_response([{"type": "function_call", "call_id": "submit",
            "name": "submit_flag", "arguments": json.dumps({"candidate": "synthetic-candidate"})}]))
    def export(client, trace_id, model_calls, tool_calls, directory):
        rows = []
        for span in read_spans(telemetry, trace_id):
            kind = span.attributes.get("langfuse.observation.type")
            rows.append({"id": format(span.context.span_id, "016x"), "name": span.name,
                "type": {"generation": "GENERATION", "tool": "TOOL", "event": "EVENT"}.get(kind, "SPAN"),
                "traceId": trace_id, "parentObservationId": format(span.parent.span_id, "016x") if span.parent else None,
                "input": attribute(span, "input"), "output": attribute(span, "output"), "endTime": span.end_time})
        # Substitute only the remote read API, keeping normal pagination/export/completeness code.
        local_client = SimpleNamespace(api=SimpleNamespace(observations=SimpleNamespace(get_many=lambda **kw:
            SimpleNamespace(data=[SimpleNamespace(model_dump=lambda row=row, **kw: row) for row in rows],
                            meta=SimpleNamespace(cursor=None)))))
        return read_model_trace(local_client, trace_id, model_calls, tool_calls, directory)
    with OpenAI(api_key="synthetic", max_retries=0,
                http_client=httpx2.Client(transport=httpx2.MockTransport(handle))) as client:
        respond, usage = make_responder(client, model_settings, langfuse_public_key="pk-lf-ctf590-local")
        report = run_manual_challenge(settings, path, tmp_path / "run", langfuse=telemetry["client"],
            respond=respond, model_usage=usage, verify_candidate=lambda *a: {"correct": True}, export_trace=export)
    assert len(requests) == report["result"]["model_calls"] == 1
    assert report["evidence_complete"] and report["result"]["verified_success"]
    assert all(report["evidence_checks"].values())
    assert "expected_answer_not_in_root" not in report["evidence_checks"]
    original_task = json.dumps(load_manual_task(path)[0], ensure_ascii=True)
    assert requests[0]["input"][0] == {"role": "system", "content": SYSTEM_PROMPT}
    assert requests[0]["input"][1] == {"role": "user",
        "content": f"{MANUAL_HTB_PROMPT_PREFACE}\n\n{original_task}"}
    saved_public_task = tmp_path / "run/public-task.json"
    assert saved_public_task.read_text() == original_task + "\n"
    rows = json.loads((tmp_path / "run/observations.json").read_text())["data"]
    tool = next(row for row in rows if row["name"] == "submit_flag")
    assert tool["input"] == {"candidate": "synthetic-candidate"} and tool["output"] == {"correct": True}


def test_setup_cli_saves_file_only_task_without_credentials_or_docker(tmp_path):
    source = tmp_path / "download"
    source.mkdir()
    (source / "handout").write_bytes(b"synthetic CLI fixture")
    entered = "\n".join(["CLI example", "misc", "Public description", ".", str(source), "", "y", ""])
    environment = dict(os.environ)
    for key in ("LITELLM_TOKEN", "LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY", "LANGFUSE_BASE_URL"):
        environment.pop(key, None)
    environment["PATH"] = str(tmp_path / "no-executables")  # No Docker executable available.
    result = subprocess.run([sys.executable, "-m", "ctf_agent", "setup-manual", "--output", str(tmp_path / "tasks")],
        input=entered, text=True, capture_output=True, timeout=10, env=environment)
    assert result.returncode == 0, result.stderr
    paths = list((tmp_path / "tasks").glob("*/task.json"))
    assert len(paths) == 1 and load_manual_task(paths[0])[0]["endpoints"] == []
    assert "No agent has run" in result.stdout
