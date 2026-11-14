# Project status

Last reviewed: November 14, 2026 (America/New_York).

## Current step

**Usage preservation implemented and verified; workflow/model options ready for discussion.**
Both affected target images now use checksum-pinned Ubuntu socat 1.7.3.3 while
retaining their OS, libraries, application, command, user, relay and 60-second
inactivity limit. Synthetic/readiness checks passed. The approved follow-up
achieved **2/2 verified development successes**: roppity in 204.16 active seconds,
baby-boi in 330.42, both targets running before cleanup. Estimated combined model
cost: $0.03305. [Correction and evidence](evidence/listener-update/README.md).

The user considered optional concurrency, then chose to retain the existing
sequential runner. The exploratory additions were removed; the regular batch
function, CLI and batch tests match main byte-for-byte. No parallel runner ships.

The prior documentation reconciliation is on main at `bc3ca3a`; the listener
diagnosis/correction and usage-preservation changes remain uncommitted for review.
Current documentation has been reconciled with the completed fix and sequential
runner decision; dated history and submitted report artifacts remain preserved.

The [November 14 improvement review](docs/IMPROVEMENT_OPTIONS.md#current-review-and-proposed-comparison--november-14)
separates completed changes from proposals. Reported-call usage preservation is
now implemented: `known_usage` survives later failures; unknown complete totals
stay null. Fifty-eight focused offline tests passed. Local error/export record
improvements remain proposals, alongside brief optional plans/notes (behavior).
The user now requests at least two challenges per category and three trials each,
and allows both development and test tasks for practice. The
[expanded proposal](docs/IMPROVEMENT_OPTIONS.md#expanded-comparison-and-baseline-freeze--november-14)
contains 12 CTFTiny tasks (ten Hard, two Easy), 36 baseline + 36 candidate attempts.
Use separate frozen source checkouts and ordinary sequential batches for the two
manifest lists. Reused scored tasks are tuning evidence; original scored records
remain unchanged. Exact selection/spending/readiness and behavior edits remain
for review; no batch has started and no Git snapshot has been created.
Read-only checks confirmed native costs on all 43 generations of the two latest
traces; root SPAN costs are null. [Accounting and cost evidence](evidence/usage-preservation/README.md).

## Start here

| Document | Responsibility |
| --- | --- |
| [AGENTS](AGENTS.md) | Working agreement, boundaries and agent reading order |
| [README](README.md) | Current setup, commands and result locations |
| [DESIGN](docs/DESIGN.md) | Implemented architecture, contracts and tradeoffs |
| [PROJECT_HISTORY](docs/PROJECT_HISTORY.md) | Dated milestones and the complete preserved status history |
| [EXPERIMENTS](docs/EXPERIMENTS.md) | Detailed hypotheses, changes, verification and comparison limits |
| [REFERENCES](docs/REFERENCES.md) and [ASSIGNMENT](ASSIGNMENT.md) | Original resources, requirements and instructor clarifications |
| [Evidence index](evidence/README.md) | Retained supporting records; some older records are linked at historical commits |
| [DEVELOPMENT_GUIDE](docs/DEVELOPMENT_GUIDE.md) | Preserved November 11 README; historical context, not current setup authority |
| [Part 1 report](docs/REPORT.md) | Team's submitted/report snapshot; Word/PDF versions remain unchanged |

## Implemented baseline

Agent/tool/model behavior retains scored baseline **`aedfd62`**, with the new
two-image target-listener correction and additive usage-accounting records.
Team reporting/submission updates through
**`36307ce`** and historical scored records remain unchanged. The configuration source is
[configs/development.toml](configs/development.toml): Luna/medium, 8,192 output
tokens, 2 MiB serialized input, 90-second requests, 600-second attempts,
120-second commands, 40 model calls and 80 tool calls. Solver limits remain
1 CPU/1 GiB/64 PIDs; one confirmed blocked-command recovery is permitted.

The solver/evaluator boundary, permitted endpoints, private-data separation,
submission recording and cleanup remain enforced. Native Langfuse tracing and the
existing sequential batch runner remain in use. Rebuilding the solver can resolve
mutable upstream downloads; exact-image reproduction uses the recorded archive
checksum and per-run image IDs, not merely a Git commit.

## Assignment checklist

- [x] Agent, tools, trusted verification and enforced controls implemented;
  verification records are in [retained evidence](evidence/README.md).
- [x] Development experiments and trace-supported improvement discussion recorded.
  Small/uncontrolled comparisons retain their limitations; see EXPERIMENTS/report.
- [x] Thirty counted scored solve trials recorded: **29 verified successes**;
  pass@1/2/3 = **96.7% / 100% / 100%** under the documented estimator.
- [x] Separate model/API incident preserved: 31 attempts across the two selected
  batches, with the incident excluded from solve denominators and included in
  resource accounting. [Policy, provenance and metrics](evidence/scored/README.md).
- [x] Report formats, aggregation/audit/plotting scripts and scored records present.
  Earlier team status reports package/video delivery via Canvas; external delivery
  and demo provenance are not independently verified by this documentation edit.
- [x] Documentation reconciliation merged/pushed to main; remaining accuracy items
  are carried below.
- [x] Diagnose the repeated target exits using exact listeners and synthetic children.
- [x] Implement and validate the listener-only correction; two development retries succeeded.
- [x] Retain the original sequential batch runner; remove the concurrency experiment.
- [x] Preserve known usage through later request failures/missing usage, without
  replacing unknown complete totals or changing stopping/retry behavior.

## Open issues and limits

1. **The listener fix is verified; broader reliability is not guaranteed.** Both
   fixed targets survived synthetic crashes and real development runs. One fresh
   success per target is not a solve-rate estimate or proof every service issue
   is resolved. No `nofork`, restart, extra init or permission/budget relaxation
   was adopted. [Current handoff](docs/TARGET_PROCESS_ISSUE.md).
2. **External-service failures can stop a batch.** The scored model/API incident
   also lacked a trace export; its precise cause is unconfirmed. The target was
   still running. No automatic retry/resume is implemented.
3. **Partial usage is preserved; complete billing can still be unknown.** New
   records retain `known_usage` after failures, while whole-attempt totals stay
   null when incomplete. Historical records are unchanged; the unexported scored
   incident's usage remains unknown. Local estimates still omit the cache-write
   premium visible in native Langfuse costs. Durable local error categories and
   stronger export-payload checks remain proposals.
4. **Timing labels need review.** `aggregate.py` reads `result.total_seconds` as
   wall time; `run.json.total_seconds` covers the broader launch. The report calls
   its time launch-to-finish. The report/scripts are preserved pending an explicit
   decision about the field/label; these intervals must not be conflated.
5. **Submission tag/demo provenance needs confirmation.** Team documents refer to
   `part1-submission`, but no local/remote tag was found during the November 13
   check. Earlier status also flags video identifiers outside this repository.
6. **Candidate improvements remain proposals.** Compaction, plans/notes, continuation,
   larger budgets, stronger models and service workarounds are not approved by
   this reconciliation. Historical proposals are in [IMPROVEMENT_OPTIONS](docs/IMPROVEMENT_OPTIONS.md).

## Next action and authorization

Review the completed accounting correction and proposed planning/notes package,
the expanded three-trial selection and baseline freeze, with continuation kept
as a separate conditional experiment. Keep the original
sequential batch behavior and Luna. Further runtime changes, challenge selection/
runs, commits and pushes are not authorized by this milestone. Commits remain
the user's responsibility.

## Current milestone verification

November 14 usage preservation: **58 focused offline tests passed**, two Docker
cases deselected, with no model generation or challenge run. Live Langfuse and
Duke checks were read-only; no hosted setting/model change. Evidence and current
source hashes are [here](evidence/usage-preservation/README.md). The listener counts
and hashes below describe the earlier milestone, before the accounting change.

November 14 listener correction:

- Both images: 20 normal exits, 20 deliberate child crashes, 20 bidirectional
  exchanges, peer disconnect/reconnect and actual 60-second timeout/reconnect
  passed, with listeners running and no remaining connection child.
- Original base layers/configuration and socat features preserved; package
  checksum verified against Ubuntu's official index.
- Ordinary readiness passed for both targets. One overlapping global cleanup
  assertion is preserved with its passing sequential rerun; all original local
  controls/cleanup passed. [Records](evidence/listener-update/readiness.json).
- Final offline suite for this milestone: **167 passed**, 49 Docker cases
  deselected. Compilation/whitespace checks passed. [Audit](evidence/listener-update/audit.json).
- Two live development attempts succeeded; both evidence exports and cleanups
  passed, no scope incidents or solver restarts. Historical scored results,
  report artifacts, model settings and dependencies remain unchanged.

Earlier diagnosis and reconciliation verification remain in
[project history](docs/PROJECT_HISTORY.md) and linked evidence; those checks are
historical rather than newly repeated validation.

Documentation follow-up: checked local Markdown file-link targets in 13 current
documents/evidence summaries, correction source/record hashes and unchanged
regular-run/configuration/report files. No missing file targets, hash mismatches
or whitespace errors were found. No runtime tests or paid runs were repeated.
