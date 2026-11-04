# Complexity cleanup verification

November 3, 2026 (America/New_York).

**34 fast tests and all 19 synthetic Docker checks passed.** No live model calls,
CTFTiny attempts, pilots, scored runs, or improvement experiments occurred.

## Changes and scope

- `request_response()` owns response-turn/time checks, callback execution,
  response validation, and related events. `run_agent()` owns history, sequential
  tools, and appending observations. The catch around the whole turn was narrowed
  to expected stopping at deadline/tool boundaries.
- Eight response-envelope cases now test the pure validator directly instead of
  constructing full mocked attempts. Representative loop cases retain rejection,
  logging-bound, recovery, ID reuse, and stopping checks. The repeated terminal-
  reason variants were reduced to one shared loop path; real guard/deadline
  mechanisms retain distinct Docker coverage.
- `tests/fixtures/traces.py` reads JSONL for assertions across four test modules.
  Standard `pytest.raises()` replaces manual exception assertions where raising
  is guaranteed. Network-denial checks retain their return-or-raise behavior.
- `self-check` delegates discovery of all Docker-marked cases to pytest, then saves
  the same provenance, JUnit results, suite/attempt records, and cleanup evidence.
  It no longer names only one test file or requires a hard-coded count of 17.
- An unused Docker stdin parameter and redundant adjacent deadline check were
  removed. No classes, framework, generic validator, or dependency was added.
- Unexpected Docker kill errors/timeouts now record `solver_stop_failed` and make
  the attempt an infrastructure failure. Missing/already-stopped containers remain
  harmless. The original stop trigger remains in `attempt_stopping`; cleanup still
  attempts both removals. The monitor join allows its three-second kill timeout to
  finish before tracing closes.

New focused regressions distinguish daemon failure, kill timeout, missing container,
and already-stopped container. They check failure evidence/classification and both
cleanup calls using substitutes, with no host command execution. Another regression
confirms an unrelated response-recording RuntimeError still propagates when stopping
occurs concurrently. The fast-test count therefore increased even though fewer
cases need full lifecycle fixtures; test count was not a simplification target.

Response-envelope compatibility policy, prompts, limits, configuration defaults,
tool/evaluator implementations, firewall rules, worker code, and Dockerfiles were
not changed. Strict protocol fields and duplicated default values remain review
items for separate decisions. See [context design](../../docs/DESIGN.md#context-passed-between-turns)
for the full-history strategy, state ownership, and function return behavior.

## Reproduce

```sh
uv sync --frozen
uv run python -m pytest -q --disable-plugin-autoload --junitxml=runs/cleanup-fast.xml
uv run python -m ctf_agent build-images
uv run python -m ctf_agent self-check --output runs
```

One self-check now includes the original 17 controls and two scripted-loop cases.
Use fresh run directories and run Docker verification sequentially because cleanup
checks query the shared project label. Actual checks used the already synchronized
`.venv/bin/python`, equivalent to these commands.

The first invocation found the project image tags absent and stopped before any
test attempts. Its [startup failure](self-check-f70f1a59591c/suite.json) is retained.
Rebuilding the unchanged Dockerfiles restored the tags using cached layers; the
subsequent combined suite passed. Actual image IDs/ARM64 architecture are in its
provenance. No image-policy or dependency-pin change was needed.

## Retained evidence

- [Fast-test JUnit report](pytest-fast.xml): 34 passed, no failures/errors/skips.
- [Combined suite](self-check-cac703cb24ae/suite.json): 19 passed, pytest exit code
  zero, cleanup verified, settings, source hashes, image provenance, and run IDs.
- [Docker JUnit report](self-check-cac703cb24ae/pytest.xml): per-case outcomes and
  properties linking each case to its attempt.
- Each run directory contains its complete `trace.jsonl` and `summary.json`.
- [Post-run audit](verification.json): current source hashes match; all previous
  19 Docker check identities and effective configuration values are preserved;
  all 19 trace sequences and one-result-per-executed-tool counts verify; six
  prohibited IPv4 probes retain independent packet-denial events. Scripted request
  message counts replay from initial public history, replies, and observations.

[Scripted success](self-check-cac703cb24ae/68a25461b357/summary.json) retained five
turns/five tools, recovering from a failed command, writing/running a solver script,
retrieving a generated flag through the permitted target interface, and stopping
after verified success. The later requested sibling command did not execute.
[Late response](self-check-cac703cb24ae/8591978d7520/summary.json) retained one turn,
zero tools, and `wall_limit`; the solver stopped during the response wait and the
late command was discarded. No unexpected stop failures occurred in the real
container checks; the new failure cases use controlled substitutes.

Pytest recorded 0.083 seconds for fast tests and 53.836 seconds for Docker tests.
The encompassing launcher recorded **54.194444 seconds**. These are setup timings,
not a controlled performance comparison. Both the launcher and independent final
Docker queries found no project containers or networks. Earlier evidence remains
unchanged. All actual model-call and gateway-cost counts remain zero.

Python callbacks still cannot be forcibly interrupted; a callback ignoring its
timeout can delay host cleanup while the watchdog independently attempts to stop
the solver. No token-aware context fitting, live transport policy, gateway/model
compatibility, pricing/account limits, AMD64 execution, or CTFTiny integration was
established. Stop for review before beginning the next milestone.
