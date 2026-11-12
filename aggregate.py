"""Aggregate scored run-batch directories into the required report metrics.

Reads ``batch.json`` and each attempt's ``run.json`` under one or more batch
directories and prints the per-challenge table, pass@k, average solve rate with
sample standard deviation, and the time/token/cost resource totals (failed
attempts included).

Usage:
    # Raw, single batch exactly as it ran (stopped batches shown as-is):
    uv run --frozen python aggregate.py batch-3480f37c9289

    # Merged final: a primary batch plus a resume batch that fills missing
    # trials. Trials are reindexed per challenge in directory order, and
    # infrastructure incidents (e.g. response_source_error) are pulled out of
    # the solve trials and reported separately rather than counted as failures:
    uv run --frozen python aggregate.py batch-3480f37c9289 \\
        runs/scored-resume/batch-XXXX --json out.json

    # Final scored numbers, with the usage trace_audit.py recovered for the
    # attempt whose run.json has none:
    python aggregate.py batch-3480f37c9289 batch-6f25081707a3 \\
        --recovered-usage evidence/scored/trace-audit.json \\
        --json evidence/scored/final_summary.json

pass@k is the unbiased estimator 1 - C(n-c, k) / C(n, k) averaged over
challenges (n trials, c successes), so it does not depend on trial order.

The script is read-only over the batch directories and uses only the standard
library. Failed and stopped attempts are counted in resources; usage missing
from run.json is filled from --recovered-usage when given, and any still-missing
usage is reported separately so the totals stay honest.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path

# Outcomes that reflect harness/gateway faults rather than a genuine solve
# attempt. In merged mode these are reported as incidents and excluded from the
# solve-rate denominators, but still counted in the resource totals.
INFRA_OUTCOMES = {"response_source_error"}


def load_attempts(batch_dir: Path) -> tuple[dict, list[dict]]:
    """Return (batch summary, per-attempt records) for a batch directory.

    Each returned attempt merges its ``batch.json`` row with the fields pulled
    from its ``run.json`` result block. Records that cannot be read are kept with
    ``record_loaded`` set to False so they still count as attempts.
    """
    batch = json.loads((batch_dir / "batch.json").read_text())
    attempts = []
    for row in batch.get("attempts", []):
        record_path = batch_dir / row["record"]
        result = {}
        loaded = False
        if record_path.exists():
            try:
                result = json.loads(record_path.read_text()).get("result", {}) or {}
                loaded = True
            except (json.JSONDecodeError, OSError):
                loaded = False
        tokens = result.get("tokens") or {}
        attempts.append(
            {
                "challenge_id": row["challenge_id"],
                "run_id": result.get("run_id"),
                "trial": row["trial"],
                "source": batch_dir.name,
                "status": row.get("status"),
                "outcome": row.get("outcome"),
                "verified_success": bool(row.get("verified_success")),
                "record_loaded": loaded,
                "model_calls": result.get("model_calls"),
                "tool_calls": result.get("tool_calls"),
                "input_tokens": tokens.get("input"),
                "output_tokens": tokens.get("output"),
                "cached_input_tokens": tokens.get("cached_input"),
                "reasoning_tokens": tokens.get("reasoning"),
                "cost_usd": result.get("cost_usd"),
                "active_seconds": result.get("active_seconds"),
                "wall_seconds": result.get("total_seconds"),
                "usage_complete": result.get("usage_complete"),
                "usage_recovered": False,
            }
        )
    return batch, attempts


def apply_recovered_usage(attempts: list[dict], recovered: dict) -> None:
    """Fill missing token/cost fields from trace_audit.py's recovered_usage."""
    for a in attempts:
        found = recovered.get(a["run_id"])
        if a["input_tokens"] is None and found:
            tokens = found["tokens"]
            a.update(input_tokens=tokens["input"], output_tokens=tokens["output"],
                     cached_input_tokens=tokens["cached_input"],
                     reasoning_tokens=tokens["reasoning"], cost_usd=found["cost_usd"],
                     usage_recovered=True)


def _sum(values) -> float:
    """Sum, ignoring None (missing usage on failed attempts)."""
    return sum(v for v in values if v is not None)


