"""Budget-paced orchestration over an HTB event: planning, per-challenge limits,
task prefaces and cross-run notes. Host-only; wraps run_htb_challenge without
changing the tuned agent loop.

The policy here is a starting point, not a measured optimum: tighter caps on
easy challenges and a global budget protect the fixed token allowance, but none
of these settings is proven to improve the solve rate.
"""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import json
import os
import threading
import uuid

# Easiest first; unknown difficulties sort last.
DIFFICULTY_ORDER = ["very easy", "easy", "medium", "hard", "insane"]

# Per-difficulty attempt ceilings. These are caps, not targets: the agent stops
# as soon as it solves. Wall seconds are generous relative to turns.
# Budget is not the constraint here, so every difficulty gets the full allowance:
# 3600s wall, 200 model turns, high reasoning effort. Easiest-first ordering still
# harvests likely solves early, but nothing is starved by a tighter per-difficulty
# cap. The global budget is a safety ceiling only (real per-challenge cost is cents).
UNIFORM_LIMITS = {"max_model_turns": 200, "wall_seconds": 3600.0, "reasoning_effort": "high"}
DEFAULT_POLICY = {
    "global_budget_usd": 20.0,            # safety ceiling; actual spend is cents/challenge
    "reserve_hard_below_fraction": 0.40,  # defer hard/insane only if budget ever runs low (won't normally fire)
    "skip_categories": [],                # e.g. ["hardware"] when unsupported locally
    "default_limits": dict(UNIFORM_LIMITS),
    "difficulty_limits": {
        "very easy": dict(UNIFORM_LIMITS),
        "easy":      dict(UNIFORM_LIMITS),
        "medium":    dict(UNIFORM_LIMITS),
        "hard":      dict(UNIFORM_LIMITS),
        "insane":    dict(UNIFORM_LIMITS),
    },
}

FLAG_FORMAT_HINT = ("HTB challenge flags have the form HTB{...}. Submit the exact string "
                    "including the HTB{} wrapper; do not submit a partial or reformatted value.")

# Brief, additive methodology hints per category (prepended to the task, never a
# change to the system prompt). Keyed by the lowercase category label.
CATEGORY_HINTS = {
    "web": "Map the application's routes, parameters and how it builds responses, then test inputs "
           "systematically; the flag is usually reachable through the app's own logic or an input-handling flaw.",
    "pwn": "Identify the binary and its protections (checksec), characterise how it handles input, and build "
           "and test your approach locally against the provided binary before the remote target.",
    "rev": "Identify the binary (file, strings), then use static analysis and decompilation (radare2, angr) to "
           "map how input relates to the success condition, and recover the required input or key.",
    "reversing": "Identify the binary (file, strings), then use static analysis and decompilation (radare2, angr) "
                 "to map how input relates to the success condition, and recover the required input or key.",
    "crypto": "Identify the scheme and parameters, look for implementation or parameter weaknesses, and prefer a "
              "cheap check against the provided artifact before an expensive computation.",
    "forensics": "Examine the provided artifacts with suitable tools (metadata, file carving, packet and stream "
                 "inspection) and follow the evidence to the hidden data.",
    "stego": "Inspect the media's structure and metadata, try standard extraction tools, and look for data hidden "
             "in unused or least-significant fields.",
    "misc": "Read the task closely for the intended mechanism, and work from the provided files or service "
            "methodically.",
    "osint": "Work only from the provided material and the task's own scope; do not contact unlisted systems.",
    "blockchain": "Inspect the contract or chain state provided, identify the vulnerable interaction, and test it "
                  "against the given endpoint.",
    "coding": "Read the exact input/output contract, implement a solution, and verify it on the provided examples "
              "before submitting.",
}


def difficulty_rank(challenge: dict) -> int:
    difficulty = str(challenge.get("difficulty", "")).strip().lower()
    return DIFFICULTY_ORDER.index(difficulty) if difficulty in DIFFICULTY_ORDER else len(DIFFICULTY_ORDER)


