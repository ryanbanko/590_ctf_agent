"""Human guidance with local SDK spans and substituted solver/model operations."""

from contextlib import contextmanager
from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import sys
import time

import pytest

from ctf_agent.agent import AttemptStopped, run_agent
from ctf_agent.attempt import run_attempt
from ctf_agent.guidance import (MAX_MESSAGE_BYTES, MAX_MESSAGES, PREFACE, atomic_json,
                                guidance_status, message_files, queue_guidance,
                                receive_guidance, start_guidance)
from .fixtures.responses import tool_response
from .fixtures.tracing import attribute, read_spans


@contextmanager
def manual_attempt(path, settings, telemetry, respond, *, enabled=True, **overrides):
    model_usage = overrides.pop("model_usage", None)
    with run_attempt(settings | overrides, "substitute", [], None, path,
            langfuse=telemetry["client"], mode="htb-manual", label="synthetic guidance",
            respond=respond, verify_candidate=lambda value, remaining: {"correct": value == "correct"},
            allow_guidance=enabled, model_usage=model_usage) as run:
        yield run


@pytest.mark.parametrize("ending", ["success", "text", "turn_limit", "deadline", "scope"])
def test_unused_guidance_preserves_history_counters_and_stopping(
        tmp_path, local_attempt, settings, telemetry, ending):
    records = []
    for enabled in (False, True):
        histories = []
        def respond(**kwargs):
            histories.append(deepcopy((kwargs["messages"], kwargs["tools"])))
            if ending in {"deadline", "scope"}:
                run["stop"]("wall_limit" if ending == "deadline" else "scope_violation")
            if ending == "text":
                return {"role": "assistant", "content": "Finished without a candidate."}
            candidate = "correct" if ending == "success" and len(histories) == 2 else "wrong"
            return tool_response("submit_flag", {"candidate": candidate}, str(len(histories)))
        path = tmp_path / str(enabled)
        with manual_attempt(path, settings, telemetry, respond, enabled=enabled, max_model_turns=2) as run:
            reason = run_agent("public", run["respond"], run["call_tool"],
                               receive_guidance=run.get("receive_guidance"))
        result = run["result"]
        records.append((histories, reason, {key: result[key] for key in
            ("termination_reason", "verified_success", "scripted_turns", "model_calls", "tool_calls")}))
        if enabled:
            assert result["guidance_messages"] == 0 and not result["human_assisted"]
        else:
            assert not (path / "guidance").exists()
            assert "receive_guidance" not in run
    assert records[0] == records[1]


def test_guidance_during_response_and_tool_is_ordered_persistent_and_traced(
        tmp_path, local_attempt, settings, telemetry, monkeypatch):
    histories, queued = [], []
    def respond(**kwargs):
        histories.append(deepcopy(kwargs["messages"]))
        if len(histories) == 1:
            queued.append(queue_guidance(tmp_path, "A suggestion sent during the response"))
        return tool_response("run_command", {"command": "synthetic"}, str(len(histories))) if len(histories) < 3 else {
            "role": "assistant", "content": "No further actions."}
    def execute(*args):
        if len(histories) == 1:
            queued.append(queue_guidance(tmp_path, "An observation sent during the tool"))
        return {"stdout": "synthetic result", "exit_code": 0}
    monkeypatch.setattr("ctf_agent.attempt.execute_tool", execute)
    with manual_attempt(tmp_path, settings, telemetry, respond) as run:
        assert run_agent("public", run["respond"], run["call_tool"],
                         receive_guidance=run["receive_guidance"]) == "completed_without_success"
    assert len(histories[0]) == 2
    assert histories[1][-3]["role"] == "tool"
    expected = [{"role": "user", "content": PREFACE + "\n\n" + row["text"]} for row in queued]
    assert histories[1][-2:] == expected
    assert histories[2][4:6] == expected  # retained, rather than appended a second time
    status = guidance_status(tmp_path)
    assert [row["id"] for row in status["messages"]] == [row["id"] for row in queued]
    assert all(row["request"] == 2 and row["status"] == "included_in_request" for row in status["messages"])
    assert run["result"]["guidance_messages"] == 2 and run["result"]["human_assisted"]
    assert run["result"]["scripted_turns"] == 3 and run["result"]["tool_calls"] == 2
    spans = read_spans(telemetry, run["result"]["trace_id"])
    events = [span for span in spans if span.name == "human_guidance_delivered"]
    root = next(span for span in spans if span.name == "attempt")
    assert len(events) == 2 and all(span.parent.span_id == root.context.span_id for span in events)
    assert [attribute(span, "input")["text"] for span in events] == [row["text"] for row in queued]


