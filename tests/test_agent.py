"""Public-loop behavior through bounded functions and the real Langfuse SDK."""

import json
import time
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from ctf_agent.agent import AttemptStopped, MAX_RESPONSE_BYTES, SYSTEM_PROMPT, run_agent, validate_response
from ctf_agent.config import DEFAULTS
from ctf_agent.tools import TOOL_DEFINITIONS
from .fixtures.responses import tool_response
from .fixtures.tracing import attribute, read_spans


def test_observations_drive_recovery_and_only_public_history_is_passed(local_attempt, telemetry, monkeypatch):
    worker = Mock(side_effect=[{"exit_code": 7, "stdout": "", "stderr": "failed"},
                               {"exit_code": 0, "stdout": "new observation", "stderr": ""}])
    monkeypatch.setattr("ctf_agent.tools.invoke_worker", worker)
    histories = []

    def respond(*, messages, tools, timeout_seconds):
        assert 0 < timeout_seconds <= DEFAULTS["wall_seconds"]
        assert messages[0]["content"] == SYSTEM_PROMPT
        assert messages[1] == {"role": "user", "content": "Only this public task"}
        assert tools[0]["function"]["name"] == "run_command"
        serialized = json.dumps({"messages": messages, "tools": tools})
        for private in ["private-expected-answer", "private-network", "private-gateway",
                        run["run_id"], str(run["directory"])]:
            assert private not in serialized
        histories.append(messages)
        if len(histories) == 1:
            messages[0]["content"] = "callback mutation"
            tools[0]["function"]["name"] = "callback mutation"
            return tool_response("run_command", {"command": "exit 7"}, "failed-command")
        if len(histories) == 2:
            assert json.loads(messages[-1]["content"])["exit_code"] == 7
            assert messages[-1]["tool_call_id"] == "failed-command"
            return tool_response("run_command", {"command": "echo new observation"}, "changed-command")
        assert json.loads(messages[-1]["content"])["stdout"] == "new observation"
        return {"role": "assistant", "content": "Cannot complete the task."}

    with local_attempt(respond, "Only this public task") as run:
        assert run_agent("Only this public task", run["respond"], run["call_tool"]) == "completed_without_success"
    assert run["result"]["scripted_turns"] == 3 and run["result"]["tool_calls"] == 2
    assert worker.call_count == 2 and TOOL_DEFINITIONS[0]["name"] == "run_command"
    spans = read_spans(telemetry, run["result"]["trace_id"])
    generations = sorted((span for span in spans if span.name == "scripted-response"), key=lambda span: span.start_time)
    assert [len(attribute(span, "input")["messages"]) for span in generations] == [2, 4, 6]
    assert sum(span.attributes.get("langfuse.observation.type") == "tool" for span in spans) == 2
    assert "private-expected-answer" not in "".join(span.to_json() for span in spans)
    assert run["result"]["model_calls"] == 0 and run["result"]["tokens"] is None
    assert run["result"]["cost_usd"] == 0 and not run["result"]["cleanup_errors"]
    assert not (run["directory"] / "trace.jsonl").exists()


@pytest.mark.parametrize("name,arguments", [
    ("run_command", "{broken json"), ("run_command", "[]"), ("unknown_tool", "{}"),
    ("write_file", '{"path":"../escape","content":"x"}'),
])
def test_invalid_arguments_return_observations_and_consume_tool_budget(local_attempt, telemetry, name, arguments):
    requests = []

    def respond(**request):
        requests.append(request)
        if len(requests) == 1:
            response = tool_response(name, {}, "invalid")
            response["tool_calls"][0]["function"]["arguments"] = arguments
            return response
        assert json.loads(request["messages"][-1]["content"])["error"]["kind"] == "validation_error"
        return {"role": "assistant", "content": "Stop after observing the rejection."}

    with local_attempt(respond) as run:
        assert run_agent("public", run["respond"], run["call_tool"]) == "completed_without_success"
    assert run["result"]["tool_calls"] == 1 and len(requests) == 2
    tools = [span for span in read_spans(telemetry, run["result"]["trace_id"])
             if span.attributes.get("langfuse.observation.type") == "tool"]
    assert len(tools) == 1 and attribute(tools[0], "input") is None
    assert attribute(tools[0], "output")["error"]["kind"] == "validation_error"


def test_wrong_submission_then_success_stops_sibling_tools_and_later_turns(local_attempt):
    requests = []

    def respond(**request):
        requests.append(request)
        if len(requests) == 1:
            return tool_response("submit_flag", {"candidate": "wrong"}, "wrong")
        assert json.loads(request["messages"][-1]["content"]) == {"correct": False}
        response = tool_response("submit_flag", {"candidate": "private-expected-answer"}, "correct")
        response["tool_calls"] += tool_response("run_command", {"command": "must not execute"}, "after-success")["tool_calls"]
        return response

    with local_attempt(respond) as run:
        assert run_agent("public", run["respond"], run["call_tool"]) == "success"
        assert run_agent("public", run["respond"], run["call_tool"]) == "success"
    assert len(requests) == 2 and run["result"]["tool_calls"] == 2
    assert run["result"]["verified_success"] is True


@pytest.mark.parametrize("local_attempt,reason,turns,tool_calls", [
    ({"max_model_turns": 2}, "model_turn_limit", 2, 2),
    ({"max_tool_calls": 1}, "tool_limit", 2, 1),
], indirect=["local_attempt"])
def test_repeated_invalid_actions_reach_the_enforced_limits(local_attempt, reason, turns, tool_calls):
    requests = []

    def respond(**request):
        requests.append(request)
        return tool_response("unknown_tool", {}, f"call-{len(requests)}")

    with local_attempt(respond) as run:
        assert run_agent("public", run["respond"], run["call_tool"]) == reason
    assert run["result"]["scripted_turns"] == turns and run["result"]["tool_calls"] == tool_calls


