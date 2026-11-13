# Evidence

Each folder is kept because a document or test uses it.

This index describes retained evidence. The [current handoff](../PROJECT_STATUS.md),
[milestone history](../docs/PROJECT_HISTORY.md) and
[target issue](../docs/TARGET_PROCESS_ISSUE.md) link to the relevant records.
Older evidence removed during submission cleanup stays in Git history; repaired
historical links open a fixed commit. This reconciliation restores no raw evidence
files and changes no recorded results, hashes or test fixtures.

Pinned historical files can also be read without a browser from a full checkout,
for example `git show aedfd62:evidence/target-precleanup-snapshot/README.md`.

| Folder | Contents | Used by |
| --- | --- | --- |
| `ryan-shared-runs/` | Sanitized run records and traces: pilot, baseline and Experiments A–C | Report (results, trace review, answer-lookup check) |
| `scored/` | Final metrics, trace-usage audit and figures; attempt records in the two root batch directories | Report, reporting scripts |
| `development-trace-review/` | Baseline trace review, cost check, gateway model prices | Report |
| `unseen-development-trace-review/` | Trace review of the ten-challenge development batch | Report, `docs/EXPERIMENTS.md` |
| `final-runtime-readiness/` | Readiness checks of the ten held-out environments | Report |
| `scope-recovery/` | Offline and Docker control-test results | Report, `docs/EXPERIMENTS.md` |
| `reasoning-medium-scope-stop/` | Experiment B scope incident | Report, `docs/EXPERIMENTS.md` |
| `validation-checkpoint-prompt/` | Experiment D runs, prompt versions, prepared follow-up command | Report, `docs/EXPERIMENTS.md` |
| `target-snapshot-batch-review/`, `docker-process-constraints/`, `service-lifecycle-investigation/` | Pwn target exits and Docker tests | Report, `docs/EXPERIMENTS.md` |
| `prompt-recovery/` | Experiment 1 trial review | `docs/EXPERIMENTS.md` |
| `solver-libraries/` | Experiment 2 build and checks | `docs/EXPERIMENTS.md` |
| `agent-usability/`, `execution-simplification/` | Experiment 3 checks and the later move to one shell per command | `docs/EXPERIMENTS.md` |
| `nyu-runtime-pilot/` | Pilot batch | `docs/EXPERIMENTS.md` |
| `agent-first-fix-batch/` | Experiment A batch | `docs/EXPERIMENTS.md` |
| `nyu-solver-integration/` | Solver image record, including the archive checksum | `README.md` |
| `ctftiny-readiness/index-metadata.json` | CTFTiny index metadata | `tests/test_challenge.py` (checks the held-out selection rule) |
