"""One challenge launcher: public task, isolated tools, and trusted evaluation."""

from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import signal
import subprocess
import sys
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
    for pattern in ["ctf_agent/*.py", "docker/*.py", "docker/*.Dockerfile", "docker/NYU-LICENSE", "tests/**/*.py",
                    "configs/*.toml", "configs/*.json", "pyproject.toml", "uv.lock"]:
        for path in sorted(Path(".").glob(pattern)):
            hashes[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
    return {"images": images, "commit": commit.stdout.strip() if commit.returncode == 0 else None,
            "working_tree_dirty": bool(changed.stdout), "source_sha256": hashes,
            "docker": docker("version", "--format", "{{.Server.Version}}"), "config": settings}


def read_model_trace(client, trace_id: str, model_calls: int, tool_calls: int,
                     directory: Path, *, from_start_time: datetime | None = None):
    """Export complete native observations through the existing Python client."""
    since = from_start_time or datetime.now(timezone.utc) - timedelta(days=1)
    until = datetime.now(timezone.utc) + timedelta(minutes=5)
    deadline = time.monotonic() + 90
    while time.monotonic() < deadline:
        rows, cursor = [], None
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("Complete model trace was not readable within 90 seconds")
            page = client.api.observations.get_many(
                trace_id=trace_id, cursor=cursor, limit=100,
                from_start_time=since, to_start_time=until,
                fields="core,basic,time,io,metadata,model,usage",
                expand_metadata="config,image_ids,model_settings",
                request_options={"timeout_in_seconds": min(10, remaining), "max_retries": 0})
            rows.extend(item.model_dump(mode="json", by_alias=True) for item in page.data)
            cursor = page.meta.cursor
            if cursor is None:
                break
        roots = [row for row in rows if row["name"] == "attempt"]
        generations = [row for row in rows if row["type"] == "GENERATION"]
        tools = [row for row in rows if row["type"] == "TOOL"]
        if (len(roots) == 1 and len(generations) == model_calls and len(tools) == tool_calls
                and all(row.get("traceId") == trace_id for row in rows)
                and any(row["name"] == "sandbox_cleanup" for row in rows)
                and all(row.get("endTime") for row in rows)):
            (directory / "observations.json").write_text(json.dumps({"data": rows}, indent=2) + "\n")
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
            with run_attempt(settings, target["network"], target["endpoints"],
                             challenge.flag, directory, langfuse=langfuse, label=challenge_id,
                             public_task=task, respond=respond, model_usage=model_usage,
                             mode=report["mode"]) as run:
                report["files"] = stage_files(files, run["solver"],
                                             run["remaining_seconds"]())
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
                    rows = export_trace(langfuse, result["trace_id"], result["model_calls"], result["tool_calls"], directory)
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


def launch_batch(experiment_path: Path, dataset_json: Path, manifest_path: Path,
                 challenge_ids: list[str], trials: int, output_root: Path) -> Path:
    """Sequence the existing CLI in fresh processes; keep an index of its records."""
    if type(trials) is not int or trials < 1:
        raise ValueError("trials must be a positive integer")
    if not challenge_ids or len(set(challenge_ids)) != len(challenge_ids):
        raise ValueError("Provide distinct challenge IDs; use trials for repeats")
    manifest = json.loads(manifest_path.read_text())
    if set(challenge_ids) - set(manifest["development"] + manifest["scored"]):
        raise ValueError("Choose challenge IDs from the manifest")
    modes = {"scored" if cid in manifest["scored"] else "development" for cid in challenge_ids}
    if len(modes) != 1:
        raise ValueError("Keep development and scored challenges in separate batches")
    load_experiment(experiment_path)
    directory = output_root / ("batch-" + uuid.uuid4().hex[:12])
    directory.mkdir(parents=True, exist_ok=False, mode=0o700)
    snapshot = directory / "experiment.toml"
    snapshot.write_bytes(experiment_path.read_bytes())
    planned = len(challenge_ids) * trials
    index = {"status": "running", "mode": modes.pop(), "challenges": challenge_ids,
             "trials": trials, "planned_attempts": planned, "attempts": []}
    index_path = directory / "batch.json"
    started = time.monotonic()
    print(f"Batch records: {directory}", flush=True)
    print(f"Planned attempts: {planned}", flush=True)
    try:
        for trial in range(1, trials + 1):
            for challenge_id in challenge_ids:
                output = directory / f"attempt-{len(index['attempts']) + 1:03d}"
                row = {"challenge_id": challenge_id, "trial": trial, "status": "started",
                       "directory": output.name}
                report, result = {}, {}
                index["attempts"].append(row)
                index_path.write_text(json.dumps(index, indent=2) + "\n")
                command = [sys.executable, "-m", "ctf_agent", "run-challenge",
                           "--experiment", str(snapshot.resolve()), "--dataset", str(dataset_json),
                           "--manifest", str(manifest_path), "--challenge", challenge_id,
                           "--output", str(output)]
                try:
                    with subprocess.Popen(command, start_new_session=True) as process:
                        try:
                            returncode = process.wait()
                        except KeyboardInterrupt:
                            process.send_signal(signal.SIGINT)
                            process.wait()
                            raise
                finally:
                    reports = list(output.glob("challenge-*/run.json"))
                    if len(reports) == 1:
                        report = json.loads(reports[0].read_text())
                        result = report.get("result", {})
                        row.update(record=str(reports[0].relative_to(directory)),
                                   run_id=result.get("run_id"), trace_url=report.get("trace_url"),
                                   outcome=result.get("termination_reason"),
                                   verified_success=result.get("verified_success"))
                if (returncode != 0 or len(reports) != 1 or not report.get("evidence_complete")
                        or report.get("challenge_id") != challenge_id
                        or not result.get("run_id") or not result.get("termination_reason")
                        or result.get("cleanup_errors")
                        or row["outcome"] in {"scope_violation", "guard_failure", "infrastructure_error",
                                               "response_source_error"}):
                    raise RuntimeError("Batch stopped for review; inspect batch.json and the attempt records")
                row["status"] = "completed"
        index["status"] = "completed"
    except KeyboardInterrupt:
        index["status"] = "interrupted"
        if index["attempts"]:
            index["attempts"][-1]["status"] = "interrupted"
        raise
    except Exception as error:
        index.update(status="stopped", error_type=type(error).__name__)
        if index["attempts"]:
            index["attempts"][-1]["status"] = "stopped"
        raise
    finally:
        index["total_seconds"] = round(time.monotonic() - started, 6)
        index_path.write_text(json.dumps(index, indent=2) + "\n")
    return directory
