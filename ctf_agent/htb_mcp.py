"""Host-only client for the Hack The Box CTF MCP server (Streamable HTTP).

All functions run on the trusted host. The bearer token is read from
HTB_MCP_TOKEN and never passed to the solver or written to traces. The server
is stateless (no Mcp-Session-Id), so one initialize handshake precedes any
number of tool calls on the same session.

Only the standard library is used for transport; `transport` can be substituted
in tests so no network call is made. HTB wraps upstream failures in a normal
result with isError=false, so errors are detected from the payload's own
`error`/`status_code` fields, not the MCP isError flag.
"""

from contextlib import contextmanager
import json
import os
import urllib.error
import urllib.request

ENDPOINT = "https://mcp.hackthebox.ai/v1/ctf/mcp/"
PROTOCOL_VERSION = "2025-06-18"
# Cloudflare (error 1010) bans the default Python-urllib signature; present a
# normal browser user-agent.
USER_AGENT = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/131.0.0.0 Safari/537.36")


class HtbMcpError(RuntimeError):
    """An HTB tool call failed, either at the MCP layer or upstream in HTB's API."""

    def __init__(self, tool: str, message: str, status_code=None):
        super().__init__(f"{tool}: {message}" + (f" (status {status_code})" if status_code else ""))
        self.tool = tool
        self.status_code = status_code


def urllib_transport(endpoint: str, token: str, *, timeout: float = 30.0):
    """Return a post(payload) -> list[message] function over Streamable HTTP."""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "Authorization": f"Bearer {token}",
        "MCP-Protocol-Version": PROTOCOL_VERSION,
        "User-Agent": USER_AGENT,
    }

    def post(payload: dict) -> list[dict]:
        request = urllib.request.Request(endpoint, data=json.dumps(payload).encode("utf-8"),
                                         method="POST", headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                raw = response.read().decode("utf-8", "replace")
                content_type = response.headers.get("Content-Type", "")
        except urllib.error.HTTPError as error:
            body = error.read().decode("utf-8", "replace")[:2000]
            raise HtbMcpError("transport", f"HTTP {error.code}: {body}", error.code) from None
        except urllib.error.URLError as error:
            raise HtbMcpError("transport", f"could not reach server: {error.reason}") from None
        if "text/event-stream" in content_type:
            return [json.loads(line[5:].strip()) for line in raw.splitlines()
                    if line.startswith("data:") and line[5:].strip()]
        return [json.loads(raw)] if raw.strip() else []

    return post


def _result(messages: list[dict], request_id: int, tool: str):
    for message in messages:
        if message.get("id") == request_id:
            if "error" in message:
                error = message["error"]
                raise HtbMcpError(tool, error.get("message", json.dumps(error)), error.get("code"))
            return message.get("result")
    raise HtbMcpError(tool, "no response for request")


def _unwrap(result, tool: str, raise_on_error: bool = True):
    """Return the parsed payload of a tools/call result.

    HTB returns upstream failures as ordinary text/structured content with
    isError=false, so the `error` field is read from both the structured payload
    and the decoded text content. With raise_on_error (the default) an error is
    raised; with it false the payload is returned as-is so the caller can
    interpret it (submit_flag reports a wrong flag as an error 400, which is a
    normal rejection, not a failure).
    """
    if not isinstance(result, dict):
        raise HtbMcpError(tool, "malformed result")
    structured = result.get("structuredContent")
    content = result.get("content") or []
    text = next((item.get("text") for item in content if item.get("type") == "text"), None)
    payload = structured
    if text is not None:
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            payload = text
    error = None
    if isinstance(structured, dict) and structured.get("error"):
        error = (structured["error"], structured.get("status_code"))
    elif isinstance(payload, dict) and payload.get("error"):
        error = (payload["error"], payload.get("status_code"))
    if error and raise_on_error:
        raise HtbMcpError(tool, error[0], error[1])
    return payload


@contextmanager
def htb_session(*, token: str | None = None, endpoint: str = ENDPOINT, transport=None):
    """Yield a bounded call(name, arguments) function after one initialize handshake.

    `transport` overrides the default urllib transport for tests. The token is
    read from HTB_MCP_TOKEN when not given and is never returned or logged.
    """
    token = token or os.environ.get("HTB_MCP_TOKEN")
    if not token:
        raise ValueError("Set HTB_MCP_TOKEN in the host environment")
    post = transport if transport is not None else urllib_transport(endpoint, token)
    _result(post({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
        "protocolVersion": PROTOCOL_VERSION, "capabilities": {},
        "clientInfo": {"name": "ctf-agent-htb", "version": "0.1"}}}), 1, "initialize")
    post({"jsonrpc": "2.0", "method": "notifications/initialized"})
    state = {"next_id": 2}

    def call(name: str, arguments: dict | None = None, *, raise_on_error: bool = True):
        request_id = state["next_id"]
        state["next_id"] += 1
        messages = post({"jsonrpc": "2.0", "id": request_id, "method": "tools/call",
                         "params": {"name": name, "arguments": arguments or {}}})
        return _unwrap(_result(messages, request_id, name), name, raise_on_error)

    yield call


# Thin wrappers over the HTB tools the launcher uses. Each takes the `call`
# function yielded by htb_session; integer ids match the server's schema.

def list_events(call):
    return call("list_ctf_events")


def retrieve_ctf(call, ctf_id: int):
    return call("retrieve_ctf", {"ctf_id": ctf_id})


def get_download_link(call, challenge_id: int):
    return call("get_download_link", {"challenge_id": challenge_id})


def start_container(call, challenge_id: int):
    return call("start_container", {"challenge_id": challenge_id})


def stop_container(call, challenge_id: int):
    return call("stop_container", {"challenge_id": challenge_id})


def container_status(call, challenge_id: int):
    return call("container_status", {"challenge_id": challenge_id})


def submit_flag(call, challenge_id: int, flag: str):
    # raise_on_error is false: a wrong flag comes back as an error 400, which is
    # a normal rejection the caller interprets, not a transport failure.
    return call("submit_flag", {"challenge_id": challenge_id, "flag": flag}, raise_on_error=False)
