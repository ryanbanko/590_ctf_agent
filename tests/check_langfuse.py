"""Send one existing synthetic flow and audit its hosted Langfuse observations."""

from datetime import datetime, timezone
from functools import partial
import importlib.metadata
import json
import os
from pathlib import Path
import time
import uuid

from langfuse import Langfuse

from ctf_agent.agent import run_agent
from ctf_agent.attempt import run_attempt
from ctf_agent.config import load_settings
from ctf_agent.docker import docker
from .check_controls import collect_provenance
from .fixtures.responses import synthetic_response
from .fixtures.target import synthetic_target


def audit_trace(observations: list, result: dict, expected_flag: str, secret_key: str) -> dict | None:
    """Return checks once the complete trace is readable; reject mismatched evidence."""
    roots = [item for item in observations if item.name == "attempt"]
    tools = sorted((item for item in observations if item.type == "TOOL"),
                   key=lambda item: (item.metadata or {}).get("step", 0))
    generations = sorted((item for item in observations if item.type == "GENERATION"),
                         key=lambda item: item.start_time)
    required_events = {"guard_ready", "sandbox_ready", "attempt_stopping", "sandbox_cleanup"}
    if (len(roots) != 1 or len(tools) != result["tool_calls"]
            or len(generations) != result["scripted_turns"]
            or not required_events <= {item.name for item in observations}
            or any(item.end_time is None for item in observations)
            or any(item.output is None for item in roots + tools + generations)):
        return None
    root = roots[0]
    root_output = json.loads(root.output)
    submissions = [item for item in tools if item.name == "submit_flag"]
    checks = {
        "trace_ids_match": all(item.trace_id == result["trace_id"] for item in observations),
        "parentage": root.parent_observation_id is None and all(
            item.parent_observation_id == root.id for item in observations if item is not root),
        "summary_matches": all(root_output.get(key) == result[key] for key in (
            "run_id", "trace_id", "termination_reason", "verified_success", "tool_calls", "scripted_turns")),
        "verified_success": result["verified_success"] and result["termination_reason"] == "success",
        "five_turns_and_tools": len(tools) == len(generations) == 5,
        "tool_steps": [(item.metadata or {}).get("step") for item in tools] == [1, 2, 3, 4, 5],
        "tool_inputs_and_outputs": all(item.input is not None and item.output is not None for item in tools),
        "full_history": [len(json.loads(item.input)["messages"]) for item in generations] == [2, 4, 6, 8, 10],
        "submission_verdicts": [json.loads(item.output) for item in submissions] == [
            {"correct": False}, {"correct": True}],
        "verified_observed_candidate": len(submissions) == 2 and json.loads(submissions[1].input)["candidate"] == expected_flag,
        "expected_answer_not_in_root": expected_flag not in root.model_dump_json(),
        "secret_key_not_in_trace": all(secret_key not in item.model_dump_json() for item in observations),
        "no_model_calls": result["model_calls"] == 0 and result["cost_usd"] == 0,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError("Hosted trace checks failed: " + ", ".join(failed))
    return checks


def wait_for_trace(client, result: dict, expected_flag: str, secret_key: str, seconds: float = 90):
    """Poll the documented observations API, including cursor pages, until complete."""
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        observations, cursor = [], None
        while True:
            page = client.api.observations.get_many(trace_id=result["trace_id"], cursor=cursor,
                limit=1000, fields="core,basic,time,io,metadata", expand_metadata="config,image_ids",
                request_options={"timeout_in_seconds": 10, "max_retries": 0})
            observations.extend(page.data)
            cursor = page.meta.cursor
            if cursor is None:
                break
            if time.monotonic() >= deadline:
                raise TimeoutError("Hosted trace pagination exceeded the verification deadline")
        checks = audit_trace(observations, result, expected_flag, secret_key)
        if checks is not None:
            return observations, checks
        time.sleep(min(2, max(0, deadline - time.monotonic())))
    raise TimeoutError("Complete hosted trace was not readable before the verification deadline")


def check_langfuse(config_path: Path, output_root: Path) -> Path:
    missing = [name for name in ("LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY", "LANGFUSE_BASE_URL")
               if not os.getenv(name)]
    if missing:
        raise ValueError("Set these host environment variables: " + ", ".join(missing))
    directory = output_root / ("langfuse-check-" + uuid.uuid4().hex[:12])
    directory.mkdir(parents=True, exist_ok=False, mode=0o700)
    client = Langfuse(timeout=10)
    report = {"mode": "hosted-synthetic-check", "time_utc": datetime.now(timezone.utc).isoformat(),
              "langfuse_version": importlib.metadata.version("langfuse"), "passed": False,
              "phase": "authentication", "model_calls": 0, "cost_usd": 0.0}
    started = time.monotonic()
    try:
        if not client.auth_check():
            raise RuntimeError("Langfuse authentication failed")
        report["authenticated"] = True
        report["phase"] = "synthetic-attempt"
        settings = load_settings(config_path)
        report["provenance"] = collect_provenance(settings)
        with synthetic_target(settings) as target:
            url = f'http://{target["address"]}:8000/'
            task = f"Retrieve the synthetic flag from {url} and submit it."
            with run_attempt(settings, target["network"], target["gateway"], target["endpoints"],
                             target["expected_flag"], directory, langfuse=client, label="hosted-synthetic-check",
                             public_task=task, respond=partial(synthetic_response, url)) as run:
                reason = run_agent(task, run["respond"], run["call_tool"])
                if reason != "success":
                    raise RuntimeError("Synthetic verification did not succeed")
            result = run["result"]
            # Keep only in trusted memory for the readback audit; never export an answer key.
            expected = target["expected_flag"]
        report.update(run_id=result["run_id"], trace_id=result["trace_id"], phase="hosted-readback")
        print(f'Run: {result["run_id"]}; trace: {result["trace_id"]}', flush=True)
        observations, checks = wait_for_trace(client, result, expected, os.environ["LANGFUSE_SECRET_KEY"])
        (directory / "observations.json").write_text(
            "[\n" + ",\n".join(item.model_dump_json(by_alias=True) for item in observations) + "\n]\n")
        containers = docker("ps", "--all", "--filter", "label=ctf590.managed=true", "--format", "{{.Names}}")
        networks = docker("network", "ls", "--filter", "label=ctf590.managed=true", "--format", "{{.Name}}")
        report["cleanup_verified"] = not containers and not networks
        report["checks"] = checks
        report["observation_count"] = len(observations)
        report["trace_url"] = client.get_trace_url(trace_id=result["trace_id"])
        report["passed"] = report["cleanup_verified"]
        report["phase"] = "finished"
    except Exception as error:
        report["error_type"] = type(error).__name__
        raise RuntimeError(f'Langfuse check failed during {report["phase"]}; see {directory}/check.json') from None
    finally:
        try:
            client.shutdown()
        finally:
            report["total_seconds"] = round(time.monotonic() - started, 6)
            (directory / "check.json").write_text(json.dumps(report, indent=2) + "\n")
            print(f"Evidence: {directory}", flush=True)
    if not report["passed"]:
        raise RuntimeError(f"Cleanup verification failed; see {directory}/check.json")
    print(f'Hosted trace verified: {report["trace_url"]}', flush=True)
    return directory
