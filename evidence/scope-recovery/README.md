# One blocked-command recovery and scope instructions — November 8

Implemented the user-approved milestone against `b6ec0e5`. The
[hypothesis was recorded before implementation](../../docs/EXPERIMENTS.md#one-blocked-connection-recovery-and-scope-clarification--november-8).
The user selected the interpretation that prevented access can receive corrective
feedback; this is [user direction, not professor confirmation](../../docs/REFERENCES.md#november-8-blocked-connection-recovery--user-direction).
The original scope-stopped development result remains unchanged.

## Behavior

- Scope instructions name exact task endpoint addresses, protocols and ports.
  Discoveries in source/files/responses do not expand that scope. Pip-only external
  access and visible tool-purpose sentences remain.
- Current profiles add explicit `max_scope_recoveries = 1`; 0 selects strict
  first-denial stopping. Model identity, medium reasoning, 8,192 tokens and all
  other settings remain fixed. Both current profiles have identical parsed values.
- The unchanged firewall drop counter confirms a prevented connection. A fresh
  delta during `run_command` interrupts the Docker client. The controller resets
  the solver, audits the still-running guard, acknowledges the cumulative count,
  consumes the allowance and returns `scope_denied`, permitted endpoints and reset
  flags. All old processes/connections end; files/packages persist. Target state,
  run ID, deadlines and call counters are preserved. No command is retried.
- The next normal agent turn receives the feedback. Multiple packets for that
  command/reset are one incident. NFLOG notifications reread the counter; delayed
  old log lines do not consume another incident or reset allowance.
- A new incident after recovery, strict mode, a denial detected outside active
  command handling, invalid/missing/decreasing counters, lost guard, failed reset
  and existing terminal/deadline conditions remain terminal. Guard rules, images,
  permissions, network endpoints and dependencies are unchanged.
- Partial command output remains available through the existing capture mechanism.
  Already delivered copies survive reset; failed/previous delivery is not retried
  or granted another budget. Summaries retain `scope_incidents`, `scope_recoveries`
  and the last independently observed cumulative `denied_packets`, captured after
  cleanup joins the monitor. A later success retains its incident counts.

Changes stay in existing functions/modules and ordinary dictionaries/events/locks;
no new service, application class, agent tool or command-text network parser.
Normal commands retain the existing pre/post counter checks. The readiness helper
now exercises the configured allowance before its terminal-denial check; no real
challenge preparation was rerun during this milestone.

## Verification

| Check | Result | Retained report |
| --- | --- | --- |
| Full offline suite including counter/guard/deadline races, cancellation, batch continuation and capture state | 149 passed | [offline.xml](offline.xml) |
| Final focused offline checks after asynchronous summary-counter finalization | 77 passed | [offline-final.xml](offline-final.xml) |
| Full synthetic Docker suite | 47 passed | [docker.xml](docker.xml) |
| Final four recovery checks under the completed code | 4 passed | [docker-final.xml](docker-final.xml) |

The focused checks overlap the full suites; counts are not independent additional
cases. The full Docker suite preceded final capture-delivery and summary-counter
hardening; focused checks cover those edits. Intermediate reports and raw native
spans remain under ignored `runs/scope-recovery/`. One intermediate post-recovery
proof failed after blocked access and feedback passed. Its broad PID/`sleep`
assertion could match a new process after PID reuse; tightened it to identify
the old `sleep 29` child and added specific assertion messages. All four final
checks passed. The original failure had no assertion-specific message, so PID
reuse is the likely explanation rather than an independently confirmed cause.
The failed report remains at `runs/scope-recovery/docker-counters-final.xml`.
[verification.json](verification.json) records exact ordering, report/
source/image/configuration hashes, saved summaries and filtered feedback.
[experiment.toml](experiment.toml) is the non-secret configuration used.

The live-listener test uses a fixture-only forbidden service and an independent
controller query of its accepted-connection count. It stays at **zero** before
and after the blocked command. That test also verifies file persistence, death
of a detached child, retrieval of interrupted raw output, unchanged target startup,
same attempt/counters/deadline, and successful work through the permitted endpoint.
Another scripted-loop test checks denial feedback reaches the next response before
forcing a second incident, which stops. Separate tests cover between-command
denial, failed reset, strict-mode network boundaries, delayed log delivery, counter
rewind/corruption, guard failure and terminal reasons during restart. Existing
private-data, evaluator, timeout, toolkit and cleanup controls pass.

Source and image checks confirm unchanged guard/solver images, guard source and
Dockerfiles, dependency declarations/lock, model settings and existing limits.
No managed containers/networks remain after verification. All saved synthetic
summaries have zero live model calls and no cleanup errors. No real challenge,
held-out contents, benchmark answers or write-ups were consulted during this work.
No hosted writes or image rebuilds were needed. Implementation is uncommitted.

To reproduce the current checks with existing images and no model keys:

```sh
uv run --frozen pytest -q
uv run --frozen pytest -m docker -q -x --ctf-output runs/scope-recovery-reproduction
```

Actual verification used `uv run --no-sync` and a temporary writable uv cache.
Tests use the native SDK's local exporter and fixed synthetic commands; they do
not replay commands from development traces on the host.

## Limits and next step

The allowance covers an active command/reset episode, not an unlimited series of
agent retries. All processes are reset together. A denial detected between commands
is deliberately terminal. Recovery relies on the existing trusted immutable guard
drop rule and a readable monotonic counter; uncertain audits stop. The mechanism
does not add a detector for successful access through a compromised guard and does
not authorize such access. Existing pip-purpose enforcement limitations remain.

These checks prove mechanical recovery and unchanged blocking, not that a model
will obey the revised wording or solve more challenges. Review this milestone,
then separately authorize one fresh web development check if desired. Preserve
the original scope-stopped trial and keep this controller/prompt change separate
from the already recorded reasoning/headroom experiment. No real retry was run.
