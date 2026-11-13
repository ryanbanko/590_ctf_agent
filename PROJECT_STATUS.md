# Project status

Last reviewed: November 13, 2026 (America/New_York).

## Current step

**Reconcile documentation with the team's updated main before further competition
work.** The user approved a documentation branch based on `36307ce`; it preserves
team additions and restores context. Runtime, configuration, reporting tools,
submitted report artifacts and recorded results are unchanged.

The documentation changes are complete: a dated development guide, restored
target-exit handoff, the complete earlier status record in project history,
updated agent reading guidance and repaired links. Local verification passed
(details below). Next: review the diff and remaining accuracy questions with the
user before another milestone.

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

The runtime matches scored agent commit **`aedfd62`**. The team's reporting and
submission updates through **`36307ce`** are retained. The configuration source is
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
- [ ] Review this documentation reconciliation and resolve the accuracy items below.
- [ ] Select and authorize the next competition-development milestone.

## Open issues and limits

1. **Target listener/container exits remain unresolved.** Four development targets
   exited code 1 before removal; generic native/emulated child-process checks did
   not establish a fix. [Current handoff](docs/TARGET_PROCESS_ISSUE.md).
2. **External-service failures can stop a batch.** The scored model/API incident
   also lacked a trace export; its precise cause is unconfirmed. The target was
   still running. No automatic retry/resume is implemented.
3. **A failed model request nulls whole-attempt usage.** The offline audit recovered
   completed-generation usage for one scored attempt; the unexported incident's
   usage/cost remains unknown. Reported cost is an estimate, not complete billing.
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

Show the branch/diff and checks to the user for review. No live/model calls,
scored retries, challenge-program inspection, target
changes or new behavior experiment are part of this milestone. The user intends
to push the reconciliation branch; no remote push has been performed here.

## Current milestone verification

- All 569 inline links in 34 Markdown files checked for local file/heading targets;
  35 distinct pinned historical Git objects verified locally. External sites were
  not fetched or checked for availability.
- Complete old README content and prior status body preserved, allowing only the
  documented heading/context wrappers and link-destination changes.
- 1,284 protected files byte-identical to team main: runtime/configuration/tests,
  dependencies, reporting scripts, report artifacts, scored records and non-Markdown
  evidence. Original reference URLs and professor quotations preserved.
- Offline aggregation exactly matches committed `final_summary.json`; 29 existing
  challenge-loader tests passed. No Docker/model/hosted checks were run.
- `git diff --check` passed. Historical test counts remain in their original
  records and are not presented as fresh verification. See the
  [reconciliation history entry](docs/PROJECT_HISTORY.md#documentation-reconciliation--november-13).
