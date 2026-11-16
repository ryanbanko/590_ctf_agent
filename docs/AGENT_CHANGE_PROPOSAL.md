# Concrete agent change proposal — November 15, 2026

Later November 16 decision: the user withdrew the planning/notes-plus-50-turn
candidate after its trial review and selected the original prompt/40-turn
configuration. The active runtime now matches `0395835`; only documentation and
retained evidence differ from that commit. All 41 rollback checks passed.
[Review and exact rollback](../evidence/planning-notes/rollback/README.md).
The implementation status and proposals below belong to their dated checkpoints.

November 16 status: the user subsequently approved a shorter brief-planning/
optional-notes paragraph on the original `0395835` prompt, plus a default model
allowance of 50 instead of 40 turns. That combined condition is now implemented
and passed 41 focused offline checks; no live trial has run.
[Exact adopted wording, settings and evidence](../evidence/planning-notes/README.md).
The detailed N1 wording and other implementation proposals below are preserved
historical drafts; they are not all adopted. The earlier validation/readability
candidate is withdrawn from active use, with all original evidence retained.

Later November 15 update: the external connection-description pilot was not
adopted. The user subsequently approved a system-prompt validation/readability
revision, implemented with 36 passing offline tests. Its subsequent user-run pilot
achieved 6/6 successes; the later four-category expansion achieved another 12/12.
It is reasonable to retain the revision, with no causal improvement claim.
[Expanded review](../evidence/validation-expanded-review/README.md),
[initial pilot review](../evidence/validation-pilot-review/README.md),
[exact candidate and preceding results](../evidence/prompt-validation/README.md).
The recommendations and implementation claims below preserve the earlier proposal
checkpoint; consult PROJECT_STATUS.md for current authorization and next steps.

Original status: **proposal only; no runtime change or new attempt authorized/performed.**
This refines the [36-trace review](../evidence/notes-baseline-review/README.md)
using the actual implementation. It separates mechanical corrections, behavior
experiments and unresolved infrastructure questions. The current runtime remains
commit `0395835`; documentation and derived metadata are newer.

## Recommendation

Measure context growth now from existing exports, then add small passive local
request profiles when implementation is approved. The smallest next **behavior
experiment** changes only the connection-reading paragraph in the `run_command`
description. Test that on three existing practice tasks, three trials each, before
expanding. Optional working-state notes are a separate, worthwhile experiment for
tracking evidence, assumptions, rejected tests and reusable results. They are not
limited to preventing forgetting.

Do not combine notes, output elision, tool annotations, multiple-call enablement,
budget/model changes and a service repair in one comparison. Keep the original
baseline and failure. Proposed code below is not implemented by this document.

## What the implementation already does

- `agent.run_agent()` accepts a list of tool calls and invokes them sequentially.
  All sibling arguments were chosen before their results were available. The
  next model response comes after that list, unless success or an enforced stop
  ends it early. Each call consumes its own tool budget and receives a linked
  result. `tests/test_agent.py` already covers success/terminal stopping between
  siblings. Normal ordered multi-result replay deserves a targeted check if this
  feature is ever enabled live.
- `agent.make_responder()` explicitly requests `parallel_tool_calls=False`.
  The current live policy therefore asks for at most one call, even though the
  controller tolerates multiple returned calls. The controller does not execute
  siblings concurrently. Simply removing the option changes the requested API
  behavior; leave it explicit.
- `tools.TOOL_DEFINITIONS` already explains `/bin/sh`, explicit Bash, a fresh shell
  per call, stateful exchanges in one script/connection, restart behavior and
  output capture. Shell working-directory/environment changes do not transfer to
  another call. Files/packages and some normal background processes can persist;
  a timeout restart ends all solver processes and connections. A restarted solver
  is not a restarted target.