def challenge_limits(challenge: dict, policy: dict) -> dict:
    difficulty = str(challenge.get("difficulty", "")).strip().lower()
    return dict(policy["difficulty_limits"].get(difficulty, policy["default_limits"]))


def plan_challenges(event: dict, policy: dict, category_label) -> list[dict]:
    """Return the unsolved challenges to attempt, easiest and cheapest first."""
    skip = {c.strip().lower() for c in policy.get("skip_categories", [])}
    candidates = [c for c in event.get("challenges", [])
                  if not c.get("solved") and category_label(c).strip().lower() not in skip]
    return sorted(candidates, key=lambda c: (difficulty_rank(c), c.get("points") or 0, c.get("id") or 0))


def should_attempt(challenge: dict, policy: dict, spent_usd: float) -> tuple[bool, str]:
    """Decide whether to attempt one challenge given cumulative spend."""
    budget = policy["global_budget_usd"]
    if spent_usd >= budget:
        return False, "budget_exhausted"
    remaining_fraction = (budget - spent_usd) / budget if budget > 0 else 0.0
    if (difficulty_rank(challenge) >= DIFFICULTY_ORDER.index("hard")
            and remaining_fraction < policy["reserve_hard_below_fraction"]):
        return False, "deferred_hard_low_budget"
    return True, "attempt"


def build_preface(challenge: dict, notes_text: str, category_label, base: str = "") -> str:
    """Assemble the additive task preface: base + flag format + category hint + notes."""
    category = category_label(challenge).strip().lower()
    parts = [base, FLAG_FORMAT_HINT, CATEGORY_HINTS.get(category, "")]
    if notes_text.strip():
        parts.append("Notes from earlier attempts on this challenge (verify each claim before relying on "
                     "it; they may be wrong or incomplete):\n" + notes_text.strip())
    return "\n\n".join(part for part in parts if part.strip())


# --- cross-run notes -------------------------------------------------------

def notes_path(notes_root: Path, ctf_id: int, challenge_id: int) -> Path:
    return notes_root / f"{ctf_id}-{challenge_id}.md"


def read_notes(path: Path, *, max_bytes: int = 32_768) -> str:
    """Return stored notes, truncated to the most recent max_bytes, or ''."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, ValueError):
        return ""
    return text[-max_bytes:] if len(text) > max_bytes else text


def extract_final_text(run_directory: Path) -> str:
    """Best-effort: the agent's last message text from the exported trace.

    The system prompt asks the agent to end with what it established and what is
    blocked, so the final assistant message is the useful cross-run summary. The
    export schema can vary, so every access is defensive and '' is returned when
    nothing readable is found.
    """
    try:
        rows = json.loads((run_directory / "observations.json").read_text())["data"]
    except (OSError, ValueError, KeyError):
        return ""
    generations = [row for row in rows if row.get("type") == "GENERATION"]
    generations.sort(key=lambda row: row.get("endTime") or row.get("startTime") or "")
    for row in reversed(generations):
        text = _message_text(row.get("output"))
        if text:
            return text
    return ""


def _message_text(output) -> str:
    """Pull human-readable assistant text out of a generation's output field."""
    if isinstance(output, str):
        return output.strip()
    if isinstance(output, dict):
        if isinstance(output.get("content"), str):
            return output["content"].strip()
        for key in ("text", "output_text", "content"):
            found = _message_text(output.get(key))
            if found:
                return found
        return ""
    if isinstance(output, list):
        texts = []
        for item in output:
            if isinstance(item, dict) and item.get("type") in (None, "message", "output_text", "text"):
                texts.append(_message_text(item.get("content", item.get("text", ""))))
        return "\n".join(t for t in texts if t).strip()
    return ""


