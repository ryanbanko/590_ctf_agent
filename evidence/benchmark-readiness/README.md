# Shared challenge launcher and selected-ten readiness

Completed November 4, 2026 (America/New_York). This approved milestone finishes
Section 1 setup for the selected ten CTFTiny challenges and the existing development
example. **63 fast tests and eleven zero-model preparation commands passed.**
The user will perform Section 2. No model request, solve, flag submission, pilot,
scored attempt or hosted trace upload was made during this milestone.

## Scope and implementation

One `run-challenge --challenge ID` replaces `run-development`. Both development
and scored IDs use the same package loader, file staging, model loop, tools,
evaluator and controls. The existing manifest supplies an automatic result label;
its ten held-out IDs and forty development IDs are unchanged. CTFTiny remains the
active scope; additional NYU dataset setup was deferred.

The supplied service/image/alias/internal-port configuration is reused instead
of hard-coding the development target. File-only challenges use the same solver
path without a service. Missing target images are pulled and resolved local image
IDs are recorded per attempt. Published ports and Docker socket mounts are removed;
unsupported arrangements fail closed. No module, dependency, tool or second runner
was added. Obsolete single-target fields were removed from the manifest.

The selected web service revealed a real compatibility issue: Nginx needs writable
log/temp storage and CHOWN during startup. The disposable target now has a normal
writable layer and only CHOWN/SETUID/SETGID capabilities, with the existing isolation
and resource limits. The solver remains non-root/read-only with no capabilities,
private files, credentials, socket or host mounts. Model-controlled commands never
execute on the host or in an administrative target shell.

## Actual verification

```sh
.venv/bin/python -B -m pytest -q --junitxml=evidence/benchmark-readiness/pytest-fast-final.xml
.venv/bin/python -B -m ctf_agent prepare-challenge --challenge ID --output evidence/benchmark-readiness
```

The second command was invoked separately and sequentially for `pwn-baby-boi` and
each of the ten reserved IDs. A distinct process per command matches ordinary CLI
use and the Langfuse client lifetime. The full synthetic 19-case Docker suite was
not repeated; its prior passing evidence remains at [langfuse](../langfuse/README.md).
Solver/guard/worker controls were unchanged; actual changed target configurations
received the real preparation checks below.

| Challenge ID | Environment | Final result |
| --- | --- | --- |
| `pwn-baby-boi` | Development service | Passed |
| `cry-babycrypto` | File-only | Passed |
| `cry-collision-course` | File-only | Passed |
| `for-whyos` | File-only | Passed |
| `msc-quantum-leap` | File-only | Passed |
| `msc-weak-password` | File-only, no contestant files | Passed |
| `pwn-puffin` | Service | Passed |
| `pwn-slithery` | Service | Passed |
| `pwn-unlimited-subway` | Service | Passed |
| `rev-rebug-2` | File-only | Passed |
| `web-smug-dino` | Service | Passed |

Each command ran two fresh target/network/solver cycles, verifying exact public
file inventory, hashes and ownership, private boundaries, non-root/zero-capability
solver, no host mounts/published target ports, and isolated networks. Service
connectivity was TCP connect-and-close only, with no reading of response contents.
Cycle two deliberately attempted TEST-NET `198.51.100.1:443`; independent NFLOG
denial evidence and solver stopping were required. Fresh reset and cleanup passed.
The approximately 24 MB contestant log in `for-whyos` fit the existing workspace.
The package's nonstandard flag-format warning for that entry prints no answer.

The post-run audit passed for **all 22 cycles**: nonempty native spans, exactly one
root, matching trace IDs, complete timestamps, root parentage, tool counts matching
summaries, independent denial events and no expected answer in spans/public task.
Trusted `nyuctf` loading read answer keys programmatically without printing them;
no evaluation solutions, write-ups or answer values were inspected. Model and
scripted-response counts are zero. Model cost is **$0**.

## Records and diagnostics

- [suite.json](suite.json) identifies all eleven final passing checks.
- [verification.json](verification.json) retains the 22-cycle audit and final
  source/configuration hashes. Per-check provenance retains the actual snapshot
  used during each command; routine wording/config cleanup followed those checks.
- [pytest-fast-final.xml](pytest-fast-final.xml) records **63 passed**, 19 Docker
  cases deselected, pytest time 0.72 seconds. Earlier fast-test output is retained.
- [inventory.json](inventory.json) contains only selected public setup metadata,
  listed filenames/sizes and endpoints, without answer values or solutions.
- Each final check directory contains `check.json`, two lifecycle records/runtime
  Compose configurations where applicable, public-task records, attempt summaries
  and native local `otel-spans.json` exports. These SDK snapshots are test evidence,
  not an additional runtime tracing system.

Earlier diagnostic attempts remain beside the passing runs. In one batch diagnostic,
repeatedly constructing/shutting down the same Langfuse project client in a single
Python process reused SDK state: later native exports were empty and denial-evidence
checks failed. Those checks correctly remained failed. Separate normal CLI invocations
resolved the issue without new application tracing machinery. The web diagnostics
also preserve failures before target startup permissions were corrected. The first
post-writable-layer failure still lacked CHOWN; final startup and connectivity pass.
`suite.json` selects the final results rather than treating those diagnostics as
successful runs. Older milestone evidence has not been changed.

## Meaning and handoff

The shared launcher can now prepare and launch each of the selected ten, with the
same execution path as development. Offline SDK-transport launch tests verify
multi-turn observation/action/submission flow for both labels; earlier live synthetic
and user-run development traces establish model integration. No new paid integration
attempt was needed here.

Preparation does not establish a solve, sufficient solver tools, contestant AMD64
execution, every possible Compose arrangement, or compatibility of the other 39
CTFTiny entries. Local images/source remain unfrozen for scored comparison. The
whole Part 1 assignment still needs development experiments, held-out evaluation,
metrics, report and a real successful-run demo. [README](../../README.md) provides
current commands; [PROJECT_STATUS.md](../../PROJECT_STATUS.md) records the handoff.
Stop for review before further assistant-started experiments or model calls.
