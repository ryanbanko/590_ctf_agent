# Docker/process constraint investigation — November 11

The user authorized investigating process lifecycle and accidental Docker
constraints, excluding challenge logic, binaries, sources and payload analysis.
This milestone used only newly authored generic Python/socat containers. No
benchmark service was started or modified; no model request or submission occurred.

**Result:** no added per-target resource constraint was found. The basic listener
failure did not reproduce with a forking generic listener on either architecture.
A deliberately one-connection listener did reproduce the PID-1 error/exit-code
pattern, including with Docker init. This narrows the investigation but does not
establish the historical targets' exact cause or listener configuration.

## Constraint audit

| Component | Current project settings | Interpretation |
| --- | --- | --- |
| Solver | 1 CPU, 1 GiB RAM, no swap, 64 PIDs; UID/GID 1000, dropped capabilities except CHOWN, no-new-privileges, init | Explicit per-container controls; not target limits |
| Guard | 0.25 CPU, 128 MiB RAM, no swap, 16 PIDs; read-only root, 8 MiB temporary filesystem, selected network capabilities | Explicit guard controls; not target limits |
| Target launcher | Preserves supplied resource/process settings; image architecture pinned; fresh bridge/network/storage names | No added target CPU/RAM/PID quota, ulimit, capability drop, seccomp override or read-only root was found |
| Docker VM | Docker Desktop 28.3.2, ARM64, eight CPUs, 8,322,969,600 bytes RAM (about 7.75 GiB), cgroup v2, runc, builtin seccomp | Shared global ceiling and default kernel filtering still apply |

The four saved generated target Compose records have no explicit resource limits,
ulimits, init, restart policy or TTY settings among the audited fields; their only
reported field is `platform: linux/amd64`. The launcher source does not inject
limits into those services. It removes host port publishing from both and the
Docker-socket mount from one. Socket removal is not a sufficient explanation for
both environments, because the other has no such adjustment. Its functionality
was not inspected or restored. The assigned endpoint uses the bridge IP directly.

For a generic supplied Compose service, direct Compose and the existing
`challenge_target()` launcher produced **identical** inspected HostConfig and
inside-container cgroup/rlimit records on both ARM64 and AMD64:

- Memory and CPU quota fields zero/unset; PID limit unset.
- `memory.max`, `memory.swap.max` and `pids.max` read `max`; `cpu.max` read
  `max 100000`. These indicate no measured per-container quota, not unlimited VM resources.
- NPROC/address-space limits unlimited; open-file limit 1,048,576.
- No custom capability/security option or read-only root; init unset and restart
  policy `no`. Docker's normal builtin seccomp still applies when SecurityOpt is unset.

Docker documents the distinction between default access to host resources and
[explicit container resource limits](https://docs.docker.com/engine/containers/resource_constraints/).
Our equal memory/memory-swap settings disable swap for solver/guard. They do not
carry across a network connection to the target. No project code changing daemon
or Docker Desktop CPU/RAM settings was found. Historical targets had no OOM flag;
that alone is not proof that global contention never occurred.

## Controlled process checks

The pre-check hypothesis is recorded in [EXPERIMENTS](../../docs/EXPERIMENTS.md).
The diagnostic uses socat **1.7.4.4** on Python 3.13.2/Debian bookworm. Children
either exit normally or deliberately signal themselves with SIGSEGV; orphan cases
fork a child and let its parent exit. Core files are disabled. No task program,
input parsing, payload or contestant artifact is involved. A separate generic
client has the solver's CPU/RAM/PID limits and uses fixed Python socket exchanges.
It does not reproduce the complete guard/solver image or traffic workload.

| Generic listener / child | Init | Native ARM64 | Emulated AMD64 |
| --- | --- | --- | --- |
| Forking / normal exit | No | Survived 5/5 connections | Survived 5/5 |
| Forking / attached signal 11 | No | Survived 5/5 | Survived 5/5 |
| Forking / orphan normal exit | No | Survived 5/5 | Survived 5/5 |
| Forking / orphan signal 11 | No | Survived 5/5 | Survived 5/5 |
| Forking / orphan signal 11 | Yes | Survived 5/5 | Survived 5/5 |
| One connection, no fork / attached signal 11 | No | Exited code 1; next connection failed | Not run |
| One connection, no fork / attached signal 11 | Yes | Exited code 1; next connection failed | Not run |

The no-init one-connection control logged:

```text
socat[1] E waitpid(): child 13 exited on signal 11
```

That has the same message shape as the passive historical PID-1 record. It proves
that this signature is **not unique** to Docker failure, emulation failure or
missing init. It does not prove a historical target lacked `fork`; earlier
multiple connections in those runs make a simple one-connection explanation
insufficient without examining the listener/wrapper arrangement.

The [packaged socat child handler](https://sources.debian.org/src/socat/1.7.4.4-2/xiosigchld.c/)
distinguishes registered EXEC children from anonymous listener children, with
different error handling. This supports checking the actual process arrangement
next; the historical socat version/options were not established here. Docker's
[init guidance](https://docs.docker.com/engine/containers/multi-service_container/)
describes child reaping, which does not guarantee listener application survival.

## Evidence, limits and next step

- [Native checks](native-arm64.json), [AMD64 checks](emulated-amd64.json),
  [one-connection controls](one-shot-control.json).
- [Audit, source hashes and record hashes](audit.json). Historical Compose data
  is reduced to resource/process-control fields; argv/environment are excluded.
- [Explicit diagnostic helper](../../tests/check_process_lifecycle.py). Original
  local build logs/context and target records remain under `runs/process-lifecycle/`.

All twelve synthetic cases completed; all 50 forking-listener connections worked.
Both positive controls exited as designed. Diagnostic containers/networks and
temporary image tags were removed; launcher cleanup errors were empty. A narrowly
filtered final Docker check found no remaining `ctf590-process-*` containers or
networks. Temporary build cache/base-image layers may remain. No production
runtime, target command, restart policy, security control or model setting changed.

The expected solver/fixture tags were absent from the connected engine. These
tests therefore use generic images, not the historical solver image. The engine
reports the historical Docker version/host architecture, but identical historical
VM state or emulator implementation is not established. The generated Compose
audit is not a retrospective `docker inspect` of removed historical containers.
Other listener versions/options, wrappers, traffic patterns or global contention
are not ruled out by these small checks.

Automatic approval review rejected both a broad cached-image inventory and a
subsequent known-image startup-argument read. The first was replaced by an allowed
query for known generic images. The second remains unperformed: the reviewer judged
that reading historical Entrypoint/Cmd could expose private task arguments and
cross the user's challenge-exclusion boundary, even with filtered output.

Recommended next milestone, subject to the user's review: inspect **only** the
historical listener/wrapper startup arrangement and listener version, with task
program paths/arguments and content excluded. Reproduce any discovered distinction
using the same trivial child. Do not add init, automatic restarts, looser limits or
new network permissions based solely on the present evidence. If that metadata
read is outside the intended boundary, preserve the diagnosis as unresolved.
