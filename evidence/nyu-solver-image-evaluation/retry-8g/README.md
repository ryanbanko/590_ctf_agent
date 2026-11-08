# NYU image retry with 8 GiB Docker memory

**Historical evaluation.** Subsequently integrated into the production build;
see the [integration checkpoint](../../nyu-solver-integration/README.md) and
[latest full validation](../../pre-git-validation/README.md).
Statements below describe the pre-integration state, including the then-unchanged
defaults and pending recommendation.

November 7, 2026. **Build succeeded; 34/34 candidate checks passed.**
Recommend the tested frozen NYU-based image with a small child recipe for broader
CTF tooling. Default project images/configuration remain unchanged pending review.
No model calls, hosted uploads, real challenge attempts or held-out answer review.

## Build and actual resources

The user saved 8,192 MiB in Docker Desktop. The existing daemon initially still
reported 16 GiB; a normal Desktop restart with no running containers applied it.
Docker then reported 8,322,969,600 usable bytes (kernel overhead below 8 GiB).

The unchanged release `20250206`, commit `112cfa3`, built for AMD64/UID 1000 in
**1,036.861 seconds (17m 17s)**. Source Dockerfile hash matches the first attempt.
The build context remained just the supplied Dockerfile/entrypoint (2,704 bytes).
No NYU host setup script, agent framework or new execution subsystem was used.
[Build result](build-result.json), [build log](build.log).

The 10 GiB host reserve and 45-minute observation bound did not trigger. The
continuous host-space checks recorded a minimum around **25.2 GiB**; detailed
15-second samples recorded a minimum around 25.4 GiB. These cover the upstream
build, not later container unpacking, tests and archive creation. VM memory samples
during installation/export showed roughly **6.7–7.0 GiB available**, with the VM's
1 GiB swap unused. Mac swap varied and remained substantial; do not attribute
the successful retry solely to RAM. fMRIPrep cleanup also provided more disk space.
[65 resource samples](resources.jsonl), [memory samples](memory-checkpoints.jsonl).

The first raw-image probe exceeded its 60-second Docker-client timeout. No running
probe container remained; a repeat with per-import progress completed in 1.405s.
Cold image preparation/unpacking is a possible explanation, not a proven cause.
Include a one-time Docker-only image preflight after build/load before attempts;
do not assume first startup fits the runner's 15-second creation allowance.
[Probe result](initial-probe.json).

## Minimal adaptation and checks

The supplied image already has a writable home and venv under `/home/ctfplayer`.
It lacks `/workspace`, NumPy and Pillow in that selected Python environment.
The [eight-line child recipe](adapter/Dockerfile) adds the workspace/ownership,
our output/non-terminal environment settings, and those two libraries. No new
venv, permissions relaxation, worker or runtime abstraction was added.
The adapter built in **7.96 seconds**, resolving **NumPy 2.2.6 / Pillow 12.3.0**;
`pip check` passed. [Adapter build](adapter-build.log).

The diagnostic probe's read-only filesystem caused temporary-directory/Chepy
errors; those are not failures under our actual writable runtime. The candidate
controls use that normal runtime and its existing CPU/RAM/PID/deadline limits.
Only the solver image differs in [candidate.toml](candidate.toml).

**29 existing compatibility/control cases and five additional checks passed**:

- Standard command/file/copy tools, executable handouts, all six existing Python
  library capabilities, private evaluator submissions and scripted agent behavior.
- Scope denial/incident evidence, credentials/mount/socket/capability boundaries,
  hard limits, interruption/cleanup, fresh state, and timeout process reset with
  persistent files/packages. Supplied `sudo` could not elevate privileges.
- SageMath integer factorization and rational matrix determinant.
- radare2 function analysis of a small benign compiled program.
- angr symbolic execution of a benign integer function, recovering its input.
- GCC multilib compilation and execution of a benign ELF32 program.

The additional tests ran under the existing 1 GiB solver limit; no limit was raised.
[34-case report](candidate-controls.xml), [results/timings](checks.json),
[console](candidate-controls.log), [local summaries and SDK spans](candidate-controls/).

Two existing environment tests were made path-independent and now install a tiny
local wheel with `--no-index --no-deps`, avoiding assumptions about a named public
package. Both also passed on the current image. Additional toolkit tests live in
`tests/check_image_tools.py`, selected explicitly, so they do not become baseline
requirements for the old image. Application/agent/model/guard/SDK code is unchanged.

## Toolkit gaps, footprint and freezing

The upstream installer returned success despite a Kali dependency conflict,
Sherlock's missing requirements file and a missing Cutter binary. Hashcat, John,
steghide and Cutter were absent in the probe; the Sherlock wrapper's presence is
not proof it works. We did not repair or claim support for those optional extras.
The positive recommendation concerns the existing capabilities and additional
functional checks above, not every program mentioned by the installer.

Docker displays roughly **11.4 GB** for the upstream image versus **1.16 GB** for
ours; the adapted candidate displays **11.5 GB**. Parent and child share layers;
their displayed sizes must not be added.
The tested adapter archive is **2,938,151,424 bytes** (about 2.94 GB decimal),
compared with the preserved current archive's 266 MB. Python is 3.10.12 rather
than 3.13.2, and some library versions differ. Basic compatibility passing is not
a guarantee of every API, native tool, challenge, live GDB or solve performance.

The candidate is frozen by image identity, a checksummed local Git-ignored archive
and complete OS/Python inventories. Archive platform, blob hashes and RootFS were
verified against the tested image. [Frozen artifact](frozen-candidate.json),
[OS inventory](os-packages.txt), [Python inventory](python-packages.txt).
It has not been uploaded or automatically distributed to teammates. Rebuilding
the floating upstream installer is not equivalent to loading this frozen artifact.

Original solver identity/RootFS and normal configuration are unchanged; no managed
test containers/networks remain. [Preservation](preservation.json).
The evaluation retains both upstream and child images plus archives; final host
availability was around 13 GiB. The 11.5 GB image figure is not total evaluation
disk consumption. A storage-accounting query briefly returned a missing-snapshot
error; its immediate retry succeeded. No resets or broad pruning were used.

## Recommendation and proposed integration

Adopt the tested NYU-based artifact plus the small child recipe if accepting the
larger toolkit/storage footprint. This follows the user's preference for supplied
components and gives verified SageMath/radare2/angr/multilib capabilities without
maintaining their installation logic ourselves. Do not repair the optional
installer chain or adopt NYU's agent/host framework.

A subsequent reviewed integration should use **one final solver Dockerfile**:
reuse the pinned upstream installation body and append the tested workspace/
environment/library additions. Omit the unused HTTP entrypoint copy/startup;
our runner already selects the idle command. This preserves the existing
`build-images` flow without a new parent-build wrapper or permanently retaining
two images. Remove the replaced solver setup and two solver requirements files;
pin the two resolved additions. Verify the combined build before changing defaults.
Document frozen-artifact loading and a zero-model image preflight. Retain inventories
and artifact identities. Runtime
copy/exec/restart, three tools, scope guard, evaluator, model, Langfuse and batch
remain unchanged. No second permanent execution backend is proposed.

This does not remove further controller infrastructure: those simplifications
already happened. Keeping our image remains the smaller disk/build option; adding
selected tools later would retain responsibility for their provisioning. On the
tested broader-toolkit path, the supplied base plus small adapter is the recommended
complete setup. Stop for review before default integration or a live pilot.

[Machine-readable result](evaluation.json). No solve-rate improvement is claimed.
