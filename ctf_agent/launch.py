"""One challenge launcher: public task, isolated tools, and trusted evaluation."""

from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import time
import uuid

import httpx2
from langfuse import Langfuse
from langfuse.openai import OpenAI

from .agent import make_responder, reject_gateway_errors, run_agent
from .attempt import run_attempt
from .challenge import challenge_target, contestant_files, load_challenge, public_task, stage_files
from .config import load_experiment
from .docker import docker


def collect_provenance(settings: dict, *, target_images: dict | None = None) -> dict:
    images = {}
    references = {role: settings[f"{role}_image"] for role in ("solver", "guard")}
    references.update({"target": settings["target_image"]} if target_images is None else target_images)
    for role, reference in references.items():
        images[role] = json.loads(docker("image", "inspect", "--format",
            '{"id":{{json .Id}},"architecture":{{json .Architecture}}}', reference))
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True)
    changed = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, check=True)
    hashes = {}
    for pattern in ["ctf_agent/*.py", "docker/*.py", "docker/*.Dockerfile", "tests/**/*.py",
                    "configs/*.toml", "configs/*.json", "pyproject.toml", "uv.lock"]:
        for path in sorted(Path(".").glob(pattern)):
            hashes[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
    return {"images": images, "commit": commit.stdout.strip() if commit.returncode == 0 else None,
            "working_tree_dirty": bool(changed.stdout), "source_sha256": hashes,
            "docker": docker("version", "--format", "{{.Server.Version}}"), "config": settings}


def read_model_trace(trace_id: str, model_calls: int, tool_calls: int, directory: Path):
    """Export a complete trace through the pinned official CLI, including failures."""
    environment = dict(os.environ, LANGFUSE_HOST=os.environ["LANGFUSE_BASE_URL"])
    since = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    until = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
    command = ["npx", "--yes", "@langfuse/cli@1.3.1", "api", "observations", "list",
               "--trace-id", trace_id, "--from-start-time", since, "--to-start-time", until,
               "--fields", "core,basic,time,io,metadata,model,usage",
               "--expand-metadata", "config,image_ids,model_settings", "--all", "--max-items", "100", "--json"]
    deadline = time.monotonic() + 90
    while time.monotonic() < deadline:
        completed = subprocess.run(command, env=environment, capture_output=True, text=True,
                                   timeout=min(25, max(1, deadline - time.monotonic())))
        if completed.returncode:
            raise RuntimeError("Langfuse CLI readback failed; raw error omitted")
        payload = json.loads(completed.stdout)
        rows = payload.get("body", payload)["data"]
        roots = [row for row in rows if row["name"] == "attempt"]
        generations = [row for row in rows if row["type"] == "GENERATION"]
        tools = [row for row in rows if row["type"] == "TOOL"]
        if (len(roots) == 1 and len(generations) == model_calls and len(tools) == tool_calls
                and all(row.get("traceId") == trace_id for row in rows)
                and any(row["name"] == "sandbox_cleanup" for row in rows)
                and all(row.get("endTime") for row in rows)):
            (directory / "cli-observations.json").write_text(completed.stdout)
            return rows
        time.sleep(min(2, max(0, deadline - time.monotonic())))
    raise TimeoutError("Complete model trace was not readable within 90 seconds")


def run_challenge(settings: dict, dataset_json: Path, manifest_path: Path, challenge_id: str,
                    directory: Path, *, langfuse, respond, model_usage: dict,
                    export_trace=read_model_trace) -> dict:
    """Run one selected challenge; clients are owned by the caller.

    Package objects/answers remain in this trusted function. The model loop sees
    only public task text and the runner's bounded functions. Offline verification
    can supply real SDKs with substituted transports; no test module is imported.
    """
    directory.mkdir(parents=True, exist_ok=False, mode=0o700)
    started = time.monotonic()
    report = {"challenge_id": challenge_id, "phase": "loading",
              "evidence_complete": False, "model_calls": 0, "model_settings": dict(model_usage["model_settings"])}
    try:
        manifest = json.loads(manifest_path.read_text())
        challenge = load_challenge(dataset_json, challenge_id, manifest_path)
        report["mode"] = "scored" if challenge_id in manifest["scored"] else "development"
        files = contestant_files(challenge)
        report["withheld_build_files"] = sorted(name for name in challenge.files if str(PurePosixPath(name)) not in files)
        report["dataset"] = {"revision": manifest["revision"], "index_sha256": manifest["index_sha256"]}
        report["phase"] = "target-startup"
        with challenge_target(challenge, directory / "target") as target:
            report["target"] = target
            report["provenance"] = collect_provenance(settings, target_images=target["images"])
            task = public_task(challenge, files, target["endpoints"])
            (directory / "public-task.json").write_text(task + "\n")
            report["phase"] = "attempt"
            with run_attempt(settings, target["network"], target["gateway"], target["endpoints"],
                             challenge.flag, directory, langfuse=langfuse, label=challenge_id,
                             public_task=task, respond=respond, model_usage=model_usage,
                             mode=report["mode"]) as run:
                report["files"] = stage_files(files, run["solver"], settings["workspace_mb"] * 1024 * 1024, 5)
                run_agent(task, run["respond"], run["call_tool"])
        report["phase"] = "trace-export"
    except BaseException as error:
        report["error_type"] = type(error).__name__
        raise
    finally:
        # The attempt may fail before its context yields; its summary still exists.
        summaries = list(directory.glob("*/summary.json"))
        try:
            if summaries:
                result = json.loads(summaries[0].read_text())
                report.update(result=result, model_calls=result["model_calls"])
                report["trace_url"] = langfuse.get_trace_url(trace_id=result["trace_id"])
                if export_trace is not None:
                    rows = export_trace(result["trace_id"], result["model_calls"], result["tool_calls"], directory)
                    roots = [row for row in rows if row["name"] == "attempt"]
                    root = roots[0] if len(roots) == 1 else None
                    secrets = [os.environ[name] for name in ("LITELLM_TOKEN", "LANGFUSE_SECRET_KEY") if os.getenv(name)]
                    report["evidence_checks"] = {
                        "one_root": root is not None,
                        "parentage": root is not None and all(row.get("parentObservationId") == root["id"] for row in rows if row is not root),
                        "expected_answer_not_in_root": root is not None and challenge.flag not in json.dumps(root),
                        "credentials_absent": all(secret not in json.dumps(rows) for secret in secrets),
                        "target_cleanup": not report["target"]["cleanup_errors"],
                        "solver_cleanup": not result["cleanup_errors"],
                    }
                    report["evidence_complete"] = all(report["evidence_checks"].values())
        except Exception as error:
            report["trace_export_error_type"] = type(error).__name__
        finally:
            report["total_seconds"] = round(time.monotonic() - started, 6)
            (directory / "run.json").write_text(json.dumps(report, indent=2) + "\n")
            print(f"Run records: {directory}", flush=True)
    if export_trace is not None and not report["evidence_complete"]:
        raise RuntimeError("Attempt records incomplete; inspect run.json before further runs")
    print(f'Outcome: {report["result"]["termination_reason"]}; verified success: {report["result"]["verified_success"]}', flush=True)
    return report


def launch_challenge(experiment_path: Path, dataset_json: Path, manifest_path: Path,
                       challenge_id: str, output_root: Path):
    """Own host-only clients and use the configured per-attempt limits."""
    names = ("LITELLM_TOKEN", "LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY", "LANGFUSE_BASE_URL")
    missing = [name for name in names if not os.getenv(name)]
    if missing:
        raise ValueError("Set host environment variables: " + ", ".join(missing))
    settings, model = load_experiment(experiment_path)
    directory = output_root / ("challenge-" + uuid.uuid4().hex[:12])
    client = Langfuse(timeout=10)
    try:
        if not client.auth_check():
            raise RuntimeError("Langfuse authentication failed")
        with OpenAI(api_key=os.environ["LITELLM_TOKEN"], base_url=model["base_url"],
                    max_retries=0, timeout=model["request_seconds"],
                    http_client=httpx2.Client(event_hooks={"response": [reject_gateway_errors]})) as model_client:
            respond, usage = make_responder(model_client, model,
                langfuse_public_key=os.environ["LANGFUSE_PUBLIC_KEY"])
            return run_challenge(settings, dataset_json, manifest_path, challenge_id, directory,
                                   langfuse=client, respond=respond, model_usage=usage)
    finally:
        client.shutdown()
