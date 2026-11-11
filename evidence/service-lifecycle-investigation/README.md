# Development service investigation — November 11

The user authorized investigation of `pwn-roppity` and `pwn-baby-boi` after
repeated connection failures. The user subsequently asked to avoid examining the
challenge itself, and preferred a fresh small rerun if infrastructure checks did
not reproduce the outage. No challenge logic/binary/source analysis or recorded
exploit execution was performed during this investigation. No answers, solutions,
write-ups, administrative target shell or held-out contents were consulted.

## Findings

| Model-free check | Result |
| --- | --- |
| Roppity: three connect/close, three banner read/close, three short-line exchanges | All nine connected; listener stayed running; no restart/OOM or scope incident |
| Baby-boi: same nine exchanges | All nine connected; listener stayed running; no restart/OOM or scope incident |
| Roppity: one fixed 256-byte invalid line followed by ordinary reconnections | A child signal-11 signature appeared; the listener remained running and three subsequent connections succeeded |

The invalid-line check completed **before** the user's request to avoid the
challenge part; no further stress test was performed. The retained diagnostic
helper has that option removed and performs only the nine ordinary exchanges.
No exploit bytes, addresses or code were copied from traces. Response content was
discarded; only byte counts, EOF/error categories and timing were recorded. Target
logs were reduced to counts of fixed signal/error signatures; no log text is shared.

Targets used the **same image IDs as the historical failed attempts**:

- Roppity: `sha256:e0fe9b2db871e1324ab71bc85d308783b6224fd62271d8ea4df3962aace4047c`.
- Baby-boi: `sha256:e92afa986ce9c1fd01cdffb38cb46b8e66ffb802dab9382e912d33003144c665`.

Engine: Docker 28.3.2, ARM64. Probes ran as fixed scripts through the normal
isolated solver and enforced assigned endpoints, with the local in-memory SDK
exporter. Zero model calls, zero submissions, zero paid API requests. All three
completed checks recorded no target/solver cleanup errors or scope incidents.

An initial diagnostic failed before starting a solver because Docker `top` requires
a PID column in custom process output. The helper was corrected to request PID
and command name while retaining only names. Target cleanup succeeded; the
failed diagnostic is retained in [filtered records](checks.json), not classified
as a challenge or agent failure. The final helper also passed syntax compilation.

## What remains unknown

The old runs show initial connectivity followed by timeouts/no-route errors. Their
saved target state covers startup only; normal launch cleanup removes the target
before later inspection. These new short checks did **not reproduce that outage**.
They do not establish that targets remained healthy in the old attempts, rule out
intermittent networking/emulation/resource issues, or prove all payload behavior.
One generic child crash surviving is not proof every crash/payload is harmless to
the listener. No native-AMD64 comparison or long-running soak was performed.

There is no demonstrated infrastructure fix to apply now. Prefer a small fresh
development rerun. If the error recurs, passive lifecycle/network event evidence
before cleanup would be more useful than speculative target changes or automatic
target restarts. Adding that instrumentation is a separate proposed change.

## Fresh rerun

The user started `batch-8c72ac67cab7`. Its first roppity attempt again lost endpoint
access and ended without success. The [infrastructure-only first-attempt review](rerun-first-attempt-review.md)
records chronology, evidence limits and the proposed passive diagnostics. Other
attempts/batch status were not finalized by that review; no full-batch outcome is
claimed here. The command below remains the original rerun instruction, not a
request to replace or relaunch the active batch.

[Snapshot](experiment.toml): current Luna/medium/8,192, 2 MiB input, 90-second
requests, 600-second attempts. The investigation changes no production agent,
image, endpoint, guard or target lifecycle behavior. The only added executable
source is [the explicit diagnostic helper](../../tests/check_service_lifecycle.py).

```sh
uv run --frozen --env-file .env python -m ctf_agent run-batch \
  --experiment evidence/service-lifecycle-investigation/experiment.toml \
  --challenges pwn-roppity pwn-baby-boi \
  --trials 2 \
  --output runs/pilots/pwn-service-recheck
```

This schedules four paid autonomous development attempts and has **not** been
launched here. Preserve all earlier failures and the new trial outcomes. It tests
repeatability under current conditions, not a service fix or isolated prompt effect.
The historical raw private target directories remain Git-ignored; only selected
diagnostic fields/source hashes appear in `checks.json`.
