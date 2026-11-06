"""Basic Responses integration checks using real SDKs and an offline HTTP transport."""

import json

import httpx2
from langfuse.openai import OpenAI
from langfuse import Langfuse
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
import pytest

from ctf_agent.agent import AttemptStopped, run_agent
from ctf_agent.agent import make_responder, reject_gateway_errors
from .fixtures.tracing import attribute, read_spans


def sdk_response(output, *, status="completed", usage=True):
    return {"id": "resp_test", "object": "response", "created_at": 1,
            "model": "gpt-6-luna", "status": status, "output": output,
            "usage": {"input_tokens": 100, "output_tokens": 20, "total_tokens": 120,
                      "input_tokens_details": {"cached_tokens": 10},
                      "output_tokens_details": {"reasoning_tokens": 5}} if usage else None}


def test_native_reasoning_and_tool_results_reach_next_request_with_one_generation_per_call(local_attempt, telemetry, model_settings):
    requests = []
    purpose = "I will submit this candidate to learn whether the evaluator accepts it."
    outputs = [
        [{"id": "rs_test", "type": "reasoning", "summary": [{"type": "summary_text",
          "text": "Check the tool result before deciding what to do next."}], "encrypted_content": "opaque-test-context"},
         {"id": "msg_purpose", "type": "message", "role": "assistant", "status": "completed",
          "content": [{"type": "output_text", "text": purpose, "annotations": []}]},
         {"type": "function_call", "call_id": "call_wrong", "name": "submit_flag", "arguments": '{"candidate":"wrong"}'}],
        [{"type": "function_call", "call_id": "call_correct", "name": "submit_flag",
          "arguments": '{"candidate":"private-expected-answer"}'}],
    ]

    def handle(request):
        assert request.url.path == "/v1/responses"
        data = json.loads(request.content)
        assert data["store"] is False and data["max_output_tokens"] == model_settings["max_output_tokens"]
        assert data["reasoning"] == {"effort": model_settings["reasoning_effort"], "summary": "auto"} and not data["parallel_tool_calls"]
        assert all(tool["type"] == "function" and tool["strict"] is False for tool in data["tools"])
        assert "private-expected-answer" not in request.content.decode()
        requests.append(data)
        return httpx2.Response(200, json=sdk_response(outputs[len(requests) - 1]))

    with OpenAI(api_key="dummy-gateway-key", base_url=model_settings["base_url"], max_retries=0,
                http_client=httpx2.Client(transport=httpx2.MockTransport(handle))) as client:
        respond, usage = make_responder(client, model_settings, langfuse_public_key="pk-lf-ctf590-local")
        with local_attempt(respond, model_usage=usage) as run:
            assert run_agent("public", run["respond"], run["call_tool"]) == "success"
    assert requests[1]["input"][-4:] == [*outputs[0],
        {"type": "function_call_output", "call_id": "call_wrong", "output": '{"correct": false}'}]
    result = run["result"]
    assert result["model_calls"] == result["tool_calls"] == 2 and result["scripted_turns"] == 0
    assert result["tokens"] == {"input": 200, "output": 40, "cached_input": 20, "reasoning": 10}
    assert result["cost_usd"] == pytest.approx(2 * (90 * model_settings["input_usd_per_million"]
        + 10 * model_settings["cached_input_usd_per_million"]
        + 20 * model_settings["output_usd_per_million"]) / 1_000_000)
    assert "cost_reserved_usd" not in result
    spans = read_spans(telemetry, result["trace_id"])
    root = next(span for span in spans if span.name == "attempt")
    generations = [span for span in spans if span.name == "model-response"]
    assert len(generations) == 2 and not any(span.name == "scripted-response" for span in spans)
    assert all(span.parent.span_id == root.context.span_id for span in generations)
    assert all(attribute(span, "usage_details") is not None for span in generations)
    assert "Check the tool result before deciding what to do next." in generations[0].to_json()
    assert purpose in generations[0].to_json()


@pytest.mark.parametrize("override,reason", [
    ({"max_requests": 0}, "model_request_limit"),
    ({"max_input_bytes": 1}, "model_input_limit"),
])
def test_caps_prevent_http_requests(override, reason, model_settings):
    def unexpected(request):
        pytest.fail("Budget rejection sent an HTTP request")

    with OpenAI(api_key="dummy", max_retries=0,
                http_client=httpx2.Client(transport=httpx2.MockTransport(unexpected))) as client:
        respond, usage = make_responder(client, model_settings | override)
        with pytest.raises(AttemptStopped, match=reason):
            respond(messages=[{"role": "user", "content": "public"}], tools=[], timeout_seconds=1)
        assert usage["model_calls"] == 0


