# Passive target diagnostics before removal — November 11

Implemented the user-approved diagnostic milestone, keeping application behavior
and benchmark solving outside the investigation. The [pre-change hypothesis](../../docs/EXPERIMENTS.md#passive-target-snapshot-before-cleanup--november-11)
connects repeated connection failures and startup-only records to the missing
target end-state evidence. This is instrumentation, not a demonstrated service fix.

## Change and where to find it

`ctf_agent/challenge.py` reuses one snapshot function for startup and final target
state. The final `service_checks.before_cleanup` is collected before Compose
removes target containers/networks. It appears in `target/target.json` and the
launcher's `run.json` target object.

Each service retains status/running/restarting, restart count, exit code,
OOM-killed and health status, plus network names/IDs/IP addresses. No environment,
argv, healthcheck command/log bodies, files or answer values are serialized.
Collection is passive: no service connection, target shell, payload or restart.
It is not exposed to the solver/model.

The final snapshot shares a three-second allowance across services. Missing
containers are marked `missing`; other inspection errors are `unavailable` with
an error type, without raw exception text. Unexpected diagnostic errors are
separate from cleanup errors. Diagnostic failure does not change the original
outcome/exception or prevent cleanup. Genuine cleanup failures still fail as
before. Startup readiness remains strict; final diagnostics do not assert that
the target is healthy. No new setting, dependency, monitor or agent tool.

## Actual verification

- **49 offline cases passed** across target diagnostics, challenge integration and
  development launcher tests. Checks cover healthy/exited/OOM/detached metadata,
  privacy, missing/error capture, continued inspection of other services, shared
  diagnostic allowance, preservation of original outcomes/exceptions and cleanup
  failure precedence. [JUnit](offline.xml).
- **Four distinct synthetic Docker cases passed**: unhealthy startup, exited
  dependency, externally removed service and live network-detached service.
  The initial run had three passes and a fixture-image resolution failure in the
  startup case. That single case passed on focused retry. Preserve both
  [initial report](docker-initial.xml) and [retry](docker-startup-retry.xml).
- All five synthetic target records, including that initial setup failure,
  recorded no cleanup errors. [Whitelisted snapshots and source hashes](checks.json).
  Full generated Compose/private runtime files remain under ignored `runs/`.
- Zero model calls, paid API requests, real challenge attempts or challenge
  logic/source/binary inspection. Current prompt, Luna/medium/8,192, 2 MiB input,
  90-second requests, 600-second attempts, images and guard policies remain fixed.

The native Docker tests intentionally stop/remove/disconnect only disposable
synthetic services. No existing user batch was modified; the preceding pwn batch
had already completed before application source changed. Its four ordinary
unsuccessful outcomes do not establish an identical cause across trials.

## Limits and next rerun

The snapshot is taken at teardown, after solver cleanup; it is not state at the
exact instant a connection failed. A target could recover or change between those
times. It does not record listener processes, continuous lifecycle events or packet
delivery. If targets remain running and attached after another failure, more
specific passive networking/listener diagnostics would be a separate next step.
Inspection can consume up to roughly three seconds of extra teardown time, outside
the active attempt allowance. This does not extend model execution or retry limits.

From the repository root, a fresh user-run diagnostic pilot can use:

```sh
uv run --frozen --env-file .env python -m ctf_agent run-batch \
  --experiment evidence/target-precleanup-snapshot/experiment.toml \
  --challenges pwn-roppity pwn-baby-boi \
  --trials 2 \
  --output runs/pilots/pwn-target-snapshots
```

This schedules four paid development attempts and has not been launched here.
Preserve all failed attempts. Compare final target state with connection-error
timestamps and startup state before drawing a runtime diagnosis. Do not interpret
exit code 137 alone as proof of OOM; inspect the separate OOM field.