def _mean(values):
    present = [v for v in values if v is not None]
    return statistics.fmean(present) if present else None


def per_challenge(attempts: list[dict], trials: int) -> list[dict]:
    """One row per challenge: trials run, successes, solve rate, and pass@k."""
    order = []
    by_id: dict[str, list[dict]] = {}
    for a in attempts:
        if a["challenge_id"] not in by_id:
            by_id[a["challenge_id"]] = []
            order.append(a["challenge_id"])
        by_id[a["challenge_id"]].append(a)

    rows = []
    for cid in order:
        runs = sorted(by_id[cid], key=lambda a: a["trial"])
        successes = [a for a in runs if a["verified_success"]]
        row = {
            "challenge_id": cid,
            "trials_run": len(runs),
            "successes": len(successes),
            "solve_rate": len(successes) / len(runs) if runs else 0.0,
            "outcomes": [a["outcome"] for a in runs],
        }
        # Unbiased pass@k: chance that k of the n trials, drawn without
        # replacement, include at least one success.
        n, c = len(runs), len(successes)
        for k in range(1, trials + 1):
            row[f"pass@{k}"] = 1 - math.comb(n - c, k) / math.comb(n, k) if n >= k else None
        for field in ("model_calls", "tool_calls", "input_tokens", "output_tokens",
                      "wall_seconds", "cost_usd"):
            row[f"mean_{field}"] = _mean([a[field] for a in runs])
        rows.append(row)
    return rows


def trial_solve_rates(attempts: list[dict], trials: int) -> list[float]:
    """Solve rate within each trial index, across the challenges run in it."""
    rates = []
    for t in range(1, trials + 1):
        runs = [a for a in attempts if a["trial"] == t]
        if runs:
            rates.append(sum(a["verified_success"] for a in runs) / len(runs))
    return rates


def resources(attempts: list[dict]) -> dict:
    """Totals and per-attempt means across all attempts (failures included)."""
    n = len(attempts)
    with_usage = [a for a in attempts if a["input_tokens"] is not None]
    return {
        "attempts": n,
        "attempts_with_usage": len(with_usage),
        "attempts_with_recovered_usage": sum(a["usage_recovered"] for a in attempts),
        "attempts_missing_usage": n - len(with_usage),
        "model_calls_total": _sum(a["model_calls"] for a in attempts),
        "tool_calls_total": _sum(a["tool_calls"] for a in attempts),
        "input_tokens_total": _sum(a["input_tokens"] for a in attempts),
        "output_tokens_total": _sum(a["output_tokens"] for a in attempts),
        "cost_usd_total": _sum(a["cost_usd"] for a in attempts),
        "wall_seconds_total": _sum(a["wall_seconds"] for a in attempts),
        "mean_input_tokens": _mean([a["input_tokens"] for a in attempts]),
        "mean_output_tokens": _mean([a["output_tokens"] for a in attempts]),
        "mean_total_tokens": _mean(
            [
                (a["input_tokens"] + a["output_tokens"])
                if a["input_tokens"] is not None and a["output_tokens"] is not None
                else None
                for a in attempts
            ]
        ),
        "mean_wall_seconds": _mean([a["wall_seconds"] for a in attempts]),
        "mean_active_seconds": _mean([a["active_seconds"] for a in attempts]),
        "mean_cost_usd": _mean([a["cost_usd"] for a in attempts]),
    }


