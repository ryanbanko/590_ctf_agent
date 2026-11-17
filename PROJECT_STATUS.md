# Project status

Last reviewed: November 17, 2026 (America/New_York).

HTB manual limits are now one hour, 200 model requests and 240 tool calls in both
Luna and optional Sol profiles. The latest successful Omni Watch run used 1,650
seconds and 45 model/tool calls; the higher limits are operator-selected ceilings,
not evidence that longer attempts improve performance or a spending target. The
user watches live traces and may stop early. CTFTiny's defaults are unchanged.
Both profiles load with the derived request cap; no challenge run was started for
this update. [Rationale and checks](evidence/htb-budget-update/README.md).

Sol diagnostic follow-up: both user-run Void attempts stopped on first-request
HTTP 400 with zero tools. After the initial three passing synthetic probes,
a production-shaped harmless request passed; replaying the latest failed first
API request reproduced a provider **`cyber_policy` content rejection**. The replay
executed no tools and started no solver/target interaction. The original errors
retain status only, so their precise bodies remain unavailable. Five diagnostic
model requests total; $0.000614 covers only the first three, not complete costs.
Diagnostics are stopped; runtime/default Luna configuration remain unchanged and
the optional Sol profile is retained. Preserve both failed runs and unknown usage.
[Requests, evidence and limits](evidence/sol-compatibility/README.md).