@pytest.mark.parametrize("ending", ["text", "success", "deadline", "turn_limit"])
def test_late_messages_remain_undelivered_and_cannot_resume(
        tmp_path, local_attempt, settings, telemetry, ending):
    calls = []
    def respond(**kwargs):
        calls.append(kwargs)
        queue_guidance(tmp_path, "Too late for this request")
        if ending == "deadline":
            run["stop"]("wall_limit")
        return ({"role": "assistant", "content": "Stopping"} if ending in {"text", "deadline"}
                else tool_response("submit_flag", {"candidate": "correct" if ending == "success" else "wrong"}, "one"))
    with manual_attempt(tmp_path, settings, telemetry, respond, max_model_turns=1) as run:
        run_agent("public", run["respond"], run["call_tool"], receive_guidance=run["receive_guidance"])
    assert len(calls) == 1 and run["result"]["guidance_messages"] == 0
    assert guidance_status(tmp_path)["messages"][0]["status"] == "undelivered"
    with pytest.raises(ValueError, match="closed"):
        queue_guidance(tmp_path, "Cannot restart")


@pytest.mark.parametrize("corruption", ["json", "oversized", "symlink", "unreadable", "too_many"])
def test_inbox_failure_is_visible_and_does_not_stop_solving(
        tmp_path, local_attempt, settings, telemetry, capsys, corruption):
    def respond(**kwargs):
        return tool_response("submit_flag", {"candidate": "correct"}, "one")
    with manual_attempt(tmp_path, settings, telemetry, respond) as run:
        path = tmp_path / "guidance/messages/bad.json"
        if corruption == "symlink":
            other = tmp_path / "host-only"
            other.write_text("not public")
            path.symlink_to(other)
        elif corruption == "unreadable":
            path.mkdir()
        elif corruption == "too_many":
            for i in range(MAX_MESSAGES + 1):
                path.with_name(str(i) + ".json").write_text("{}")
        else:
            path.write_text("x" * 40000 if corruption == "oversized" else "{")
        assert run_agent("public", run["respond"], run["call_tool"],
                         receive_guidance=run["receive_guidance"]) == "success"
    assert "Guidance disabled" in capsys.readouterr().out
    assert run["result"]["guidance_errors"] == 1 and not run["result"]["human_assisted"]


def test_expired_hook_never_reads_or_delivers_inbox(tmp_path, local_attempt, settings, telemetry):
    with manual_attempt(tmp_path, settings, telemetry, lambda **kw: pytest.fail("Unexpected request"),
                        wall_seconds=0.05) as run:
        queue_guidance(tmp_path, "Pending at expiry")
        time.sleep(0.08)
        with pytest.raises(AttemptStopped, match="wall_limit"):
            run["receive_guidance"]()
    assert guidance_status(tmp_path)["messages"][0]["status"] == "undelivered"


def test_cli_queues_and_reports_without_credentials_or_docker(tmp_path):
    tmp_path.mkdir(exist_ok=True)
    state = start_guidance(tmp_path, "synthetic")
    environment = dict(os.environ)
    for key in ("LITELLM_TOKEN", "LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY", "LANGFUSE_BASE_URL"):
        environment.pop(key, None)
    environment["PATH"] = str(tmp_path / "no-executables")
    command = [sys.executable, "-m", "ctf_agent", "guide", "--run", str(tmp_path)]
    result = subprocess.run(command + ["--message", "Example guidance"], env=environment,
                            capture_output=True, text=True, timeout=10)
    assert result.returncode == 0 and "queued" in result.stdout
    result = subprocess.run(command + ["--status"], env=environment, capture_output=True, text=True, timeout=10)
    assert result.returncode == 0 and json.loads(result.stdout)["messages"][0]["status"] == "queued"
    for text in (" ", "x" * (MAX_MESSAGE_BYTES + 1)):
        with pytest.raises(ValueError):
            queue_guidance(tmp_path, text)
    atomic_json(state["directory"] / "state.json", state["info"] | {"pid": 2147483647})
    with pytest.raises(ValueError, match="no longer running"):
        queue_guidance(tmp_path, "stale process")
    assert len(message_files(state["directory"])) == 1