- `docker.bounded_exec()` already returns `stdout`, `stderr`, `exit_code`,
  `timed_out`, `truncated`, `output_bytes`, `preview_bytes` and conditional capture
  metadata. Omitted-byte markers distinguish head/tail excerpts. `tools.execute_tool()`
  adds `solver_restarted` and `process_state_reset` after a completed recovery.
  `tools.scope_feedback()` supplies explicit scope/reset guidance. Successful
  delivery adds solver-readable capture paths; capture errors remain visible.
- `agent.responses_input()` replays public history, native assistant output and
  linked tool results, including opaque encrypted reasoning. Files are not
  automatically injected. Existing prompt instructions already ask for selective
  output, saved intermediates, independent validation and revised assumptions.
  There is no automatic compaction or notes subsystem.

## 1. Context growth and selective retrieval

Being under 2 MiB is only an admission check. It says nothing about relevance,
attention, repetition or the cost of replaying earlier text. Cached tokens still
occupy context; caching discounts cost rather than making irrelevant material
useful.

The [new derived profiles](../evidence/agent-change-proposal/context-growth.json)
cover all 355 generation usage records. Request bodies are available for 353.
Whyos trial 2 grows from 1,033 to 170,959 input tokens over 16 requests, with a
27,419-token jump at request 5. Its final request contains about 427 KB of
serialized tool-result items and 118 KB of opaque reasoning items. Gibberish-check
trial 1 jumps by 33,458 input tokens at request 4. These changes include new model
and tool material; the token delta cannot be attributed exclusively to one tool.
JSON bytes by item type are a size decomposition, not tokenizer attribution.
Opaque reasoning was counted by size, never decoded or copied into the evidence.

### C1 — passive request profiles

**Exact change:** in `ctf_agent/agent.py:make_responder`, add a bounded
`usage["request_profiles"]` list, one entry for each actually submitted request,
no more than `max_requests`. Measure request bytes at the existing serialization
point, counts/item bytes after `responses_input`, and elapsed time with
`time.monotonic()` around `client.responses.create`. Record:

```text
request_index
request_bytes
input_item_count
item_json_bytes_by_type
input_tokens, cached_input_tokens, output_tokens, reasoning_tokens
elapsed_seconds_monotonic
provider_status
error_type                 # only on exception; class name, no raw message/body
```

Initialize returned-usage fields to null; fill only when reported. An API exception
does not become a zero-token request. Preserve existing whole/known usage totals
and all stopping rules. Profile request sizes before sending but do not create a
fake submitted-call entry when the existing byte guard rejects a request.
`attempt.request_response()` already copies model usage into the result in
`finally`; existing local `summary.json`/`run.json` and root output can retain the
profiles. No new SDK API, trace backend, tokenizer, model-visible budget feedback
or dependency is needed. Input growth is calculated from adjacent reported input
counts after return, not predicted before the model call.

**Evidence / benefit:** current totals conceal sharp growth; offline exports
already make it measurable, but missing exports lose that view. Local profiles
also help distinguish monotonic request duration from the observed wall-clock
span anomaly. They measure inefficiency without changing the model's input.

**Type / priority / effort:** confirmed measurement gap; proposed additive
instrumentation, P1, small-to-moderate implementation. Not a demonstrated solve fix.

**Verify:** extend `tests/test_model.py` using the existing offline HTTP transport:
exact request size, ordinal/one record per submitted request, usage reconciliation,
null unknown usage, exception preservation, no fake call on byte rejection, and
monotonic elapsed time under simulated wall-clock jumps. Assert identical outbound
request contents and unchanged retry/stop behavior. Retain Langfuse 5.1.0/OpenAI
3.44.0 for reproducibility; SDK upgrades are separate work.

### C2 — narrower new output before older-output elision

**Exact later prompt replacement:** replace the existing first two output-guidance
sentences in `agent.SYSTEM_PROMPT` with:

> Keep command output focused on the current question. Save broad searches and
> disassembly to workspace files; print a count and a small relevant excerpt with
> its path and line range or address range. Narrow the next read using that
> evidence instead of printing the same large region again. Preserve errors,
> unexpected results and completion output.

Keep the existing capture-path, exact-value and intermediate-reuse instructions.
Use ordinary `run_command` file reads; no new retrieval tool. Do not impose an
arbitrary excerpt size on every task or truncate errors to meet it.

