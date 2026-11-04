"""Readback completeness, secrecy, pagination, and ingestion-lag handling."""

from datetime import datetime, timezone
import json
from types import SimpleNamespace
from unittest.mock import Mock

from langfuse.api.commons.types.observation_v2 import ObservationV2
from langfuse.api.observations.types import ObservationsV2Meta, ObservationsV2Response
import pytest

from .check_langfuse import audit_trace, wait_for_trace


@pytest.fixture
def hosted_trace():
    result = {"run_id": "test-run", "trace_id": "a" * 32, "termination_reason": "success",
              "verified_success": True, "tool_calls": 5, "scripted_turns": 5,
              "model_calls": 0, "cost_usd": 0.0}
    expected, secret = "ctf{synthetic-readback}", "sk-lf-test-secret"
    now = datetime.now(timezone.utc)
    rows = []

    def add(name, kind, input=None, output=None, metadata=None):
        item = ObservationV2(id=f"{len(rows) + 1:016x}", trace_id=result["trace_id"], project_id="test",
            name=name, type=kind, start_time=now, end_time=now,
            parent_observation_id=rows[0].id if rows else None,
            input=json.dumps(input) if input is not None else None,
            output=json.dumps(output) if output is not None else None, metadata=metadata)
        rows.append(item)

    add("attempt", "SPAN", {"task": "public"}, result)
    actions = [
        ("run_command", {"command": "exit 7"}, {"exit_code": 7}),
        ("write_file", {"path": "fetch.py", "content": "public script"}, {"bytes_written": 13}),
        ("run_command", {"command": "python fetch.py"}, {"stdout": "observed synthetic flag"}),
        ("submit_flag", {"candidate": "wrong"}, {"correct": False}),
        ("submit_flag", {"candidate": expected}, {"correct": True}),
    ]
    for step, (name, inputs, outputs) in enumerate(actions, 1):
        add("scripted-response", "GENERATION", {"messages": [{}] * (2 * step)}, {"role": "assistant"})
        add(name, "TOOL", inputs, outputs, {"step": step})
    for name in ("guard_ready", "sandbox_ready", "attempt_stopping", "sandbox_cleanup"):
        add(name, "EVENT")
    return rows, result, expected, secret


def test_hosted_readback_matches_summary_and_rejects_partial_trace(hosted_trace):
    rows, result, expected, secret = hosted_trace
    assert all(audit_trace(rows, result, expected, secret).values())
    assert audit_trace(rows[:-1], result, expected, secret) is None


@pytest.mark.parametrize("leak", ["expected", "secret"])
def test_hosted_readback_rejects_sensitive_root_data(hosted_trace, leak):
    rows, result, expected, secret = hosted_trace
    rows[0] = rows[0].model_copy(update={"metadata": {"leaked": expected if leak == "expected" else secret}})
    with pytest.raises(ValueError, match="expected_answer_not_in_root" if leak == "expected" else "secret_key_not_in_trace"):
        audit_trace(rows, result, expected, secret)


def test_hosted_readback_polls_for_ingestion_and_reads_cursor_pages(hosted_trace, monkeypatch):
    rows, result, expected, secret = hosted_trace
    request = Mock(side_effect=[
        ObservationsV2Response(data=[], meta=ObservationsV2Meta()),
        ObservationsV2Response(data=rows[:8], meta=ObservationsV2Meta(cursor="next-page")),
        ObservationsV2Response(data=rows[8:], meta=ObservationsV2Meta()),
    ])
    client = SimpleNamespace(api=SimpleNamespace(observations=SimpleNamespace(get_many=request)))
    monkeypatch.setattr("tests.check_langfuse.time.sleep", lambda seconds: None)
    received, checks = wait_for_trace(client, result, expected, secret)
    assert received == rows and all(checks.values())
    assert [call.kwargs["cursor"] for call in request.call_args_list] == [None, None, "next-page"]
    assert all(call.kwargs["trace_id"] == result["trace_id"] for call in request.call_args_list)


def test_hosted_readback_deadline_does_not_claim_completion(hosted_trace):
    _, result, expected, secret = hosted_trace
    client = Mock()
    with pytest.raises(TimeoutError, match="verification deadline"):
        wait_for_trace(client, result, expected, secret, seconds=0)
    client.api.observations.get_many.assert_not_called()
