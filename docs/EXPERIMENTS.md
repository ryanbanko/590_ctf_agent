# Section 2 experiment log

This is the detailed experimental record. [Project history](PROJECT_HISTORY.md)
summarizes milestones; [current status](../PROJECT_STATUS.md) owns the active task
and next action. “Current,” “proposed” and “not implemented” in dated entries refer
to that checkpoint. Keep original hypotheses, failed checks and limits; later
results supersede pending notes without erasing them. Historical evidence links
may open the version retained in Git rather than the current checkout.

Use this file for development trace findings, hypotheses recorded before live
comparisons, the exact change, run references and conclusions. Keep raw evidence
in Langfuse and run records; use `PROJECT_STATUS.md` for the overall checklist.
This is Section 2 of [Part 1](../ASSIGNMENT.md), not the later competition Part 2.

## Optional human guidance: implementation and offline checks — November 18

Hypothesis before live testing: allowing a watching human to supply a correction
or suggestion between model turns may help recover from a mistaken conclusion
without restarting an attempt. This changes the condition to human-assisted solving
when guidance is used; it is not evidence of an autonomous performance improvement.
The user approved implementation/offline checks only and explicitly retained
text-only stopping. A live usefulness comparison remains separate.

Implemented on `feat/htb-guidance` from clean `htb-manual` commit `7cb1837`:
manual-only `--allow-guidance`, a second-terminal `guide` command, a bounded local
file queue, user-message insertion before the next request, and local/Langfuse
receipt records. The exact wrapper is “Human guidance: Consider this alongside
the evidence gathered so far.” Message text stays verbatim after the wrapper.
No system-prompt, tool, model, budget, dependency, solver image or scope change.
Without the flag there are no queue filesystem operations. Enabled but unused
guidance adds no model/tool calls or prompt text.

113 controller/conversation/native SDK/manual/guidance checks plus 25 launcher/batch
checks passed, with two Docker cases deselected. Checks compare disabled and empty
inboxes for histories, tool schemas, counters and five stopping conditions; verify
guidance arriving during response/tool work, persistence/order, malformed queue
handling, symlink rejection, bounds, late input, expiry, source failure and startup
failure. Native mocked-transport requests confirm insertion after linked tool
results without extra requests/tools. A pre-existing test still expected the older
manual budgets; corrected its expectation to the existing committed profile.

Seven local timing samples of 200 empty-inbox checks had a median total of 3.21 ms
(0.016 ms/check). This is a small local-directory measurement on this Mac, not a
general latency guarantee. No real challenge, paid model request, Docker operation,
hosted mutation, commit or push occurred. Provider acceptance/model adoption,
live routing and behavioral benefit are untested. No crash-resume feature exists;
an abrupt process loss can leave delivery unconfirmed. Review before a live trial.
[Implementation, command history and evidence](../evidence/htb-guidance/README.md).

## Repeated Sol HTTP 400: provider rejection reproduced — November 17

The user's unchanged retry `c49236369760` again stopped on the first request,
with zero tools and clean cleanup/export. Two further diagnostic requests narrowed
the cause: the original system prompt, three production tools and 8192-token cap
with harmless user text completed; the latest failed initial API request, rebuilt
from its recorded input/tools and unchanged model settings, returned HTTP 400.
Its bounded error capture contains a nested provider `cyber_policy` code and the
message that the content was flagged for possible cybersecurity risk. This
identifies the reproduced rejection; the two original error bodies were not
retained and cannot be independently inspected. No single triggering phrase is
identified. No prompt rephrasing, alias change or fallback was attempted.

These were API-only diagnostics: no solver, target contact or returned-tool
execution. Five diagnostic requests total across the two stages; the original
$0.000614 native subtotal covers only the first three. Rejected usage is unknown.
No application/config change was made; diagnostics stopped, default Luna and the
optional Sol profile remain. [Follow-up evidence](../evidence/sol-compatibility/followup.json).
Original three-probe evidence below is preserved as its earlier checkpoint.

## Sol HTTP 400 and bounded compatibility probes — November 17

The user's first Sol Void attempt `b5a999ddfb5c` stopped at the first request with
HTTP 400, zero tools and successful cleanup/export. Raw error details were excluded
by the existing privacy hook. After the user suggested simple single calls, ran
at most the three announced synthetic requests: plain text, runner reasoning/replay
options, then one synthetic function definition. All completed; no function was
executed. The exact configured name worked, so no alias variation was needed.

Native Langfuse readback verified each root/generation and cost: $0.000614 combined.
The probes changed the input, output cap and tool set compared with the failed full
request, so they do not diagnose its cause or establish complete solver integration.
No runtime/configuration change, challenge retry, Docker operation, target contact,
commit or push. Preserve unknown failed-request usage and the original failure.
The user may make one unchanged retry; recurring HTTP 400 needs a sanitized detailed
diagnostic, rather than repeated name guessing. [Evidence and request snapshots](../evidence/sol-compatibility/README.md).

## Optional Sol manual profile — November 17

The user requested a ready-to-run GPT-6.1 Sol configuration for repeating their
manual HTB test. Added `configs/htb-sol.toml`, selected explicitly with
`--experiment`; Luna's manual and development defaults remain unchanged. Compared
with the manual Luna profile, exactly four parsed fields differ: model identity
and the three accounting rates. Medium reasoning, 8,192 output tokens, 900 seconds,
60 model requests, 80 tools and all other settings remain fixed. Rates match the
retained November 14 Duke metadata; they are not a new live pricing/billing check.

Hypothesis for the user-selected comparison: Sol may improve decisions on the same
task under the existing bounds, but may use different calls/tokens/time and has
higher unit prices. A single repeat cannot establish a general model advantage;
the operator must reset the remote instance and update changed endpoints for a
fresh-state comparison. No assistant-started live trial is part of this milestone.

Offline verification loaded the complete file through `load_experiment`, checked
the exact four-field delta, the derived 60-request cap, unchanged 900-second/80-tool
limits and matching recorded pricing rates. No new tests, dependency, runtime or
prompt change, model call, Docker operation, target request, hosted mutation,
commit or push. Stop for review; the user can run the existing manual command with
the explicit profile. This is configuration readiness, not live Sol compatibility
or a measured performance/cost result.

## HTB manual wall and call limits — November 17

After reviewing Omni Watch, the user requested more wall time and model turns,
then selected a 30-minute wall limit. That run stopped at 900 seconds after 20
model requests and 15 tool spans, with three solver restarts; its 60-request cap
was not reached. The trace showed several unconfirmed bot-execution hypotheses,
so a larger allowance may extend unproductive probing. The user will monitor live
traces and can stop early.

Updated both HTB-only profiles to 1,800 seconds, 100 model requests and 120 tool
calls. The proportional call increase keeps the tool cap from binding too early
if many model responses request small commands. Per-request timeout, solver/guard
resource limits, reasoning, output cap and scope controls are unchanged. CTFTiny's
development configuration remains unchanged. These are operational limits, not
evidence of improved success or a cost guarantee; the longer wall can increase
total spend. This change does not start a challenge attempt.

Offline loader checks confirm both profiles parse and derive 100 model requests;
the new wall/model/tool limits match. No model request, target contact, Docker
operation or broad test suite was run. [Change record and checks](../evidence/htb-budget-update/README.md).

## HTB manual limit extension — November 17

After the 30-minute setting was in place, the user selected a one-hour wall limit
and a 200-model-request ceiling. The latest Omni Watch run had succeeded in 1,650
seconds with 45 model and 45 tool calls, so it did not exhaust the earlier
30-minute/100-request/120-tool limits. The larger settings are an operator-chosen
ceiling for future monitored attempts; they do not establish a need for more
resources or predict improved performance. A one-hour attempt can permit greater
spend if it continues for longer.

Both HTB profiles now use 3,600 seconds, 200 model requests and 240 tool calls.
The tool allowance keeps the observed roughly one-tool-per-request pattern from
making the tool cap bind before the requested turn cap. CTFTiny defaults,
per-request timeout, command timeout, output cap, resource/isolation bounds,
scope and recovery behavior remain unchanged. The live operator can stop early.

Offline config-loader verification confirms both profiles parse and derive the
200-request cap; CTFTiny still matches `HEAD`. No model request, challenge run,
Docker operation or broad test suite was run. [Checks and history](../evidence/htb-budget-update/README.md).

## Narrative descriptions and newest manual attempt — November 17

At the user's request, compared four supplied HTB descriptions with the newest
manual run, DNS Dossier `695912dc3f8c`. No treatment was introduced. Seven model
calls established actual service behavior and led to locally recorded human
acceptance; about 136 of 167.377 active seconds were spent awaiting that verdict.
The brief joking description did not prevent evidence-driven progress.

The original export timed out. A read-only hosted retrieval saved a supplemental
export with seven generations and six command tools, all with payloads, but no
root/submission/terminal spans. Preserve `evidence_complete: false`; local accepted
submission records do not fill missing hosted observations. Source/prompt identity
matches current runtime. The [review](../evidence/htb-description-review/README.md)
proposes retaining the original task text and, if desired, testing a small trusted
framing clarification. No automatic rewriting, category playbook, memory change,
prompt implementation, new run/model call, command replay or Docker operation.
One successful control does not establish a benefit from additional instructions.

## Earlier manual attempt: model-action evaluation — November 17

Read-only review of user-run Blueprint Heist `c6bd2379fdc2`, explicitly limited
by the user to model actions, not challenge analysis. No experimental treatment
was introduced. The unchanged prompt inspected files first and explained actions;
later repeated candidate lists, overbroad negative conclusions and an unvalidated
diagnostic preceded text-only stopping after 212.4 seconds/16 model calls. No
enforced budget caused the stop, but remaining budget does not prove solvability.
All 16 generation/15 tool payloads, call-result replay links, current source/prompt
identity and usage reconciliation passed. No submissions or recorded timeouts,
restarts, scope incidents or cleanup errors. This one case does not support a
category-wide missing procedure or an automatic prompt change. [Full review and
observation references](../evidence/htb-latest-trace-review/README.md).
Documentation/derived metadata only; no source/configuration, original record,
new attempt/model call, command replay, Docker or hosted operation changed.

## Operational/category preface assessment — November 17

Read-only hypothesis review, **not an implemented experiment**. Directly checked
selected traces and source contracts after repository/evidence orientation.
Stale-session answers, delayed reads, high-volume inspection, artifact mutation
and expensive computation align more closely with operational characteristics
than category labels. Successful HTTP and small-file controls constrain blanket
guidance. Verified NYU's pinned category/server-type template precedent without
consulting challenge solutions; no causal benefit is established.

Proposed first condition: unchanged original prompt plus one short stateful-network
preface; fixed current CTFTiny settings/images and fresh controls. A formative
four-task/two-trial/two-condition design would use 16 attempts; a category arm
would require a separate comparison decision. This is a proposal, not spending
authorization. Existing tool wording already requests same-connection interaction,
so the hypothesis concerns more concrete emphasis/adoption. Prior connection,
validation and notes trials remain distinct conditions with their limitations.

[Assessment, selected observations, inventory checks and draft](../evidence/task-preface-review/README.md)
retain the evidence and review limits. Documentation/derived metadata only;
no runtime/configuration/tests, original records, model call, Docker operation,
hosted write, recorded-command execution, commit or push changed. Stop for review
before implementation or a paid pilot; manual HTB readiness remains separate.

## Planning/notes review and original-baseline rollback — November 16

The user ran initial batch `055588a94b64` (five successes; the fifth export timed
out) and breadth-development batch `e7f3dbb55808` (five successes, one service-
blocked ending, one model/API incident with failed export). The two originally
scored-list practice tasks were not started. Preserve all 12 outcomes across ten
distinct tasks, including the two extra repeats; this is not a completed 12-task
once-each comparison or a 36-attempt campaign.

Read-only behavior review found no explicit notes.md use or write_file call in
the ten available local exports. All 97 available generation inputs match the
candidate; one of the 98 exported generations lacks input/output, and two tool
observations in that same successful run also lack both payloads. Two complete
exports are unavailable. Initial forward-looking action explanations are visible,
but do not establish a maintained/revised task-level working state; private
planning is not inferred. No attempt exceeded 29 model calls, so the extra ten
turns provided no observed benefit.

Successful short workflows remain concise. A longer success still contains empty
inspections, oversized output, unsupported explanations and a lost distinction
between original and modified artifacts during correction. Other successes show
useful narrow checks and recovery, behavior also present historically. These
observations support **limited adoption and no demonstrated benefit**, not proof
of a causal regression. Existing historical/unpaired, mixed-condition and
service/evidence limitations remain.

