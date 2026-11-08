# Production NYU solver integration

Completed November 7, 2026 (America/New_York). **100 offline tests and 34 normal
Docker checks passed; the verified NYU-based image is now the default.** No model
calls, hosted uploads, real challenge attempts, held-out answer review, commit
or push. The earlier lean solver and its local archive remain preserved.

## Reuse and changes

One production [solver Dockerfile](../../docker/solver.Dockerfile) copies the
installation body from NYU release `20250206`, revision
`112cfa33f5c0a06a20e49af525ac8eb07ec98457`. [Source accounting](source.json)
records the unchanged upstream body. The unused HTTP entrypoint is omitted.
Project additions provide `/workspace` ownership, non-terminal/unbuffered settings,
NumPy 2.2.6/Pillow 12.3.0, OS/Python inventories and idle startup. NYU already
supplies its writable home and Python environment. No runtime venv creation,
parent-build wrapper, daemon, new execution backend or startup subsystem was added.
The copied source is accompanied by [MIT attribution](../../docker/NYU-LICENSE).

Removed active `docker/solver-requirements.in` and `.txt`; their originals are
[archived](../solver-libraries/README.md). The prior active recipe/tests/provenance
input are also retained in [baseline](baseline/solver.Dockerfile). Five candidate
checks were consolidated into normal [Docker tests](../../tests/test_controls.py),
so no separate image-test module remains. Only the source-provenance file list
changes in application Python. Agent/prompt, three tools, execution/restart,
guard/evaluator, model integration, Langfuse, batch and numeric limits are unchanged.

## Verification

- Existing `build-images` command with a separate candidate image tag passed in
  **14.031s**, using cached upstream installation layers. This was not a fresh
  network/install build. [Result](build-result.json), [log](build.log).
- First create/start of the combined image: **0.734s**; first Python exec:
  **0.171s**, Python 3.10.12. Base layers and host caches remained from evaluation,
  so this is not a clean-machine cold benchmark. [Measurement](first-start.json).
  The current 15-second create allowance sufficed here; no preflight mechanism
  or timeout extension was needed. The earlier unexplained raw-probe timeout is
  preserved in the independent evaluation, not treated as a proven cold-start cost.
- **100 offline tests passed**: [console](offline.log), [JUnit](offline.xml).
- The normal `self-check` discovered and passed **34 Docker cases** in 144.20s:
  [console](controls.log), [complete suite/provenance](controls/self-check-b998afd71903/suite.json).
  These cover all three tools, executable/file copying, evaluator/privacy,
  credentials/socket/capabilities, scope denials/incident records, hard limits,
  restart cleanup with file/package persistence, fresh trials, interruption,
  Compose DNS/backend/fresh volume behavior and useful records.
- Additional functional cases cover SageMath arithmetic/matrices, radare2 benign
  binary analysis, angr symbolic execution of a toy function, ELF32 compilation/
  execution and inability of supplied sudo to elevate. The existing **1 GiB**
  solver limit was retained; pip checks install a tiny local wheel offline.
- Cleanup passed. After switching only the default tag, its RootFS and runtime
  configuration were matched to the tested artifact; the full suite was not
  needlessly repeated for a tag alias.

## Frozen default and preserved baseline

[Artifact metadata](frozen-image.json), [Docker inspection](integrated-image.json),
[OS inventory](os-packages.txt), [Python inventory](python-packages.txt),
[local image listing](image-list.txt). Docker reports the integrated image at
roughly **11.5 GB**, compared with the lean baseline's **1.16 GB**. Its compressed
archive is **2,938,163,200 bytes**. These are different storage measures; aliases
and shared layers must not be summed as independent images.

The default is `ctf590-solver:m1`. Docker's recorded tested index identity is
`7e2c0a9b3a24…`; its AMD64 manifest identity is `e89863b15497…`. Docker inspection
can expose either descriptor. Exact RootFS and runtime configuration were compared,
and archive configuration/layer blob hashes verified (21 blobs). Archive config
and inspected config agree, normalizing absent/null Docker defaults. The archive
contains the normal `m1` tag, so loading it requires no retagging.

Local Git-ignored archive:
`runs/frozen-images/ctf590-solver-nyu-integrated-20261107.tar`.
SHA-256:
`249c1aa8a0a58744753f2d5d68febb189a3c6918e3856cef3ebfa11ee9af8979`.

The original lean image remains tagged `ctf590-solver:before-nyu-evaluation-00e6a41`;
its RootFS/configuration match the [pre-switch inspection](baseline-image.json).
Its [previous verified archive](../nyu-solver-image-evaluation/frozen-current-image.json)
remains unchanged. Neither image binary has been uploaded or distributed. About
**11.0 GiB** host space remained after the additional archive; no broad pruning,
reset or deletion was performed during integration.

## Limits and handoff

The broader toolkit replaces our selected package provisioning, not controller
infrastructure (already simplified). It costs more disk/build time and uses
Python 3.10 rather than 3.13. Upstream's floating repositories/downloads remain;
source rebuilds need verification and are not identical to loading this artifact.
Optional upstream failures persist: hashcat, John, steghide and Cutter absent,
Sherlock wrapper broken. No claim that all installed programs or live GDB work,
that every challenge is ready, or that solve rate improves. No repairs were made
to the optional installer chain.

[README setup](../../README.md#one-time-setup) explains source builds, optional
frozen-image loading and unchanged challenge commands. Fresh-machine cold startup
and teammate archive loading have not been measured here. Review this checkpoint,
then save a source checkpoint and separately authorize final-runtime environment
readiness refresh and a small live development pilot.
