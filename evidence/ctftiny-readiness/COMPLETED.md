# CTFTiny readiness completed

November 4, 2026 (America/New_York). **56 fast tests and the real development
preparation check pass.** Zero model calls, paid model usage, flag submissions,
hosted uploads, or challenge solving. This is setup evidence, not a pilot or score.

## Changes

- Created the authorized local baseline commit `028f560`. The previous approval
  service failure did not recur. Candidate files were checked for both configured
  secret credentials; no matches, and `.env` remained ignored. Nothing was published.
- Obtained a sparse CTFTiny checkout at
  `f1c9531672c45b24b7fb5f3aa44a7ac33d3602f8`; canonical index hash matches the
  preserved metadata. The ten held-out IDs and 40 development IDs are unchanged.
  Only `ctftiny/pwn/baby_boi` was materialized beyond root metadata. No held-out
  answers, solutions, or write-ups were consulted.
- Pinned/locked `nyuctf==1.1.1`, including its declared `pathlib==1.0.1` dependency.
  The loader uses the explicit CTFTiny index and rejects scored IDs, mismatched
  revisions/indexes, and dirty checkouts. Package objects and the answer remain trusted.
- Added a small target context manager. Runtime Compose retains the supplied
  image/alias but removes its Docker socket mount and host-port publishing. It
  adds a fresh internal isolated network and explicit target resource/security limits.
- Pinned target image
  `llmctf/2019q-pwn-baby_boi@sha256:e92afa986ce9c1fd01cdffb38cb46b8e66ffb802dab9382e912d33003144c665`.
  Its AMD64 service actually responded under Docker emulation on this ARM64 host.
- Added `prepare-challenge`. All probes use the isolated non-root solver and the
  existing bounded tools/guard. No administrative target shell is used. Native
  Langfuse spans are captured locally with its supported in-memory exporter.

## Actual verification

```sh
.venv/bin/python -B -m pytest -q --disable-plugin-autoload -p no:cacheprovider --junitxml=evidence/ctftiny-readiness/pytest-readiness-fast-final.xml
.venv/bin/python -B -m ctf_agent prepare-challenge --output evidence/ctftiny-readiness
```

[Fast JUnit](pytest-readiness-fast-final.xml): **56 passed**, 19 Docker cases
deselected, no failures/errors/skips; pytest reported 0.48 seconds. Three new
cases verify dirty-checkout rejection, safe Compose adaptation without mutation,
and target-start failure cleanup. The existing staging case now checks the actual
unprivileged Python extraction transport. The previous 19-case synthetic suite was
not repeated: solver/guard/worker, firewall, tool behavior, and resource defaults
are unchanged; focused real target checks cover the new boundaries.

The [final check](ctftiny-readiness-1924b29078cd/check.json) passed in **5.169884
seconds**. Both cycles loaded the real package metadata and staged only its three
listed contestant files: `baby_boi`, `libc-2.27.so`, and `baby_boi.c`. The source
file is explicitly part of the public contestant inventory. File sizes/hashes and
UID/GID 1000 matched inside the solver. The complete workspace inventory matched
that list; private metadata, flag file, build files, solver scripts, and evaluator
storage were not copied. Socket, credentials, and a host-only marker were absent.

- Cycle 1: run `72023debf6fb`, two fixed tools, `readiness_complete`.
- Cycle 2: run `d74737846985`, three fixed tools, `scope_violation` from the intended
  unapproved-port probe. Independent NFLOG evidence and stopped-solver state passed.
- Both targets responded over the allowed TCP/8000 endpoint. Readiness probes
  only connect/read initial data and report its byte count; no exploit is sent.
- Target/solver identities were fresh, contestant files matched after reset, and
  no persistent target volumes or host ports existed. All target, solver, guard,
  and network removals passed; the final project-label query was empty.
- Expected answer was absent from native spans. There were zero model/scripted
  generations, no candidate submissions, and no verified challenge success claim.
- Per-cycle Compose/target records, summaries, and native `otel-spans.json` remain
  under the final check directory. Source hashes, image IDs/architectures, settings,
  dataset pin/hash, and baseline commit are in provenance. New changes are not committed
  or frozen for scoring.

[Final audit](verification.json) passes all checks: current source hashes match,
the two traces have 8/10 complete observations and correct parentage/tool counts,
expected answers and configured secret credentials are absent, local documentation
links resolve, and all 268 previously committed evidence files are byte-for-byte
unchanged. An independent Docker query also found no managed containers/networks;
the pinned dataset worktree remained clean.

## Retained diagnostics and limits

The [first diagnostic](ctftiny-readiness-11d7040c7aa6/check.json) failed at Docker cp:
the daemon rejected copying into a read-only root, even though `/workspace` is tmpfs.
Its attempt summary and successful target cleanup are preserved. That initial
failure's native spans were not saved by the first version of the check harness;
it is incomplete diagnostic evidence, not a passing benchmark record. The harness
now saves SDK span snapshots in `finally`, including failed setup attempts.

Staging was corrected to stream a validated archive through Docker exec into
Python's standard data-filtered tar extractor as UID/GID 1000. The read-only root,
tmpfs, no-host-mount boundary, and existing solver limits were retained.
The [first successful check](ctftiny-readiness-f383f8fc2b16/check.json) is also
preserved. The final run additionally verified explicit resource cleanup and
records the finalized tracing/provenance changes. Original November 3
[partial evidence](README.md), progress JSON, and JUnit remain unchanged.

Only the reviewed development target is supported. The solver remains native ARM64
with its existing Python tools; running/analyzing contestant AMD64 binaries and
real solving have not been established. The published target image was used without
rebuilding its flag; live answer verification was not exercised for this target.
The local SDK snapshots are not hosted Langfuse readback. No new account/model
availability or spending was checked.

Stop for review. Next proposed milestone: a development launch command connecting
the existing model loop to this prepared environment, after agreeing on settings
and an explicit request/spending cap.