def append_notes(path: Path, *, challenge_name: str, outcome: str, turns, summary: str) -> None:
    """Append one dated attempt entry; keep notes human-readable and bounded."""
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = [f"## {challenge_name} — {outcome} ({turns} model turns)"]
    entry.append(summary.strip() if summary.strip() else "(no end-of-run summary captured)")
    with path.open("a", encoding="utf-8") as handle:
        handle.write("\n".join(entry) + "\n\n")


def attempt_cost(report: dict) -> float:
    """Known model cost of one attempt, from its recorded usage (0.0 if unknown)."""
    result = report.get("result") or {}
    known = result.get("known_usage") or {}
    cost = known.get("cost_usd")
    return float(cost) if isinstance(cost, (int, float)) else 0.0


def _load_report(directory: Path) -> dict:
    """The canonical per-attempt record finish_run always writes, or {}."""
    try:
        return json.loads((directory / "run.json").read_text())
    except (OSError, ValueError):
        return {}


MAX_WORKERS = 6  # safety cap: N concurrent solvers need N CPUs/GiB and N model streams


def run_event(experiment_path: Path, ctf_id: int, output_root: Path, *, policy: dict | None = None,
              notes_root: Path | None = None, limit: int | None = None, workers: int = 1,
              manual_verify: bool = False):
    """Attempt an event's challenges easiest-first within a global budget.

    Opens the model and MCP clients once, then for each planned challenge builds a
    fresh responder at the difficulty's reasoning effort and turn cap, injects the
    flag-format/category/notes preface, runs it, records cost and outcome, and
    stores an end-of-run note. One challenge's failure never stops the event;
    only an exhausted budget does. Returns the event summary and writes event.json.

    workers>1 solves challenges concurrently (for a faster finish / better placement,
    not more solves), capped at MAX_WORKERS. The MCP client is serialized with a
    lock (one round-trip at a time); shared state is lock-protected. With several
    attempts in flight the budget can overshoot by up to `workers` attempts, so the
    global budget keeps headroom. Default workers=1 is the proven sequential path.
    """
    from .launch import open_model_clients, run_htb_challenge, MANUAL_HTB_PROMPT_PREFACE
    from .agent import make_responder
    from .htb import category_label
    from .manual import manual_verdict
    from . import htb_mcp

    policy = policy or DEFAULT_POLICY
    notes_root = notes_root or Path("runs/htb/notes")
    workers = max(1, min(workers, MAX_WORKERS))
    verdict_lock = threading.Lock()  # serialize human prompts when manual_verify + workers>1
    output_root.mkdir(parents=True, exist_ok=True)
    event_dir = output_root / ("event-" + uuid.uuid4().hex[:12])
    event_dir.mkdir(parents=True, mode=0o700)
    summary = {"ctf_id": ctf_id, "status": "running", "workers": workers, "spent_usd": 0.0,
               "budget_usd": policy["global_budget_usd"], "planned": [], "solved": [], "attempts": []}
    index_path = event_dir / "event.json"
    state_lock = threading.Lock()

    def save():
        index_path.write_text(json.dumps(summary, indent=2) + "\n")

    save()
    print(f"Event records: {event_dir}", flush=True)
    with open_model_clients(experiment_path) as (settings, model, langfuse, client), \
            htb_mcp.htb_session() as raw_call:
        mcp_lock = threading.Lock()

        def call(name, arguments=None, **kwargs):
            # Serialize MCP round-trips: the client shares one request-id counter and
            # the HTB server is stateless. Polling sleeps happen between calls, unlocked.
            with mcp_lock:
                return raw_call(name, arguments, **kwargs)

        event = htb_mcp.retrieve_ctf(call, ctf_id)
        if not isinstance(event, dict):
            raise RuntimeError("Unexpected event payload from retrieve_ctf")
        plan = plan_challenges(event, policy, category_label)
        if limit is not None:
            plan = plan[:limit]
        summary["planned"] = [c["id"] for c in plan]
        save()
        print(f"Planned {len(plan)} challenge(s); budget ${policy['global_budget_usd']:.2f}; "
              f"workers {workers}", flush=True)

        def attempt_one(challenge) -> str:
            cid = challenge["id"]
            with state_lock:
                allowed, reason = should_attempt(challenge, policy, summary["spent_usd"])
                if not allowed:
                    summary["attempts"].append({"challenge_id": cid, "name": challenge.get("name"),
                                                "status": reason})
                    save()
                    print(f"  skip {cid} {challenge.get('name')}: {reason}", flush=True)
                    return reason
                limits = challenge_limits(challenge, policy)
                row = {"challenge_id": cid, "name": challenge.get("name"),
                       "difficulty": challenge.get("difficulty"), "limits": limits, "status": "started"}
                summary["attempts"].append(row)
                save()
            per_settings = settings | {"max_model_turns": limits["max_model_turns"],
                                       "wall_seconds": limits["wall_seconds"]}
            per_model = model | {"reasoning_effort": limits["reasoning_effort"],
                                 "max_requests": limits["max_model_turns"]}
            respond, usage = make_responder(client, per_model,
                                            langfuse_public_key=os.environ.get("LANGFUSE_PUBLIC_KEY"))
            note_file = notes_path(notes_root, ctf_id, cid)
            preface = build_preface(challenge, read_notes(note_file), category_label,
                                    base=MANUAL_HTB_PROMPT_PREFACE)
            directory = event_dir / f"challenge-{cid}-{uuid.uuid4().hex[:8]}"
            verifier = None
            source = "htb-mcp"
            if manual_verify:
                label = challenge.get("name") or str(cid)

                def human_verify(candidate, remaining, _label=label):
                    with verdict_lock:  # one human prompt at a time across workers
                        return manual_verdict(_label, candidate, remaining)

                verifier = human_verify
                source = "htb-human-relay"
            print(f"  run  {cid} {challenge.get('name')} [{challenge.get('difficulty')}] "
                  f"turns<= {limits['max_model_turns']} effort={limits['reasoning_effort']}", flush=True)
            try:
                run_htb_challenge(per_settings, ctf_id, cid, directory, langfuse=langfuse, respond=respond,
                                  model_usage=usage, call=call, prompt_preface=preface,
                                  verify_candidate=verifier, verification_source=source)
            except Exception as error:  # noqa: BLE001 - keep the event going; record the failure
                with state_lock:
                    row.update(error_type=type(error).__name__, error=str(error)[:300])
            report = _load_report(directory)
            result = report.get("result") or {}
            cost = attempt_cost(report)
            with state_lock:
                row.update(status="completed" if report else "error",
                           outcome=result.get("termination_reason"),
                           verified_success=result.get("verified_success"),
                           run_id=result.get("run_id"), trace_url=report.get("trace_url"), cost_usd=cost)
                summary["spent_usd"] = round(summary["spent_usd"] + cost, 6)
                if result.get("verified_success"):
                    summary["solved"].append(cid)
                    print(f"       SOLVED {cid} (${cost:.4f}); spent ${summary['spent_usd']:.4f}", flush=True)
                else:
                    print(f"       {row.get('outcome') or row.get('error_type')} "
                          f"(${cost:.4f}); spent ${summary['spent_usd']:.4f}", flush=True)
                save()
            try:
                append_notes(note_file, challenge_name=challenge.get("name") or str(cid),
                             outcome=str(row.get("outcome") or row.get("error_type") or row.get("status")),
                             turns=result.get("model_calls") or 0, summary=extract_final_text(directory))
            except OSError:
                pass
            return row.get("outcome") or "error"

        if workers == 1:
            for challenge in plan:
                if attempt_one(challenge) == "budget_exhausted":
                    break
        else:
            with ThreadPoolExecutor(max_workers=workers) as pool:
                list(pool.map(attempt_one, plan))
    summary["status"] = "completed"
    save()
    print(f"Done. Solved {len(summary['solved'])}/{len(summary['planned'])}; "
          f"spent ${summary['spent_usd']:.4f} of ${policy['global_budget_usd']:.2f}", flush=True)
    return summary
