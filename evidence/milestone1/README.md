# Isolated-tools milestone evidence

Date: November 3, 2026 (America/New_York).

Historical snapshot: the unittest command below describes the original code. The
current checkout uses pytest; use the [main README](../../README.md) and
[current evidence](../pytest-refactor/README.md) for current verification commands.

**Result: 17/17 synthetic container checks and 5/5 contract tests passed.**
This is setup/control evidence only. It is not a CTFTiny solving attempt, development
pilot, scored comparison, or autonomous model demonstration. No model API was called.

## Reproduce

From the repository root, with Python 3.13.2 and Docker running:

```sh
python3 -m unittest discover -s tests -v
python3 -m ctf_agent build-images
python3 -m ctf_agent self-check
```

The frozen Python dependency resolution also works with `uv sync --frozen` and
`uv run python ...`; this milestone has no third-party Python dependencies.
The commands and real checks are implemented in
[check_controls.py](../../tests/check_controls.py) and
[test_contracts.py](../../tests/test_contracts.py).

After this historical run, the synthetic suite and target lifecycle moved from
`ctf_agent/` to `tests/`. Original trace and provenance JSON files below remain
unchanged, including their original source paths and hashes.

## Recorded run

[Suite record](self-check-4d0aaf683763/suite.json) includes the exact configuration,
Docker version, image IDs/architectures, per-file source SHA-256 values, and all
check outcomes. The recorded source hashes were compared with the final tested
files after the run and matched. There is no Git commit yet, so the commit field
is null; this is an inspectable milestone, not the course's frozen configuration.

Environment: macOS ARM64 host, Docker Engine 28.3.2 / Linux ARM64,
Compose 2.39.1, host/container Python 3.13.2. The full suite took **45.279662
seconds**, including fresh synthetic target setup and teardown for each check.
Every attempt records active, cleanup, and total elapsed time, including failures.
Model calls: **0**. Gateway cost: **$0**. Token usage: inapplicable (`null`).

| Check | Run ID and complete trace | Terminal reason |
| --- | --- | --- |
| Commands, file execution, wrong/correct submission, stop after success | [1acb349a57ec](self-check-4d0aaf683763/1acb349a57ec/trace.jsonl) | success |
| File validation, symlinks, host-file/credential boundaries, zero capabilities, resource configuration, bounded output | [81bf9673fd9b](self-check-4d0aaf683763/81bf9673fd9b/trace.jsonl) | completed_without_success |
| Timeout with a child in a separate session | [35b6d8ac25e8](self-check-4d0aaf683763/35b6d8ac25e8/trace.jsonl) | command_timeout |
| Timeout after the command closes stdout/stderr | [4216e7f30743](self-check-4d0aaf683763/4216e7f30743/trace.jsonl) | command_timeout |
| Tool-call cap | [3f39f04559c6](self-check-4d0aaf683763/3f39f04559c6/trace.jsonl) | tool_limit |
| Independent wall deadline while a command sleeps | [7b4789efd961](self-check-4d0aaf683763/7b4789efd961/trace.jsonl) | wall_limit |
| Loss of the guard kills the solver | [a56b53096e52](self-check-4d0aaf683763/a56b53096e52/trace.jsonl) | guard_failure |
| Loss of the worker is a terminal infrastructure error | [7f1aea5644b6](self-check-4d0aaf683763/7f1aea5644b6/trace.jsonl) | infrastructure_error |
| IPv6 cannot reach an external destination | [7d1bf97d41d0](self-check-4d0aaf683763/7d1bf97d41d0/trace.jsonl) | completed_without_success |
| Live but unapproved port on the assigned target | [cb443537109f](self-check-4d0aaf683763/cb443537109f/trace.jsonl) | scope_violation |
| External direct-IP request | [5f585c6e44e9](self-check-4d0aaf683763/5f585c6e44e9/trace.jsonl) | scope_violation |
| Actual Docker-host bridge address | [b4bc6f4ea70a](self-check-4d0aaf683763/b4bc6f4ea70a/trace.jsonl) | scope_violation |
| Docker embedded DNS | [e08be823a9f7](self-check-4d0aaf683763/e08be823a9f7/trace.jsonl) | scope_violation |
| External DNS | [4b5b5d48335e](self-check-4d0aaf683763/4b5b5d48335e/trace.jsonl) | scope_violation |
| A live unrelated container on another private network | [f787019e6545](self-check-4d0aaf683763/f787019e6545/trace.jsonl) | scope_violation |
| Keyboard interruption | [d1b632c63a9a](self-check-4d0aaf683763/d1b632c63a9a/trace.jsonl) | user_cancel |
| Nonexistent solver image, without a pull | [12a5a46df5c5](self-check-4d0aaf683763/12a5a46df5c5/trace.jsonl) | infrastructure_error |

