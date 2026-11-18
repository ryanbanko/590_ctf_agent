"""Orchestration core: planning, per-challenge limits, prefaces, notes, budget."""

import json

from ctf_agent import compete
from ctf_agent.htb import category_label


def challenge(cid, difficulty, category_id=2, points=100, solved=False, name=None):
    return {"id": cid, "difficulty": difficulty, "challenge_category_id": category_id,
            "points": points, "solved": solved, "name": name or f"c{cid}"}


POLICY = compete.DEFAULT_POLICY


# --- planning ---------------------------------------------------------------

def test_plan_orders_easiest_and_cheapest_first():
    event = {"challenges": [
        challenge(1, "hard", points=300),
        challenge(2, "easy", points=200),
        challenge(3, "easy", points=100),
        challenge(4, "very easy", points=500),
    ]}
    order = [c["id"] for c in compete.plan_challenges(event, POLICY, category_label)]
    assert order == [4, 3, 2, 1]  # very easy, then easy by points, then hard


def test_plan_skips_solved_and_skip_categories():
    policy = dict(POLICY, skip_categories=["web"])  # category_id 2 -> Web
    event = {"challenges": [
        challenge(1, "easy", category_id=2),        # Web -> skipped
        challenge(2, "easy", category_id=4, solved=True),  # solved -> skipped
        challenge(3, "easy", category_id=5),        # Reversing -> kept
    ]}
    assert [c["id"] for c in compete.plan_challenges(event, policy, category_label)] == [3]


def test_unknown_difficulty_sorts_last():
    event = {"challenges": [challenge(1, "mystery"), challenge(2, "easy")]}
    assert [c["id"] for c in compete.plan_challenges(event, POLICY, category_label)] == [2, 1]


# --- per-challenge limits ---------------------------------------------------

def test_challenge_limits_uniform_across_difficulties():
    for diff in ("very easy", "easy", "medium", "hard", "insane", "unknown"):
        limits = compete.challenge_limits(challenge(1, diff), POLICY)
        assert limits["max_model_turns"] == 200
        assert limits["wall_seconds"] == 3600.0
        assert limits["reasoning_effort"] == "high"


# --- budget gating ----------------------------------------------------------

def test_should_attempt_stops_at_budget():
    ok, reason = compete.should_attempt(challenge(1, "easy"), POLICY, spent_usd=POLICY["global_budget_usd"])
    assert ok is False and reason == "budget_exhausted"


def test_should_attempt_defers_hard_when_budget_low():
    spent = POLICY["global_budget_usd"] * 0.8  # 20% left, below the 30% reserve
    assert compete.should_attempt(challenge(1, "hard"), POLICY, spent)[0] is False
    assert compete.should_attempt(challenge(1, "easy"), POLICY, spent)[0] is True  # easy still allowed


def test_should_attempt_allows_when_healthy():
    assert compete.should_attempt(challenge(1, "insane"), POLICY, spent_usd=0.0)[0] is True


# --- prefaces ---------------------------------------------------------------

def test_build_preface_includes_flag_format_and_category():
    preface = compete.build_preface(challenge(1, "easy", category_id=3), "", category_label, base="BASE")
    assert "BASE" in preface
    assert "HTB{...}" in preface
    assert "protections" in preface  # the pwn hint (category_id 3)


def test_build_preface_includes_notes_when_present():
    preface = compete.build_preface(challenge(1, "easy"), "tried xoring the key, failed", category_label)
    assert "earlier attempts" in preface
    assert "tried xoring the key" in preface
    # No notes -> no notes section.
    assert "earlier attempts" not in compete.build_preface(challenge(1, "easy"), "   ", category_label)


# --- notes store ------------------------------------------------------------

def test_notes_roundtrip(tmp_path):
    path = compete.notes_path(tmp_path, 3755, 79390)
    assert compete.read_notes(path) == ""  # missing -> empty
    compete.append_notes(path, challenge_name="DNS Dossier", outcome="wall_limit",
                         turns=42, summary="found a format string at offset 6")
    text = compete.read_notes(path)
    assert "DNS Dossier" in text and "format string at offset 6" in text and "42 model turns" in text
    compete.append_notes(path, challenge_name="DNS Dossier", outcome="success", turns=55, summary="")
    text = compete.read_notes(path)
    assert "no end-of-run summary captured" in text  # empty summary handled
    assert text.count("## DNS Dossier") == 2  # appended, not overwritten