def test_queue_rejects_disabled_destination_and_enforces_total_message_cap(tmp_path):
    with pytest.raises(ValueError, match="no guidance inbox"):
        queue_guidance(tmp_path, "Not enabled")
    start_guidance(tmp_path, "synthetic")
    for i in range(MAX_MESSAGES):
        queue_guidance(tmp_path, str(i))
    with pytest.raises(ValueError, match="At most"):
        queue_guidance(tmp_path, "one too many")
    assert len(message_files(tmp_path / "guidance")) == MAX_MESSAGES


def test_guidance_startup_failure_does_not_stop_solve(
        tmp_path, local_attempt, settings, telemetry, monkeypatch, capsys):
    def unavailable(*a):
        raise OSError("synthetic inbox failure")
    monkeypatch.setattr("ctf_agent.guidance.start_guidance", unavailable)
    with manual_attempt(tmp_path, settings, telemetry,
            lambda **kw: tool_response("submit_flag", {"candidate": "correct"}, "one")) as run:
        assert "receive_guidance" not in run
        assert run_agent("public", run["respond"], run["call_tool"]) == "success"
    assert run["result"]["guidance_errors"] == 1
    assert "Could not enable guidance" in capsys.readouterr().out


def test_stop_after_preparing_message_does_not_record_a_request(
        tmp_path, local_attempt, settings, telemetry):
    with manual_attempt(tmp_path, settings, telemetry,
            lambda **kw: pytest.fail("Responder must not run after stopping")) as run:
        queue_guidance(tmp_path, "Pending suggestion")
        def receive_then_stop():
            messages = run["receive_guidance"]()
            run["stop"]("wall_limit")
            return messages
        assert run_agent("public", run["respond"], run["call_tool"],
                         receive_guidance=receive_then_stop) == "wall_limit"
    assert run["result"]["guidance_messages"] == 0
    assert guidance_status(tmp_path)["messages"][0]["status"] == "undelivered"


def test_request_failure_preserves_guidance_attempt_without_claiming_acceptance(
        tmp_path, local_attempt, settings, telemetry):
    def failed(**kwargs):
        assert kwargs["messages"][-1]["content"] == PREFACE + "\n\nSuggestion"
        raise RuntimeError("synthetic request failure")
    with manual_attempt(tmp_path, settings, telemetry, failed) as run:
        queue_guidance(tmp_path, "Suggestion")
        assert run_agent("public", run["respond"], run["call_tool"],
                         receive_guidance=run["receive_guidance"]) == "response_source_error"
    assert guidance_status(tmp_path)["messages"][0]["status"] == "included_in_request"
    assert run["result"]["human_assisted"]


def test_guidance_reaches_native_sdk_request_without_extra_calls(
        tmp_path, local_attempt, settings, telemetry, model_settings, monkeypatch):
    import httpx2
    from langfuse.openai import OpenAI
    from ctf_agent.agent import make_responder
    from .test_model import sdk_response

    requests = []
    monkeypatch.setattr("ctf_agent.attempt.execute_tool", lambda *a: {"stdout": "synthetic", "exit_code": 0})
    def handle(request):
        requests.append(json.loads(request.content))
        if len(requests) == 1:
            queue_guidance(tmp_path, "Inspect the evidence")
            action = {"name": "run_command", "arguments": json.dumps({"command": "synthetic"})}
        else:
            action = {"name": "submit_flag", "arguments": json.dumps({"candidate": "correct"})}
        return httpx2.Response(200, json=sdk_response([
            {"type": "function_call", "call_id": str(len(requests)), **action}]))
    with OpenAI(api_key="synthetic", max_retries=0,
            http_client=httpx2.Client(transport=httpx2.MockTransport(handle))) as client:
        respond, usage = make_responder(client, model_settings, langfuse_public_key="pk-lf-ctf590-local")
        with manual_attempt(tmp_path, settings, telemetry, respond, model_usage=usage) as run:
            assert run_agent("public", run["respond"], run["call_tool"],
                             receive_guidance=run["receive_guidance"]) == "success"
    assert len(requests) == run["result"]["model_calls"] == run["result"]["tool_calls"] == 2
    assert requests[1]["input"][-2]["type"] == "function_call_output"
    assert requests[1]["input"][-1] == {"role": "user", "content": PREFACE + "\n\nInspect the evidence"}
    assert guidance_status(tmp_path)["messages"][0]["request"] == 2