**Evidence / benefit:** five whyos preview overflows and large replay histories.
This makes existing output guidance more operational; it is not a missing capture
feature. It may reduce irrelevant replay even when caps never bind.

**Type / priority / effort:** behavior experiment, P2, small prompt change.
Verify reduced input-growth spikes, cumulative/peak tokens and repeated large
excerpts, alongside unchanged solve/diagnostic quality. Separately count narrow
retrievals; fewer tokens with many extra calls is not automatically better.

**Older recoverable outputs:** reducing them could be useful, but defer automatic
elision until C1/C2 establish the remaining cost. A later opt-in implementation
would build a model-facing view in `responses_input()` that shortens only older,
large `run_command` stdout/stderr with a delivered complete archive. Retain call
IDs, result envelopes, errors, exit/timeout/reset/capture metadata, submissions,
recent outputs, system/task and native assistant items. Preserve original tool
observations/archive evidence and trace the exact shortened request the model saw.
Never silently drop messages, tool pairs, encrypted reasoning, uncaptured output,
partial/failed captures or the only copy of evidence. Previously delivered solver
files can later be changed/deleted; a path alone cannot guarantee recovery. That
limitation and retrieval-failure behavior need testing before claiming lossless
elision. This is a separate P3 experiment with moderate effort, not a prerequisite
for improving context use. A generic summarizer/compactor is not proposed now.

## 2. Feedback and call granularity

### T1 — one precise connection-contract edit

**Exact change:** in `ctf_agent/tools.py:TOOL_DEFINITIONS`, replace only:

> Keep stateful read/compute/respond interactions in one script using the same
> connection.

with:

> Read a prompt and send its answer on the same connection; a new connection may
> have different state. Buffer TCP chunks until the expected delimiter or length,
> EOF, or a bounded overall read deadline. One recv or an idle timeout does not
> establish a complete response.

Retain the surrounding shell, shorter internal deadlines, restart, scope and
capture wording. Protocol delimiters/lengths must come from observed/public
protocol evidence. A deadline can end an incomplete read; the wording does not
declare all deadline-ended buffers complete.

**Evidence / benefit:** all three algebra trials carried an answer to a new
session; crypto and pwn repeatedly confused short/partial reads with a complete
response or service failure. The existing same-connection sentence did not
prevent those choices. The replacement names the concrete mistake and a bounded
alternative without embedding task-specific code.

**Type / priority / effort:** behavior experiment, P1, small. This is the smallest
recommended next experiment, described below. Check the existing tool-schema /
agent contract tests; a new test that merely matches the wording is not useful.
A generic delayed/split-prompt fixture may check the available client behavior
if needed, but cannot establish that the model follows the wording. That requires
the behavior pilot. No shared socket client, PTY, cross-call session registry or
`nc` replacement is needed.

### T2 — short conditional annotations, if T1 leaves interpretation problems

**Exact change:** add a small pure `command_notices(returned)` function in
`ctf_agent/tools.py`, called from
`attempt.call_tool()` after `scope_feedback()` and before `tool.update(output=...)`.
For `run_command` only, append an optional `notices` list using final controller
flags. Omit it for an ordinary result. Use fixed text, with no generated summary:

| Predicate | Proposed notice |
| --- | --- |
| `truncated == True` | `stdout/stderr contain excerpts. Inspect capture paths for omitted command output; check capture/delivery status.` |
| `process_state_reset == True` | `All solver processes and connections ended. Files/packages persist. The controller did not restart target services. Re-establish required state.` |
| capture `complete == False`, non-null `error`, or `delivery_error` | `Retained output may be partial or unavailable in the solver. Check capture status and usable solver_path entries.` |

Avoid duplicating the already explicit scope-denial prose. Existing booleans and
paths remain the machine-readable contract; annotations do not change truncation,
recovery or stop policy. Additional strings count toward future request bytes;
keep them conditional and bounded, not an identical paragraph after every call.