At the user's explicit direction, removed the planning/notes paragraph and
restored the 40-turn default. Agent source and default configuration now match
`0395835` byte-for-byte; all other runtime/configuration/test/dependency files are
unchanged. The earlier validation revision remains withdrawn. All 41 focused
offline checks passed after rollback. No new test cases, model/challenge run,
Docker operation, hosted mutation, recorded-command execution, commit or push.
[Per-run outcomes/hashes, behavior references, snapshots and rollback checks](../evidence/planning-notes/rollback/README.md).

Stop for review. No further prompt iteration, continuation policy, budget change
or completion of the remaining practice tasks starts automatically. Retain the
original runtime and all experiment evidence; remaining working-tree differences
from the last commit are documentation and retained evidence.

## Brief plans/optional notes and 50 turns — November 16

The user approved restoring the exact original `0395835` prompt, adding the agreed
brief-planning/optional-notes paragraph and increasing `max_model_turns` from 40
to 50 to allow room for note operations. This is a **combined prompt-and-budget
candidate**, not an isolated notes experiment. The default loader derives the
API request allowance from the same field. The 600-second wall deadline,
80-tool-call cap, other settings, tools, loop, dependencies and Docker remain.

**Hypothesis before live testing:** brief revisable plans and optional notes help
complex attempts maintain direction, reuse valid work and avoid repeating rejected
approaches, with limited overhead for straightforward tasks. Ten additional turns
allow more note operations within existing time/tool limits; useful decisions and
benefit are not guaranteed. Plans accompany tool calls; text-only replies still
end attempts. Existing file tools handle notes, with no automatic injection or
compaction. Old note text remains in native replay after a file overwrite.

The earlier validation/readability candidate was not selected as the default:
the latest read-only assessment found recurring diagnostic/correction problems
and higher aggregate resources despite a lower median time. Small historical,
unpaired comparisons do not establish prompt causality. Its exact prompts,
18/18 pilot and incomplete full-rerun records remain preserved unchanged.

**Verification:** 41 existing focused offline checks passed, covering public prompt
propagation, recovery, native text/tool replay, success/text-only/terminal stops,
bounded accounting and configuration sharing/validation. Mechanical checks verify
exact original-plus-paragraph identity, non-prompt AST identity, the sole parsed
configuration delta of 40 to 50 and preservation of existing source/evidence.
[Exact snapshots, diffs and checks](../evidence/planning-notes/README.md).
No new test cases, live model calls, challenge attempts, Docker operations, hosted
changes, command replay, commit or push occurred. Offline checks do not establish
model adoption, useful notes or performance improvement.

Stop for review before a separately approved pilot. Compare against the original
40-turn baseline as a combined condition; a fresh original-prompt control at 50
turns would be needed to isolate the prompt effect from the larger allowance.
Include complex tasks and a short-task control, preserve all failures/incidents,
and assess success, repeated work, reuse, calls/time/tokens/cost, note overhead,
stale claims and actual adoption. Rarely used notes are limited-adoption evidence.

## Full validation rerun, partial agent-pattern review — November 16

Batch `aaab2a5084b8` stopped after 23 development attempts: 20 successes,
model_turn_limit on `61bf8e65e52b`, wall_limit on `4fbd9b2b538b`, and a final
response_source_error with ConnectError on export (`83687a3f80cf`). The earlier
user-confirmed VPN batch is separate. Seven development and six test-task trials
remain unstarted. The final API trace is unavailable; do not infer its preceding
agent behavior. Known usage remains partial rather than substituted for totals.

The user explicitly narrowed review to observable agent reasoning/action patterns.
The [pattern review](../evidence/validation-full-review/README.md) finds premature
external explanations for failed self-tests, confident validation claims before
a discriminating check, escalation/repetition without narrowing the weakest
premise, and corrections that miss dependent code. Successful cases isolate a
small prerequisite and use feedback to select the next action. The 40-turn run
acknowledged its own layout error only at step 24; later self-test bugs undermined
further external-restriction claims. The wall-limited run consumed two command
allowances on diagnostic/search approaches before a simpler check came late.
No task solution or infrastructure correction is proposed; no runtime edit,
model call, container operation or command replay occurred during this review.
The earlier 18/18 pilot is preserved, not used to hide these later failures.

## Expanded validation regression completed — November 15

User-run batch `10010bdf842e` completed pwn-pilot, rev-gibberish-check,
web-shreeramquest and for-1black0white three times each: **12/12 successes**,
matching their original controls. New candidate/control totals: 1166.17/1139.70
recorded active seconds and $0.08215334/$0.09574549 estimated cost (about 2% more
time and 14% less cost). With the first six trials, this revision has 18/18
successes versus 17/18, 1865.46/1525.42 active seconds and
$0.11704363/$0.11645893 estimated cost. The single baseline failure was service-
related. These are reused practice tasks and historical comparisons, not causal
proof of validation improvement. [All trials, metrics and limits](../evidence/validation-expanded-review/README.md).

Pwn, web and forensics completed without excessive new validation rituals.
Reversing trial 1 checked predictions against the original artifact before its
later search. Trials 2/3 still searched reconstructed behavior before sufficient
original-artifact validation and each hit a timeout/restart before succeeding.
No scope incident or cleanup error occurred. Trial 3 also produced 500,979 output
bytes; the tool returned a marked 65,536-byte preview with complete full capture.
Largest individual context was 95,997 reported input tokens. Output discipline
and unvalidated reconstructions remain improvement targets.

Pwn trial 1 `7b008496a52b` lacks generation 9 input/output and tool 8/9 input/output:
six missing required local export fields despite structural `evidence_complete`
and local verified success. Its final submission payload/verdict cannot be
independently inspected; hosted observations were not re-fetched. Reversing trial
2 `fe967b23c21b` has a 314.303-second command span for a requested 120 seconds,
returned timeout, and a 525.337-second root span versus 331.335 local active
seconds. Host sleep/clock effects are plausible but unconfirmed. Native spans
must not be equated with local active or CPU time. Both findings recur separately
from the original baseline's known export/timing discrepancies.

All 117 available expanded request bodies match the candidate; one is absent.
All recorded runtime hashes identify the same revision, differing from original
source only in agent.py. Settings, limits, tool descriptions, dataset and images
match. It is reasonable to retain this small revision after regression coverage,
without claiming an efficiency gain. The user subsequently requested commands
for the original full 12-task/36-attempt practice set. No further run, runtime
edit, model call, Docker operation or command replay occurred during this review.

## Validation-prompt pilot completed and reviewed — November 15

User-run batch `bfa61beea669` completed cry-lupin and msc-algebra three times each:
**6/6 verified successes**, versus 5/6 for the corresponding historical baseline.
Lupin active seconds: 374.69, 74.11, 43.29; Algebra: 50.87, 121.39, 34.94. Total
active time was 699.29 versus 385.72 seconds; local estimated model cost was
$0.03489029 versus $0.02071344. Means include the baseline's early service failure;
medians and per-task/per-trial metrics are also retained. There is no aggregate
resource-efficiency improvement. No solver restart, scope incident, target
restart/OOM or cleanup error was recorded.

The [all-trial review](../evidence/validation-pilot-review/README.md) separates
observed validation from causal claims. Lupin 2 tested a local encoded sample
after a failed prediction before switching strategy. Lupin 1's initial parser
failures returned cheaply, but six avoidable parser/import mistakes and later
repeated work remained. Lupin 3 needed two patches for one shape assumption.
Algebra 2 repeated fixed answers across fresh sessions before eventual recovery;
Algebra 3 printed 44,928 characters in one command, growing the following input
from 7,493 to 31,813 tokens. Existing baseline traces also contain validation.
No scope-denial event exercised the relocated scope paragraph.

Exact candidate prompt identity is verified in all 62 model requests, and all
62 generation plus 62 tool input/output payloads are present. Only `agent.py`
differs in runtime source hashes; model/settings, budgets, dataset and per-task
images match baseline. Three unpaired randomized trials/task, historical/cache
conditions, different solution paths and combined behavior/readability edits
limit inference. The baseline's one failure was service-related; its absence
cannot be credited to validation. Compare against the original baseline, not
only the rejected connection candidate.

Recommendation: retain the candidate unchanged for reviewed broader testing,
without claiming a demonstrated solve-rate/efficiency gain. Proposed expansion:
the remaining ten original practice tasks, three trials each. A fresh original
control would strengthen inference at extra cost. No further run was launched;
this review made documentation/derived-evidence changes only, with no model
call, Docker operation, command replay or runtime edit. Original records remain
unchanged and Git-ignored; derived evidence includes hashes and observation IDs.

## Validation and prompt readability revision — November 15

The user approved one prompt revision after reviewing the original system prompt.
Hypothesis: explicit cheap checks, stopping expensive dependent work after failed
preparation, and checking corrections before expensive reruns will reduce wasted
computation. Scope recovery moves verbatim beside network rules; two sentence
splits improve readability. This is one behavior-and-readability condition, not
an isolated measurement of validation wording. Original-checker priority and the
independent-validation warning remain, along with output/reuse, summaries,
submission, stopping and scope policy. Only `SYSTEM_PROMPT` changes in runtime
source; model, limits, tools, loop, images and dependencies remain fixed.

All **36 focused offline tests passed**. The [evidence](../evidence/prompt-validation/README.md)
preserves exact prompts, source hashes and retained-instruction checks. No new
model call or Docker operation occurred during this edit. Offline tests verify
integration, not better model behavior. Proposed next stage: cry-lupin and
msc-algebra, three fresh trials each, then broader practice coverage if warranted.
Stop for review before these later paid stages. Compare success, time/cost,
expensive failed commands, repeated work and useful versus unnecessary checks.

## Service diagnostics and connection-description pilot — November 15

Before this revision, fixed service probes reproduced persistent remote JSON errors
after closing the first connection at four seconds (3/3); five-second closes did
not reproduce them (0/3). Six longer/same-connection controls received data without
that error. The listener stayed running. An interrupted initialization/publication
mechanism is consistent with synthetic tests, but actual private state/write code
was not inspected. No target repair, readiness workaround or budget relaxation
was adopted. [Sanitized diagnostic snapshot](../evidence/prompt-validation/service-diagnostic-summary.json)
predates the subsequent live pilot; its pending-comparison field is historical.
Raw fixed-probe scripts/reports remain external temporary artifacts, not a
fully retained reproducibility package.

The user-run external connection-description candidate batch `26e636f325ef`
completed **1/3 successes** versus **2/3** for that task in the earlier baseline.
Trial 1 succeeded in 28.89 active seconds; trials 2/3 hit 600 seconds during later
computation and correction. Initial reads completed in all three without the
earlier remote JSON error. One full command timeout caused a solver restart;
another command returned Killed/137 without establishing its cause. The candidate
cost $0.02835505 in local gateway-rate estimates, versus $0.00652700 for the three
baseline trials. All 38 model replies contained tool calls; 37 included purpose
text. This does not establish benefit or harm from the unchanged summary rule.

Fresh randomized instances, three trials, historical comparison and different
solution paths prevent causal solve-rate claims. The user chose the original
tool description, which remains unchanged in the main checkout. The earlier
agent-started run `5a6bc0060000` was interrupted for user handoff (`user_cancel`,
five model calls, $0.00236938 estimated) and remains separate from the three
completed trials. [Derived trace review and hashes](../evidence/prompt-validation/connection-pilot-review.json)
retain original trace links without flags or trace payloads. Original raw runs
remain external. These observations motivated validation work; they are not
results for the new validation prompt.

## Concrete implementation and experiment proposal — November 15 follow-up

The user requested exact changes for context efficiency, result-specific feedback,
multiple tool calls, broader planning/notes value and recurring infrastructure
findings. The [concrete proposal](AGENT_CHANGE_PROPOSAL.md) defines separate
instrumentation, diagnostic and behavior milestones; none has been implemented.
The smallest behavior condition replaces only command-tool connection-reading
wording. Proposed pilot: open-ellipti-ph, algebra and pilot, three trials each,
against their nine existing baseline attempts; fresh A/B would require additional
authorization/spending. Historical comparison and small-sample limits remain.

[Derived profiles](../evidence/agent-change-proposal/README.md) cover 355 reported
usage records and 353 available request bodies, reconciling every run total.
Two missing generation inputs expand the earlier six-action-field count to eight
request/action fields. All initial inventories succeeded; 35 final inventories
explicitly unavailable and one event metadata gap align with the implementation's
post-kill optional inventory. Proposed skip semantics are precise about the
stopping flag and do not assume successful kill. Library-identity assumptions
remain separate from known image differences and the corrected listener.

The source review confirms sequential sibling support but an explicit one-call
live request policy. Existing truncation/capture/reset metadata is retained;
wrapper-derived feedback cannot certify server/inner-script completeness. Notes
would support hypotheses/rejected tests/reuse as well as memory, with revisions,
bounded optional file use and no repeated injection. Prior writes remain in replay.
No runtime tests, new model calls, Docker operations, task-private inspection or
original-record modifications occurred; documentation/derived-metadata checks only.

