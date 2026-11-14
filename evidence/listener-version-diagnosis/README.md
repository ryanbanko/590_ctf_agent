# Listener exit diagnosis — November 14, 2026

This is the preserved diagnosis milestone, before a production change. The later
[approved correction and two successful development retries](../listener-update/README.md)
supersede the pending-fix notes below; original records/hashes remain unchanged.

**Diagnosis:** both exact development images contain socat 1.7.3.2, which has an
upstream post-fork diagnostic-channel bug. A synthetic child crash reproduces the
historical listener exit without either challenge program or our solver/guard.
Production remains unchanged; the correction is a separate review step.

## What was inspected

The user approved the process investigation and expanded its scope to service
definitions/startup scripts and paths/arguments needed to understand process
handling. Both image defaults are a direct `socat -T60` command with a forking TCP
listener, service-user switch and EXEC address. Saved effective Compose records
have null command/entrypoint overrides. See [metadata](metadata.json).

Only those two known images' startup metadata and the socat version command were
read. All live services replaced the original executable with our fixed harmless
shell child. No task binary/source, payload, solution, flag, environment dump or
answer key was inspected; no real challenge/model run occurred.

## Reproduction and controls

The [helper](../../tests/check_listener_image.py) creates a disposable internal
bridge, starts only the installed listener, copies a synthetic shell script and
connects using a generic Python client. No published ports, host mounts, solver,
guard, added target resource quota or target security override is involved.
Every case removes its containers and network. Core dumps are disabled in the
synthetic child; its signal is deliberate, not a crash in challenge code.

Final helper verification:

| Child / listener arrangement | Roppity image | Baby-boi image |
| --- | --- | --- |
| Normal child exit, supplied listener options | 20/20 connections; listener running | 20/20; running |
| Child sends itself SIGSEGV, supplied listener options | First connection works; listener exits 1; next fails | Same |
| Same child SIGSEGV, append `nofork` to EXEC address | 20/20 connections/crashes; listener running | 20/20; running |

Earlier exploratory checks reproduced the exit with Docker `--init`, without the
service-user switch, and with a one-second delay before the child signal. Verbose
synthetic logs reproduce `socat[1] E waitpid(): child ... exited on signal 11`.
One child identifies its parent as the per-connection relay while the fatal
message appears under the master PID: the log prefix is not proof that the master
actually reaped that grandchild.

All [16 records](audit.json) are preserved: ten exploratory and six final cases.
Final cases have the current helper's SHA-256; exploratory records retain the
hashes of earlier helper revisions. Earlier differences added debug/PID reporting
and diagnostic switches; final cleanup removed unused orphan/disconnect modes.
Expected failures are retained as failures, not relabeled as healthy services.

## Why this explains the symptom

In the generic 1.7.3.2 source, `error.c` initializes a socketpair for deferred
signal-handler messages/exit requests. The fork setup in `xioinitialize.c` does
not replace that inherited pair. An EXEC child failure is reported through
`xiosigchld.c`; another forked process can consume the deferred fatal message and
exit. This also explains intermittent survival and misleading master-PID logs.

The upstream **1.7.3.3** entry says this mechanism could
“reach and kill the wrong process.” Its correction introduces per-child diagnostic
socket initialization (`diag_fork()`), present in the reviewed 1.7.4.4 source.
See the [upstream changelog in Debian's source archive](https://sources.debian.org/src/socat/1.7.4.4-2/CHANGES)
and [release-source archive hashes/file hashes](audit.json). The original release
sources were read from MacPorts' source mirror; no downloaded source was executed.
Some direct Ubuntu/Debian URLs were unavailable and the upstream site's TLS check
failed; verified HTTPS to the source mirror succeeded without disabling validation.

The exact-image reproduction, matching historical signature and upstream fix
support this diagnosis strongly. We have not run a native AMD64 comparison or a
fixed-version listener inside the original images. This does not explain every
unsuccessful challenge attempt or establish a solving improvement. The earlier
generic tests used 1.7.4.4, which already contains the correction; their success
does not contradict this result.

## Correction options, pending review

1. **Prefer a pinned listener-only update/backport containing the upstream fix.**
   Preserve the image's application/runtime, user, listening endpoint, relay I/O
   and `-T60` behavior. First test the fixed listener against this reproduction,
   then normal I/O, inactivity/disconnect behavior and cleanup. Record any target
   compatibility adjustment; do not change historical images/results in place.
2. **`EXEC:...,nofork` is a demonstrated workaround, not an equivalent replacement.**
   It keeps listener forking but directly executes the child in each connection
   process. The extra relay disappears; stdin/stdout become the accepted socket
   instead of the relay socketpair, and the relay transfer loop is bypassed.
   Its inactivity-timer and disconnect behavior therefore need explicit review.
   It is a one-option change, but not necessarily the smallest behavioral change.
3. **Do not add automatic restart, privileges or larger budgets for this bug.**
   Restart hides an exit and resets state; init did not prevent the reproduction.

## Constraint review

| Current choice | Assessment from this investigation |
| --- | --- |
| Target limits/capabilities | No additional restriction is needed to reproduce the failure. The production target adapter preserves supplied settings; earlier target quotas were already removed. |
| Removing published host ports | Compatible with our direct bridge endpoint. The synthetic failure also occurs with ordinary Docker networking. No evidence that port publishing repairs it. |
| Removing shared Docker socket | Important host/evaluator boundary; cannot explain a reproduction that needs no socket. Tasks requiring Docker administration remain a separate compatibility decision. |
| Solver 1 CPU / 1 GiB / 64 PIDs and guard limits | Potential limits for expensive work, but neither container exists in the failing reproduction. No basis to raise them to fix this exit. |
| New shell per command, no PTY | A usability tradeoff, not this listener failure. Stateful network exchanges must stay in one script/connection; that does not require a persistent terminal subsystem. |
| Whole-solver reset after command timeout | Deliberately ends all background processes/connections. Worth reviewing if later evidence shows collateral loss; not responsible for this reproduction or the historical zero-restart failure. |
| AMD64 on ARM64 emulation | Still a compatibility/performance consideration. This investigation does not isolate its contribution; the upstream bug predates our Docker setup and does not justify globally loosening controls. |
| Diagnostic access | Earlier excessive filtering prevented identification of the actual listener version/options. User-approved infrastructure metadata access resolved that obstacle without exposing challenge logic or changing solver access. |

No control was loosened. The simplest next work is a targeted listener correction,
not a broader sandbox redesign, new session framework or supervisor.

## Repeat without challenge execution

The two exact target images and a local `python:3.13.2-slim-bookworm` client image
must already exist. The helper never pulls/rebuilds those target images.

```sh
.venv/bin/python -m tests.check_listener_image --image roppity --mode normal
.venv/bin/python -m tests.check_listener_image --image roppity --mode signal --debug
.venv/bin/python -m tests.check_listener_image --image roppity --mode signal --nofork-exec
# Repeat with --image baby-boi; --init and --without-user-switch are diagnostic controls.
```

These commands intentionally reproduce an unhealthy synthetic service in the
baseline crash case. Inspect `case.end` and connection records; helper exit 0
means the diagnostic completed, not that the listener stayed healthy.