def test_timeout_is_not_retried_and_unknown_usage_is_not_free(local_attempt, telemetry, model_settings):
    requests = []

    def timeout(request):
        requests.append(request)
        raise httpx2.ReadTimeout("synthetic timeout", request=request)

    with OpenAI(api_key="dummy", max_retries=0,
                http_client=httpx2.Client(transport=httpx2.MockTransport(timeout))) as client:
        respond, usage = make_responder(client, model_settings, langfuse_public_key="pk-lf-ctf590-local")
        with local_attempt(respond, model_usage=usage) as run:
            assert run_agent("public", run["respond"], run["call_tool"]) == "response_source_error"
    assert len(requests) == 1 and run["result"]["model_calls"] == 1
    assert run["result"]["cost_usd"] is None and not run["result"]["usage_complete"]
    assert run["result"]["tool_calls"] == 0


def test_late_native_response_keeps_usage_but_cannot_execute_tools(local_attempt, model_settings):
    def late(request):
        run["stop"]("scope_violation")
        return httpx2.Response(200, json=sdk_response([{
            "type": "function_call", "call_id": "late", "name": "run_command", "arguments": '{"command":"echo late"}'}]))

    with OpenAI(api_key="dummy", max_retries=0,
                http_client=httpx2.Client(transport=httpx2.MockTransport(late))) as client:
        respond, usage = make_responder(client, model_settings, langfuse_public_key="pk-lf-ctf590-local")
        with local_attempt(respond, model_usage=usage) as run:
            assert run_agent("public", run["respond"], run["call_tool"]) == "scope_violation"
    assert run["result"]["model_calls"] == 1 and run["result"]["tokens"]["output"] == 20
    assert run["result"]["cost_usd"] > 0 and run["result"]["tool_calls"] == 0


def test_raw_provider_error_does_not_reach_automatic_tracing(model_settings):
    secret = "dummy-sensitive-gateway-key"
    exporter = InMemorySpanExporter()
    tracing = Langfuse(public_key="pk-lf-model-masking", secret_key="sk-lf-local",
                       tracer_provider=TracerProvider(), span_exporter=exporter)

    def denied(request):
        return httpx2.Response(401, json={"error": {"message": "Reflected credential: " + secret}})

    try:
        with OpenAI(api_key=secret, max_retries=0,
                    http_client=httpx2.Client(transport=httpx2.MockTransport(denied),
                        event_hooks={"response": [reject_gateway_errors]})) as client:
            respond, usage = make_responder(client, model_settings, langfuse_public_key="pk-lf-model-masking")
            with tracing.start_as_current_observation(name="mask-check"):
                with pytest.raises(RuntimeError, match="gateway_http_401"):
                    respond(messages=[{"role": "user", "content": "public"}], tools=[], timeout_seconds=1)
        tracing.flush()
        exported = "".join(span.to_json() for span in exporter.get_finished_spans())
        assert "gateway_http_401" in exported and secret not in exported
        assert usage["model_calls"] == 1 and usage["cost_usd"] is None
    finally:
        tracing.shutdown()


@pytest.mark.parametrize('missing_call', [1, 2])
def test_valid_responses_continue_with_unknown_usage(local_attempt, missing_call, model_settings):
    calls = []

    def handle(request):
        calls.append(request)
        number = len(calls)
        output = [{'type': 'function_call', 'call_id': f'call_{number}', 'name': 'submit_flag',
                   'arguments': json.dumps({'candidate': 'wrong' if number == 1 else 'private-expected-answer'})}]
        return httpx2.Response(200, json=sdk_response(output, usage=number != missing_call))

    with OpenAI(api_key='dummy', max_retries=0,
                http_client=httpx2.Client(transport=httpx2.MockTransport(handle))) as client:
        respond, usage = make_responder(client, model_settings, langfuse_public_key='pk-lf-ctf590-local')
        with local_attempt(respond, model_usage=usage) as run:
            assert run_agent('public', run['respond'], run['call_tool']) == 'success'
    assert run['result']['verified_success'] and run['result']['model_calls'] == 2
    assert run['result']['tokens'] is None and run['result']['cost_usd'] is None
    assert run['result']['usage_complete'] is False
    assert run['result']['tool_calls'] == 2