**Evidence / benefit:** errors interpreting partial output or state motivate a
trial of more immediate feedback, but current metadata already covers these
mechanics. Benefit remains unproven and this does not repair a script that reads
one chunk and exits successfully before wrapper truncation can occur.

**Type / priority / effort:** optional feedback experiment, P2, small-to-moderate.
Verify compound truncation/reset/capture errors, late scope recovery, ordinary
results receiving no notices, and unchanged fields/control behavior in existing
tool/scope tests. Include a synthetic script that deliberately receives one server
chunk then exits 0: wrapper notices must not claim the server response was complete.

### What the wrapper can and cannot know

It knows its Docker subprocess result, received stdout/stderr byte counts,
excerpt omission, whether captured bytes were retained/delivered, observed
timeout/cancellation, and whether its own restart completed. It knows the shell
entry point and per-call working directory. It can report those facts.

It cannot infer TCP protocol completion, why a remote service was silent, whether
an inner pipeline stage succeeded, whether a model hypothesis is correct, whether
exit 137 was OOM, or whether the script saved every value needed later.
`capture.complete` concerns retained **command output**, not all server output.
An outer exit 0 can coexist with caught exceptions, an earlier failing command or
discarded network bytes. Do not add fields such as `server_response_complete`,
`all_steps_succeeded` or `target_healthy` inferred from command output.

### Multiple calls: supported, keep current live policy

There is plausible value for independent inspections or writing then executing
an already planned file. There is no opportunity to adapt the second call's
arguments to the first result within that response. A recoverable first-call
timeout/reset could also invalidate subsequent preplanned actions without a new
model decision. Independent inspections can already be grouped in a single shell
script, with explicit failure handling.

**Proposal:** no loop/configuration change now. Keep `parallel_tool_calls=False`
and the sequential executor. If later enabled as its own experiment, first test
two normal results in order, matching call IDs on the next native replay, budget
exhaustion between siblings, success/terminal short-circuiting and the intended
policy after recoverable resets. Then test gateway/model support on benign tasks.
Changing generation call multiplicity would not introduce concurrent execution
or a parallel batch runner. Current baseline traces do not establish a benefit.

## 3. Optional working state: planning, notes and revision

### N1 — one prompt paragraph, no memory framework

**Exact change:** add the following paragraph to `agent.SYSTEM_PROMPT` after the
existing assumption/validation guidance, as a separate candidate condition:

> For multi-step work, keep a brief working state: observed facts and evidence
> paths, assumptions to test, rejected tests and their conclusions, reusable
> results and when they remain valid, and the next discriminating action. Revise
> it after a contradiction or change of approach. If useful across calls,
> overwrite notes.md in /workspace with the latest numbered revision, at most 150
> words; read it when needed. Treat it as a fallible index to original evidence,
> not proof. Skip notes for straightforward tasks and do not repeat them in every
> response.

This supports hypothesis management, avoiding duplicate tests, choosing a useful
next action and reusing valid work even with perfect memory. Trace examples
include lengthy model revisions, repeated deterministic candidates and late
component checks. It does not prove that notes would have fixed them.

Use existing `write_file`/`run_command` only. There is no mandatory note write per
turn, automatic injection/read, cross-attempt storage or planner model. The file
persists across a solver restart, while live sockets/processes do not; a note
about a live connection cannot restore it. Keep exact long values in data files
instead of notes. Invalidate a reusable result when its inputs/assumptions change.
For `write_file`, the argument is the workspace-relative `path: "notes.md"`.

Overwriting the file prevents file-history accumulation, **not** conversation
accumulation: earlier write arguments and printed notes remain in native replay.
Numbered revisions, a 150-word bound, selective reads, infrequent material updates
and no per-request injection reduce redundancy but cannot erase stale history.
The latest revision must label uncertain/rejected claims and point to evidence.
Do not call this a compaction mechanism.

