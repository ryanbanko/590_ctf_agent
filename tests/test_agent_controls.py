"""Scripted loop integration with real SDK spans and isolated synthetic targets."""

import json
from functools import partial
import time

import pytest

from ctf_agent.agent import run_agent
from ctf_agent.attempt import run_attempt
from ctf_agent.docker import docker
from .fixtures.responses import synthetic_response, tool_response
from .fixtures.tracing import attribute, save_spans

pytestmark = pytest.mark.docker


def test_scripted_loop_recovers_and_verifies_through_target(settings, target, output_root, telemetry, record_property):
    label = "scripted_loop_recovers_and_verifies_through_target"
    record_property("check_name", label)
    url = f'http://{target["address"]}:8000/'
    public_task = f"Retrieve the synthetic flag from {url} and submit it."

    respond = partial(synthetic_response, url)

    with run_attempt(settings, target["network"], target["gateway"], target["endpoints"],
                     target["expected_flag"], output_root, langfuse=telemetry["client"],
                     label=label, public_task=public_task, respond=respond) as run:
        record_property("run_id", run["run_id"])
        assert run_agent(public_task, run["respond"], run["call_tool"]) == "success"
    assert run["result"]["scripted_turns"] == 5 and run["result"]["tool_calls"] == 5
    spans = save_spans(telemetry, run["directory"], run["result"]["trace_id"])
    tools = [span for span in spans if span.attributes.get("langfuse.observation.type") == "tool"]
    generations = [span for span in spans if span.name == "scripted-response"]
    assert len(tools) == len(generations) == 5
    assert all(attribute(span, "output") is not None for span in tools)
    assert not any(attribute(span, "input").get("command") == "echo must-not-run-after-success" for span in tools)
    root = next(span for span in spans if span.name == "attempt")
    assert target["expected_flag"] not in root.to_json()
    assert all(span.parent.span_id == root.context.span_id for span in tools + generations)


def test_scripted_late_response_cannot_execute_tools(settings, target, output_root, telemetry, record_property):
    label = "scripted_late_response_cannot_execute_tools"
    record_property("check_name", label)

    def respond(*, messages, tools, timeout_seconds):
        # An uncooperative callback must not keep the solver running or execute a late tool.
        time.sleep(timeout_seconds + 0.1)
        deadline = time.monotonic() + 2
        while docker("inspect", "--format", "{{.State.Running}}", run["solver"]) != "false":
            assert time.monotonic() < deadline, "Watchdog did not stop solver during response wait"
            time.sleep(0.02)
        return tool_response("run_command", {"command": "echo must-not-run-after-deadline"}, "late")

    with run_attempt(settings | {"wall_seconds": 8}, target["network"], target["gateway"], target["endpoints"],
                     target["expected_flag"], output_root, langfuse=telemetry["client"],
                     label=label, public_task="Synthetic deadline check", respond=respond) as run:
        record_property("run_id", run["run_id"])
        assert run_agent("Synthetic deadline check", run["respond"], run["call_tool"]) == "wall_limit"
    assert run["result"]["scripted_turns"] == 1 and run["result"]["tool_calls"] == 0
    spans = save_spans(telemetry, run["directory"], run["result"]["trace_id"])
    generation = next(span for span in spans if span.name == "scripted-response")
    assert attribute(generation, "metadata.discarded") is True
    assert not any(span.attributes.get("langfuse.observation.type") == "tool" for span in spans)
