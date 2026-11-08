# Prompt, command contract and recoverable output — November 8

Implemented the user-approved combined milestone against documentation checkpoint
`4620032` and runtime baseline `616b5f2`. The hypothesis was recorded before changes
in [EXPERIMENTS](../../docs/EXPERIMENTS.md#combined-prompt-tool-contract-and-output-recovery--hypothesis-recorded-november-8).
This evidence establishes synthetic behavior and controls, not a solving improvement.
No real challenge attempts, model calls, held-out contents, benchmark answer keys, hosted
writes, dependency changes or image rebuilds were involved in this implementation
verification. At that milestone implementation was uncommitted for review.

**Later November 8 update:** implementation and this evidence were committed in
`e7e366c`. The user subsequently ran the eleven-ID development batch; its
[separate record](../agent-first-fix-batch/README.md) reports 6/11 successes and a
supplemental `rev-tablez` export. The original synthetic reports/hashes below remain
unchanged; live behavioral trace review is still pending.

## Implemented behavior

- System instructions describe the verified AMD64 environment, installed toolkit,
  writable locations, persistence and live-debugging limitation. Focused validation,
  original-artifact comparisons and contradiction diagnosis replace overlapping
  recovery text. Concise visible tool purposes and evaluator-only success remain.
- The command contract states new `/bin/sh` shells, no cross-call input, same-
  connection exchanges, internal deadlines and timeout restart effects. Actual
  timeout bounds still come from configuration. No new agent tools or sessions.
- The existing selector reader keeps at most 64 KiB combined raw preview bytes
  and inserts explicit per-stream omitted-byte markers. On overflow it saves the
  buffered beginning **before eviction**, then streams raw stdout/stderr to separate
  files. Short output creates no files. Invalid UTF-8 stays intact in raw artifacts.
- New explicit positive-integer settings bound retained bytes to 10 MiB per
  command and 100 MiB per attempt. The latter counts across solver restarts.
  Caps/storage errors do not stop draining or erase late diagnostics. The summary
  reports `captured_output_bytes`.
- Private `outputs/<capture-id>/{stdout,stderr}.bin` artifacts survive cleanup.
  A fixed non-root Python writer receives them through Docker stdin, without
  loading the whole file into host memory. No-follow directory traversal and
  exclusive file creation reject symlinks, collisions and special files. Only
  acknowledged copies receive solver-readable paths under `/workspace/.command-output`.
- `capture` distinguishes completeness, bytes retained, cap exhaustion, storage
  failure and delivery failure. Timeout output is partial. Copies share a five-
  second delivery allowance clipped to the remaining attempt deadline. Ordinary
  delivery errors preserve the command result. Internal delivery timeout is
  terminal infrastructure failure, preserving a bounded result event, because
  killing the Docker client alone could leave its writer running. Delivery never
  restarts the solver or overrides an existing terminal reason.

Only two attempt settings were added. The recorded model table and all pre-existing
attempt settings match the baseline exactly. Solver/guard/target images and SDK
versions remain unchanged. No framework, application class, daemon or additional
detailed trace backend was introduced.

## Actual verification

| Check | Result | Evidence |
| --- | --- | --- |
| Full offline suite, including write/close fault injection and delivery-stop races | 132 passed | [offline.xml](offline.xml) |
| Full synthetic Docker suite before final close-error hardening | 42 passed in 176.99s | [docker.xml](docker.xml) |
| Final output-focused Docker subset after hardening | 10 passed in 38.02s | [docker-output-final.xml](docker-output-final.xml) |
| Additional actual-default-size capture/delivery check | 1 passed in 4.88s | [docker-default-cap.xml](docker-default-cap.xml) |
| Saved summaries/artifacts and cleanup audit | 52 summaries, 19 overflow observations; no model calls, cleanup errors or remaining managed containers/networks | [verification.json](verification.json) |

The ten focused cases overlap the full suite; the default-size case was added
afterward. Together these cover **43 distinct Docker cases**, not 53 independent
cases. The full suite was not repeatedly rerun after unrelated documentation edits.
One added fault-injection test initially wrapped a read handle in a mock without
context-manager support. Restricted injection to write handles, added close-fault
coverage and reran the offline suite successfully. Its original failure report
remains at `runs/first-fix/offline-final.xml`; no command-result defect caused it.

Offline checks cover threshold/threshold-plus-one, exact original prefix/middle/end,
mixed streams, invalid UTF-8, long lines, cap exhaustion while draining, open/write/
close failures, streamed input and terminal/deadline races. Existing model-history
and native-SDK trace tests verify the same prompt/schema and capture metadata
reach the responder and recorded observations.

Docker checks prove UID-1000 file retrieval by size/hash, short-output no-file
behavior, timeout reset with retrievable partial stdout/stderr, safe path refusal,
surviving host artifacts, continued commands after retention exhaustion, existing
scope/private-data controls, evaluator stops, background cleanup and toolkit use.
The final 10 MiB check received 10,485,769 bytes, retained exactly 10,485,760,
reported incomplete/capped capture, retained the late preview and retrieved the
prefix in the solver. Source/image/config/prompt hashes and report hashes are in
`verification.json`; original summaries, native spans and raw files remain under
ignored `runs/first-fix/`.

To reproduce the current suites from the repository root (no `.env` or model key):

```sh
uv run --frozen pytest -q
uv run --frozen pytest -m docker -q -x --ctf-output runs/first-fix-reproduction
```

Actual verification used `uv run --no-sync` with the existing locked environment
and a writable temporary uv cache. Tests substitute the local SDK exporter; they
do not upload synthetic spans. Docker must be running with the existing images.

Final documentation checks passed for 174 local links/heading targets and
`git diff --check`. Recorded application/configuration/test hashes match the
current source; new public evidence passed credential/candidate-pattern checks.

## Limits and next step

Output files preserve received bytes only. Timeout, disk errors and caps can leave
partial files; stdout/stderr do not reconstruct exact cross-stream ordering.
Retaining host and solver copies can consume twice the logical capture allowance;
arbitrary solver files still have no per-attempt disk quota. Delivery adds up to
five seconds of bounded execution time within the original attempt allowance.
Storage failures and delivery timeout handling were fault-injected offline;
real Docker checks cover ordinary delivery and rejection paths.

At the synthetic-verification handoff, mechanical acceptance checks had passed
and no performance comparison had run; none of the earlier eleven traces was
runtime-truncated. The later user-run batch is recorded in the update above,
with detailed behavioral review still pending. Model/effort/token
allowances, planning, notes, continuation, compaction and cost-estimate reconciliation
remain separate work. Any later effect belongs to the bundled package unless its
components are compared separately.
