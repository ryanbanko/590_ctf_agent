# Evidence

Each folder is kept because a document or test uses it.

This index describes retained evidence. The [current handoff](../PROJECT_STATUS.md),
[milestone history](../docs/PROJECT_HISTORY.md) and
[target issue](../docs/TARGET_PROCESS_ISSUE.md) link to the relevant records.
Older evidence removed during submission cleanup stays in Git history; repaired
historical links open a fixed commit. The November 13 documentation reconciliation
restored no raw evidence files and changed no recorded results, hashes or test
fixtures. The November 14 listener diagnosis and correction add new records in
the two listener folders below; earlier evidence remains unchanged.

Pinned historical files can also be read without a browser from a full checkout,
for example `git show aedfd62:evidence/target-precleanup-snapshot/README.md`.

| Folder | Contents | Used by |
| --- | --- | --- |
| `sol-compatibility/` | Two user-run Sol HTTP 400s; five diagnostic requests, with failed-request replay identifying a provider cyber-policy rejection | Current status, history and experiments |
| `htb-budget-update/` | HTB Luna and Sol wall/model/tool allowances raised to 30 minutes/100/120; offline config checks | Current status, history and experiments |
| `htb-description-review/` | November 17 narrative-description assessment and newest DNS Dossier run; local human acceptance, partial hosted refresh and unimplemented framing draft | Current status, history and experiments |
| `htb-latest-trace-review/` | Earlier November 17 Blueprint Heist attempt, evaluated for observable model actions only; checked payloads/replay/usage and behavioral findings | Current status, history and experiments |
| `task-preface-review/` | November 17 direct trace/source assessment of category versus operational prefaces, checked inventories, draft and unrun comparison proposal | Current status, history and experiments |
| `htb-manual/` | Manual HTB integration, separate competition limits, offline checks and unverified live boundaries | Current status, README, DESIGN and history |
| `ryan-shared-runs/` | Sanitized run records and traces: pilot, baseline and Experiments A–C | Report (results, trace review, answer-lookup check) |
| `scored/` | Final metrics, trace-usage audit and figures; attempt records in the two root batch directories | Report, reporting scripts |
| `development-trace-review/` | Baseline trace review, cost check, gateway model prices | Report |
| `unseen-development-trace-review/` | Trace review of the ten-challenge development batch | Report, `docs/EXPERIMENTS.md` |
| `final-runtime-readiness/` | Readiness checks of the ten held-out environments | Report |
| `scope-recovery/` | Offline and Docker control-test results | Report, `docs/EXPERIMENTS.md` |
| `reasoning-medium-scope-stop/` | Experiment B scope incident | Report, `docs/EXPERIMENTS.md` |
| `validation-checkpoint-prompt/` | Experiment D runs, prompt versions, prepared follow-up command | Report, `docs/EXPERIMENTS.md` |
| `target-snapshot-batch-review/`, `docker-process-constraints/`, `service-lifecycle-investigation/` | Pwn target exits and Docker tests | Report, `docs/EXPERIMENTS.md` |
| `listener-version-diagnosis/` | November 14 exact-listener synthetic reproduction, socat bug diagnosis and constraint review | Current status, target issue, `docs/EXPERIMENTS.md` |
| `listener-update/` | Binary-only listener correction, synthetic/readiness checks and two successful development retries | Current status, README, DESIGN and experiments |
| `usage-preservation/` | Reported-call usage preservation, focused offline checks, read-only native-cost check and fixed-volume model-cost comparison | Current status, README, DESIGN and improvement review |
| `notes-baseline-review/` | November 15 assistant-assisted review of all 36 practice-baseline attempts; per-trial metadata/hashes, category findings, priorities and comparison limits | Current status, improvement options and experiment/history records |
| `agent-change-proposal/` | Per-request token-growth/item-byte profiles for 355 generations, inventory-event classification and implementation-aware proposal checks; no new runs | `docs/AGENT_CHANGE_PROPOSAL.md`, current shortlist/status/history |
| `prompt-validation/` | Exact original/revised prompts and offline verification; preceding service-diagnostic and non-adopted connection-pilot summaries | Current status, design, experiments and history |
| `planning-notes/` | November 16 planning/notes-plus-50-turn implementation checkpoint: exact prompts/settings, diffs and offline verification; later trials and withdrawal are recorded under rollback/ | Current status, README, design, experiments and history |
| `planning-notes/rollback/` | Later November 16 trial review: 12 outcomes, limited adoption and evidence gaps; exact original prompt/40-turn rollback, preserved records and offline verification | Current status, README, design, experiments and history |
| `validation-pilot-review/` | All six validation-prompt pilot traces and six historical controls; metrics, behavior, provenance and limits | Current status, design, experiments and history |
| `validation-expanded-review/` | Twelve additional trials/controls, combined 18-trial metrics, recurring payload gaps and timing anomaly | Current status, design, experiments and history |
| `scored-recheck-stop/` | Metadata-only record of the separate later response-source/export stop; cause unconfirmed | Current status; separate from the 36-attempt practice baseline |
| `prompt-recovery/` | Experiment 1 trial review | `docs/EXPERIMENTS.md` |
| `solver-libraries/` | Experiment 2 build and checks | `docs/EXPERIMENTS.md` |
| `agent-usability/`, `execution-simplification/` | Experiment 3 checks and the later move to one shell per command | `docs/EXPERIMENTS.md` |
| `nyu-runtime-pilot/` | Pilot batch | `docs/EXPERIMENTS.md` |
| `agent-first-fix-batch/` | Experiment A batch | `docs/EXPERIMENTS.md` |
| `nyu-solver-integration/` | Solver image record, including the archive checksum | `README.md` |
| `ctftiny-readiness/index-metadata.json` | CTFTiny index metadata | `tests/test_challenge.py` (checks the held-out selection rule) |

- [`validation-full-review/`](validation-full-review/README.md): November 16 partial full-rerun agent-pattern review; 23 outcomes, two solver failures and one unavailable API trace.
