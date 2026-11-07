# Execution simplification checkpoint

Completed November 6, 2026. No live model requests, challenge solving, new hosted
traces, pilot or scored attempts. Target/network policy and image selection are
separate later checkpoints. [Plan](../../docs/SIMPLIFICATION_PLAN.md).

## Baseline and scope

The clean baseline is commit `64f6385fb788f2c54e2a4f0ca6a661fd8d1c51d1`.
[Baseline identities](baseline.json) preserve source/settings/image hashes. The
previous solver image is retained locally as `ctf590-solver:baseline-64f6385`
(see baseline.json for its full image identity). No Git commit/push was
performed. Existing historical evidence remains unchanged.

Standard Docker copy, exec, init and restart replace the worker service. A
writable disposable solver has ordinary home/temp storage and an image-prepared
venv. Trusted pre-agent copying assigns ownership with CHOWN; model commands are
UID/GID 1000, have zero effective capabilities and cannot gain privileges.

Existing head/tail and no-follow file-writing ideas are adapted into a bounded
host reader and one-shot in-solver writer. Small custom restart coordination and
initial inventory remain. The custom guard/evaluator/agent/tracing/batch are
reused; these are not claimed as NYU-supplied code. No runtime dependency is added.

Removed: the 354-line worker, socket/RPC, PTY/session lifecycle, Linux supervisors/
subreapers, tar staging/extraction, output identifiers/base64/artifact copying,
per-tool package scans and obsolete contracts/tests/settings. Runtime Python
across `ctf_agent/` and `docker/` decreases **1,906 → 1,575 lines (331 fewer)**.

## Verification

- [93 offline tests](fast-tests.xml) passed: private evaluator boundary, model
  adapter/history, native SDK export/pagination, failed recovery, terminal-stop
  races, batch interruption/incident records and configuration controls.
- [28 synthetic Docker cases](self-check-1a9243536e1f/suite.json) passed in one
  complete run, with cleanup verified. Includes actual copying/ownership/modes,
  libraries/utilities, writable home/pip, subsequent execution, restart persistence,
  detached/background reset, late output, limits, guard loss, denied traffic,
  submissions and interruption/setup cleanup. Native SDK spans use local transport.
- [Two fresh development preparation cycles](ctftiny-readiness-8e13f7024ff4/check.json)
  passed for `pwn-baby-boi`: real contestant-file hashes/ownership, permitted TCP
  connect-and-close, private boundaries, denied traffic, fresh state and cleanup.
  No target response contents or solving were needed.
- [Final verification/provenance](verification.json) records image identities,
  current source hashes, unchanged agent/guard/dependencies, counts and tradeoffs.
  Only `workspace_mb` was removed from resolved attempt settings; model settings
  and other controls are unchanged. It lists post-Docker housekeeping edits:
  offline-tested batch classification/tests and the subsequently exercised
  preparation check. Execution/solver/control-test source matches the full run.

Reproduce sequentially, from the repository root:

```sh
uv run --frozen python -m ctf_agent build-images
uv run --frozen python -m pytest -q
uv run --frozen python -m ctf_agent self-check
uv run --frozen python -m ctf_agent prepare-challenge --challenge pwn-baby-boi
```

The first Docker run passed five checks then failed a capability-name assertion
(`CAP_CHOWN` versus `CHOWN`); the corrected focused run passed seven cases.
Those XML/trace records remain under `docker-first*` and `docker-focused*`.
Offline follow-ups corrected a nested-metadata assertion and removed the stale
missing-usage batch outcome test; retained failed/first XML and the final passing
XML distinguish that work. No production recovery failure was suppressed.

## Deliberate losses and remaining limits

No cross-call interactive terminal or model-directed input to an existing process.
A timeout resets **all** solver processes/connections, including unrelated tasks;
files and pip installs survive. Targets/guard, run ID, counters and original
deadline do not reset. Recovery failure and scope/guard/deadline stops remain
terminal; there is no automatic retry. Race tests use substituted Docker calls,
not a daemon stress test.

There is no portable workspace disk quota or automatic full-output retrieval.
Bounded head/tail observations retain explicit truncation; commands may redirect
output themselves. Initial package inventory is retained; optional final capture
is commonly unavailable after terminal stop and that fact is traced. Old artifacts
are retained in their historical records. CPU/RAM/PID/time/call/output/write and
model limits, independent denial evidence and trusted submissions remain.

This verifies infrastructure behavior for these checks, not solve rate or every
challenge. Supplied NYU image has not been built/selected. Current target Compose
rewrites and guard/network topology remain unchanged. Stop for checkpoint review
before that next stage or a separately authorized live pilot.