**Type / priority / effort:** behavior experiment, P2, small code/prompt effort,
potentially useful for complex tasks; broader value than preventing forgetting.
Verify readable notes survive a benign timeout restart using existing filesystem
checks. In live comparison score whether notes are updated after contradictions,
distinguish assumptions/facts, prevent repeated rejected tests, and lead to the
stated next test. Count note reads/writes, extra calls/tokens, stale statements
reused and exact-value errors. A plan-plus-notes paragraph measures that package;
separating the value of writing files requires another condition.

## 4. Recurring infrastructure and observability

### I1 — expected terminal inventory skip

The final package-inventory issue is understood at the lifecycle level.
`attempt.stop_attempt()` calls `sandbox.stop_solver()`, which kills the solver.
`run_attempt()` later calls `snapshot_packages(..., "final", 2)` in cleanup.
Trying `docker exec` in that stopped container predictably produces an unavailable
inventory. In these 36 exports, all 36 initial inventories explicitly succeeded;
35 final events explicitly report unavailable/RuntimeError; one inventory event
has missing metadata and cannot be classified from its payload. These host-only
diagnostics do not enter the agent's tool history and did not cause solve stops.
The current DESIGN and historical simplification evidence already mention the
final inventory limitation. It is not a missing package or terminal-session bug.

**Exact change:** in `sandbox.snapshot_packages()`, if `phase == "final"` and
`sandbox["stopping"].is_set()`, emit:

```json
{"phase":"final","available":false,"status":"skipped","reason":"attempt_stopping"}
```

and return without `bounded_exec`. Use `attempt_stopping`, not `solver_stopped`:
the flag itself does not prove Docker kill succeeded. Keep initial inventory and
actual attempted-inventory errors unchanged. Do not restart the solver or delay
terminal stopping just to collect package data. This does not provide a final
package manifest; in-run installs remain in command records. A guaranteed final
manifest would be a separate design choice with more lifecycle work.

**Type / priority / effort:** confirmed diagnostic/lifecycle mismatch; proposed
small correction, P2, easy. Verify no exec after final stopping, correct skip
event, and continued initial/real-error behavior with substituted Docker calls.
No model campaign is needed to establish this contract.

### I2 — supplied/runtime library differences

Three issues must remain distinct:

1. **Solver versus target libraries:** the solver and supplied target are
   separate images, so matching libraries is not promised. The solver uses the
   Ubuntu 22.04 NYU recipe; the two old pwn targets retain their original runtime.
   Commands can inspect/analyze public files without assuming the local execution
   runtime equals the remote service runtime. Document this; do not globally make
   images match.
2. **Supplied contestant library versus observed service behavior:** the traces
   show inconsistent assumptions/offset deductions; they do not fingerprint the
   loaded remote library. Earlier evidence also calls this mismatch unconfirmed.
   If it remains operationally important, compare the public handout's hash/build
   ID with identified loader/library metadata in the trusted target image, plus
   recorded service configuration and any loader-path overrides. Use a benign
   child to test loader behavior. No challenge logic, private environment dump,
   expected answers or task process memory is needed. Keep diagnostics on the
   trusted side and do not supply target-private files to the solver. Whether the
   benchmark intentionally ships differing artifacts is a separate question.
3. **Package database versus effective socat version:** this is already explained.
   The approved derivative copies only `/usr/bin/socat`, so the base package
   database can show the old package. `socat -V`, compatibility labels, image IDs
   and the recorded adjustment identify the active binary. Base layers/config
   checks confirm no application library upgrade was introduced by that repair.

**Exact change now:** documentation only in this proposal and the improvement
shortlist. No library substitution, package upgrade, linker override or Docker
permission change. Further metadata comparison is a conditional diagnosis under
`tests/` using the existing exact-image test pattern, not a fix in `challenge.py`.

**Type / priority / effort:** known design differences/documentation, plus an
unresolved artifact/runtime-identity claim; P2 conditional, moderate diagnosis.
Verify any claim using hashes/build IDs and original versus derivative identity,
not a failed computation alone. The fixed listener is already validated; no new
listener workaround is proposed.

### O1 — local error and full required-payload audit