Optional [Sol manual profile](configs/htb-sol.toml) prepared at the user's request.
It preserves the HTB limits and medium reasoning, changing only model identity
and the three local pricing fields relative to Luna. Its wall/call limits were
later raised together with Luna's profile to 1,800 seconds/100 requests/120 tools.
Configuration loading and the derived 100-request cap passed offline checks.
Pricing uses the retained November 14 gateway snapshot. Luna remains the default; select Sol with
`--experiment configs/htb-sol.toml`. Preparation started no model call or challenge
attempt; the later user run and diagnostic probes are recorded above.
[Condition and verification](docs/EXPERIMENTS.md#optional-sol-manual-profile--november-17).

Previously reviewed manual trace: DNS Dossier `695912dc3f8c` records human-relayed
acceptance after seven model/seven tool calls and 167.377 active seconds, including
about 136 seconds awaiting the verdict. The [description review](evidence/htb-description-review/README.md)
finds evidence-driven discovery despite a brief joking description. The original
export timed out; a read-only supplemental retrieval contains all seven generations
and six command tools, but no root/submission/terminal spans. Local acceptance and
cleanup records are distinct from missing hosted evidence; `evidence_complete`
remains false. A small narrative-framing clarification is proposed, not implemented.
No new attempt, runtime change or paid call occurred during review.

Earlier user-run manual trace: Blueprint Heist `c6bd2379fdc2` ended without success
after 16 model calls/15 tools and 212.4 active seconds, with no submission,
timeout, restart or recorded scope/cleanup incident. At the user's direction,
the [review](evidence/htb-latest-trace-review/README.md) evaluates model actions
only: good initial inspection, then repeated variants, overbroad negative
conclusions, an unvalidated diagnostic and a text-only stop. Complete local
payloads were checked. No challenge-solving recommendation or runtime change;
no new attempt was started. This run establishes live command/HTTP/export
behavior for that attempt, but does not exercise human verdict input.

Read-only prompt-preface assessment: operational guidance is worth a small
separate test, starting with stateful-network interactions; six category
checklists have weaker trace support. Rechecked original metadata/export hashes
and selected traces, including successful controls and both validation failures.
NYU's pinned generic templates provide category/server-type precedent, not proof
of benefit. [Evidence, draft and proposed comparison](evidence/task-preface-review/README.md).
No runtime/configuration change or new attempt; implementation and paid testing
remain separate milestones. The manual HTB readiness handoff below remains active.

## Current step

**The manual HTB fallback is implemented and offline-verified on `feat/htb-manual`.**
The user authorized branch creation and the first implementation milestone:
interactive ZIP/folder task setup, shared isolated execution, human-relayed
accepted/rejected/cancel/error flag verdicts, submission records and a separate
900-second/60-model-call configuration (80 tools). Langfuse remains the tracing
system. All **204 offline tests passed; 49 Docker cases were deselected**.
The first broad check exposed an unsubstituted SDK trace-URL lookup in a new test;
the corrected local test also supplies the cleanup event required by export.
[Implementation, commands, checks and limits](evidence/htb-manual/README.md).

During that implementation milestone, no real challenge attempt, Docker/VPN
operation, paid model call, hosted mutation, MCP implementation, commit or push
occurred. The user has since performed live manual attempts; the latest review
is linked above. Its evidence supersedes the earlier pending-live handoff only
for the behavior actually observed. Raw tasks/submissions remain local and
Git-ignored; old benchmark records are unchanged.

**Before this milestone, the original `0395835` prompt and 40-turn default were restored.** The
user withdrew planning/notes plus 50 turns after review found limited adoption
and no demonstrated benefit. Both agent.py and development.toml match that commit
byte-for-byte. The manual integration now extends shared controller/launch code;
the rollback's other-file identity claims describe that earlier checkpoint.
All 41 focused offline rollback checks passed. At that checkpoint, remaining
uncommitted work was documentation and retained experiment evidence.
[Decision, review and verification](evidence/planning-notes/rollback/README.md).

The user-run candidate recorded 12 attempts across ten distinct tasks: ten
verified successes, one service-blocked ending and one model/API stop. Ten local
exports show no explicit notes.md use or write_file call. No attempt exceeded 29
model calls, so the extra allowance provided no observed benefit. Two exports
are unavailable and one successful export has six missing payload fields.
The two originally scored-list practice tasks were not started. Keep all records;
limited adoption and historical unpaired comparisons do not prove regression.

**The previous full validation rerun remains incomplete: 20 successes, two solver-limit failures,
and one API incident after 23 development attempts.** Batch `aaab2a5084b8` stopped
on response_source_error; trace export also returned ConnectError. Seven remaining
development attempts and six test-task attempts have not run. The earlier VPN-
interrupted batch `ce84d7e598bd` is separate. The final API trace is unavailable;
its precise request failure is not diagnosed.

At the user's direction, the [earlier validation review](evidence/validation-full-review/README.md)
focuses on agent patterns only. Main weaknesses: inferring external restrictions
from unvalidated self-tests, confident claims before verification, repeated
variations without narrowing the cause, and incomplete checking of corrections.
Successful runs instead isolate one uncertainty and branch on observed results.
The 40-turn and 600-second failures expose limits of that prompt revision; more
persistence/budget or another broad rule is not an established fix. That review
made no runtime change or new run. The later planning/notes trial review and
rollback are recorded separately above. Keep all failures and incomplete usage.

The earlier six-category pilot achieved 18/18; those records remain in
[expanded pilot evidence](evidence/validation-expanded-review/README.md) and
[first pilot evidence](evidence/validation-pilot-review/README.md). Its small,
unpaired samples did not establish a causal solve-rate or efficiency gain.
The exact prompt, 36 passing offline checks and rollback snapshot remain in
[prompt evidence](evidence/prompt-validation/README.md). During those trials,
model, budgets, tool contracts, loop and Docker matched the original baseline.

The preserved 36-attempt practice baseline achieved **35 successes**. The later
external connection-description pilot achieved **1/3**, compared with **2/3** in
the same task's baseline: one 29-second success and two 600-second wall limits.
All three initial service reads completed without the earlier JSON error, but
later computation/validation mistakes consumed the failed runs. Small randomized
samples establish neither improved reliability nor causal regression. That tool
description was not adopted; the main tool definitions still match `0395835`.
Fixed service probes separately reproduced persistent JSON errors after a
four-second early disconnect (3/3), while five-second disconnects did not reproduce
them (0/3). Exact private state/write behavior was not inspected or repaired.

Plans/notes were tried and withdrawn. Passive instrumentation, conditional
feedback and payload/error-record improvements remain proposals. The
[baseline review](evidence/notes-baseline-review/README.md)
and [concrete proposal](docs/AGENT_CHANGE_PROPOSAL.md) preserve their earlier
conditions and findings, including eight payload gaps and one timing discrepancy.

Both affected target images now use checksum-pinned Ubuntu socat 1.7.3.3 while
retaining their OS, libraries, application, command, user, relay and 60-second
inactivity limit. Synthetic/readiness checks passed. The approved follow-up
achieved **2/2 verified development successes**: roppity in 204.16 active seconds,
baby-boi in 330.42, both targets running before cleanup. Estimated combined model
cost: $0.03305. [Correction and evidence](evidence/listener-update/README.md).

The user considered optional concurrency, then chose to retain the existing
sequential runner. The exploratory additions were removed; the regular batch
function, CLI and batch tests match main byte-for-byte. No parallel runner ships.

The listener diagnosis/correction and usage-preservation changes were committed
on main at **`0395835`**, which is the clean recorded baseline for all 36 attempts.
The earlier reconciliation is at `bc3ca3a`. Dated history and original scored/
submitted report artifacts remain preserved. The active prompt and CTFTiny default
configuration match `0395835`; the manual HTB branch adds shared controller/launch
changes and a separate configuration. Documentation and evidence retain all candidate
decisions/results. Commits and pushes remain the user's responsibility.

The [November 14 improvement review](docs/IMPROVEMENT_OPTIONS.md#current-review-and-proposed-comparison--november-14)
separates completed changes from proposals. Reported-call usage preservation is
now implemented: `known_usage` survives later failures; unknown complete totals
stay null. Fifty-eight focused offline tests passed. Local error/export record
improvements remain proposals. Brief optional plans/notes were tested with a
50-turn allowance and withdrawn after review; their evidence remains preserved.
The user authorized at least two challenges per category and three trials each,
allowing both development and test tasks for practice. The
[expanded proposal](docs/IMPROVEMENT_OPTIONS.md#expanded-comparison-and-baseline-freeze--november-14)
contains 12 CTFTiny tasks (ten Hard, two Easy), 36 baseline + 36 candidate attempts.
The baseline ran in two ordinary manifest-separated batches: development
`471fe180c113` (29/30) and test-task practice `39f3da0c8fa3` (6/6). Their recorded
source/settings and per-task images match across trials. The later connection
pilot is separate; the withdrawn validation-prompt candidate has eighteen completed
pilot trials plus the separately recorded partial full rerun. Reused scored
tasks are tuning evidence; original scored records remain
unchanged. Raw runs are Git-ignored; the shareable review includes per-trial
metadata, source/export hashes and trace links, without answers or trace payloads.
The November 14 read-only checks confirmed native costs on all 43 generations
of the two listener-validation traces; root SPAN costs are null.
[Accounting and cost evidence](evidence/usage-preservation/README.md).

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
The active agent prompt/tools/model adapter and CTFTiny default configuration match
`0395835`, including the original practice-baseline prompt and 40-turn allowance.
The manual branch extends orchestration/verification; its separate configuration
uses 900 seconds/60 model calls/80 tools. Both withdrawn candidates and
their original settings/results remain in evidence.
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
- [x] Complete and review the authorized 12-task/36-attempt practice baseline;
  preserve the service-blocked failure and comparison limitations.

## Open issues and limits

1. **The listener fix is verified; broader reliability is not guaranteed.** Both
   fixed targets survived synthetic crashes and real development runs. One fresh
   success per target is not a solve-rate estimate or proof every service issue
   is resolved. No `nofork`, restart, extra init or permission/budget relaxation
   was adopted. The new practice baseline also has three roppity successes, with
   no comparable listener exit observed. [Current handoff](docs/TARGET_PROCESS_ISSUE.md).
2. **External-service failures can stop a batch.** The scored model/API incident
   also lacked a trace export; its precise cause is unconfirmed. The target was
   still running. A separate later scored recheck stopped after 12 successes and
   a response-source error; its final trace export also failed and the precise
   request error remains unconfirmed. [Local metadata record](evidence/scored-recheck-stop/review.json).
   This is separate from the 36-attempt baseline. No automatic retry/resume is implemented.
3. **Partial usage is preserved; complete billing can still be unknown.** New
   records retain `known_usage` after failures, while whole-attempt totals stay
   null when incomplete. Historical records are unchanged; the unexported scored
   incident's usage remains unknown. Local estimates still omit the cache-write
   premium visible in native Langfuse costs. Durable local error categories and
   stronger export-payload checks remain proposals. The full request/action audit
   finds eight absent fields in one structurally complete successful trace; six
   were counted in the earlier generation-output/tool-payload review.
4. **Timing labels need review.** `aggregate.py` reads `result.total_seconds` as
   wall time; `run.json.total_seconds` covers the broader launch. The report calls
   its time launch-to-finish. A new baseline trace also shows a 132.7-second hosted
   model span within 83.3 local active seconds; clock/sleep effects are possible
   but not diagnosed. The report/scripts are preserved pending an explicit
   decision about the field/label; these intervals must not be conflated.
5. **Submission tag/demo provenance needs confirmation.** Team documents refer to
   `part1-submission`, but no local/remote tag was found during the November 13
   check. Earlier status also flags video identifiers outside this repository.
6. **Prompt improvement is unproven.** The original 36 attempts did not exhaust
   their top-level limits. The withdrawn validation revision achieved 18/18 in
   pilots, then 20 successes, two limit failures and an API stop in the partial
   full rerun. Planning/notes plus 50 turns recorded 12 attempts with limited
   visible adoption and no demonstrated benefit; the user selected the original
   runtime. This does not establish causal regression. Continuation,
   compaction, other budget/model changes and target-state repairs remain
   unimplemented. The prioritized review separates recurring agent behavior from
   service reliability.
   [IMPROVEMENT_OPTIONS](docs/IMPROVEMENT_OPTIONS.md).

## Next action and authorization

Review the [description/framing assessment](evidence/htb-description-review/README.md)
and the [earlier model-action findings](evidence/htb-latest-trace-review/README.md).
The latest user-run attempt demonstrated assigned-service interaction and a locally
recorded human acceptance; its hosted export remains incomplete. The small framing
draft and separately discussed persistent handoff remain proposals. No behavior
change or follow-up run starts automatically. Any implementation/live stage needs
separate authorization; no Docker operation, hosted mutation, budget/prompt
change, commit or push starts automatically.
MCP can later fill the same public task and trusted verification function.
Preserve the [rollback and trial findings](evidence/planning-notes/rollback/README.md),
all failures/API/export gaps and the unchanged CTFTiny defaults. Further
planning/notes iteration and the remaining practice tasks are not scheduled.

## Current milestone verification

November 16 manual HTB fallback: **204 offline tests passed, 49 Docker cases
deselected**. Covered ZIP/folder import (including the documented password),
unsafe path/symlink/special-file/duplicate/size rejection, saved-task validation,
CLI setup without credentials/Docker, y/n recovery, cancellation/EOF/Ctrl-C,
verification errors, wall expiry/late verdict rejection, submission records,
local bridge cleanup, CTFTiny regression and real SDK model/tool tracing/export
with local transports. The initial broad suite had 201 passes and one test-fixture
failure; its cause/correction are retained in the evidence. Docker isolation and
real target routing are inherited controls, not newly live-verified here. No
solve-rate/cost benefit or working MCP/hosted integration is claimed.
[Verification and remaining limits](evidence/htb-manual/README.md).

November 16 rollback: **41 focused offline checks passed** after restoring the
original prompt and 40-turn default. Source/default config match `0395835`
byte-for-byte, shared turn/request caps are 40, and all unrelated source/settings/
tests/dependencies remain preserved. Candidate snapshots, original verification,
local outcomes/export hashes and limitations remain in evidence. No new live
model/challenge run, Docker operation, hosted mutation, recorded-command replay,
commit or push occurred. Only documentation/evidence differ from the last commit.
[Review and rollback checks](evidence/planning-notes/rollback/README.md).

November 16 planning/notes implementation: **41 focused offline checks passed**.
Verified exact original-plus-paragraph prompt identity, unchanged non-prompt AST,
the sole parsed default setting delta of 40 to 50 and shared model/request caps.
Existing tests cover prompt propagation, recovery/replay, text-only/success/
terminal stops and configuration/accounting contracts. Original candidate evidence
and all unrelated runtime/config/test files were preserved; no new test cases,
Docker/model/challenge/hosted operation, command replay, commit or push occurred.
Offline passing checks do not establish adoption, solve rate or efficiency.
[Snapshots, checks and comparison limits](evidence/planning-notes/README.md).

November 16 pattern review: inspected the 22 available local traces, emphasizing
all steps of the two ordinary failures and contrasting successful workflows.
The final API incident lacks a local trace. The review uses visible purposes,
actions and feedback, not hidden internal reasoning. Preserved local outcomes,
record/export hashes and step references; no new model call, Docker operation,
recorded-command execution or runtime change.

November 15 regression expansion: 12/12 additional successes, 18/18 combined.
All available expanded request bodies (117/118) match the exact candidate prompt;
all runtime source hashes identify the same revision, with only `agent.py`
differing from baseline. Tool descriptions, settings, dataset and per-task images
match. One generation and two tools lack both payload fields in the Pwn 1 local
export despite `evidence_complete: true`; required payload completeness is not
proved by structural checks. A reversing span also disagrees with local active
time. [Preserved findings and hashes](evidence/validation-expanded-review/README.md).
This review performed no new model call, Docker operation, command replay or runtime edit.

November 15 validation-pilot review: all six user-run trials succeeded. The exact
candidate prompt appears in all 62 requests; all generation/tool input/output
payloads are present. Only `agent.py` differs from baseline runtime source;
model/settings, limits, dataset and per-task image provenance match. Recorded
hashes, per-trial behavior and historical-comparison limits are preserved in
[evidence](evidence/validation-pilot-review/README.md). This review performed no
new model call, Docker operation, command replay or runtime edit.

November 15 prompt revision: **36 focused offline tests passed**. Exact before/
after prompts and a mechanically checked inventory of retained instructions are
preserved in [evidence](evidence/prompt-validation/README.md). Only the system-prompt
literal changed in runtime source. No Docker operation or new model call occurred
during this edit. Earlier service diagnostics and the user-run connection pilot
are separately summarized there; their results do not validate this new prompt.

November 15 implementation-aware follow-up: derived per-request token growth and
item-byte profiles for 355 generations (353 available request bodies), reconciled
usage against all 36 original runs, and inspected existing loop/tool/lifecycle
code and historical evidence. All 36 initial inventories succeeded; 35 final
unavailable events are explicit, one inventory event has missing metadata. Two
additional null generation inputs expand the earlier six-field payload count
to eight. [Derived evidence and proposal checks](evidence/agent-change-proposal/README.md).
No runtime code, model input/configuration or original run was changed; no new
model call, Docker operation or runtime test was performed.

November 15 trace review: covered all 36 attempts; checked original record/export
hashes, observation counts, per-task image/config identity and complete capture
flags. Audited usage totals and individual context peaks without replaying trace
commands. Documented six payload gaps and one timing discrepancy. Documentation
links/JSON/whitespace are checked separately in the review's
[checks record](evidence/notes-baseline-review/checks.json). No
runtime test suite, model call or Docker operation was repeated for this review.

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