def summarize(batch: dict, attempts: list[dict], incidents: list[dict] | None = None) -> dict:
    """Metrics over ``attempts`` (the solve trials). ``incidents`` are infra
    faults: excluded from solve rates but added to the resource totals and listed."""
    incidents = incidents or []
    trials = batch.get("trials", max((a["trial"] for a in attempts), default=1))
    rows = per_challenge(attempts, trials)
    rates = trial_solve_rates(attempts, trials)
    per_chal_rates = [r["solve_rate"] for r in rows]

    pass_at = {}
    for k in range(1, trials + 1):
        vals = [r[f"pass@{k}"] for r in rows if r[f"pass@{k}"] is not None]
        pass_at[f"pass@{k}"] = (sum(vals) / len(vals)) if vals else None

    completed = [a for a in attempts if a["status"] == "completed"]
    successes = [a for a in attempts if a["verified_success"]]
    return {
        "batch_status": batch.get("status"),
        "mode": batch.get("mode"),
        "planned_attempts": batch.get("planned_attempts"),
        "trials": trials,
        "attempts_run": len(attempts),
        "attempts_completed": len(completed),
        "verified_successes": len(successes),
        "overall_solve_rate": len(successes) / len(attempts) if attempts else 0.0,
        "pass_at_k": pass_at,
        "mean_trial_solve_rate": _mean(rates),
        "trial_solve_rate_sd_pp": (
            statistics.stdev(rates) * 100 if len(rates) > 1 else 0.0
        ),
        "per_challenge_solve_rate_sd_pp": (
            statistics.stdev(per_chal_rates) * 100 if len(per_chal_rates) > 1 else 0.0
        ),
        "per_trial_solve_rates": rates,
        "per_challenge": rows,
        "resources": resources(attempts + incidents),
        "incidents": [
            {
                "challenge_id": a["challenge_id"],
                "source": a.get("source"),
                "outcome": a["outcome"],
                "model_calls": a["model_calls"],
                "tool_calls": a["tool_calls"],
            }
            for a in incidents
        ],
    }


def merge_batches(loaded: list[tuple[dict, list[dict]]]) -> tuple[dict, list[dict], list[dict]]:
    """Combine several batches into reindexed solve trials plus incidents.

    ``loaded`` is a list of (batch summary, attempts) in directory order. For each
    challenge, attempts are concatenated in that order; infrastructure incidents
    (``INFRA_OUTCOMES``) are separated out, and the remaining solve attempts are
    renumbered ``trial`` = 1..N. Returns (synthetic batch meta, trial attempts,
    incident attempts).
    """
    sequenced = []
    for source_index, (_, attempts) in enumerate(loaded):
        for a in attempts:
            sequenced.append({**a, "source_index": source_index})

    incidents = [a for a in sequenced if a["outcome"] in INFRA_OUTCOMES]
    solves = [a for a in sequenced if a["outcome"] not in INFRA_OUTCOMES]

    by_id: dict[str, list[dict]] = {}
    order = []
    for a in solves:
        if a["challenge_id"] not in by_id:
            by_id[a["challenge_id"]] = []
            order.append(a["challenge_id"])
        by_id[a["challenge_id"]].append(a)

    reindexed = []
    max_trials = 0
    for cid in order:
        runs = sorted(by_id[cid], key=lambda a: (a["source_index"], a["trial"]))
        max_trials = max(max_trials, len(runs))
        for i, a in enumerate(runs, start=1):
            reindexed.append({**a, "trial": i})

    meta = {
        "status": "merged",
        "mode": loaded[0][0].get("mode"),
        "trials": max_trials,
        "planned_attempts": len(order) * max_trials,
    }
    return meta, reindexed, incidents


def _fmt(x, nd=2):
    if x is None:
        return "—"
    if isinstance(x, float):
        return f"{x:.{nd}f}"
    return str(x)


