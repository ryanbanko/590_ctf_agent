"""Plain scripted assistant messages for loop checks; no model backend."""

import json


def tool_response(name: str, arguments: dict, call_id: str) -> dict:
    return {"role": "assistant", "tool_calls": [{
        "id": call_id, "type": "function",
        "function": {"name": name, "arguments": json.dumps(arguments)},
    }]}


def synthetic_response(url: str, *, messages, tools, timeout_seconds):
    """Fixed synthetic recovery flow; candidates come only from tool observations."""
    assert timeout_seconds > 0 and len(tools) == 3
    if messages[-1]["role"] == "user":
        return tool_response("run_command", {"command": "exit 7"}, "failed-command")
    observation = json.loads(messages[-1]["content"])
    previous = messages[-1]["tool_call_id"]
    if previous == "failed-command":
        assert observation["exit_code"] == 7
        source = ("import urllib.request\n"
                  f"print(urllib.request.urlopen({url!r}, timeout=2).read().decode())\n")
        return tool_response("write_file", {"path": "fetch.py", "content": source}, "write")
    if previous == "write":
        assert observation["bytes_written"] > 0
        return tool_response("run_command", {"command": "python fetch.py"}, "fetch")
    if previous == "fetch":
        assert observation["exit_code"] == 0 and json.loads(observation["stdout"])["flag"]
        return tool_response("submit_flag", {"candidate": "wrong-synthetic-candidate"}, "wrong")
    assert previous == "wrong" and observation == {"correct": False}
    fetched = next(message for message in messages if message.get("tool_call_id") == "fetch")
    candidate = json.loads(json.loads(fetched["content"])["stdout"])["flag"]
    response = tool_response("submit_flag", {"candidate": candidate}, "correct")
    response["tool_calls"] += tool_response("run_command", {
        "command": "echo must-not-run-after-success"}, "after-success")["tool_calls"]
    return response