Each directory also contains a `summary.json`. The suite asserted successful
cleanup for every attempt, and finally checked that no `ctf590.managed=true`
containers or networks remained. It does not delete unrelated Docker resources.

## What the network evidence establishes

The allowed HTTP service returned a candidate through its intended interface.
The same synthetic target also had a second live listening port, confirmed by
trusted readiness checks, which the solver was prevented from contacting.

All six prohibited IPv4 destinations produced NFLOG packet evidence in a
`network_denied` event and ended their attempts. Those records identify the source,
destination, and transport port independently of the command's returned text.
External probes use reserved documentation addresses rather than public services.
The host probe uses the real default-bridge gateway address read by trusted code.

The IPv6 probe failed with `Network is unreachable`: it verifies lack of an
external IPv6 route, not an NFLOG denial. IPv6 remains unsupported by the initial
endpoint policy. A blocked IPv4 request ends the run; a local routing error is
recorded as a command failure.

No expected answer is separately logged. The synthetic success trace includes the
candidate obtained from the service and submitted to the evaluator, as required.

## Failures found and corrected during implementation

1. Docker isolated networks omit a normal `Gateway` metadata field. Target
   startup originally assumed it existed. The corrected setup derives a synthetic
   next hop within the isolated subnet; forbidden external probes reach the
   OUTPUT firewall for auditing and are dropped there. It does not enable target
   routing or provide an internet gateway.
2. tcpdump's standard account drop needs `SETUID`/`SETGID`, even when invoked as
   root. Startup initially failed before the solver started. The guard now has
   those narrowly scoped capabilities and the collector drops to its packaged
   unprivileged account. The solver still has **zero** capabilities.
   Preserved failure traces:
   [first](startup-failures/030d0225ad1f/trace.jsonl),
   [second](startup-failures/1779636c3b7b/trace.jsonl).
3. A host-probe test initially tried to resolve `host.docker.internal` inside the
   target, whose external DNS forwarding was deliberately disabled. The corrected
   test reads the Docker-host bridge address from trusted metadata, preserving
   the target's network restrictions.
4. Review found that a command can close output streams while continuing to run.
   The worker now waits against the command deadline as well as reading pipes;
   a regression check confirms proper timeout and whole-container termination.

These are implementation diagnostics, not the assignment's later controlled
agent-improvement experiment. Earlier local probe traces remain under ignored
`runs/`; the final complete suite and the cited startup failures are retained here.

## Dependency and coverage limits

[Resolved ARM64 OS package inventory](guard-os-packages-arm64.txt) records all
119 installed guard packages. Python base images use a pinned digest; directly
installed firewall packages use exact versions. Debian transitive packages are
recorded, but the build is not promised bit-for-bit reproducible across repository
changes. Retain the tested image IDs or export images when freezing later.

The checks verify configured memory, CPU and process limits; they do not stress
every resource limit or measure peak resource consumption. Host-side malformed
worker output has an independent bound in code, but deliberate protocol-tampering
attacks were not part of this suite. Sudden host process death/SIGKILL recovery
has not been tested. These are finite containment checks, not a universal escape audit.

Still pending: adaptive loop, live gateway compatibility, model/resource pricing,
actual AMD64 execution, real CTFTiny Compose compatibility, contestant-file staging,
target resets, analysis tool selection, and all later course experiments/results/demo.
The existing NYU/CTFTiny Compose files have not been modified or replaced.