## Practice baseline completed and reviewed — November 15

All 36 selected baseline attempts ran at clean commit `0395835`, with identical
recorded source/settings and stable images per task: development batch
`471fe180c113` achieved 29/30; test-task practice batch `39f3da0c8fa3` achieved
6/6. The sole ordinary unsuccessful ending returned repeated remote JSON-loading
errors while its container stayed running. Its cause is unconfirmed and its
failure remains counted. Planning/notes and continuation have not been implemented
or tested as candidate conditions.

The user requested category-by-category review of agent, tools, context and
infrastructure. The [assistant-assisted review](../evidence/notes-baseline-review/README.md)
covers every trial, including successful recovery, with metrics, observation IDs,
hashes, ranked proposals and limitations. Main recurring opportunities are
same-connection buffered reads, early independent validation/bounded searches,
and selective output. No existing top-level budget caused a stop. Largest
individual input is 170,959 reported tokens; aggregate replay is not context size.
Three command timeout restarts recovered; a separate search returned 137 without
establishing OOM. Six required payload fields are absent in one otherwise
structurally complete successful trace. One hosted/local timing discrepancy
prevents treating all span latencies as request durations.

These findings refine the pre-existing notes hypothesis; they do not establish
an improvement or prove forgetting. An infrastructure repair and a behavior edit
must not be credited as a notes-only effect. Keep all baseline failures, separate
the later scored-recheck API/export incident, and acknowledge the ceiling,
three-trial/task dependence, practice reuse, environment/cache and cost-basis
limits. No recorded commands, challenge-private source or answer files were
executed/read during review; no new model calls, Docker diagnostics or runtime
edits occurred. Only documentation and metadata review records were added.

## Expanded practice comparison — November 14 proposal