def test_terminal_event_during_response_discards_actions(local_attempt, telemetry):
    def respond(**request):
        run["stop"]("scope_violation")
        return tool_response("run_command", {"command": "must not execute"}, "late")

    with local_attempt(respond) as run:
        assert run_agent("public", run["respond"], run["call_tool"]) == "scope_violation"
    assert run["result"]["tool_calls"] == 0
    generation = next(span for span in read_spans(telemetry, run["result"]["trace_id"]) if span.name == "scripted-response")
    assert attribute(generation, "metadata.discarded") is True and attribute(generation, "output") is None


def test_expired_deadline_discards_response_before_watchdog_notices(local_attempt, monkeypatch):
    def respond(**request):
        monkeypatch.setattr("ctf_agent.attempt.time", SimpleNamespace(monotonic=lambda: time.monotonic() + 61))
        return tool_response("submit_flag", {"candidate": "private-expected-answer"}, "late")

    with local_attempt(respond) as run:
        assert run_agent("public", run["respond"], run["call_tool"]) == "wall_limit"
    assert run["result"]["tool_calls"] == 0


def test_terminal_event_between_sibling_tools_stops_the_batch(local_attempt):
    response = tool_response("submit_flag", {"candidate": "wrong"}, "first")
    response["tool_calls"] += tool_response("run_command", {"command": "must not execute"}, "second")["tool_calls"]
    with local_attempt(lambda **kwargs: response) as run:
        def first_tool(name, arguments):
            result = run["call_tool"](name, arguments)
            run["stop"]("scope_violation")
            return result
        assert run_agent("public", run["respond"], first_tool) == "scope_violation"
    assert run["result"]["tool_calls"] == 1 and run["result"]["scripted_turns"] == 1


def test_text_claiming_success_is_not_evaluator_success(local_attempt):
    with local_attempt(lambda **kwargs: {"role": "assistant", "content": "I solved it!"}) as run:
        assert run_agent("public", run["respond"], run["call_tool"]) == "completed_without_success"
    assert run["result"]["verified_success"] is False and run["result"]["tool_calls"] == 0


@pytest.mark.parametrize("response", [
    None, {"role": "tool", "content": "wrong role"}, {"role": "assistant", "content": 7},
    {"role": "assistant", "tool_calls": "not a list"}, {"role": "assistant", "content": ""},
    {"role": "assistant", "tool_calls": [None]},
    {"role": "assistant", "content": "x" * (MAX_RESPONSE_BYTES + 1)},
], ids=["non-object", "role", "content", "calls", "empty", "call-envelope", "oversized"])
def test_malformed_response_envelopes(response):
    with pytest.raises(ValueError):
        validate_response(response, set())


def test_response_rejection_stops_without_tools_or_oversized_trace(local_attempt, telemetry):
    response = {"role": "assistant", "content": "x" * (MAX_RESPONSE_BYTES + 1)}
    with local_attempt(lambda **kwargs: response) as run:
        assert run_agent("public", run["respond"], run["call_tool"]) == "response_error"
    assert run["result"]["tool_calls"] == 0
    generation = next(span for span in read_spans(telemetry, run["result"]["trace_id"]) if span.name == "scripted-response")
    assert attribute(generation, "output") is None
    assert "1 MiB" in attribute(generation, "metadata.validation_error")
    assert len(generation.to_json()) < 10_000


def test_duplicate_call_ids_in_one_response():
    response = tool_response("submit_flag", {"candidate": "wrong"}, "duplicate")
    response["tool_calls"] *= 2
    with pytest.raises(ValueError, match="unique"):
        validate_response(response, set())


def test_reused_call_id_in_later_turn_stops_execution(local_attempt):
    response = tool_response("submit_flag", {"candidate": "wrong"}, "duplicate")
    with local_attempt(lambda **kwargs: response) as run:
        assert run_agent("public", run["respond"], run["call_tool"]) == "response_error"
    assert run["result"]["tool_calls"] == 1


def test_response_source_error_is_terminal_and_does_not_log_exception_text(local_attempt, telemetry):
    def respond(**request):
        raise RuntimeError("secret-in-error-message")

    with local_attempt(respond) as run:
        assert run_agent("public", run["respond"], run["call_tool"]) == "response_source_error"
    assert run["result"]["tool_calls"] == 0
    trace = "".join(span.to_json() for span in read_spans(telemetry, run["result"]["trace_id"]))
    assert "secret-in-error-message" not in trace and "RuntimeError" in trace


def test_unrelated_runtime_error_is_not_hidden_by_concurrent_stopping(local_attempt):
    response = tool_response("submit_flag", {"candidate": "wrong"}, "first")
    with local_attempt(lambda **kwargs: response) as run:
        def broken_tool(name, arguments):
            run["stop"]("scope_violation")
            raise RuntimeError("unrelated programming failure")
        with pytest.raises(RuntimeError, match="unrelated programming failure"):
            run_agent("public", run["respond"], broken_tool)


def test_loop_accepts_only_public_interfaces():
    requests = []
    def respond(**request):
        requests.append(request)
        raise AttemptStopped("model_turn_limit")
    assert run_agent("public", respond, lambda name, args: pytest.fail("Unexpected tool")) == "model_turn_limit"
    assert set(requests[0]) == {"messages", "tools"}
