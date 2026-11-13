# Target listener exits: teammate handoff

Status: **open; cause unresolved; no service fix implemented.** November 11, 2026.
Scope: Docker, listener/wrapper processes and lifecycle. Challenge programs,
sources, payloads, answers and solving strategies are outside this investigation.

## Observed failure and impact

The user-run `pwn-target-snapshots/batch-bebe62296ff3` completed four attempts,
two each for `pwn-roppity` and `pwn-baby-boi`. All four targets were **exited with
code 1 before removal**, with no OOM flag, target restart, scope denial or cleanup
error. All four attempts ended without verified success. This establishes a
repeated infrastructure symptom, not a common underlying cause for every attempt.

Attempt 003 provides the strongest timing evidence, in UTC:

| Time | Event |
| --- | --- |
| 21:19:24 | Target starts |
| 21:20:59 | Docker records target exit, code 1 |
| 21:21:04.940 | Subsequent connection attempt fails |
| 21:21:32.859 | Later tool reports `No route to host` |
| 21:22:08 | Attempt stops and target is removed |

The exit precedes these connection failures and is about 69 seconds before
cleanup. The lost connection cannot be explained solely by end-of-attempt cleanup
in this case. Attempt 002 had zero solver restarts, so solver restart alone does
not explain every target exit.

Filtered listener logs contain several child signal-11 reports and finally:

```text
socat[1] E waitpid(): child 21 exited on signal 11
```

Earlier child failures left the listener running. The reason the main listener
later exits remains unknown. Empty target IPs in final snapshots accompany exited
containers; they are not independent proof of a bridge or firewall defect.

## Evidence and completed investigation

Everything linked here can be reviewed from the repository without Docker,
gateway credentials or access to the local `runs/` directory:

- [Four-attempt lifecycle review](../evidence/target-snapshot-batch-review/README.md)
  and [filtered records with trace URLs](../evidence/target-snapshot-batch-review/review.json).
- [Docker/process audit and complete synthetic case table](../evidence/docker-process-constraints/README.md),
  including ARM64/AMD64 JSON results and source/record hashes.
- [Earlier service probes and limitations](../evidence/service-lifecycle-investigation/README.md).
- [Implemented pre-cleanup snapshot and verification](https://github.com/ryanbanko/590_ctf_agent/blob/aedfd62cf8379adee73a30546592036af6f82a42/evidence/target-precleanup-snapshot/README.md).

Findings that should guide a fix:

1. **No accidentally added target quota was found.** The saved generated Compose
   records have no explicit CPU/RAM/PID/ulimit restrictions among audited fields.
   Generic direct-Compose and project-launched services had identical measured
   HostConfig/cgroup/rlimit settings on both architectures. The old imposed
   256 MiB target policy was removed in the earlier target simplification.
2. **Solver/guard limits are separate.** Solver: 1 CPU, 1 GiB RAM, 64 PIDs.
   Guard: 0.25 CPU, 128 MiB RAM, 16 PIDs. Both have swap disabled. The inspected
   Docker Desktop VM has eight CPUs/about 7.75 GiB RAM shared globally. Historical
   global contention is not ruled out by the absence of an OOM flag.
3. **Basic child failures did not kill a generic forking listener.** Ten variants
   across native ARM64 and emulated AMD64 survived all 50 connections, including
   attached/orphan signal-11 exits. The tested socat version was 1.7.4.4.
4. **The PID-1 signature does not diagnose missing init.** A deliberately
   one-connection generic listener reproduced the message shape and exit code 1.
   It exited with init enabled too. This does not establish that the historical
   listener lacked `fork`; those runs had earlier successful interactions.
5. **Our adaptations remain relevant but unproven causes.** Host port publishing
   is removed from both targets; a Docker-socket bind is removed from one. Socket
   removal alone cannot explain both. The assigned endpoint uses the bridge IP.
   The adaptations' full semantic effect was not assessed here.

The generic tests do not reproduce the historical image, listener version/options,
wrapper, complete guard/solver environment or traffic sequence. The original
containers were removed, and their effective HostConfig was not retained. Do not
treat the synthetic results as proof that every Docker/emulation issue is excluded.

## Suggested next checks, in order

1. Establish the actual listener version and startup/process arrangement: which
   process is PID 1, where connection forking happens, which process waits for
   each child, and whether a wrapper exits or execs. Compare image defaults with
   effective Compose overrides. Keep task program content out of the analysis.
2. Recreate that arrangement using a trivial child with controlled normal/signal
   exits. Change one variable at a time: listener options, wrapper behavior, then
   init or architecture if evidence points there. Preserve failing controls.
3. If it still does not reproduce, capture only lifecycle events, PID/PPID/process
   names, resource counters and listener-error categories during a separately
   authorized rerun. Correlate the main-process exit with the first failed
   connection and controller cleanup; avoid collecting task output unnecessarily.
4. Propose the smallest demonstrated correction. Preserve supplied service
   behavior and isolation. Init, automatic restart, broader permissions or larger
   budgets are not established fixes. Automatic restart can conceal the failure
   and reset service state, so it needs an explicit rationale and comparison.

The historical startup-argument read was **not performed**: automatic approval
review judged that Entrypoint/Cmd could expose private task arguments and cross
the user's challenge-exclusion boundary, even with filtered output. Clarify that
boundary with the user before that next step. This handoff does not authorize a
paid rerun, scored run, service modification or challenge-program inspection.

## Relevant implementation and reproducer

- [Target integration](../ctf_agent/challenge.py): `target_compose()`,
  `challenge_target()`, `snapshot_target_services()`.
- [Solver/guard lifecycle and limits](../ctf_agent/sandbox.py): `start_sandbox()`,
  `restart_solver()`, `stop_solver()`.
- [Current budgets](../configs/development.toml).
- [Generic diagnostic](../tests/check_process_lifecycle.py). These commands build
  disposable generic images, may download packages/base layers, and make zero
  model calls. They do not start benchmark services:

```sh
.venv/bin/python -m tests.check_process_lifecycle --platform linux/arm64
.venv/bin/python -m tests.check_process_lifecycle --platform linux/amd64
.venv/bin/python -m tests.check_process_lifecycle --platform linux/arm64 --one-shot-control
```

Native ARM64 was tested on Apple Silicon; choose platforms supported by the
teammate's engine. Saved results remain the evidence for this milestone. The
helper removes its containers, networks and temporary image tags; build cache and
base layers may remain. Do not substitute real task programs into these checks.

A prospective fix should explain the original process failure, keep the listener
available across the intended repeated connections/child exits, preserve scope
and lifecycle records, and pass appropriate synthetic checks before any authorized
development comparison. Retain unsuccessful historical attempts rather than
replacing them with retries. No fix or improvement in solve rate is claimed yet.
