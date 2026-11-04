"""One host-side Responses adapter with a conservative request/spending budget."""

import json

from .agent import AttemptStopped


# Approved synthetic-check settings; these are not a scored configuration.
MODEL_SETTINGS = {
    "model": "gpt-6-luna",
    "base_url": "https://litellm.oit.duke.edu/v1",
    "reasoning_effort": "low",
    "max_requests": 4,
    "max_output_tokens": 1024,
    "max_input_bytes": 32768,
    "request_seconds": 20.0,
    "max_cost_usd": 0.10,
    "input_usd_per_million": 0.10,
    "output_usd_per_million": 0.50,
    "cached_input_usd_per_million": 0.01,
}


def reject_gateway_errors(response):
    """Retain HTTP status without sending a raw provider error body to tracing."""
    if response.is_error:
        raise RuntimeError(f"gateway_http_{response.status_code}")


def responses_input(messages: list[dict]) -> list[dict]:
    """Replay native output, including reasoning, alongside linked tool results."""
    items = []
    for message in messages:
        if message["role"] == "assistant":
            items.extend(message["response_items"])
        elif message["role"] == "tool":
            items.append({"type": "function_call_output", "call_id": message["tool_call_id"],
                          "output": message["content"]})
        else:
            items.append(message)
    return items


def make_responder(client, settings: dict = MODEL_SETTINGS, *, langfuse_public_key: str | None = None):
    """Return a bounded source and its non-secret usage record, fresh per attempt.

    The supplied client must use Langfuse's OpenAI integration and max_retries=0.
    Reservations include failures/timeouts; unknown usage is never reported as free.
    """
    settings = dict(settings)
    usage = {"model_settings": settings, "model_calls": 0, "cost_usd": 0.0,
             "cost_reserved_usd": 0.0, "usage_complete": True,
             "tokens": {"input": 0, "output": 0, "cached_input": 0, "reasoning": 0}}

    def respond(*, messages, tools, timeout_seconds):
        if usage["model_calls"] >= settings["max_requests"]:
            raise AttemptStopped("model_request_limit")
        request = {"model": settings["model"], "input": responses_input(messages),
                   "tools": [{"type": "function", **tool["function"], "strict": False} for tool in tools],
                   "reasoning": {"effort": settings["reasoning_effort"]},
                   "max_output_tokens": settings["max_output_tokens"],
                   "store": False, "include": ["reasoning.encrypted_content"],
                   "parallel_tool_calls": False}
        input_bytes = len(json.dumps(request, ensure_ascii=True).encode())
        if input_bytes > settings["max_input_bytes"]:
            raise AttemptStopped("model_input_limit")
        # Byte-level tokenization needs no more than one token per input byte.
        # Add 1024 tokens for framing and price all input at the 1.25x cache-write
        # rate. No cache discount is assumed when reserving the request's cost.
        reserved = ((input_bytes + 1024) * settings["input_usd_per_million"] * 1.25
                    + settings["max_output_tokens"] * settings["output_usd_per_million"]) / 1_000_000
        if usage["cost_reserved_usd"] + reserved > settings["max_cost_usd"]:
            raise AttemptStopped("model_cost_limit")
        usage["model_calls"] += 1
        usage["cost_reserved_usd"] += reserved
        try:
            response = client.responses.create(**request, name="model-response",
                langfuse_public_key=langfuse_public_key,
                timeout=min(timeout_seconds, settings["request_seconds"]))
        except Exception:
            usage.update(cost_usd=None, usage_complete=False)
            raise
        if response.usage is None:
            usage.update(cost_usd=None, usage_complete=False)
            raise AttemptStopped("model_usage_missing")
        returned = response.usage
        cached = getattr(returned.input_tokens_details, "cached_tokens", 0) or 0
        reasoning = getattr(returned.output_tokens_details, "reasoning_tokens", 0) or 0
        for field, count in {"input": returned.input_tokens, "output": returned.output_tokens,
                             "cached_input": cached, "reasoning": reasoning}.items():
            usage["tokens"][field] += count
        if usage["cost_usd"] is not None:
            usage["cost_usd"] += ((returned.input_tokens - cached) * settings["input_usd_per_million"]
                + cached * settings["cached_input_usd_per_million"]
                + returned.output_tokens * settings["output_usd_per_million"]) / 1_000_000
        if response.status != "completed":
            raise AttemptStopped("model_response_incomplete")
        items = [item.model_dump(mode="json", exclude_none=True) for item in response.output]
        if any(item["type"] not in {"message", "function_call", "reasoning"} for item in items):
            raise AttemptStopped("model_response_unsupported")
        return {"role": "assistant", "content": response.output_text,
                "response_items": items,
                "tool_calls": [{"id": item["call_id"], "type": "function",
                                "function": {"name": item["name"], "arguments": item["arguments"]}}
                               for item in items if item["type"] == "function_call"]}

    return respond, usage
