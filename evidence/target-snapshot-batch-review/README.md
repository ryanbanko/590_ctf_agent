# Target snapshot batch: Docker/process findings — November 11

Read-only monitoring of user-run `batch-bebe62296ff3`, limited to container
lifecycle, process-error messages and connection-error categories. No challenge
logic/source/binary analysis, payload inspection/execution, target changes or
additional model requests. The running batch was never modified. All four planned
attempts have now completed without verified success.

## Finding established by the new snapshots

**All four target containers were exited with code 1 before target removal.**
All recorded `oom_killed=false`, zero target restart count and an empty assigned
IP at teardown. No scope incidents, denied packets or cleanup errors were recorded.
Some solver restarts occurred, but target termination also occurred in attempt 2
without a solver restart. Solver restarts alone are therefore not a sufficient
explanation for all four failures.

| Attempt | Service ID / trial | Active seconds | Target end state | Solver restarts |
| --- | --- | ---: | --- | ---: |
| 001 | pwn-roppity / 1 | 154.82 | exited, code 1; no OOM | 1 |
| 002 | pwn-baby-boi / 1 | 153.54 | exited, code 1; no OOM | 0 |
| 003 | pwn-roppity / 2 | 163.21 | exited, code 1; no OOM | 2 |
| 004 | pwn-baby-boi / 2 | 117.26 | exited, code 1; no OOM | 1 |

These names identify environments only; the analysis does not assess their
programs or solving strategies. [Filtered records, source hashes and trace URLs](review.json).
Raw runtime files remain local under `runs/pilots/pwn-target-snapshots/`.

## Attempt 003: stronger timing evidence

Passive Docker lifecycle observation retained these UTC timestamps:

- **21:19:24:** target start.
- **21:20:59:** target `die`, exit code **1**.
- **21:21:04.940:** tool `edb27f8362fbc128` starts the next failed connection attempt.
- **21:21:32.859:** tool `9b7fdad807542f5d` reports `No route to host`.
- **21:22:08:** attempt stops and Docker records target `destroy`.

Thus target exit preceded these connection failures and occurred about 69 seconds
before normal removal. The outage in this attempt cannot be explained solely by
normal end-of-attempt cleanup or missing persistent terminal state. The other
three end snapshots do not provide equally precise exit timelines.

Filtered listener logs show several child-process signal-11 reports under
different socat process IDs, plus:

```text
socat[1] E waitpid(): child 21 exited on signal 11
```

Earlier passive inspection found the container still running after other child
error reports. A child failure does not invariably kill the listener in the
observed environment. The PID-1 report is an important clue about process handling,
but its exact causal relationship to the subsequent exit needs a controlled
process-only reproduction. It does not identify the internal reason for that
child's exit. No challenge outputs, command arguments or environment values are
included in the filtered log record.

Docker's [process guidance](https://docs.docker.com/engine/containers/multi-service_container/)
distinguishes the container's main process from its children and describes init's
role in child-process management. This supports examining listener lifecycle;
it does not establish that adding `init: true` or a restart policy would fix this
specific behavior.

## Interpretation and next investigation

The leading established failure is **target process/container termination**;
target network unavailability follows. There is no evidence here of Docker OOM
termination. No Docker daemon failure, networking defect, emulator defect or
netcat defect is established. The main unresolved question is why the target's
main listener exits with code 1 when this process sequence occurs.

A next approved investigation should use only a disposable generic listener and
trivial child processes with controlled normal/signal exits. Compare process
survival, listener version/flags and native versus emulated execution, with init
as a separate controlled variable if justified. This avoids all actual task
programs, answer data and solving. Do not immediately add automatic restarts: they
could hide the problem and alter task state. No fix is implemented by this review.

The three-second snapshot instrumentation supplied the missing end-state evidence
as intended. It is a diagnostic improvement, not an increase in verified solve
rate. Earlier failures and the model-free probes remain preserved.