def print_report(summary: dict) -> None:
    trials = summary["trials"]
    print(f"Batch mode={summary['mode']}  status={summary['batch_status']}")
    print(
        f"Attempts: {summary['attempts_run']} run "
        f"({summary['attempts_completed']} completed) "
        f"of {summary['planned_attempts']} planned; "
        f"{summary['verified_successes']} verified successes"
    )
    print()

    head_pass = "  ".join(f"p@{k}".rjust(4) for k in range(1, trials + 1))
    print(f"{'challenge':24} {'run':>3} {'ok':>3} {'rate':>6}  {head_pass}  outcomes")
    for r in summary["per_challenge"]:
        passes = "  ".join(
            _fmt(r[f'pass@{k}'], 2).rjust(4) for k in range(1, trials + 1)
        )
        print(
            f"{r['challenge_id']:24} {r['trials_run']:>3} {r['successes']:>3} "
            f"{r['solve_rate']*100:5.0f}%  {passes}  {','.join(r['outcomes'])}"
        )
    print()

    print(f"{'challenge':24} {'model/tool calls':>16} {'input tok':>10} {'output tok':>10} "
          f"{'sec':>6} {'cost $':>8}   (means per attempt)")
    for r in summary["per_challenge"]:
        print(
            f"{r['challenge_id']:24} "
            f"{_fmt(r['mean_model_calls'],1):>7}/{_fmt(r['mean_tool_calls'],1):<8} "
            f"{_fmt(r['mean_input_tokens'],0):>10} {_fmt(r['mean_output_tokens'],0):>10} "
            f"{_fmt(r['mean_wall_seconds'],1):>6} {_fmt(r['mean_cost_usd'],4):>8}"
        )
    print()

    for k in range(1, trials + 1):
        v = summary["pass_at_k"][f"pass@{k}"]
        print(f"  pass@{k}: {_fmt(v*100 if v is not None else None,1)}%")
    print(
        f"  mean solve rate / trial: {_fmt(summary['mean_trial_solve_rate']*100,1)}% "
        f"(sample SD {_fmt(summary['trial_solve_rate_sd_pp'],1)} pp across trials)"
    )
    print(
        f"  per-challenge solve-rate sample SD: "
        f"{_fmt(summary['per_challenge_solve_rate_sd_pp'],1)} pp"
    )
    print()

    incidents = summary.get("incidents") or []
    if incidents:
        print("Infrastructure incidents (excluded from solve rates, kept in resources):")
        for inc in incidents:
            print(
                f"  {inc['challenge_id']:24} {inc['outcome']} "
                f"(model_calls={inc['model_calls']}, tool_calls={inc['tool_calls']}, "
                f"source={inc['source']})"
            )
        print()

    res = summary["resources"]
    print("Resources (all attempts, failures and incidents included):")
    print(
        f"  usage present: {res['attempts_with_usage']}/{res['attempts']} "
        f"(recovered from traces: {res['attempts_with_recovered_usage']}; "
        f"missing on {res['attempts_missing_usage']} failed/stopped)"
    )
    print(f"  model calls total: {res['model_calls_total']}   "
          f"tool calls total: {res['tool_calls_total']}")
    print(
        f"  tokens: input {res['input_tokens_total']:,}  "
        f"output {res['output_tokens_total']:,}  "
        f"(mean total/attempt {_fmt(res['mean_total_tokens'],0)})"
    )
    print(
        f"  wall time: total {_fmt(res['wall_seconds_total'],1)}s  "
        f"mean {_fmt(res['mean_wall_seconds'],1)}s  "
        f"mean active {_fmt(res['mean_active_seconds'],1)}s"
    )
    print(
        f"  cost: total ${_fmt(res['cost_usd_total'],5)}  "
        f"mean ${_fmt(res['mean_cost_usd'],5)}/attempt "
        f"(estimated from gateway rates; excludes attempts missing usage)"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "batch_dir", type=Path, nargs="+",
        help="one or more batch-<id> directories; extra ones are merged as resumes",
    )
    parser.add_argument("--json", type=Path, help="also write the summary as JSON")
    parser.add_argument("--recovered-usage", type=Path,
                        help="trace_audit.py output; fills usage missing from run.json")
    args = parser.parse_args()
    recovered = {}
    if args.recovered_usage:
        recovered = json.loads(args.recovered_usage.read_text())["recovered_usage"]

    if len(args.batch_dir) == 1:
        batch, attempts = load_attempts(args.batch_dir[0])
        apply_recovered_usage(attempts, recovered)
        summary = summarize(batch, attempts)
    else:
        loaded = [load_attempts(d) for d in args.batch_dir]
        for _, attempts in loaded:
            apply_recovered_usage(attempts, recovered)
        meta, trials_attempts, incidents = merge_batches(loaded)
        summary = summarize(meta, trials_attempts, incidents)

    print_report(summary)
    if args.json:
        args.json.write_text(json.dumps(summary, indent=2))
        print(f"\nWrote {args.json}")


if __name__ == "__main__":
    main()
