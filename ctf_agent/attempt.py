"""Trusted attempt runner: resources, bounded functions, verification, and results."""

from contextlib import contextmanager, nullcontext
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import threading
import time
import uuid

from langfuse import Langfuse

from .agent import AttemptStopped, validate_response
from .config import validate_settings
from .docker import docker
from .sandbox import audit_network, close_sandbox, make_sandbox, start_sandbox, stop_solver, snapshot_packages
from .tools import execute_tool, validate_arguments


def stop_attempt(state: dict, reason: str):
    with state["lock"]:
        if state["result"]["termination_reason"] is not None:
            return
        state["result"]["termination_reason"] = reason
    state["observation"].create_event(name="attempt_stopping", metadata={"reason": reason})
    if not stop_solver(state["sandbox"]):
        with state["lock"]:
            state["result"]["termination_reason"] = "infrastructure_error"


def remaining_seconds(state: dict) -> float:
    if state["result"]["termination_reason"] is not None:
        raise AttemptStopped(state["result"]["termination_reason"])
    remaining = state["deadline"] - time.monotonic()
    if remaining <= 0:
        stop_attempt(state, "wall_limit")
        raise AttemptStopped(state["result"]["termination_reason"])
    return remaining


def watch_deadline(state: dict):
    if not state["watchdog_done"].wait(max(0, state["deadline"] - time.monotonic())):
        stop_attempt(state, "wall_limit")