The earlier review counted six absent **generation-output/tool-input/tool-output**
fields. The request-growth follow-up found the two generation inputs are also
absent in that same successful trace: **eight missing action/request fields
across four final observations**. One package-inventory event additionally lacks
classification metadata. Preserve the original exports and distinguish this
expanded audit from the earlier six-field count.

**Exact change:** in `attempt.request_response()`'s existing exception handler,
set `result["response_error"] = {"kind":"response_source_error",
"exception_type":type(error).__name__}` before emitting the hosted event. This
retains a safe category when export fails. C1 separately retains known request
metrics. Never copy raw exception messages, provider bodies, credentials or
private runner state into the record.

In `launch.read_model_trace()` / `run_challenge()`, add a separate `payload_audit`
record with `status`, `missing_required_fields` (observation ID/field) and
`intentional_omissions`. Check completed live generation inputs/outputs and
accepted tool inputs/results, without treating intentionally absent invalid-tool
arguments or failed/cancelled response outputs as missing successes. Preserve the
existing structural `evidence_complete` meaning and batch stopping policy for this
milestone; report partial payloads explicitly instead of silently calling them
behaviorally complete. A bounded reread may use the existing export deadline;
retain partial evidence at expiry. No model/command retry or failure replacement.

**Type / priority / effort:** confirmed visibility gap, proposed correction, P1,
moderate. Verify missing input/output fixtures, intentional redaction/error cases,
existing structural audits, local error survival after export failure and
unchanged known/unknown usage and stop policy. Any stronger completeness-based
batch stopping rule needs a separate explicit decision.

## Priorities and implementation sequence

| Order | Change | Priority | Classification | Full effort | Verification |
| --- | --- | --- | --- | --- | --- |
| 1 | C1 per-request profiles | P1 | Measurement improvement | Small–moderate | Offline transport, size/usage/error/timing invariants; identical requests |
| 2 | O1 local categories and payload audit | P1 | Confirmed visibility gap; correction proposed | Moderate | Error/export fixtures; intentional omissions; no retry/stop-policy change |
| 3 | T1 connection-contract wording | P1 behavior | Experiment | Small | Existing schema/agent checks; behavior assessed in nine-attempt candidate pilot |
| 4 | Service initialization/early-close diagnosis from the original review | P1 diagnosis | Cause unresolved | Moderate; fix unknown | Generic delayed-state service with early close/reconnect; no universal active readiness probe |
| 5 | N1 optional working state | P2 behavior | Experiment with value beyond forgetting | Small; effect uncertain | Evidence/assumption revisions, repeated tests, reuse, note overhead and stale claims |
| 6 | C2 selective-output wording | P2 behavior | Experiment; capture already works | Small | Input growth, excerpts/retrieval, token/call cost and diagnostic preservation |
| 7 | I1 final inventory skip | P2 maintenance | Confirmed expected-stop mismatch; correction proposed | Small | No post-stop exec; initial/real errors retained |
| 8 | T2 conditional notices | P2 conditional | Experiment; existing fields may suffice | Small–moderate | Final-result flags and no false server/inner-stage claims |
| 9 | I2 library identity comparison | P2 conditional | Diagnosis/documentation | Moderate if needed | Hash/build-ID and loader metadata; no application/runtime substitution |
| Defer | Automatic output elision, multi-call enablement, compaction, mandatory notes, stronger model/larger budgets/new terminal | P3 | Separate hypotheses | Varies | Require a measured remaining problem and an isolated condition |

Implement mechanical bookkeeping changes in small reviewed milestones, then freeze
them identically for both sides of any new controlled behavior comparison. They
do not justify silently treating the old baseline as if it had different code.
The existing baseline can still be an explicitly historical pilot reference;
context profiles above are derived offline and available without rerunning it.

## Smallest next behavior experiment: T1 only

**Hypothesis:** naming the distinction between a TCP chunk, a bounded read and a
complete protocol message, together with fresh-session state, reduces incorrect
read/session conclusions and answer carryover without adding agent steps.

