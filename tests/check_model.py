"""Explicit one-attempt live synthetic check; requires operator spending approval."""

import json
import logging
import os
from pathlib import Path
import time
import uuid

import httpx2
from langfuse import Langfuse
from langfuse.openai import OpenAI

from ctf_agent.agent import run_agent
from ctf_agent.attempt import run_attempt
from ctf_agent.config import load_experiment
from ctf_agent.docker import docker
from ctf_agent.agent import make_responder, reject_gateway_errors
from ctf_agent.launch import collect_provenance, read_model_trace
from .fixtures.target import synthetic_target


def check_model(config_path: Path, output_root: Path):
    names = ("LITELLM_TOKEN", "LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY", "LANGFUSE_BASE_URL")
    missing = [name for name in names if not os.getenv(name)]
    if missing:
        raise ValueError("Set host environment variables: " + ", ".join(missing))
    settings, model = load_experiment(config_path)
    # Deliberately small synthetic verification; model/gateway/prices come from
    # the selected run configuration, not a second set of application defaults.
    settings |= {"wall_seconds": 60.0, "command_seconds": 10.0, "max_model_turns": 4}
    model |= {"max_requests": settings["max_model_turns"], "max_output_tokens": 1024,
              "max_input_bytes": 32768, "request_seconds": 20.0}
    directory = output_root / ("model-check-" + uuid.uuid4().hex[:12])
    directory.mkdir(parents=True, mode=0o700)
    # The SDK includes its public project identifier in instrumentation-scope
    # metadata. Only the gateway token and Langfuse secret key are secrets.
    secrets = [os.environ["LITELLM_TOKEN"], os.environ["LANGFUSE_SECRET_KEY"]]
    logging.getLogger("langfuse").setLevel(logging.ERROR)
    client = Langfuse(timeout=10)
    report = {"mode": "live-synthetic-check", "passed": False, "phase": "setup",
              "model_settings": model, "account_daily_limit_usd": 1.0,
              "account_limit_source": "user-confirmed", "model_calls": 0}
    started = time.monotonic()
    run = None
    try:
        report["provenance"] = collect_provenance(settings)
        if not client.auth_check():
            raise RuntimeError("Langfuse authentication failed")
        # No provider requests occur until the guarded solver is running.
        with OpenAI(api_key=os.environ["LITELLM_TOKEN"], base_url=model["base_url"],
                    max_retries=0, timeout=model["request_seconds"],
                    http_client=httpx2.Client(event_hooks={"response": [reject_gateway_errors]})) as model_client:
            respond, usage = make_responder(model_client, model, langfuse_public_key=os.environ["LANGFUSE_PUBLIC_KEY"])
            with synthetic_target(settings) as target:
                task = (f'Retrieve the synthetic flag from http://{target["address"]}:8000/ and submit it. '
                        'Use Python urllib.request in the isolated solver to fetch the JSON response. '
                        'The response has a flag field. This is a synthetic setup check.')
                report["phase"] = "synthetic-attempt"
                with run_attempt(settings, target["network"], target["endpoints"],
                                 target["expected_flag"], directory, langfuse=client,
                                 label="live-model-synthetic-check", public_task=task,
                                 respond=respond, model_usage=usage) as run:
                    run_agent(task, run["respond"], run["call_tool"])
                expected = target["expected_flag"]  # Trusted audit only; never exported separately.
        result = run["result"]
        report.update(model_calls=result["model_calls"], run_id=result["run_id"], trace_id=result["trace_id"],
                      phase="hosted-readback")
        rows = read_model_trace(client, result["trace_id"], result["model_calls"], result["tool_calls"], directory)
        roots = [row for row in rows if row["name"] == "attempt"]
        generations = [row for row in rows if row["type"] == "GENERATION"]
        tools = [row for row in rows if row["type"] == "TOOL"]
        serialized = json.dumps(rows)
        root = roots[0] if len(roots) == 1 else None
        checks = {
            "verified_success": result["verified_success"],
            "one_generation_per_request": len(generations) == result["model_calls"] and not result["scripted_turns"],
            "adaptive_tool_interaction": len(generations) >= 2 and any(row["name"] == "run_command" for row in tools),
            "parentage": root is not None and all(row.get("parentObservationId") == root["id"] for row in rows if row is not root),
            "complete_model_records": all(row.get("model") and row.get("input") and row.get("output")
                                           and row.get("usageDetails") for row in generations),
            "expected_answer_not_in_root": root is not None and expected not in json.dumps(root),
            "credentials_absent": all(secret not in serialized for secret in secrets),
            "within_limits": 0 < result["model_calls"] <= 4,
            "usage_available": result["usage_complete"] and result["tokens"]["input"] > 0,
        }
        report["checks"] = checks
        report["trace_url"] = client.get_trace_url(trace_id=result["trace_id"])
        report["observation_count"] = len(rows)
        report["passed"] = all(checks.values())
        report["phase"] = "finished"
    except Exception as error:
        report["error_type"] = type(error).__name__
        raise RuntimeError(f'Model check failed during {report["phase"]}; see {directory}/check.json') from None
    finally:
        try:
            client.shutdown()
        finally:
            if run is not None:
                report["result"] = run["result"]
                report["model_calls"] = run["result"]["model_calls"]
            containers = docker("ps", "--all", "--filter", "label=ctf590.managed=true", "--format", "{{.Names}}")
            networks = docker("network", "ls", "--filter", "label=ctf590.managed=true", "--format", "{{.Name}}")
            report["cleanup_verified"] = not containers and not networks
            report["passed"] = report["passed"] and report["cleanup_verified"]
            report["total_seconds"] = round(time.monotonic() - started, 6)
            (directory / "check.json").write_text(json.dumps(report, indent=2) + "\n")
            print(f"Evidence: {directory}", flush=True)
    if not report["passed"]:
        raise RuntimeError("Model check incomplete; see check.json")
    print(f'Live synthetic check verified: {report["trace_url"]}', flush=True)
    return directory