@contextmanager
def run_attempt(settings: dict, network: str, endpoints: list[dict],
                expected_flag: str, output_root: Path, *, langfuse: Langfuse,
                label: str = "synthetic", public_task: str = "Synthetic controls check", respond=None,
                model_usage: dict | None = None, mode: str = "synthetic-controls"):
    """Own one run and yield bounded respond/call_tool functions plus result metadata.

    The answer stays in this trusted scope. Neither the loop nor Langfuse receives
    the private state dictionary. The supplied Langfuse client owns detailed traces;
    summary.json and bounded command-output artifacts are retained locally. Live sources supply model_usage;
    their Langfuse OpenAI integration creates generations automatically.
    """
    validate_settings(settings)
    run_id = uuid.uuid4().hex[:12]
    directory = output_root / run_id
    directory.mkdir(parents=True, exist_ok=False, mode=0o700)
    started = time.monotonic()
    result = {"run_id": run_id, "challenge_id": label, "mode": mode,
              "termination_reason": None, "tool_calls": 0, "model_calls": 0,
              "agent_mode": None, "scripted_turns": 0, "tokens": None, "cost_usd": 0.0,
              "cleanup_errors": []}
    try:
        with langfuse.start_as_current_observation(name="attempt", input={"task": public_task},
                metadata={"run_id": run_id, "challenge_id": label, "config": settings,
                          "mode": mode}) as observation:
            result["trace_id"] = observation.trace_id
            if not observation.trace_id or observation.trace_id == "0" * 32:
                raise RuntimeError("An active Langfuse tracing client is required")
            state = {"result": result, "observation": observation, "deadline": started + settings["wall_seconds"],
                     "lock": threading.Lock(), "watchdog_done": threading.Event()}
            sandbox = make_sandbox(run_id, observation, lambda reason: stop_attempt(state, reason))
            state["sandbox"] = sandbox
            sandbox["directory"] = directory
            used_ids = set()

            def call_tool(name: str, arguments: dict) -> dict:
                remaining_seconds(state)
                if result["tool_calls"] >= settings["max_tool_calls"]:
                    stop_attempt(state, "tool_limit")
                    raise AttemptStopped(result["termination_reason"])
                result["tool_calls"] += 1
                validation_error = None
                try:
                    validate_arguments(name, arguments, settings)
                except (ValueError, TypeError) as error:
                    validation_error = {"error": {"kind": "validation_error", "message": str(error)}}
                # Rejected arguments never become trace input; accepted inputs are bounded.
                with observation.start_as_current_observation(name=str(name)[:100], as_type="tool",
                        input=arguments if validation_error is None else None,
                        metadata={"step": result["tool_calls"]}) as tool:
                    if validation_error is not None:
                        tool.update(output=validation_error, level="WARNING", status_message="validation_error")
                        return validation_error
                    try:
                        audit_network(sandbox, remaining_seconds(state))
                        seconds_left = remaining_seconds(state)
                        if name == "submit_flag":
                            returned = {"correct": arguments["candidate"] == expected_flag}
                        else:
                            returned = execute_tool(name, arguments, settings, sandbox, seconds_left)
                        audit_network(sandbox, remaining_seconds(state))
                    except (RuntimeError, TimeoutError, subprocess.TimeoutExpired, json.JSONDecodeError) as error:
                        if result["termination_reason"] is None:
                            stop_attempt(state, "wall_limit" if time.monotonic() >= state["deadline"]
                                         else "infrastructure_error")
                        tool.update(output={"error": {"kind": result["termination_reason"],
                                                     "message": str(error)[:2000]}}, level="ERROR")
                        raise AttemptStopped(result["termination_reason"]) from None
                    tool.update(output=returned)
                    if name == "submit_flag" and returned.get("correct") is True:
                        stop_attempt(state, "success")
                        if result["termination_reason"] != "success":
                            raise AttemptStopped(result["termination_reason"])
                    return returned

            def request_response(*, messages: list[dict], tools: list[dict]) -> dict:
                timeout = remaining_seconds(state)
                tools = deepcopy(tools)
                for tool in tools:
                    if tool["function"]["name"] == "run_command":
                        tool["function"]["parameters"]["properties"]["timeout_seconds"].update(
                            maximum=settings["command_seconds"], default=settings["command_seconds"])
                if result["scripted_turns"] + result["model_calls"] >= settings["max_model_turns"]:
                    stop_attempt(state, "model_turn_limit")
                    raise AttemptStopped(result["termination_reason"])
                result["agent_mode"] = "model" if model_usage is not None else "scripted"
                if model_usage is None:
                    result["scripted_turns"] += 1
                context = nullcontext() if model_usage is not None else observation.start_as_current_observation(
                        name="scripted-response", as_type="generation",
                        input={"messages": messages, "tools": tools},
                        metadata={"turn": result["scripted_turns"], "mode": "scripted",
                                  "timeout_seconds": timeout})
                with context as generation:
                    try:
                        response = respond(messages=messages, tools=tools, timeout_seconds=timeout)
                    except AttemptStopped as stopped:
                        stop_attempt(state, str(stopped))
                        raise AttemptStopped(result["termination_reason"]) from None
                    except Exception as error:
                        observation.create_event(name="response_source_error", level="ERROR",
                                                 metadata={"exception": type(error).__name__})
                        if generation is not None:
                            generation.update(level="ERROR", status_message="response_source_error",
                                              metadata={"exception": type(error).__name__})
                        if result["termination_reason"] is None:
                            stop_attempt(state, "wall_limit" if time.monotonic() >= state["deadline"]
                                         else "response_source_error")
                        raise AttemptStopped(result["termination_reason"]) from None
                    finally:
                        if model_usage is not None:
                            result.update(model_usage)
                            result["cost_kind"] = "estimated_from_gateway_rates"
                    try:
                        remaining_seconds(state)
                    except AttemptStopped:
                        observation.create_event(name="response_discarded", metadata={"reason": str(result["termination_reason"])})
                        if generation is not None:
                            generation.update(metadata={"discarded": True}, status_message=result["termination_reason"])
                        raise
                    try:
                        validate_response(response, used_ids)
                    except (ValueError, TypeError, RecursionError) as error:
                        observation.create_event(name="response_rejected", level="ERROR",
                                                 metadata={"validation_error": str(error)[:200]})
                        if generation is not None:
                            generation.update(level="ERROR", status_message="response_error",
                                              metadata={"validation_error": str(error)[:200]})
                        stop_attempt(state, "response_error")
                        raise AttemptStopped(result["termination_reason"]) from None
                    used_ids.update(call["id"] for call in response.get("tool_calls", []))
                    if generation is not None:
                        generation.update(output=response)
                    if not response.get("tool_calls"):
                        stop_attempt(state, "completed_without_success")
                        if result["termination_reason"] != "completed_without_success":
                            raise AttemptStopped(result["termination_reason"])
                    return response

            run = {"run_id": run_id, "directory": directory, "result": result,
                   "solver": sandbox["solver"], "guard": sandbox["guard"],
                   "respond": request_response, "call_tool": call_tool,
                   "remaining_seconds": lambda: remaining_seconds(state),
                   "stop": lambda reason: stop_attempt(state, reason)}
            watchdog = threading.Thread(target=watch_deadline, args=(state,), daemon=True)
            watchdog.start()
            try:
                image_ids = {}
                for role in ("solver", "guard"):
                    image_ids[role] = docker("image", "inspect", "--format", "{{.Id}}", settings[f"{role}_image"],
                                            timeout=min(5, remaining_seconds(state)))
                observation.update(metadata={"image_ids": image_ids})
                start_sandbox(sandbox, settings, network, endpoints, lambda: remaining_seconds(state))
                yield run
            except BaseException as error:
                if result["termination_reason"] is None:
                    stop_attempt(state, "user_cancel" if isinstance(error, KeyboardInterrupt) else "infrastructure_error")
                observation.update(level="ERROR", status_message=type(error).__name__)
                raise
            finally:
                if result["termination_reason"] is None:
                    stop_attempt(state, "completed_without_success")
                state["watchdog_done"].set()
                watchdog.join(timeout=4)
                result["active_seconds"] = round(time.monotonic() - started, 6)
                cleanup_started = time.monotonic()
                result["solver_restarts"] = sandbox["restarts"]
                result["captured_output_bytes"] = sandbox["captured_output_bytes"]
                snapshot_packages(sandbox, "final", 2)
                result["cleanup_errors"] = close_sandbox(sandbox)
                result["cleanup_seconds"] = round(time.monotonic() - cleanup_started, 6)
                result["verified_success"] = result["termination_reason"] == "success"
                observation.update(output=result, level="ERROR" if result["cleanup_errors"] else "DEFAULT")
                if result["cleanup_errors"]:
                    raise RuntimeError("Attempt cleanup incomplete; see summary.json")
    finally:
        if result["termination_reason"] is None:
            result["termination_reason"] = "infrastructure_error"
        result.setdefault("verified_success", False)
        flush_started = time.monotonic()
        try:
            langfuse.flush()
        finally:
            result["trace_flush_seconds"] = round(time.monotonic() - flush_started, 6)
            result["total_seconds"] = round(time.monotonic() - started, 6)
            (directory / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