**Only changed model-visible content:** the one `run_command` description sentence
replaced with the exact T1 wording. `SYSTEM_PROMPT`, other schema text, tools,
result fields/notices, notes behavior, history replay and call multiplicity stay
fixed. No N1/C2/T2 or output elision in this candidate. No shared client helper.

**Fixed:** Luna/medium; 8,192 output tokens, 2 MiB input, 90-second request,
600-second attempt/120-second maximum command/40 model/80 tool limits; solver /
guard and per-task target images; dataset and public files; three fresh trials;
scope/submissions/restarts/cleanup; no retry/continuation/concurrency. C1 can be
present equally on both freshly frozen conditions; record its provenance and
keep its metadata out of model input. I1/O1 bookkeeping must likewise be common
or explicitly documented as a separate measurement change.

**Pilot:** `cry-open-ellipti-ph`, `msc-algebra`, `pwn-pilot`, three candidate trials
each: nine new attempts if separately approved. Compare against their existing
nine baseline attempts first. This covers delayed/partial reads, fresh-session
state and one task with variable script recovery. All nine baseline trials
succeeded, so solve rate alone is insensitive. If a strict contemporaneous
comparison is desired, freeze A/B and authorize nine fresh baseline plus nine
candidate attempts, with task order balanced; that is additional spending, not
implicitly part of this proposal.

**Primary behavior metrics, labeled from observable traces:**

- Answers carried from an old connection to a different newly observed prompt.
- Claims of EOF, whole-response completeness or service failure supported only by
  a single chunk/idle timeout; distinguish a cautious uncertainty statement.
- Extra reconnect/probe calls before obtaining a complete usable prompt, allowing
  legitimate protocol exploration rather than penalizing every reconnect.
- Whether the final working reader uses observed framing / bounded reads and
  same-session exchange. A reviewer can inspect code/results; the wrapper cannot
  certify this at runtime.

**Secondary metrics:** all-trial success, model/tool calls, cumulative and peak
input, growth spikes, estimated/native cost on a consistent basis, command
timeouts/restarts, active time/tail cases, and unintended long waits. Preserve
server faults, kills and clock anomalies instead of replacing or misclassifying
them. No automated keyword score is proposed as behavioral ground truth.

**Decision:** expand to the full 12-task candidate comparison only if the trace
review shows fewer targeted mistakes, success is preserved, and the added wording
does not induce longer waits or material cost/call growth. Mixed results justify
revision or stopping rather than a claimed win. Three trials/task and a historical
comparison cannot establish statistical superiority; report per-task changes and
every trial. If the nine pilot attempts use the final frozen condition, retain
all nine and run the remaining 27 to complete 36. If the condition changes, keep
the pilot separate rather than pooling or selectively replacing trials.
N1 would then be a distinct candidate, initially using complex
reversing/forensic tasks plus a short-task control. Do not attribute T1's effect
to notes or a service repair.

## Sources and verification scope

Implementation sources: `ctf_agent/agent.py`, `attempt.py`, `tools.py`, `sandbox.py`,
`docker.py`, `launch.py`; existing agent/model/scope tests; the prior category
review; [execution-simplification record](../evidence/execution-simplification/README.md)
and [listener correction](../evidence/listener-update/README.md). Original
assignment/professor clarifications and image/SDK pins remain unchanged.

The Langfuse skill's prompt-engineering and instrumentation references were read.
[Current trace guidance](https://langfuse.com/docs/observability/best-practices),
checked November 15, supports per-generation visibility, meaningful tool results,
stable names and metadata for diagnostics. Existing native tracing remains the
integration; no migration, SDK upgrade, new annotation platform or hosted write
is proposed. Exact request history must remain faithful to what the model saw.

New work here is documentation and derived metadata only. Source/export hashes,
usage/profile counts, inventory classification and local document links are
checked in [proposal evidence](../evidence/agent-change-proposal/README.md).
No runtime test is claimed for unimplemented proposals, and no new model, Docker,
network-service experiment or task-private inspection occurred.