The user requested at least two tasks per category, preferably harder tasks, and
three trials each, then allowed development and test tasks. The
[expanded proposal](IMPROVEMENT_OPTIONS.md#expanded-comparison-and-baseline-freeze--november-14)
uses 12 CTFTiny tasks (ten Hard and two Easy), with 36 baseline and 36 planning/
notes candidate attempts. The two originally scored IDs are explicit practice
reuse; original scores remain historical and these reused tasks are no longer
fresh held-out evidence for candidate selection. Two ordinary manifest-separated
batches per condition preserve the existing runner. No batch, Git snapshot,
candidate behavior edit or new dataset integration has started. The earlier
six-task/two-trial idea below is superseded for this discussion.

## Usage preservation and cost review — November 14

At the user's request, implemented additive reported-call usage subtotals while
retaining null complete totals after any failed/missing-usage request. No solving
behavior or request/retry settings changed. Fifty-eight focused offline tests
passed, with two Docker cases deselected; the initial new test's double-decoding
assertion error is recorded. Read-only live Langfuse checks confirmed native costs
on all 43 generations in the two latest traces and null root SPAN cost fields.
Current Duke model metadata and official pricing support an approximately 18.14x
Sol/Luna fixed-volume illustration, not a spending forecast. No generation,
challenge run or hosted mutation occurred.
[Evidence, failed check, source hashes and limits](../evidence/usage-preservation/README.md).
Plans/notes together, continuation separately and Daybreak compatibility are
discussed in the improvement review; these remain proposals.

## Improvement review and proposed comparison — November 14

The user requested a review of prior experiments and remaining ideas, then asked
for the documentation to be updated. The
[current improvement review](IMPROVEMENT_OPTIONS.md#current-review-and-proposed-comparison--november-14)
records implemented versus deferred changes, ranked candidates and a proposed
six-task/two-trial baseline versus candidate comparison. The fixed listeners
belong in both conditions; the regular sequential runner remains unchanged.
Selection, candidate changes, spending allowance and paid runs await a separate
decision. No new experimental condition, challenge attempt or result is created
by this review, and historical outcomes remain unchanged.

## Fixed-listener validation — November 14

The user approved testing an updated listener in both existing images, including
normal I/O, child crashes, disconnects and the supplied 60-second inactivity limit,
followed by a small development retry if the checks pass. Keep challenge logic
out of the infrastructure review and preserve all historical results.

**Hypothesis before validation:** Ubuntu's packaged socat 1.7.3.3-2 contains the
upstream per-child diagnostic-channel correction and can replace just the socat
binary without changing the target OS, libraries, application, user or command.
The package checksum is pinned. An initial network-disabled `socat -V` check loads
successfully in a disposable original-image container; full behavior is not yet
validated. A standard two-stage Dockerfile copies only `/usr/bin/socat` into the
original content-addressed base. No custom compilation or `nofork` workaround.

Verify base-layer/config preservation, matching feature flags and version, repeated
normal and crashing children, bidirectional synthetic I/O, peer disconnects and
the actual `-T60` timeout. If these pass, apply only to the two exact known image
IDs, record the replacement and verify the ordinary launcher. Solver/guard/model
budgets and historical scored records remain unchanged.

**Completed:** the packaged binary loads in both original runtimes. Fixed images
preserve all original base layers and configuration except a compatibility label,
with matching socat feature flags. Both passed 20 normal exits, 20 child SIGSEGVs,
20 bidirectional exchanges, disconnect/reconnect, actual 60-second inactivity
timeout and subsequent reconnect/no leftover connection child. Normal readiness
passed for both targets; an overlapping global cleanup assertion was preserved
with its passing sequential rerun. The final offline suite passed 167 tests.

After the initial gateway TCP timeout and user's VPN confirmation, the approved
sequential one-attempt-per-target follow-up completed with two verified successes:
roppity 204.163 active seconds / 17 model calls, baby-boi 330.417 / 26. Both targets
were running before cleanup; no solver restart, scope incident or cleanup error.
Combined estimated cost $0.03304781; 708,442 input / 40,421 output tokens. Both
native evidence exports passed, with source hashes matching the correction.
[Full evidence and limits](../evidence/listener-update/README.md). One fresh attempt
per target is not a general solve-rate estimate; no challenge logic/payload review
was part of the infrastructure analysis. No further paid run is authorized.

## Actual listener version and startup diagnosis — November 14

The user approved diagnosing the process issue, preferring simple explanations
and fixes. The scope now explicitly includes service definitions, startup scripts
and executable paths/arguments needed to understand process handling; challenge
program logic, payloads, flags and solutions remain excluded. No paid run or
production service change is part of this diagnostic milestone.

Both exact historical images use socat 1.7.3.2 as PID 1, with `-T60`, a forking
TCP listener and `su` to a service user. The two saved effective Compose records
have null entrypoint/command overrides, so image defaults apply. Earlier generic
checks used socat 1.7.4.4 without the service-user switch.

**Hypothesis before new synthetic checks:** the actual old listener/version and
user-switch arrangement may handle child exits differently. Run only the installed
listener, replacing the challenge executable with a fixed harmless shell child.
Start with normal and signal exits; compare user switching, init or disconnect
timing only as needed. Record version, state, synthetic logs and cleanup; no
challenge executable is run. Helper: `tests/check_listener_image.py`.

**Completed:** both exact listeners reproduced exit 1 after the first synthetic
SIGSEGV; normal children survived 20 connections per image. Init, removing the user
switch and delaying the signal did not prevent the failure. The generic upstream
1.7.3.3 changelog describes the matching inherited diagnostic-channel bug; reviewed
1.7.4.4 source reinitializes that channel after fork. `EXEC ...,nofork` survived
20 synthetic crashes per image, but changes relay/I/O/timeout behavior and is not
adopted as a production correction. Six final helper cases behaved as predicted;
ten exploratory records retained. All diagnostic cleanup passed, syntax/whitespace
checks passed, zero model/real challenge runs or production changes.

The requested constraint review found no need to loosen controls for this failure:
plain Docker without our solver/guard also reproduces it. New-shell behavior,
whole-solver reset after timeouts, resource caps and emulation remain explicit
tradeoffs, not demonstrated causes. The earlier overly narrow diagnostic metadata
boundary was expanded with user approval. [Evidence, limits and next correction
options](../evidence/listener-version-diagnosis/README.md).

## Generic Docker/process investigation — November 11

The user authorized investigating the listener/process failure and possible
constraints introduced by our setup, explicitly excluding challenge logic,
binaries and payloads. No real challenge attempt or model request is authorized
by this diagnostic milestone.

**Hypothesis before synthetic checks:** an attached child failure may be handled
by its per-connection relay, while an orphan adopted by a PID-1 listener may be
handled differently and terminate the listener. Compare fixed trivial children
that exit normally, receive SIGSEGV while attached, or fork an orphan that later
receives SIGSEGV. Test Docker init as a separate variable. Inspect whitelisted
effective HostConfig/cgroup limits and compare a generic supplied Compose service
with the same service through our target launcher. Use only generic images and
new synthetic resources; always remove our containers/networks. No production
service/init/restart/security/model setting changes are part of this milestone.

The initial ten synthetic variants (native ARM64 and emulated AMD64, five each)
all survived five connections. The generic launcher/direct-Compose limit records
matched on both architectures. The orphan-child hypothesis is not reproduced.
Before a final positive control: deliberately remove only the generic listener's
`fork` option and compare signal-exit behavior with/without init. This tests whether
the observed signature uniquely identifies missing init; it is not a change to
any benchmark service or evidence of its supplied listener options.

**Completed result:** all ten forking-listener cases survived (50 successful
connections). Both one-connection controls exited code 1 and lost connectivity,
including with init. Without init the control produced the same `socat[1] E
waitpid()` message shape as the historical observation. This disproves uniqueness
of that signature, not a historical target configuration. Actual task startup
argument inspection was blocked by automatic approval review under the user's
challenge-exclusion boundary and remains unperformed. No added target quotas were
found; no production fix is justified yet. All diagnostic containers/networks and
temporary image tags were removed. [Audit, checks and limits](../evidence/docker-process-constraints/README.md).

## Passive target snapshot before cleanup — November 11

**Subsequent user-run diagnostic result:** `pwn-target-snapshots/batch-bebe62296ff3`
completed four attempts, all without verified success. All four final target states
were exited/code 1, no OOM flag and no restart. Passive lifecycle events in attempt
003 establish exit before a later connection failure, well before controller
removal. This supports the snapshot's diagnostic hypothesis, not a solving gain.
A filtered socat PID-1 child-exit message motivates a generic process-lifecycle
reproduction; it does not prove an init/emulation/listener defect or authorize a
target workaround. [Infrastructure-only review](../evidence/target-snapshot-batch-review/README.md).
No source/runtime change or new paid request was made while monitoring.

The user approved a small diagnostic change after service reachability failed
again in the first pwn rerun. The completed `pwn-service-recheck/batch-8c72ac67cab7`
contains four ordinary unsuccessful attempts (two each for roppity and baby-boi).
Only the first rerun trace has a detailed infrastructure review; do not infer an
identical cause for the other three from outcomes alone. Historical startup-only
state and removed containers leave the actual runtime cause unresolved.

**Hypothesis recorded before implementation/follow-up:** a whitelisted target
snapshot before teardown will distinguish exited/OOM-killed/restarting/missing
containers and changed network attachments from targets still running at the end.
It is end-state evidence, not proof of state at the instant a connection failed.
It diagnoses rather than repairs reachability. Snapshot collection must be bounded,
exclude environment/argv/health-log/target contents, preserve the original outcome
or exception, and never prevent cleanup. Genuine cleanup failures remain failures.

Reuse startup state extraction, include network names/IDs/IP addresses, record a
`before_cleanup` phase and sanitized error categories. Do not add a monitor,
active connection probe, target restart, dependency, agent tool or configuration
setting. Keep all current model/attempt limits and scope controls unchanged.
Verify healthy/exited/missing/error capture, privacy, exception/cleanup precedence
and real synthetic-container capture before removal. No paid challenge run is
launched by implementation; a fresh user-run development rerun remains subsequent.

Implementation complete: shared snapshot extraction and bounded best-effort
`before_cleanup` capture preserve target state in `target.json` and `run.json`.
Forty-nine focused offline cases passed. Initial synthetic Docker run: three
passed and one failed while resolving the local fixture image; that single case
passed on focused retry, for four distinct passing cases. Original failure and
retry remain recorded. Tests cover sanitized errors, shared time bound, exception/
cleanup precedence and real exited/missing/detached target records. No model call,
benchmark solving, target workaround, guard/scope change or new dependency.
[Evidence and limitations](https://github.com/ryanbanko/590_ctf_agent/blob/aedfd62cf8379adee73a30546592036af6f82a42/evidence/target-precleanup-snapshot/README.md).

## Original-artifact validation and reusable computation — November 11

### Subsequent service investigation — November 11

At the user's authorization, fixed model-free solver probes checked fresh roppity
and baby-boi services with unchanged historical target images. Both survived nine
ordinary connect/read/close/short-input exchanges. One generic roppity invalid-line
check produced a child signal-11 signature but left the listener reachable. That
check preceded the user's instruction to avoid challenge analysis; no further
stress probing or challenge-logic inspection followed. The diagnostic helper's
stress option was removed. The first diagnostic's Docker `top` formatting failure
was corrected and retained separately. All completed runs recorded clean teardown,
zero model calls/submissions and zero scope incidents.

The historical connection outage is not reproduced or explained. No production
runtime/target/image/guard/prompt change was made. The user prefers a small fresh
rerun instead of speculative fixes. [Filtered evidence and command](../evidence/service-lifecycle-investigation/README.md)
schedule two trials each for roppity and baby-boi under the current 90-second
request profile; no paid attempt was launched here. This checks repeatability,
not the effect of a service repair. Original failures remain intact.

### Subsequent 90-second request allowance — November 11

The user-run `validation-checkpoint/batch-983d82df4d2f` stopped after four of six
planned attempts. The first trial of each task succeeded (lupin 52.01 active
seconds, gibberish 406.04, x86 walk 41.11). The second lupin attempt ended on its
sixth model request: generation `c444907e2e2a0481` lasted 60.047 seconds and
recorded `Request timed out.`; event `69b69688cd4f69a2` records `APITimeoutError`.
The attempt had used 155.18 active seconds; captured generation input was about
76.6 KB, well below the 2 MiB cap. No scope incident or cleanup error was recorded.
The two remaining trials were not started. Original records remain unchanged.

The user approved raising the default request allowance from 60 to **90 seconds**.
Hypothesis before follow-up: modest additional waiting can accommodate occasional
slow requests without extending the **600-second attempt deadline**. Exact cause
(model generation, gateway queue or network stall) remains unknown. A stalled
request can waste an extra 30 seconds; the larger allowance does not prove this
historical request would have completed. No automatic retries are introduced.
Older named profiles and evidence snapshots remain unchanged. A separate
[90-second snapshot and follow-up command](../evidence/validation-checkpoint-prompt/README.md#90-second-request-follow-up)
preserve the changed condition; no live rerun is launched by this adjustment.

The user approved a small prompt change before further development testing.
Observed failures include circular checks based on incorrectly copied data,
late original-checker validation, exact-value transcription errors, and repeated
expensive computation after editing only a later stage. The current prompt already
contains broad validation/data-handling advice; this refinement makes the timing
and independence of checks more explicit rather than introducing a new tool.

**Hypothesis recorded before implementation/follow-up:** small original-artifact
checks before expensive search, exact-value rechecks after contradiction, and
saved intermediate results reduce work based on incorrect reconstructions and
repeated computation during recovery. Success may improve, but is not guaranteed;
extra validation can consume calls/time and stale checkpoints can propagate errors.
Instructions explicitly require recomputing results whose inputs/assumptions change.

Replace the working-method paragraph and add one intermediate-result sentence.
Keep Luna/medium/8,192, tools, scope, stopping behavior and existing limits fixed,
including the separately approved **2 MiB** default input cap. No planner, notes
system, submission-interface change, automatic checkpoint subsystem, service
investigation or target reset is included. The service investigation requires the
user's separate go-ahead. Verify prompt propagation, public-history/recovery and
native replay through focused existing local tests, without model/container calls.

A subsequent user-run targeted pilot can repeat `cry-lupin`,
`rev-gibberish-check`, and `rev-a-walk-through-x86-part-2` twice, preserving
failures, settings and provenance. Assess original-checker use before search,
exact-value checking after rejection, checkpoint reuse, calls/time/tokens and
verified success. The historical batch used 512 KiB, so a historical comparison
tests the combined prompt/headroom changes, not prompt causality. A clean prompt
comparison needs both versions at the same 2 MiB allowance and fresh conditions.
No live run is launched by this implementation milestone.

Implementation completed: the agreed paragraph replacement and intermediate-result
sentence are applied. Five existing focused offline cases passed (0.40 seconds),
covering prompt/public-history propagation, recovery, verified stopping and native
replay. No new tests, model/container calls, target investigation or unrelated
runtime change. [Exact prompt snapshots, settings, hashes and test evidence](../evidence/validation-checkpoint-prompt/README.md).
The follow-up command is prepared for the user; no behavioral result is claimed.

## Previously unattempted development capability test — planned November 11

### Subsequent default input-cap increase — November 11

The user approved increasing the local serialized-request cap from 512 KiB to
2 MiB, retaining Luna and deferring compaction. Before any new comparison, the
hypothesis is that additional request headroom prevents premature local input-limit
stops for otherwise supported histories. The largest recorded native input across
620 available generation observations was 112,068 tokens; the failed gibberish
attempt's reconstructed next request was about 536,570 serialized bytes. This is
an application byte guard, not the model's token context window.

Only `configs/development.toml` changes behavior. Explicit historical/comparison
profiles and saved batch snapshots retain their recorded caps. More headroom
permits longer replay and possible higher usage; it neither forces that usage nor
establishes better solving. Current configuration loading and unchanged other
settings are checked locally; no live/model/container call or behavioral comparison
is performed. Service diagnostics, validation/tool changes, notes and model
experiments remain separate decisions.

**Subsequent result/review:** `batch-8c98b0fc7e14` reached 20 scheduled attempts;
14 succeeded, five completed unsuccessfully and the final response-source failure
stopped the batch. [Detailed read-only review](../evidence/unseen-development-trace-review/README.md)
and [filtered inventory](../evidence/unseen-development-trace-review/review.json)
cover all six unsuccessful attempts plus four matched successes. The primary
findings are exact-data/validation mistakes, cumulative input growth, repeated
roppity endpoint unavailability of unknown cause, and an Android source failure
with incomplete telemetry. No fix or comparison was run; options in the report
are hypotheses for a future approved milestone. Unlike task sets and mixed/random
outcomes do not establish an improvement over earlier pilots. The pre-run plan
below remains historical.

The user requested up to three different unattempted challenges per category,
using the hardest supported development entries available and two trials each.
The [recorded plan](../evidence/ryan-shared-runs/unseen-development-three-per-category/README.md)
selects nine Hard challenges across crypto/pwn/reversing plus Easy
`msc-android-dropper`. No unattempted development web/forensics entries remain;
the other misc entry, `msc-showdown`, has an unsupported setup and is excluded.
The same medium/8,192 configuration is saved before execution; the agent and
held-out selection are unchanged. This tests capability on new development tasks,
not a controlled agent-change effect. Twenty attempts are planned, not completed.
The guide specifies existing logging and the reviewed Git-publication step so
teammates can inspect eventual results. No new model call was made in preparation.

## Shared development records for teammates — November 8

[Ryan's shared runs](../evidence/ryan-shared-runs/README.md) provides sanitized
offline copies of all 65 existing pilot attempts, including failures and scope
stops, plus a chronological guide and per-attempt index. Use it to locate evidence
for the hypotheses below without depending on another teammate's local `runs/`.
Read its export-gap, redaction and cost notes before drawing trace conclusions.
The latest medium/8,192 two-trial batch completed with 20/22 successes and no
scope recoveries; it does not demonstrate live recovery or establish a causal
gain. This handoff changes no runtime/configuration and makes no new model call.
Development pilots remain separate from the reserved scored evaluation.

## Current scope after course clarification — November 6

The [professor confirmed](REFERENCES.md#november-6-course-guide-and-professor-confirmations)
our repository Compose/private verification, Langfuse JSON exports and CTFTiny
split. Existing development records and held-out IDs remain valid; no data
migration or JSONL logging experiment is necessary. Prior observations and failed
attempts stay unchanged.

The new guide describes one fixed configuration with three trials per selected
challenge, per-challenge success/sample-SD/token/time summaries, and a demo that
need not solve. It requires trace-supported improvements/small follow-ups without
a second full evaluation. These are guide statements, not additional approvals
in the three-answer email. Earlier paired-comparison plans below are historical
research options, not a mandatory second benchmark campaign under that guide.
No new performance measurement, model request or report work has run.

The next infrastructure checkpoint is the bounded independent solver-image
comparison. Then refresh intended-environment readiness and run a separately
authorized small live pilot. SDK tracing/export and batch workflow remain.

## Experiment 1 — evidence use and recovery prompt

Date: November 4, 2026 (America/New_York).
Status: **Five user-run trials reviewed; one exploratory before/after pair available.
Repeated comparison remains pending.**

### Observed problem

The three reviewed development attempts ended with `completed_without_success`,
no flag submissions, and remaining configured limits. Earlier trace reviews found:

| Development run | Trace ID | Relevant behavior |
| --- | --- | --- |
| `challenge-ab3134582f2c` (`cry-ecxor`) | `91e0d0104daffe89fdefb9f463313fe0` | Contradictory observations did not lead to a sufficiently revised approach; a later Python error was followed by a final response. |
| `challenge-c6f12d005a7b` (`msc-algebra`) | `7c44e4b3e31f2ecabb82363586d35514` | Scripts discarded service output; the model claimed progress without explicit supporting service responses and ended without a submission. This does not establish that a flag was received. |
| `challenge-3dd76ec6c9cb` (`rev-tablez`) | `6a21114e268007b68926e06b24f63984` | Missing utilities and execution failures obstructed work; the attempt later ended after another script error. Environment fixes are documented separately. |

Local records are under `runs/challenges/<run>/`; `runs/` is Git-ignored and is
not distributed by cloning this repository. Trace IDs identify the hosted records
for teammates with project access. Preserve/export the relevant tool observations
and following model actions for the final report; this summary is not a raw trace.

### Hypothesis and change

Hypothesis, recorded before the live comparison: explicit guidance to distinguish
assumptions from observations, check corrections, preserve diagnostic/completion
output, and investigate a blocker before stopping will reduce avoidable early
exits after recoverable errors and unsupported progress claims. It may increase
calls, time and cost; higher solve rate is not assumed.

The approved [system prompt](../ctf_agent/agent.py) replaces the vague recovery
instruction with those behaviors. It also accurately describes `/workspace` as
the starting directory. It preserves scope restrictions, one brief visible tool
purpose sentence, and evaluator-confirmed success. Tools, loop, limits, model,
reasoning effort, images and dependencies are unchanged by this prompt milestone.
Enforced command timeouts and other terminal stops still end the attempt.
Before live testing, the user refined the visible explanation to ask for the
action's purpose or what it will test, rather than requiring an expected result.
This keeps action explanations visible without requiring predictions that could
reinforce an unsupported assumption. The explanation remains assistant text
alongside the tool call, not an additional tool argument.

Baseline code: commit `0c7b41c94f98c427e2c06feae40acdef74609343`.
Baseline prompt SHA-256 (UTF-8):
`28234e2dd1b78bdeeb932e1cbd9759730fc10cb48143f462c7c8632981953c81`.
Initial candidate SHA-256 (before the purpose-only refinement):
`09321d02dd4f93f3e0b4d87c0410b211ca096f7e904878bf2155d384f01626cb`.
Current candidate prompt SHA-256 (UTF-8, after stripping outer whitespace):
`cea149f0c9a0d532d3e5627fcd154897503ff09f059a4bef9f2d68b3339a473d`.
Record the candidate commit with the comparison runs before interpreting results.
Git history preserves the exact earlier prompt.

### Verification and comparison plan

**45 existing offline tests passed for the initial candidate**
([JUnit evidence](../evidence/prompt-recovery/pytest.xml)):

```sh
uv run --frozen python -m pytest tests/test_agent.py tests/test_contracts.py tests/test_model.py -q --disable-plugin-autoload
```

After the purpose-only wording refinement, both existing prompt propagation and
tracing cases passed ([2-test evidence](../evidence/prompt-recovery/purpose-only.xml)):

```sh
uv run --frozen python -m pytest tests/test_agent.py -k observations_drive_recovery -q --disable-plugin-autoload
```

These tests check that the active prompt reaches the public history
and tracing, that scripted recovery can continue, and that verification and
stopping controls remain intact. They do not establish how a live model responds
to the new wording. Docker operations and model HTTP transports are substituted;
no live calls were made. No new tests or runtime components were added.

For a small, separately authorized live comparison:

1. Choose the same development challenge IDs and equal trial counts for both
   prompts; keep the ten reserved IDs untouched. Agree on the batch size within
   the existing spending/request allowance before starting.
2. Use the updated solver environment for both prompts. Hold dataset revision,
   actual image IDs, model and all settings fixed, including
   [development.toml](../configs/development.toml). Do not rebuild images between
   conditions. Record commits, settings and image IDs from each run's provenance.
   The older three runs diagnose failures but are not a fair baseline: their
   solver environment differed.
3. Start each attempt fresh. Review recoverable error → next action, repeated
   actions without new evidence, preserved service/completion output, support for
   progress claims, and the reason for stopping. A justified decision to stop
   is not automatically a failure of recovery.
4. Record verified success/submissions, scope incidents, termination reason,
   model/tool calls, time, available tokens and estimated cost for every attempt.
   Keep failures and note the uncertainty of a small stochastic sample.

### Review of user-run trials after the change

Reviewed November 4, 2026. All five trials used the current candidate prompt
(hash above), identical application source hashes, model/settings and dataset
revision, and the updated AMD64 solver image. They were development trials.
The saved generations confirm the actual prompt; the shared Git commit alone
would be insufficient because these runs used uncommitted prompt changes.

| Challenge | Run | Outcome | Model/tool calls | Active seconds | Estimated USD |
| --- | --- | --- | --- | --- | --- |
| `cry-ecxor` | `challenge-bc5088f47d97` | Completed without success | 7 / 6 | 35.07 | 0.00308961 |
| `msc-algebra` | `challenge-97b399febefe` | Verified success | 11 / 11 | 58.00 | 0.00358691 |
| `pwn-baby-boi` | `challenge-04065b43cd41` | Command timeout | 5 / 5 | 55.80 | 0.00120823 |
| `rev-checker` | `challenge-60018c066690` | Verified success | 4 / 4 | 18.26 | 0.00088861 |
| `web-poem-collection` | `challenge-2feddbeaee2d` | Verified success | 5 / 5 | 14.07 | 0.00067602 |

Total: **3/5 verified successes**, 32 model calls, 31 tool calls, 181.20 active
seconds, 172,727 input tokens (131,498 cached), 8,023 output tokens (2,512 reasoning),
and **$0.00944938 estimated model cost**. Active time excludes cleanup/export and
is not total experiment elapsed time. No recorded scope-denial events or cleanup
errors; all five exports passed the launcher's completeness checks. This is a
small selected development sample, not a scored benchmark estimate.

Turn numbers below refer to chronological model generations in each saved export.
The corresponding tool observation follows that generation.

| Evidence | Observation and implication |
| --- | --- |
| `cry-ecxor`, turns 2–5 | The model fixed an import-path error, but appended new logic after an earlier failing statement, repeating the same exception before removing it. Recovery exists but script edits are fragile. |
| `cry-ecxor`, turns 6–7 | After another diagnostic succeeded, the model ended with an explanation of its blocker. Only 7/20 model calls and about 35/300 active seconds were used. Its explanation favors one unverified assumption; alternative explanations were not exhausted. Remaining budget alone does not prove another action would succeed. |
| `msc-algebra`, turns 3–5 | An answer from a previous connection was reused on a fresh session, then corrected. `sympy` was missing; the model switched to a dependency-free approach. Each command starts a new process; network session state does not automatically persist. |
| `msc-algebra`, turns 6–9 | Verbose output exceeded 16 KiB; a failing command returned no retained stderr. Later edits introduced a `NameError`, which the model corrected. The worker's shared first-bytes budget can consume all space before a traceback arrives. |
| `msc-algebra`, turns 9–11 | A loop dropped buffered output at EOF. The model noticed completion output was missing, fixed the EOF logging, reran, obtained a candidate and submitted it successfully. This is useful observed recovery; the earlier run did not itself prove the candidate had been received. |
| `pwn-baby-boi`, turns 2–5 | `pwn` was missing; ELF utilities provided a fallback. The later script used blocking connection/line-read/receive calls without a local timeout. Turn 5 reached the 30-second command limit with no output and the controller ended the whole attempt. The export cannot locate which blocking operation stalled or establish that a longer limit would help. A claimed runtime-library discrepancy remains unverified. |
| `rev-checker`, turns 2–4 | The model identified a mistake in its transformation, corrected it and submitted a verified candidate. |
| `web-poem-collection`, turns 3–5 | The model adjusted after a failed request, obtained a candidate through the assigned endpoint and submitted it successfully. |

Visible explanations accompanied **29/31 tool-calling generations**. The two
omissions were successful submission turns, not missing command explanations;
there is little reason to add format enforcement for that now.

### Exploratory matched pair

`challenge-7ec6c0a359e0` used the original prompt on `cry-ecxor` with the updated
solver. Comparing its provenance with `challenge-bc5088f47d97` confirms the same
dataset, contestant files, image IDs and settings; only `ctf_agent/agent.py`
differs among recorded source hashes. Its traced prompt matches the baseline hash.

| Prompt | Model/tool calls | Active seconds | Estimated USD | Result |
| --- | --- | --- | --- | --- |
| Original | 5 / 4 | 39.44 | 0.00156165 | No success; the same earlier exception prevented later appended diagnostics from executing across four calls. |
| Revised | 7 / 6 | 35.07 | 0.00308961 | No success; recovered from more script errors and ran a later diagnostic, but still stopped. |

This is one sequential, stochastic pair. It supports a behavioral observation,
not a reliable effect size or improved solve rate. The other four tasks have no
matched baseline with this solver. Older environment failures remain useful
diagnoses, not fair prompt-only controls.

### Potential next changes — not implemented

1. **Network deadlines:** first test short internal I/O deadlines and stage-specific
   diagnostics, below the outer command limit. A longer global timeout would not
   address an indefinite read. Keep terminal timeout handling for now; allowing
   continuation requires verified cleanup of all descendants, including detached
   children, while preserving wall/scope stops.
2. **Output visibility:** the observed oversized outputs were about 17 KiB. A
   32 KiB development output cap is a simple configuration-only experiment that
   would fit those outputs. Alternatively, reserve bounded stderr/tail space in
   the worker; that needs code and meaningful checks. Do not implement both at
   once. Neither change fixes output discarded by the script itself, such as an
   unprinted EOF buffer.
3. **Existing libraries:** consider pinned solver-only `pwntools` because the
   missing import recurs. `sympy` is optional: the observed fallback succeeded.
   Verify Python 3.13 compatibility before adding dependencies; avoid a large
   toolkit expansion based on guessed future needs.
4. **Recovery quality:** monitor unsupported conclusions, append-after-failure
   edits and stale connection state. Prefer a complete replacement of a short
   broken script and a focused check. The current prompt already asks for
   recovery; another broad persistence paragraph is not yet justified. A later
   reasoning-effort comparison would be a separate variable.

[Machine-readable review and trace links](../evidence/prompt-recovery/trial-review.json).
This review ran no commands in challenge containers and made no new model calls
or paid requests. Runtime code/settings remain unchanged. Further comparisons,
pilot completion and scored evaluation remain unfinished.

The design follows the assignment's evidence → hypothesis → comparison sequence,
[OpenAI guidance on clear reasoning-model prompts](https://developers.openai.com/api/docs/guides/reasoning-best-practices),
and its [agent persistence/stop-condition guidance](https://developers.openai.com/cookbook/examples/gpt-5/gpt-5_prompting_guide).
Ryan Banko approved the wording, with AI assistance from another model and OpenAI
Codex during review, implementation and documentation.

## Toolkit review — original proposal

This subsection preserves the review before approval. The six-library selection
and implementation are recorded in Experiment 2 below; reedsolo was excluded.

November 4, 2026. Public index counts: 16 reverse engineering, 11 pwn, 12 crypto,
6 miscellaneous, 3 web and 2 forensics challenges. Existing file-format evidence
includes 20 x86-64 and two x86 ELF files, three Sage files, two PNGs, an APK and
a `.pt` artifact. Extensions suggest tooling needs; they do not prove a particular
package or solution is required.

A static import scan of listed **development** Python/Sage handouts found `Crypto`,
`numpy`, `reedsolo` and `sympy`. Other unresolved names, including `rsa_values`
and `sha256`, need provenance checks; they are not automatically public packages.
Listed local modules such as `rfc8032` should remain handout imports. No supplied
code was executed and no held-out solution or flag was consulted.

| Priority | Proposed solver additions | Evidence or rationale |
| --- | --- | --- |
| First | `pwntools`, `sympy`, `pycryptodome`, `numpy`, `reedsolo` | Observed missing imports or named development-handout dependencies. Pwntools also reuses established process/ELF/connection utilities. |
| Small general additions to consider | `Pillow`, `requests` | Image files and HTTP services are present. These are convenience/coverage proposals, not observed missing-import failures. |
| Specialized coverage when selected | SageMath; JADX/APKTool plus Java; CPU PyTorch | Sage, Android and likely ML artifacts exist. Verify actual format, Python/runtime compatibility and resource fit before adding these larger stacks. |
| Defer unless evidence warrants | Ghidra/angr, extra scanners, packet-analysis suites, additional compiler targets | No current trace establishes these as the next blocker. Existing binutils/GCC/GDB/curl/archive tools already cover basic workflows. Live GDB still has the documented Apple Silicon limitation. |

NYU's [reference image](https://github.com/NYU-LLM-CTF/nyuctf_agents/blob/main/docker/baseline/Dockerfile)
preinstalls a broad toolkit, including pwntools and Sage; it is a reference, not
a requirement to copy its full image or permissions. Relevant package references:
[pwntools](https://docs.pwntools.com/en/stable/install.html),
[SymPy](https://docs.sympy.org/latest/install.html),
[PyCryptodome's Crypto namespace](https://www.pycryptodome.org/src/installation),
[NumPy](https://numpy.org/install/), [reedsolo](https://pypi.org/project/reedsolo/).

Recommendation: evaluate the five existing traces first, then make a small,
separately approved solver-image change using pinned packages. Verify benign
imports/workflows under the actual Python 3.13, non-root, read-only-root and
network/resource constraints before further paid trials. Keep subsequent prompt
comparisons on identical images; do not attribute library/environment changes to
the prompt. No new runtime tools or package-manager service is needed.

Downloads from assigned challenge endpoints remain allowed. General package
registry/internet access during attempts would exceed the assignment's endpoint
restriction. Fetch dependencies during trusted image builds, then run with the
existing guard. A preloaded offline package cache is technically possible but
adds installation/state management that this project does not currently need.

## Experiment 2 — solver libraries, output visibility and network guidance

Date: November 4, 2026 (America/New_York).
Approved scope: install pwntools, SymPy, NumPy, PyCryptodome, requests and Pillow;
exclude reedsolo; raise live output to 32 KiB; clarify internal I/O deadlines and
connection lifetime. No live model comparison was authorized in this milestone.

Hypothesis before the next live comparison: supplying established libraries will
avoid the observed missing-import detours; 32 KiB will retain the roughly 17 KiB
outputs observed in the previous trials; clearer command guidance may reduce
unbounded network reads and stale-session assumptions. This is a bundled setup
change, so a later comparison cannot attribute an effect to one component alone.
The existing recovery system prompt is unchanged.

Direct solver versions are pwntools 4.15.0, SymPy 1.14.0, NumPy 2.5.4,
PyCryptodome 4.3.0, requests 2.34.2 and Pillow 13.0.0. The standard requirements
input and resolved file pin 40 packages including transitive dependencies.
Host Python dependencies are unchanged. Downloads occur during image builds;
the attempt's endpoint-only network guard remains enforced.

The live profile sets `max_output_bytes = 32768`. The command description asks
for connection/read deadlines below the outer command limit and explains that
files persist but network connections do not automatically persist between calls.
These are model instructions, not automatic socket rewriting or a session tool.

**Timeout decision: retain 30 seconds per live command.** The observed failure
used blocking operations without a local deadline. It did not show a computation
needing a longer allowance. The new library/workflow probe completed under that
cap; larger computations can justify a separate `command_seconds` experiment.
The attempt wall limit remains 300 seconds, and command timeout remains terminal.

Benign verification checks actual library workflows inside the constrained solver,
an intentionally stalled permitted socket read with its own deadline, retention
of a 17 KiB output plus stderr, and truncation above the 32 KiB bound. A local read
timeout can return while the attempt remains active; this does not establish that
the model will follow the new guidance. The output collector still keeps the
first bounded bytes, so it does not guarantee preservation of every late error.

[Verification, build and reproduction evidence](../evidence/solver-libraries/README.md).
Verification passed: 64 fast tests, 23 synthetic controls on the installed-library
image, and four focused final-image checks after disabling unnecessary pwntools
terminal setup. The final library/workflow command took about 1.35 seconds and
the intentionally stalled read returned in about 0.22 seconds, comfortably below
the 30-second command cap. These small probes do not bound arbitrary workloads.
No real challenge was solved or model API called during this milestone. Before
another comparison, record this new image/configuration and use it consistently
across both conditions. Prior results remain historical evidence.

## Batch execution support

`run-batch` now invokes the existing single-challenge launcher sequentially for
explicit IDs and trial counts. A copied experiment file and small `batch.json`
index keep each attempt discoverable through its existing run ID, verdict, trace
link and original record. Metrics remain in the individual records. The wrapper
does not change solver/model behavior and adds no batch-budget gate, automatic
retry, parallel execution or resumption feature.

The user prefers two different development challenges per category for breadth.
Only one development forensics challenge exists, so this yields eleven IDs.
Repeating a selected challenge is a separate choice through `--trials`; breadth
and repetition measure different things. The user subsequently selected and
prepared eleven IDs; the pilot started but stopped as recorded below. The existing
account/per-attempt limits and usage records remain;
the user requested no additional batch-cost management.

[Offline verification](https://github.com/ryanbanko/590_ctf_agent/blob/aedfd62cf8379adee73a30546592036af6f82a42/evidence/batch-wrapper/README.md): 17 batch cases and
81 fast tests passed. Child outcomes were simulated to test orchestration and
record handling without paid model calls. No new benchmark results are claimed.
The record audit found the required IDs and evidence already available; demo work
was deferred. At that milestone the next step was to review the wrapper, choose
development IDs, then inspect a pilot before expanding evaluation. The later
package-policy and usability sections record subsequent work; PROJECT_STATUS
tracks the current next step.

## Temporary runtime package-index default

November 4, 2026. Batch `batch-be87c5be7ce7` stopped on its first model request
with `APITimeoutError`; the user addressed gateway access. That setup failure was
later moved intact to `runs/archive/batch-be87c5be7ce7` to keep the active pilot
folder tidy; all seven files and their contents were preserved. All eleven preparation
checks passed. The next batch, `batch-8898df326849`, completed two attempts
(`cry-ecxor`: unsuccessful; `cry-describeme`: verified success) and stopped on
`for-1black0white`. Trace `c9c2d54214afdba7520255fbdfaeb213`, generation 5, ran
`python3 -m pip install --quiet opencv-python-headless` after finding no QR decoder.
The guard recorded DNS queries for `pypi.org`, stopped the solver and preserved
complete records with successful cleanup. This was a dependency-install request.

Approved temporary change: default runtime pip to `PIP_NO_INDEX=1` and disable
its version check; state in the command description that downloads are unavailable.
The ENV line is after build-time installs and is explicitly marked for reversal.
The system prompt, installed libraries, firewall and batch stop policy are unchanged.

Hypothesis before any further live trial: an ordinary missing-package install
will fail locally and become a recoverable tool observation instead of triggering
a scope stop. The model may then use existing capabilities or end unsuccessfully.
This does not guarantee every attempted download fails softly: direct URLs,
other download commands or overrides remain subject to the network guard.
No decoder was added, and no new real challenge/model attempt ran during this fix.

[Verification and reversal instructions](https://github.com/ryanbanko/590_ctf_agent/blob/aedfd62cf8379adee73a30546592036af6f82a42/evidence/runtime-package-policy/README.md).
Verification: 81 fast tests and 24 synthetic Docker controls passed. A missing
package request failed locally in about 0.42 seconds and a following command ran
successfully in the same attempt. The new solver image is built locally. No live
trial of the revised behavior has been made.


## Experiment 3 — usable sessions, package installation and recovery

Approved November 4, 2026, before any new live comparison. Prior traces showed a
missing dependency leading to a scope stop, blocking reads ending an entire
attempt, and connections mistakenly treated as persistent between commands.
Small workspace/home constraints and beginning-only output capture were additional
implementation limitations. GDB changes are excluded at the user's request.

Hypothesis: writable Python/home/temp storage and permitted pip access let the
agent obtain dependencies; terminal sessions preserve program interactions;
confirmed descendant cleanup lets it recover from command timeouts; beginning/end
excerpts and output files retain useful diagnostics. Expanded time/call/token
allowances reduce premature stops. This bundles environment and tool changes; a
later comparison cannot attribute an effect to any one component alone.

Keep the model and reasoning effort unchanged. The live profile uses 600 seconds,
120-second ordinary commands, 60-second requests, forty model responses, eighty
tool calls, 512 KiB model input and 4,096 output tokens. The local spending cap
and reservation code are removed; usage/cost estimates remain. Output is 64 KiB
with up to 1 MiB retained per command/session. Package additions reset each attempt
and installed versions are recorded. Public HTTPS is technically available to
commands generally; the prompt limits its purpose to pip, not answer lookup.

Verification uses synthetic commands and benign package installation only. It
establishes tool behavior, isolation and cleanup, not improved benchmark success.
The prior offline package milestone and old trial records remain historical.
Current verification and reproducibility evidence: [agent usability](../evidence/agent-usability/README.md).
After handoff, review before authorizing another development pilot.


Environment verification completed: **82 fast tests, 27 distinct Docker cases**
across the main run and focused completion, and two zero-model preparation cycles
for `pwn-baby-boi`. Cleanup passed. Historical startup-deadline and absent-network
cleanup failures remain in the evidence; the corrected behavior passed. The
benign package installation/import command took approximately 1.66 seconds in
the main run. No model calls or challenge-solving attempts ran, so no solve-rate
or model-behavior improvement is claimed. Stop for review before a live pilot.


## Reliability follow-up — worker lifecycle, usage and preparation

Approved November 4, 2026 after a static review of Experiment 3's implementation.
The immediate scope is worker cleanup, terminal I/O, missing usage metadata,
consistent preparation settings and documentation. SDK export replacement,
context management, broader default consolidation and GDB were deferred at that
milestone; the following cleanup completes configuration and export work.

Hypothesis before another live trial: guaranteed supervisor cleanup, final-output
draining, explicit partial-input counts and automatic reaping prevent avoidable
session failures. Missing usage should leave totals unknown rather than discard
a valid model reply. Preparation should test the selected experiment's actual
attempt settings, free workspace and remaining staging deadline. These changes
preserve the model, numeric live profile, three tools and existing isolation.

Verification uses synthetic processes, offline model transports and zero-model
preparation only; it does not measure solve-rate improvement. Historical evidence
remains unchanged. Results are recorded in
[reliability evidence](https://github.com/ryanbanko/590_ctf_agent/blob/aedfd62cf8379adee73a30546592036af6f82a42/evidence/agent-reliability/README.md): **91 fast tests,
31 Docker cases in one complete run and two zero-model preparation cycles passed**.
Preparation settings match the selected live experiment and cleanup passed. Stop for review
before a new live pilot or scored evaluation.


## Maintenance cleanup — configuration, trace export and package snapshots

Approved November 5, 2026. Normal model/run values now live in one complete
`configs/development.toml`, with one model-call setting. The loader validates
without merging hidden defaults; the previous resolved live settings are unchanged.
The installed Langfuse SDK replaces the app's CLI subprocess and retrieves all
cursor pages while preserving completeness/privacy audits. Package inventories
are still scanned; identical inventories no longer rewrite `packages.json`.

This reduces maintenance and redundant writes; it is not a performance hypothesis
or a benchmark comparison. Checks and hosted readback use substitutes and an
existing synthetic trace, with no new model requests. See
[evidence](https://github.com/ryanbanko/590_ctf_agent/blob/aedfd62cf8379adee73a30546592036af6f82a42/evidence/config-sdk-cleanup/README.md): 95 fast tests, 31 synthetic
Docker cases with cleanup verified, and matching readback of the existing ten-row
synthetic trace passed. Context management remains
a possible later hypothesis. GDB and output-copy optimization remain deferred.

## Historical November 5 infrastructure proposal — since implemented in checkpoints 1–2

The November 5 source review led to a
[consolidated implementation proposal](https://github.com/ryanbanko/590_ctf_agent/blob/aedfd62cf8379adee73a30546592036af6f82a42/docs/SIMPLIFICATION_PLAN.md). It retains our
agent, three tools, prompt strategy, model integration, Langfuse and batch wrapper.
It proposes a writable disposable solver, standard Docker copy/exec, one-shot
file writing, bounded head/tail output and narrower target configuration changes.
Image selection is an independent build/evaluation decision.

Hypotheses to record before implementation or live comparison:

- Removing the restrictive filesystem and its staging/startup workarounds can
  preserve required boundaries with fewer runtime mechanisms.
- Restarting the same writable solver on a command timeout can eliminate command
  supervisors while allowing the agent to continue with its files/installations.
  Running processes and connections are lost; the attempt ID, limits and target
  state do not reset. Deadline/scope/guard failures remain terminal.
- Preserving supplied target behavior, with justified socket exceptions, can
  reduce compatibility problems introduced by blanket overrides.

At the proposal date these hypotheses were not verified behavior or measured
performance improvements. The supplied image was not built and restart recovery
was not prototyped. The then-current 95/31 checks covered the worker implementation.
The checkpoint results below supersede its implementation status; no solve-rate
improvement is inferred from their synthetic checks. Source and
read-only Compose configuration inspection found 17 actual socket mounts among
27 supplied definitions; previous successful runs show socket omission worked
for `cry-describeme` and `web-poem-collection`, not that every mount is unnecessary.

First verify the replacement with synthetic/offline checks and zero-solving
preparation. Keep unrelated message handling, stopping-policy, context and GDB
changes separate. Any later live pilot or comparison needs its own authorization;
preserve the old configuration, failed attempts and historical evidence.


## Infrastructure checkpoint 1 — ordinary execution and restart recovery

Approved after the consolidated review; completed November 6. Baseline is Git
`64f6385`; settings/source/image identities are preserved in
[execution evidence](../evidence/execution-simplification/README.md). The agent,
prompt, model profile, SDK export and batch workflow are unchanged. Standard Docker
copy/exec/init/restart and ordinary writable storage replace worker/session/
supervisor/archive/artifact mechanisms. Small custom wrappers retain bounded
output, structured writing, restart coordination and initial inventory.

Hypothesis: removing connected runtime mechanisms can retain required isolation,
trusted verification, scope incidents, limits, fresh trials and useful records
with less code to maintain. Infrastructure verification passed: 93 offline tests,
28 synthetic Docker cases and two fresh development preparation cycles. No live
model, solving attempt, hosted trace or performance comparison ran. This establishes
the tested control behavior, not an improvement in solve rate.

Losses are explicit: no model-directed cross-call terminal interaction, no portable
workspace quota, no automatic omitted-output artifact and no preservation of
unrelated solver processes/connections after timeout. Files/pip installs survive;
the same run/counters/deadline continue; targets and guard are not reset. A single
CHOWN capability ceiling supports trusted copying without giving model commands
effective capabilities. Supplied-target/network changes and independent image
selection remain later checkpoints; review before another live pilot.


## Infrastructure checkpoint 2 — supplied target behavior and ordinary networking

Approved after execution review; completed November 6. Hypothesis: preserving
supplied service semantics and using standard Compose project networking can
remove unnecessary overrides/topology management while retaining solver scope,
private verification, fresh trials and records. The existing nftables/NFLOG guard
is retained; it joins the challenge-facing bridge directly. Standard Docker DNS
retains supplied hostnames, and normal bridge NAT supplies package connectivity.

[Evidence](https://github.com/ryanbanko/590_ctf_agent/blob/aedfd62cf8379adee73a30546592036af6f82a42/evidence/target-network-simplification/README.md): 100 offline tests,
29 synthetic Docker cases and two fresh preparation cycles each for development
`pwn-baby-boi`, `web-shreeramquest` and `cry-ecxor`. Multi-service DNS, backend scope
and fresh named-volume state passed. Read-only host binds have offline coverage
only; Docker Desktop rejected runtime mounts. Inventory accepts 26/27 Compose
setups; privileged `msc-showdown` remains unsupported. Socket removals are explicit
exceptions; full challenge functionality is not established by startup checks.

Targets now inherit supplied/default capabilities/resource settings and normal
network connectivity. Solver limits, guard denial/incident stopping and evaluator
separation remain. Runtime Python decreases another 14 lines; the substantive
simplification is removing mechanisms and assumptions. No live model call, solving,
new hosted trace or solve-rate comparison ran. The independent image decision and
any later live pilot remain separate stages.


## Live synthetic smoke check after simplification — November 6

Approved to check the remaining real-provider/native-tool/solver/evaluator/hosted-
export path before changing the solver image. The user connected the VPN first.
Existing `model-check` ran on clean commit `00e6a41` with its established synthetic
bounds (four requests maximum, retries disabled); no normal profile changed.

Passed: two model calls/two tools, JSON retrieval through `run_command`, observed
candidate submission through `submit_flag`, trusted success, 12 complete hosted
observations and clean cleanup. Usage was 1,585 input/191 output tokens including
7 reasoning; estimated cost $0.000254 matched hosted totals. Active time was
5.72 seconds; complete check/readback 22.25 seconds. Initial model input and root
excluded the answer; credential audit passed.
[Evidence](https://github.com/ryanbanko/590_ctf_agent/blob/aedfd62cf8379adee73a30546592036af6f82a42/evidence/live-simplification-smoke/README.md).

This is live synthetic setup evidence, not a CTFTiny solve, scored trial,
performance comparison, or live verification of file writing/restarts. Existing
control evidence remains. No source/image/prompt/dependency changes were needed;
image evaluation and broader pilots remain separate checkpoints.

## Infrastructure checkpoint 3 — bounded supplied-image evaluation

November 7 follow-up: the host-reserve cancellation did not establish image
unsuitability; the comparison is reopened. Docker had ample virtual capacity.
Authorized removal of the unrelated fMRIPrep image increased actual Mac free
space from 24.29 to 34.46 GiB. An 8 GiB Docker RAM allocation is recommended,
not applied. No new build/model call or candidate compatibility result.

November 6, 2026. Evaluate whether the supplied NYU baseline reduces remaining
toolkit/environment maintenance; no change to the agent hypothesis or prompt.
Pinned release `20250206` was built unchanged under a separate AMD64/UID-1000
tag. After disconnecting the VPN resolved the observed registry EOF errors,
Ubuntu/tool/Python installation steps completed. The external installer was
canceled at the evaluation's 10 GiB host-free-space boundary after 567.92 seconds.
No completed candidate exists, so its runtime compatibility remains untested.

Retain our working image: no lower-maintenance replacement has been established.
Its identity and RootFS are unchanged; a preservation tag and checksummed local
archive freeze the current artifact. Eleven focused existing Docker controls
passed on that image. Scoped cleanup reclaimed only the evaluation's 19 cache
records (6.742 GB). No runtime/test/dependency/configuration change or new subsystem;
no model call, real challenge attempt, agent-effect comparison or candidate
performance claim. A local storage cancellation does not establish an upstream
source defect. [Evidence and unresolved checks](https://github.com/ryanbanko/590_ctf_agent/blob/aedfd62cf8379adee73a30546592036af6f82a42/evidence/nyu-solver-image-evaluation/README.md).

## Infrastructure image retry — successful November 7

The unchanged pinned NYU release built with effective 8 GiB Docker memory in
17m 17s, without hitting the host reserve; minimum continuously recorded host
space was about 25.2 GiB. VM memory samples showed ample availability and unused
VM swap. RAM was a starting allocation, not a suitability criterion; cleanup,
network/download differences and the different build outcome prevent attributing
success to RAM alone.

The eight-line child supplies `/workspace`, output environment settings and
missing NumPy/Pillow. Its build/pip check passed. All 29 existing compatibility/
control cases plus five additional sudo/SageMath/radare2/angr/multilib cases
passed under unchanged solver limits. The two portable offline wheel/home tests
also passed on the current image. No new runtime subsystem or application/model/
prompt/guard/SDK change; two existing tests adapted and five explicit image tests
added. No models, challenges, hosted traces or solve-rate comparison.

Recommend the tested frozen NYU-based artifact plus the small adapter, accepting
larger disk/build cost. The external installer ignored optional Kali/Sherlock/
Cutter errors; the positive result is limited to verified functionality. A first
60-second raw-image probe timed out and a repeat took 1.405s, so recommend a
one-time Docker image preflight before normal attempts. Exact first-probe cause
was not established. Current image/defaults are untouched and test cleanup passed.
[Build, resources, functional results, archive and proposed integration](https://github.com/ryanbanko/590_ctf_agent/blob/aedfd62cf8379adee73a30546592036af6f82a42/evidence/nyu-solver-image-evaluation/retry-8g/README.md).


## Infrastructure image integration — completed November 7

The evaluated NYU installation body is now the single production solver recipe,
with the tested workspace/environment additions, pinned NumPy/Pillow and existing
inventories. The unused HTTP entrypoint and our former active requirements files
are removed; historical inputs, lean image and archive remain available. Five
additional toolkit/control tests now run in the normal suite. No agent/prompt/
model/tool/SDK behavior, limit or new experimental hypothesis changes.

The normal source-build command passed in 14.03s using cache; 100 offline tests
and 34 Docker cases passed. First startup (0.73s) and Python execution (0.17s) fit
existing allowances on this cached host; no clean-machine cold claim is made.
The new default matches the tested image and has its own verified local archive.
Larger storage and optional upstream gaps remain. No model calls, challenge runs,
solve-rate comparison or hosted uploads. The development pilot is still separate.
[Integration evidence](../evidence/nyu-solver-integration/README.md).


## Integrated-runtime development pilot — November 7

One trial each on `msc-algebra`, `rev-checker`, `web-shreeramquest` under unchanged
agent/prompt and normal settings. First two ended in trusted success; the third
stopped on a blocked request to frontend port 4999 (only 80 permitted). Batch
stopped for review. All three have complete native exports/audits and cleanup;
18 requests/18 tools, 140.75s total, estimated $0.00596. These are pilot observations,
not a controlled solve-rate comparison. No silent replacement or retry.

The relevant web tool sequence shows port-80 application 502s before port probing.
A separate fresh zero-model diagnostic reproduced MongoDB's missing-AVX restart
loop and later Node exit/database errors. This establishes target compatibility
work and a limitation of TCP-only readiness, independently of the agent's scope
mistake. Review dependency health/compatible runtime before another pilot. No
prompt, image, guard, tool or numeric-limit change was made. Detailed trace review
remains with the user. [Evidence](../evidence/nyu-runtime-pilot/README.md).


## Target compatibility follow-up — November 7

Official MongoDB 7.0.9 ARM64, from the same release index as the original AMD64
image, passed two fresh zero-model deployments. Only Mongo's image/platform were
substituted temporarily. Normal-account registration/login/profile through port
80, database ping, stable services after 35s, fresh reset, unchanged guard/private
boundaries and cleanup passed. No solving, submissions or model/agent comparison.
This supports a target compatibility fix, not an agent-performance claim. Production
integration/readiness changes await review. [Evidence](https://github.com/ryanbanko/590_ctf_agent/blob/aedfd62cf8379adee73a30546592036af6f82a42/evidence/mongo-arm64-evaluation/README.md).


## MongoDB compatibility/readiness integration — November 7

The approved production change selects the exact tested native MongoDB 7.0.9
sibling only on ARM64 Docker engines. Native Compose wait and safe dependency-state
snapshots improve startup/preparation error detection. Two fresh normal preparation
and two normal functional cycles passed, preserving supplied service semantics,
registration/login/profile behavior, DB reset, stable services, guard/private
boundaries and cleanup. 111 offline and three targeted Docker cases passed; the
existing network/reset case required one explicitly recorded daemon-lookup retry.
[Evidence](https://github.com/ryanbanko/590_ctf_agent/blob/aedfd62cf8379adee73a30546592036af6f82a42/evidence/mongo-arm64-integration/README.md).

No agent/prompt/model/solver/endpoint change or live retry. This is infrastructure
reliability evidence, not a solve-rate or agent-improvement comparison. The original
pilot's web scope violation is retained. A live retry/recovery hypothesis remains
separate work after checkpoint review.


## Final runtime validation and fresh web retry — November 7

111 offline tests, the full 36-case Docker suite and 22 fresh readiness cycles
passed under the final code. After user VPN confirmation, a new normal-settings
`web-shreeramquest` development attempt achieved evaluator-verified success in
4 requests/4 tools (14.879s active, 27.184s total; estimated $0.00085533).
Agent/prompt and model settings were unchanged. This supports working target/live
integration after the CPU fix; a single run is not a solve-rate improvement
measurement. The prior scope-stopped attempt remains recorded. Automatic native
export and privacy/parentage/cleanup audits passed; detailed trace review is
explicitly deferred to the user. [Evidence](https://github.com/ryanbanko/590_ctf_agent/blob/aedfd62cf8379adee73a30546592036af6f82a42/evidence/pre-git-validation/README.md).

## Latest eleven-attempt development trace review — November 7

The user authorized assistant analysis of the most recent batch's messages and
tool calls. `batch-3963930b88c3` contains eleven development IDs, one trial each,
on clean recorded commit `616b5f2`. Six evaluator-verified successes; five
`completed_without_success` endings. All eleven exports/audits and cleanup passed.
No recorded scope-denial, command-timeout or output-truncation event occurred.
The five unsuccessful attempts ended after 5–9 requests with substantial time
and call headroom; this does not prove that further actions would solve.

[Review evidence](../evidence/development-trace-review/README.md) records each
challenge, trace steps, strengths, limits and alternative interventions. Concrete
gaps include mathematical candidates never checked against a supplied validator,
an incorrectly copied target reused in a supposedly independent simulation,
and unverified explanations for remote/library/solver behavior. Successful runs
also show useful recovery, dependency installation, lightweight alternatives and
immediate stopping after verification. The assistant's findings await user review.

**Proposed hypothesis, before any new comparison:** a narrow prompt refinement
requiring independent validation and a focused diagnostic before ending on an
unexplained contradiction will reduce unsupported blocker conclusions. It may
increase calls/time/cost without improving success. The existing broad recovery
instructions are already present; draft wording targets the missing behavior
rather than repeating them or encoding challenge-specific answers.

The evidence proposes a small matched development comparison, keeping everything
apart from the prompt fixed. A separate reasoning-effort comparison is an
alternative, not an implemented change. No prompt/runtime/configuration changes,
new model calls, challenge attempts or solver execution occurred during review.
No held-out contents, answer keys or write-ups were consulted. Original records
remain intact. Stop for review before implementing or running the proposal.

## Combined prompt, tool contract and output recovery — hypothesis recorded November 8

**Status:** the user supports one initial milestone containing both prompt/contract
and output work. This updates the earlier prompt-only proposal before implementation
or new model calls. See the [implementation plan](IMPROVEMENT_OPTIONS.md#consolidated-first-fix-implementation-proposal--november-8).
No behavioral comparison is authorized by this record.

### Evidence and hypotheses

The eleven reviewed development traces show unchecked derivations, validation
sharing incorrectly copied data, stale connection state and unsupported blocker
conclusions. The existing prompt already asks for recovery; simply adding more
general persistence instructions is not the proposed intervention. No runtime
output truncation occurred in these attempts, so output loss is not established
as their cause. Poorly advertised solver capabilities are a documentation gap,
but these traces do not establish that advertising them would change outcomes.

**Behavioral hypothesis:** concise verified environment/connection instructions,
specific inexpensive validation and contradiction-diagnosis guidance, and
retrievable oversized output will help the agent use original evidence and resolve
recoverable errors before ending. Expected signs are fewer unsupported blocker
conclusions and more relevant independent checks. Increased verified success is
a possible downstream effect, not a guaranteed result.

**Mechanical hypothesis:** retaining received raw stdout/stderr on overflow and
providing solver-readable paths permits exact recovery of omitted content within
explicit storage limits, preserving command results and existing deadlines,
terminal stops and isolation. Synthetic commands can check this claim without
establishing better challenge solving.

Possible regressions include unnecessary checks/retrieval calls, higher token use
or latency, conflicting or stale instructions, misleading partial-file claims,
and capture/delivery interfering with timeout or cleanup. Proposed 10 MiB/command
and 100 MiB/attempt limits are local engineering choices, not external standards.

### Verification and later comparison

Synthetic acceptance checks cover exact beginning/middle/end bytes and separate
streams; bounded previews/memory/retention; truthful partial/failure statuses;
safe non-root paths; threshold and threshold-plus-one; invalid UTF-8; long lines;
cap exhaustion; storage/delivery failure; and normal nonzero exits. Spill the
buffered prefix **before any bytes are discarded** by the existing head/tail
reader. Check background output, timeout/restart, remaining-deadline exhaustion,
concurrent terminal stop and private retention after cleanup. A failed boundary
or lifecycle check prevents handoff. Confirm prompt/tool-schema propagation.

A later separately authorized matched development comparison should keep model,
reasoning, response allowance, images, inputs and existing execution limits fixed,
changing the documented package and its new retention limits. Preserve original
records; use fresh conditions, previously successful development tasks for
regressions, and tasks with the observed failure classes. Choose trial counts and
resource allowance before calls. Leave held-out tasks untouched. Single trials
are exploratory and cannot establish a reliable solve-rate effect.

Record evaluator-confirmed success, relevant independent-check use, focused
contradiction diagnosis and whether final blocker claims are supported. Distinguish
unavailable/inapplicable checks from skipped relevant checks. Also record requests,
tools, tokens, active/total time, cost with its pricing source, capture/retrieval
events, incidents and cleanup. More calls alone are not improvement. If output
never overflows, the comparison cannot demonstrate output-recovery benefit;
synthetic evidence supports that capability. Assess the whole package; separate
causal claims require separate controlled variants. Preserve source/configuration
provenance for review and rollback.

### Primary-source design review — November 8

Rechecked these sources against current agent/tool/output behavior. They support
principles and precedents, not certification of this implementation or proof of
prompt effectiveness.

| Source | Applicable guidance and project decision |
| --- | --- |
| [OpenAI function calling](https://developers.openai.com/api/docs/guides/function-calling#best-practices-for-defining-functions) | Explain purpose, parameters and output; keep functions predictable and the tool surface small. Retain three tools and describe actual shell, timeout, truncation and retrieval behavior. |
| [OpenAI reasoning best practices](https://developers.openai.com/api/docs/guides/reasoning-best-practices#how-to-prompt-reasoning-models-effectively) | Keep instructions direct with clear constraints and success criteria. Replace overlapping text; avoid prescribing a reasoning transcript or mandatory workflow. General guidance does not establish a Luna-specific measured result. |
| [Anthropic tool engineering](https://www.anthropic.com/research/writing-tools-for-agents) | Bound returned context, explain truncation/actionable errors, clarify contracts and evaluate changes. Keep explicit omissions and retrieval instructions. Its example token limit is not our required byte limit. |
| [Pi command-tool source](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/src/core/tools/bash.ts) | Provides a bounded command preview and a retained-output path. This is implementation precedent, not a universal standard. Our head/tail preview, distinct streams, caps and controller-to-solver delivery need project-specific tests. |
| [Langfuse error analysis](https://langfuse.com/guides/cookbook/error-analysis-llm-applications) | Derive failure classes from traces, fix concrete gaps and reassess after changes. Our small assistant-reviewed sample is not a completed human annotation study or proof of prompt causality. |

Bundling follows the user's preference and trades causal attribution for one
practical milestone. Smaller isolated edits would identify individual effects
more cleanly. Model, planning, notes and continuation remain separate experiments.
No new dependency, framework, SDK upgrade or second trace backend is needed.
This review changed documentation only; no runtime/configuration/test edits,
model calls, challenge attempts or hosted writes occurred.

## Combined first-fix implementation — November 8

Implemented the authorized package after the hypothesis above and documentation
checkpoint `4620032`: verified solver instructions; independent validation and
focused diagnosis; explicit command/connection/deadline contract; marked head/tail
previews; and bounded raw output with safe solver retrieval and private retention.
Added only 10 MiB/command and 100 MiB/attempt capture settings; model, reasoning,
response bounds, existing execution limits, images and dependencies are unchanged.
Delivery has a five-second total allowance within remaining attempt time; an
internal delivery timeout stops the attempt because its remote writer may survive
the client. Ordinary capture/delivery failures retain explicit status. This is
part of maintaining the existing timeout/process boundary, not a new retry policy.

132 offline cases passed. The full 42-case Docker suite passed, followed by ten
focused output cases after close-error hardening and one additional 10 MiB default-
capacity case: 43 distinct Docker cases covered. One new fault-injection test had
a mock read-handle error, corrected before the passing final offline suite; the
original failure remains recorded. Artifact/summary audit and final managed-resource
cleanup passed. [Evidence, report files, provenance and limits](https://github.com/ryanbanko/590_ctf_agent/blob/aedfd62cf8379adee73a30546592036af6f82a42/evidence/agent-first-fix/README.md).

The mechanical hypothesis is supported by synthetic checks, including exact omitted
content recovery, caps, partial/error statuses, non-root safe paths, timeout resets
and terminal-stop precedence. Behavioral effectiveness remains unmeasured. No new
model calls, real challenges or hosted writes occurred. Review before separately
authorizing a matched development comparison; preserve all historical attempts.

## First-fix eleven-ID development rerun — November 8

After committing the package as `e7e366c`, the user ran
`batch-48f3b134d5c3`: one fresh attempt on each of the same eleven development IDs
as `batch-3963930b88c3`. This replaces the proposed six-fresh-attempt comparison
with a practical full development rerun against a historical baseline. The
original hypothesis above remains unchanged and predates the attempts.

Recorded outcomes are **6/11 successes**, equal to the historical baseline total.
`rev-tablez` changed from unsuccessful to successful, and `web-shreeramquest`
changed from successful to unsuccessful; other success outcomes match. There were
65 model requests/60 tools, 309.737431s summed active time, 450.202408s batch elapsed
time and $0.02025106 summed local configured-rate cost estimate. This is a
descriptive development record, not verified billing or scored aggregation.
No command timeouts, solver restarts, truncation/capture events, scope/guard
incidents or cleanup errors were recorded. Output recovery was not exercised.

The summary audit verified clean source provenance, matching model settings and
existing execution limits, per-challenge images, dataset and handouts; only the
two new capture limits differ in configuration. Saved export counts/end times and
existing run audits passed, but `rev-tablez` initially lacked payloads on five
observations despite its complete flag. A read-only Langfuse CLI fetch recovered
the 18-observation trace into an additional export, preserving the original.
All eleven selected exports now have their root/generation/tool payloads.
[Results, trace links, hashes, configuration and export caveat](../evidence/agent-first-fix-batch/README.md).

Detailed behavioral review is pending. One trial per task, a historical baseline
and bundled changes cannot establish a reliable or component-specific effect.
Do not describe the changed outcomes as fixes/regressions before reviewing their
evidence. The metadata audit made no new model calls, attempts, container operations
or hosted writes; no expected answers or held-out contents were consulted.
Review validation, contradiction diagnosis and stopping behavior before deciding
further experiments. A stronger export payload-completeness check is a separate
engineering follow-up, requiring no rerun of the completed challenge.

## Reasoning and token-headroom experiment — preregistered November 8

**Status:** the user requested a reasoning experiment, then explicitly added a
doubled token allowance before any medium model calls. The separate
`configs/reasoning-medium.toml` profile changes `gpt-6-luna` effort from `low` to
`medium` and per-response `max_output_tokens` from 4,096 to 8,192. The user then
requested applying these values to the active `configs/development.toml` too, so
ordinary batch commands now select medium/8,192. The named experiment profile
retains the same values. The low/4,096 reference is preserved in the prior batch's
configuration snapshot and Git. This amended hypothesis is recorded before calls;
preparation is not a completed run. The initial effort-only draft was not run.

**Hypothesis:** with prompt, tools, images and other execution limits fixed, medium
reasoning plus additional response headroom will improve independent checks and diagnosis of contradictions, reduce
unsupported unsuccessful stopping, and potentially improve evaluator-confirmed
success. It may increase reasoning tokens, latency and total cost, or produce no
quality gain. Higher token consumption alone does not support the hypothesis.
The earlier trace findings motivate this test; the new low-effort batch has only
received a metadata audit, so no behavioral diagnosis of its failures is assumed.

The low-effort reference is `batch-48f3b134d5c3` on clean `e7e366c`: 6/11 successes,
65 requests/60 tools, with complete selected exports documented in
[batch evidence](../evidence/agent-first-fix-batch/README.md). The latest saved
checkpoint `c80b61a` adds documentation/evidence to that implementation.
For an exploratory medium condition, use the same eleven development IDs, same
order and one fresh attempt each; keep held-out tasks reserved. Inspect the first
few attempts for gateway acceptance and limits before continuing. No live medium
call is made during preparation, and gateway acceptance remains unverified.

The experimental settings differ from the saved low-effort reference in
**exactly two fields**: `model.reasoning_effort` and `model.max_output_tokens`.
Both current profiles now have identical parsed values. Retain model identity,
prices, prompt/tool code, 60-second request limit, 600-second attempt
limit, call/resource/capture bounds, dataset and handouts. Snapshot the config,
source/image provenance and per-attempt settings. Do not change the setting during
the batch or selectively replace failures. Keep results in a separate output folder.

[Official Luna documentation](https://developers.openai.com/api/docs/models/gpt-6-luna)
lists medium support. The [reasoning guide](https://developers.openai.com/api/docs/guides/reasoning#allocating-space-for-reasoning)
explains that the output cap includes reasoning and recommends starting with more
headroom, such as 25,000 tokens, for initial exploration. The user-selected 8,192
is a conservative increase, not a universal standard or a guarantee of adequate
room. A response can exhaust it before visible
output. Track `model_response_incomplete`, provider incomplete details, request
timeouts and wall/call stops. If constraints bind, qualify the result as medium
under these limits; a later larger-common-budget comparison needs fresh conditions
and its own recorded scope. The allowance is per response, including reasoning
and visible output; there is no aggregate per-attempt token allowance to double.
Do not attribute cap failures solely to reasoning quality. A larger allowance
permits greater consumption but is not automatically used or billed in full.

Compare success and per-challenge outcome changes, independent validation,
contradiction diagnosis and supported stopping claims alongside model/tool calls,
input/output/reasoning/cached tokens, active/total time and cost using one documented
pricing source. Retain failed/incomplete attempts and verify export payloads before
behavioral review. The existing local/native cache-write cost discrepancy remains
a limitation; estimates are not independently verified billing.

This is a combined effort/headroom experiment: an outcome change cannot be
attributed to effort alone. One trial per challenge against a historical baseline
is exploratory. A subsequent fresh low/medium comparison at a common token limit
would separate effort more cleanly if justified by the pilot; those extra runs
are not part of this preparation.
Plans, notes, model upgrades, continuation and export-control changes are separate.

## Medium/headroom batch: final scope incident — November 8

The user ran `batch-f4ccc7f4b335` with medium/8,192. All eleven planned attempts
were reached: nine verified successes, one ordinary unsuccessful ending
(`pwn-baby-boi`) and final `web-shreeramquest` scope violation. The batch wrapper
recorded the incident and raised its intentional stop-for-review RuntimeError.
The saved batch is stopped even though the final scheduled attempt had been reached;
earlier results remain intact. Full behavioral/metric comparison remains pending.

The final trace's third tool command included a port loop after an nginx rejection
on an allowed request. Public scope allowed only `172.20.0.2:80`; independent
guard evidence records a denied attempt to `172.20.0.2:4999`, an internal listener
mentioned in served public source. The controller stopped the solver, exported
records and completed target/solver cleanup. Do not assume later ports in the
loop were reached. [Incident chronology and hashes](../evidence/reasoning-medium-scope-stop/README.md).

Actual run provenance is `c80b61a` with a dirty working tree, recorded source
hashes and copied medium/8,192 settings. Preserve that provenance and the incident.
This review executed no trace commands and made no new model calls, retries,
container operations or scope/configuration changes. Nine successes versus six
previously is descriptive; increased effort plus token headroom and one historical
comparison do not isolate an effort effect. Review traces before further changes
or retries; enforcement remains intact.

## One blocked-connection recovery and scope clarification — November 8

Before implementation, the user approved treating a firewall-confirmed prevented
connection as eligible for one corrective response in the same attempt. This is
the user's interpretation of the assignment, not a new professor confirmation.
The earlier scope-stopped attempt remains an incident under its recorded policy.

Hypothesis: explicit target address/protocol/port instructions plus one bounded
blocked-command recovery lets the agent correct a scope mistake and continue
permitted work without expanding access. A second incident, guard/counter failure,
uncertain enforcement, or a denial outside an active run_command stays terminal.
Restart the solver to end all old processes while retaining files; preserve the
original deadline and counters, record denied packets/incidents/recoveries and
return corrective tool feedback. Do not retry the offending command automatically.
The recovery is controller behavior; the prompt's effect requires live follow-up.

Use explicit max_scope_recoveries=1 (or 0 for strict stopping). Count a command's
blocked packets as one incident; acknowledge the cumulative counter only after
reset and a successful guard audit. Re-read the counter for NFLOG notifications
so delayed logs cannot reclassify an acknowledged packet as a new incident.
Verify first-denial recovery, actual denial at a live forbidden service, subsequent
permitted work, repeated/strict/idle denial stopping, counter anomalies, delayed
events and terminal/deadline precedence with offline/synthetic Docker checks.
No paid model call or real challenge retry is authorized by this implementation
milestone. Model/effort/token settings and guard rules remain fixed.

Implementation verification: 149 offline tests and 47 synthetic Docker cases
passed; final focused checks passed (77 offline and four Docker cases, overlapping
the full suites). One intermediate post-recovery proof assertion failed and was
tightened to distinguish the old child process from PID reuse; the precise cause
of the original generic assertion remains unconfirmed. The original failure is
retained. These checks support mechanical recovery and unchanged blocking, not a
model success improvement. No real retry or paid model call occurred.
[Implementation evidence and limitations](../evidence/scope-recovery/README.md).

## Manual HTB description preface — November 17

The user approved a one-sentence contextual preface for manual HTB tasks:
“Challenge descriptions vary in detail and may mix story, humor, and technical
clues.” It is prepended to the initial user message immediately before the
serialized public task. The sentence is informational; it does not prescribe a
solving method or rewrite/interpret a description.

The preface is passed only by `run_manual_challenge`; the shared runner's default
and CTFTiny path receive no preface. The original task JSON remains the content of
`public-task.json` and the input to `task_sha256`. The system prompt, endpoint
scope, tools, isolation, tracing and stopping contracts are unchanged.

The focused synthetic SDK-flow test passed. It checks the initial system message
is unchanged, the initial user message contains the exact sentence before the
original task JSON, and the saved public task remains byte-for-byte the original
JSON plus its newline. No live challenge, model call, hosted mutation or Docker
operation occurred. This verifies propagation and scope only; whether the sentence
helps or changes behavior requires a separately authorized comparison.
[Evidence and check result](../evidence/htb-description-preface/README.md).
