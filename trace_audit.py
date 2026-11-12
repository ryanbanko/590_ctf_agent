"""Audit scored attempts from their local Langfuse trace exports.

Needs the git-ignored ``observations.json`` files (they hold solver transcripts,
so they stay local). Writes one JSON file with two answer-free results:

* ``recovered_usage``: token counts and estimated cost for attempts whose
  ``run.json`` has no usage (e.g. a wall-limit stop during a model call), summed
  from the trace's model generations. For complete attempts these sums equal
  ``run.json`` exactly; ``usage_check`` records that comparison.
* ``lookup_scan``: every tool input (except flag submissions) searched for
  public hosts, public IPv4 addresses, URLs and package installs.

Usage:
    python trace_audit.py batch-3480f37c9289 batch-6f25081707a3 \\
        --json evidence/scored/trace-audit.json
"""

import argparse
import collections
import ipaddress
import json
import re
from pathlib import Path

DOMAIN = re.compile(r"\b[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*\.(?:com|org|net|io|edu|dev|gov|co|xyz|me|ai|app)\b")
IPV4 = re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}\b")
URL_HOST = re.compile(r"https?://([A-Za-z0-9.\-]+)")
PACKAGE_INSTALL = re.compile(r"pip3? install|-m pip|uv pip")


def trace_usage(generations, prices):
    """Token totals and estimated cost from Langfuse generation records."""
    tokens = {"input": 0, "output": 0, "cached_input": 0, "reasoning": 0}
    for g in generations:
        details = g.get("usageDetails") or {}
        tokens["input"] += g.get("inputUsage") or 0
        tokens["output"] += g.get("outputUsage") or 0
        tokens["cached_input"] += details.get("input_cached_tokens", 0)
        tokens["reasoning"] += details.get("output_reasoning_tokens", 0)
    cost = ((tokens["input"] - tokens["cached_input"]) * prices["input_usd_per_million"]
            + tokens["cached_input"] * prices["cached_input_usd_per_million"]
            + tokens["output"] * prices["output_usd_per_million"]) / 1e6
    return tokens, cost


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("batch_dir", type=Path, nargs="+")
    parser.add_argument("--json", type=Path, required=True)
    args = parser.parse_args()

    recovered, mismatches, missing_traces = {}, [], []
    checked_usage = 0
    scan = {"attempts_scanned": 0, "tool_calls_scanned": 0, "tool_calls_recorded": 0,
            "flag_submissions_skipped": 0, "url_hosts": collections.Counter(),
            "public_domains": collections.Counter(), "public_ipv4": collections.Counter(),
            "package_installs": 0, "denied_packets": 0, "scope_incidents": 0}

    for batch_dir in args.batch_dir:
        for run_path in sorted(batch_dir.glob("attempt-*/*/run.json")):
            result = json.loads(run_path.read_text())["result"]
            label = f"{batch_dir.name}/{run_path.parts[-3]}"
            scan["denied_packets"] += result["denied_packets"]
            scan["scope_incidents"] += result["scope_incidents"]
            trace_path = run_path.with_name("observations.json")
            if not trace_path.exists():
                missing_traces.append({"attempt": label, "challenge_id": result["challenge_id"],
                                       "outcome": result["termination_reason"]})
                continue
            rows = json.loads(trace_path.read_text())["data"]
            tokens, cost = trace_usage([r for r in rows if r["type"] == "GENERATION"], result["model_settings"])
            if result.get("tokens") is None:
                recovered[result["run_id"]] = {"attempt": label, "challenge_id": result["challenge_id"],
                                               "outcome": result["termination_reason"],
                                               "tokens": tokens, "cost_usd": round(cost, 8)}
            else:
                checked_usage += 1
                if any(tokens[k] != result["tokens"].get(k) for k in ("input", "output", "cached_input")):
                    mismatches.append(label)

            scan["attempts_scanned"] += 1
            scan["tool_calls_recorded"] += result["tool_calls"]
            for row in rows:
                if row["type"] != "TOOL":
                    continue
                scan["tool_calls_scanned"] += 1
                if row["name"] == "submit_flag":
                    scan["flag_submissions_skipped"] += 1
                    continue
                text = json.dumps(row.get("input"))
                scan["url_hosts"].update(URL_HOST.findall(text))
                scan["public_domains"].update(d.lower() for d in DOMAIN.findall(text))
                for address in IPV4.findall(text):
                    try:
                        if ipaddress.ip_address(address).is_global:
                            scan["public_ipv4"][address] += 1
                    except ValueError:
                        pass
                scan["package_installs"] += bool(PACKAGE_INSTALL.search(text))

    for key in ("url_hosts", "public_domains", "public_ipv4"):
        scan[key] = dict(scan[key])
    audit = {"recovered_usage": recovered,
             "usage_check": {"complete_attempts_compared": checked_usage, "mismatches": mismatches},
             "attempts_without_trace": missing_traces,
             "lookup_scan": scan}
    args.json.write_text(json.dumps(audit, indent=2) + "\n")
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
