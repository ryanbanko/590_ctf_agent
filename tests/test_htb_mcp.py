"""HTB MCP client: handshake, error detection and wrappers, with a fake transport."""

import json

import pytest

from ctf_agent import htb_mcp
from ctf_agent.htb_mcp import HtbMcpError, htb_session


def fake_transport(responses, *, record=None):
    """Return a post() that replays queued tools/call results by request order.

    `responses` maps a tool name to the `result` dict the server would return
    for it (or an Exception to raise). The initialize request and the
    initialized notification are answered generically. Each posted payload is
    appended to `record` when given.
    """
    def post(payload):
        if record is not None:
            record.append(payload)
        method = payload.get("method")
        if method == "initialize":
            return [{"jsonrpc": "2.0", "id": payload["id"],
                     "result": {"protocolVersion": htb_mcp.PROTOCOL_VERSION,
                                "serverInfo": {"name": "HTB MCP", "version": "test"}}}]
        if method == "notifications/initialized":
            return []
        name = payload["params"]["name"]
        outcome = responses[name]
        if isinstance(outcome, Exception):
            raise outcome
        return [{"jsonrpc": "2.0", "id": payload["id"], "result": outcome}]

    return post


def text_result(value):
    """A normal HTB result: JSON encoded inside a text content block."""
    return {"content": [{"type": "text", "text": json.dumps(value)}],
            "structuredContent": value if isinstance(value, dict) else None,
            "isError": False}


def test_requires_token(monkeypatch):
    monkeypatch.delenv("HTB_MCP_TOKEN", raising=False)
    with pytest.raises(ValueError, match="HTB_MCP_TOKEN"):
        with htb_session(transport=fake_transport({})):
            pass


def test_handshake_then_call_assigns_sequential_ids():
    record = []
    events = [{"id": 3755, "name": "Duke AI CTF"}]
    transport = fake_transport({"list_ctf_events": text_result(events)}, record=record)
    with htb_session(token="t", transport=transport) as call:
        assert htb_mcp.list_events(call) == events
        assert htb_mcp.list_events(call) == events
    methods = [item["method"] for item in record]
    assert methods == ["initialize", "notifications/initialized", "tools/call", "tools/call"]
    ids = [item["id"] for item in record if item["method"] == "tools/call"]
    assert ids == [2, 3]


def test_upstream_error_with_iserror_false_is_raised():
    # HTB wraps a 500/403 as ordinary content with isError false.
    failure = {"content": [{"type": "text", "text": json.dumps({"error": "Server Error", "status_code": 500})}],
               "structuredContent": {"error": "Server Error", "status_code": 500},
               "isError": False}
    with htb_session(token="t", transport=fake_transport({"start_container": failure})) as call:
        with pytest.raises(HtbMcpError) as info:
            htb_mcp.start_container(call, 79390)
    assert info.value.status_code == 500
    assert "Server Error" in str(info.value)


def test_error_only_in_text_content_is_raised():
    failure = {"content": [{"type": "text", "text": json.dumps({"error": "404 Not Found", "status_code": 404})}],
               "isError": False}
    with htb_session(token="t", transport=fake_transport({"container_status": failure})) as call:
        with pytest.raises(HtbMcpError) as info:
            htb_mcp.container_status(call, 1)
    assert info.value.status_code == 404


def test_mcp_protocol_error_is_raised():
    def post(payload):
        if payload.get("method") == "initialize":
            return [{"jsonrpc": "2.0", "id": payload["id"], "result": {}}]
        if payload.get("method") == "notifications/initialized":
            return []
        return [{"jsonrpc": "2.0", "id": payload["id"],
                 "error": {"code": -32602, "message": "invalid params"}}]

    with htb_session(token="t", transport=post) as call:
        with pytest.raises(HtbMcpError, match="invalid params"):
            htb_mcp.retrieve_ctf(call, 3755)


def test_submit_flag_passes_challenge_and_flag():
    record = []
    verdict = {"message": "Correct!", "isCorrect": True}
    transport = fake_transport({"submit_flag": text_result(verdict)}, record=record)
    with htb_session(token="t", transport=transport) as call:
        assert htb_mcp.submit_flag(call, 79390, "HTB{x}") == verdict
    sent = [item["params"] for item in record if item.get("method") == "tools/call"][0]
    assert sent == {"name": "submit_flag", "arguments": {"challenge_id": 79390, "flag": "HTB{x}"}}


def test_submit_flag_returns_wrong_flag_without_raising():
    # A wrong flag is an error 400; submit_flag must return it, not raise, so the
    # caller can read it as a rejection. Other tools still raise on error.
    wrong = {"content": [{"type": "text", "text": json.dumps({"error": "Wrong flag, sorry!", "status_code": 400})}],
             "structuredContent": {"error": "Wrong flag, sorry!", "status_code": 400},
             "isError": False}
    with htb_session(token="t", transport=fake_transport({"submit_flag": wrong})) as call:
        result = htb_mcp.submit_flag(call, 79390, "HTB{nope}")
    assert result == {"error": "Wrong flag, sorry!", "status_code": 400}


def test_sse_response_is_parsed():
    events = [{"id": 1, "name": "e"}]
    body = ("event: message\n"
            f"data: {json.dumps({'jsonrpc': '2.0', 'id': 1, 'result': {'protocolVersion': htb_mcp.PROTOCOL_VERSION}})}\n\n")
    call_body = ("data: " + json.dumps({"jsonrpc": "2.0", "id": 2, "result": text_result(events)}) + "\n\n")

    class FakeResponse:
        def __init__(self, text):
            self._text = text
            self.headers = {"Content-Type": "text/event-stream"}

        def read(self):
            return self._text.encode()

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    bodies = iter([body, "", call_body])

    def fake_urlopen(request, timeout=None):
        return FakeResponse(next(bodies))

    import urllib.request
    original = urllib.request.urlopen
    urllib.request.urlopen = fake_urlopen
    try:
        post = htb_mcp.urllib_transport(htb_mcp.ENDPOINT, "t")
        with htb_session(token="t", transport=post) as call:
            assert htb_mcp.list_events(call) == events
    finally:
        urllib.request.urlopen = original


def test_token_not_in_repr_of_session_record():
    # The token lives only in the Authorization header built inside the transport;
    # it must not leak into posted JSON-RPC payloads.
    record = []
    transport = fake_transport({"list_ctf_events": text_result([])}, record=record)
    with htb_session(token="super-secret-token", transport=transport) as call:
        htb_mcp.list_events(call)
    assert "super-secret-token" not in json.dumps(record)