def test_read_notes_truncates_to_recent(tmp_path):
    path = tmp_path / "n.md"
    path.write_text("OLD" + "x" * 50_000 + "RECENT")
    text = compete.read_notes(path, max_bytes=1000)
    assert text.endswith("RECENT") and "OLD" not in text and len(text) <= 1000


# --- trace summary extraction ----------------------------------------------

def test_extract_final_text_from_observations(tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    observations = {"data": [
        {"type": "GENERATION", "endTime": "2026-11-18T05:00:00Z",
         "output": {"content": "early step"}},
        {"type": "GENERATION", "endTime": "2026-11-18T05:10:00Z",
         "output": [{"type": "message", "content": "Established: the binary checks a CRC. Blocked: need the key."}]},
        {"type": "TOOL", "endTime": "2026-11-18T05:11:00Z", "output": "ignored"},
    ]}
    (run_dir / "observations.json").write_text(json.dumps(observations))
    assert "Established: the binary checks a CRC" in compete.extract_final_text(run_dir)


def test_extract_final_text_missing_is_empty(tmp_path):
    assert compete.extract_final_text(tmp_path) == ""


# --- cost accounting --------------------------------------------------------

def test_attempt_cost_reads_known_usage():
    report = {"result": {"known_usage": {"cost_usd": 0.0123}}}
    assert compete.attempt_cost(report) == 0.0123
    assert compete.attempt_cost({"result": {"known_usage": {"cost_usd": None}}}) == 0.0
    assert compete.attempt_cost({}) == 0.0


# --- run_event orchestration (model/MCP/Docker faked) -----------------------

from contextlib import contextmanager  # noqa: E402


def _patch_event(monkeypatch, event, outcomes, captured):
    from ctf_agent import launch, htb_mcp, agent

    @contextmanager
    def fake_clients(experiment_path):
        yield ({"solver_image": "s"}, {"base_url": "https://x", "request_seconds": 90.0}, None, None)

    @contextmanager
    def fake_session():
        yield (lambda *a, **k: None)

    def fake_run(settings, ctf_id, challenge_id, directory, *, langfuse, respond, model_usage,
                 call, prompt_preface=None, verify_candidate=None, verification_source="htb-mcp",
                 export_trace=None):
        captured[challenge_id] = {"settings": settings, "model_usage": model_usage, "preface": prompt_preface,
                                  "verify_candidate": verify_candidate, "verification_source": verification_source}
        directory.mkdir(parents=True, exist_ok=True)
        solved, cost = outcomes[challenge_id]
        report = {"result": {"verified_success": solved, "run_id": f"r{challenge_id}", "model_calls": 7,
                             "termination_reason": "success" if solved else "wall_limit",
                             "known_usage": {"cost_usd": cost}}, "trace_url": "u"}
        (directory / "run.json").write_text(json.dumps(report))
        (directory / "observations.json").write_text(json.dumps({"data": [
            {"type": "GENERATION", "endTime": "2026-11-18T05:00:00Z",
             "output": {"content": f"summary for {challenge_id}"}}]}))

    monkeypatch.setattr(launch, "open_model_clients", fake_clients)
    monkeypatch.setattr(launch, "run_htb_challenge", fake_run)
    monkeypatch.setattr(htb_mcp, "htb_session", fake_session)
    monkeypatch.setattr(htb_mcp, "retrieve_ctf", lambda call, cid: event)
    monkeypatch.setattr(agent, "make_responder", lambda client, model, **kw: (object(), {"model": model}))


def test_run_event_plans_limits_notes_and_solves(tmp_path, monkeypatch):
    event = {"name": "Test", "challenges": [
        challenge(10, "very easy", category_id=2, points=100),
        challenge(11, "easy", category_id=5, points=100),
        challenge(12, "hard", category_id=3, points=300),
    ]}
    outcomes = {10: (True, 0.01), 11: (False, 0.02), 12: (True, 0.03)}
    captured = {}
    _patch_event(monkeypatch, event, outcomes, captured)

    summary = compete.run_event(tmp_path / "exp.toml", 3755, tmp_path / "out", notes_root=tmp_path / "notes")

    assert summary["planned"] == [10, 11, 12]          # easiest first
    assert summary["solved"] == [10, 12]
    assert round(summary["spent_usd"], 4) == 0.06      # all three costs summed
    assert summary["status"] == "completed"
    # per-challenge difficulty caps applied
    assert captured[10]["settings"]["max_model_turns"] == 200
    assert captured[12]["settings"]["max_model_turns"] == 200
    assert captured[12]["model_usage"]["model"]["reasoning_effort"] == "high"
    # preface carries flag format + the per-category hint (12 is pwn)
    assert "HTB{...}" in captured[12]["preface"]
    assert "protections" in captured[12]["preface"]
    # a note was stored per challenge
    assert "summary for 10" in (tmp_path / "notes" / "3755-10.md").read_text()


def test_run_event_concurrent_attempts_all_and_serializes_mcp(tmp_path, monkeypatch):
    event = {"challenges": [challenge(c, "easy") for c in (10, 11, 12, 13)]}
    outcomes = {10: (True, 0.01), 11: (True, 0.01), 12: (False, 0.01), 13: (True, 0.01)}
    captured = {}
    _patch_event(monkeypatch, event, outcomes, captured)

    summary = compete.run_event(tmp_path / "exp.toml", 3755, tmp_path / "out", workers=3,
                                notes_root=tmp_path / "notes")

    assert summary["workers"] == 3
    assert set(captured) == {10, 11, 12, 13}          # every challenge attempted
    assert sorted(summary["solved"]) == [10, 11, 13]
    assert round(summary["spent_usd"], 4) == 0.04     # all costs counted under the lock
    assert len(summary["attempts"]) == 4


def test_run_event_manual_verify_routes_to_human(tmp_path, monkeypatch):
    event = {"challenges": [challenge(10, "easy")]}
    captured = {}
    _patch_event(monkeypatch, event, {10: (True, 0.01)}, captured)

    # Default: MCP verification (no override passed).
    compete.run_event(tmp_path / "exp.toml", 3755, tmp_path / "o1", notes_root=tmp_path / "n1")
    assert captured[10]["verify_candidate"] is None
    assert captured[10]["verification_source"] == "htb-mcp"

    # manual_verify: a human-relay callable is passed and the source changes.
    compete.run_event(tmp_path / "exp.toml", 3755, tmp_path / "o2", notes_root=tmp_path / "n2",
                      manual_verify=True)
    assert callable(captured[10]["verify_candidate"])
    assert captured[10]["verification_source"] == "htb-human-relay"


def test_run_event_clamps_workers_to_cap(tmp_path, monkeypatch):
    event = {"challenges": [challenge(10, "easy")]}
    _patch_event(monkeypatch, event, {10: (True, 0.01)}, {})
    summary = compete.run_event(tmp_path / "exp.toml", 3755, tmp_path / "out", workers=999,
                                notes_root=tmp_path / "notes")
    assert summary["workers"] == compete.MAX_WORKERS


def test_run_event_stops_when_budget_exhausted(tmp_path, monkeypatch):
    event = {"challenges": [challenge(10, "easy"), challenge(11, "easy"), challenge(12, "easy")]}
    outcomes = {10: (False, 0.01), 11: (False, 0.02), 12: (False, 0.01)}
    captured = {}
    _patch_event(monkeypatch, event, outcomes, captured)
    policy = dict(compete.DEFAULT_POLICY, global_budget_usd=0.015)

    summary = compete.run_event(tmp_path / "exp.toml", 3755, tmp_path / "out",
                                policy=policy, notes_root=tmp_path / "notes")

    assert 12 not in captured                            # third never ran: budget hit
    assert summary["attempts"][-1]["status"] == "budget_exhausted"
    assert summary["spent_usd"] <= 0.03
