# Review of the 36 practice-baseline traces — November 15, 2026

**35/36 attempts succeeded. The sole unsuccessful attempt encountered repeated
remote JSON-loading errors.** Successful attempts also contain recurring,
recoverable problems: incomplete socket reads, answers carried across new
connections, unvalidated reconstructions, oversized searches and noisy output.
These support targeted improvements; they do not establish that a larger model,
more permissions, a persistent terminal or more budget is needed.

This is an **assistant-assisted qualitative review**, not human annotation or a
new scored evaluation. All 36 attempts were examined, category by category,
including successful runs. Behavioral findings use the available chronological
model/tool outputs and selected recorded tool inputs. Numeric checks use original
run records and observation exports. Six absent payload fields limit the final
steps of one crypto trace; that attempt's success is verified by its run record,
not independently reconstructed from its missing final tool output.

November 15 follow-up: the six-field count above covers generation outputs and
tool inputs/outputs. A [full request audit](../agent-change-proposal/README.md)
also finds two missing generation inputs in that same trace, making eight
required request/action fields unavailable. The [concrete proposal](../../docs/AGENT_CHANGE_PROPOSAL.md)
refines the recommendations below and replaces its broad first experiment with
a one-variable command-description comparison. Original records remain unchanged.

No recorded commands were executed. No task/private source, expected-answer file
or published solution was consulted. No agent, tool, model setting, container or
original run/export was changed. New generations, retries and diagnostic Docker
experiments were not run.

## Sources, condition and accounting

- Development baseline: `runs/pilots/notes-comparison/baseline-development/batch-471fe180c113`:
  30 attempts, 29 successes and one `completed_without_success`.
- Authorized test-task practice: `runs/pilots/notes-comparison/baseline-test-practice/batch-39f3da0c8fa3`:
  six attempts, six successes.
- Twelve CTFTiny tasks, two per category, three trials each; ten published Hard
  labels and two Easy labels. This is the selection proposed November 14.
- Every attempt records clean source commit
  `0395835e693a80813635721eb2619113c7aa7700`, identical source hashes/model settings,
  the same solver/guard images, and stable target image identities within each task.
  Listener correction and usage preservation are present; planning/notes and
  automatic continuation are absent. The two ordinary runners are sequential;
  the metadata does not make the two separately launched batches one sequential
  session or control host load between them.
- Luna/medium; 8,192 output tokens per response including reasoning; 2 MiB request
  byte cap; 90-second request timeout; 600-second attempt allowance; 120-second
  maximum command; 40 model/80 tool calls; solver 1 CPU/1 GiB/64 PIDs.
- 355 model calls and 354 tool calls; 8,724,629 cumulative input tokens and
  205,361 output tokens including reasoning. Cumulative input includes replay of
  earlier context and is not a single context-window size.
- Local configured-rate estimates total **$0.28988808**. Exported native
  generation costs sum to **$0.317246804956**. These are two accounting bases,
  not independent bills; native costs include cache-write pricing omitted by
  local estimates. Keep both labels rather than mixing them in a comparison.
- All 36 have structural `evidence_complete`, known usage and cleanup records.
  There are no recorded scope incidents/recoveries or top-level resource-limit /
  API termination reasons. Three command timeouts caused three solver restarts;
  one additional command returned 137. These are distinct events, not attempt
  failures.

[review.json](review.json) retains per-trial metrics, original record/export
hashes, trace links, payload-gap identifiers and timing caveats, without payloads
or candidate values. Original `runs/` artifacts are Git-ignored and will not be
available to teammates merely by pushing this summary. Langfuse trace links also
require access to the project. The findings and inventory here can be reviewed
without that access; deeper reinspection requires the separately shared export.
The [checks record](checks.json) documents source/count/hash and documentation
verification for the initial review snapshot. Its document hashes predate the
follow-up addendum; the new proposal evidence checks the current documents and
rechecks unchanged original exports.

## Category review

Active seconds below are the local runner's recorded interval. They are not
launch time or hosted span elapsed time. Trials remain in their original order;
the failed attempt is included in category statistics.

| Category | Verified successes | Median active seconds | Maximum active seconds | Local estimated USD |
| --- | ---: | ---: | ---: | ---: |
| Crypto | 5/6 | 82.07 | 167.68 | 0.02159 |
| Pwn | 6/6 | 162.41 | 200.49 | 0.04948 |
| Reversing | 6/6 | 137.12 | 259.98 | 0.08553 |
| Web | 6/6 | 15.87 | 35.78 | 0.00652 |
| Forensics | 6/6 | 107.13 | 194.34 | 0.09423 |
| Misc | 6/6 | 69.39 | 335.65 | 0.03254 |

### 1. Crypto

`cry-lupin` trials 1/3 succeeded after saving a large response to a file and
checking its structure. Both reached a missing Python dependency after doing
work, installed it, and reran their computation. Early import checks and saving a
valid intermediate would avoid this particular repetition. The prompt already
asks for intermediate reuse; adding the same generic instruction again is not a
demonstrated fix.

Trial 2, run `b291028aaa4f`, stopped after 47.89 seconds and seven model calls.
After an initial read timeout, repeated connections returned a remote traceback
from JSON loading before useful service data. Tools `0cf0c4317acc5c59`,
`f4efc4aaae51c0aa` and `a0821bef68378d0f` support a persistent service-state
blocker within that attempt. Startup and pre-cleanup container states both say
running, no restart, no OOM and no healthcheck. The final model message separates
the blocker from what could be established. **Unused budget is weak evidence for
premature stopping here.** The error proves a parse failure, not that the file was
empty, nor why it became invalid. An initialization race or an early-disconnect
effect is a hypothesis, not a diagnosed cause.

All three `cry-open-ellipti-ph` trials initially treated a short read deadline as
no output. Later reads obtained data. Trial 3 tool `064504ef2c59fb08` is especially
useful: successive short waits on the same connection eventually received the
banner. In trial 2, generation `237b197cb82e9a31` instead inferred a single
long-lived process from empty short reads. Newline experiments also changed the
amount of waiting, so they do not isolate newline as the cause of the response.
The agent needs to distinguish first-byte delay, an idle read timeout, EOF and
protocol completion. It does not need an interactive terminal to do that.

Recoverable Sage/backend/type mistakes occurred, and trial 2 mixed a successful
result with a trailing Bash-only `${PIPESTATUS[1]}` diagnostic under `/bin/sh`
(`4d1395ae70ebd9fe`, exit 2). The agent correctly retained the useful output.
Trial 1 has six absent export fields across its final two generations/two tools;
the last computation/submission cannot be fully behaviorally reviewed.

**Interpretation:** one service-state failure observed once in this set; repeated
client read/diagnostic mistakes across trials. Do not silently remove the failed
trial or substitute a fresh success. Start a separate infrastructure diagnosis
with a generic delayed-initialization service and early disconnects; preserve
benchmark semantics and avoid private-state reads or automatic resets.

### 2. Pwn

All six succeeded. No target exit comparable to the historical listener failure
was observed. This is useful confirmation on the current images, not proof of
universal service reliability.

`pwn-pilot` varied substantially: 7, 18 and 5 model calls; 34.8, 154.8 and 27.0
active seconds. Trial 1's first construction violated its own size constraint
(`bb3f69b66eb35272`); a compact replacement worked. Trial 2 repeatedly revised
unvalidated low-level assumptions, then made progress with small local probes
and component tests (`472e4a486ba15c20`, `fd0cc2e08cab0bd0`). A partial banner read
also required correction. The efficient third trial used available library
primitives directly. Prefer cheap size/type/assertion checks and verified APIs;
do not encode the successful task-specific approach into the general prompt.

`pwn-roppity` consistently took 15–16 calls and 170–200 seconds. The agent found
contradictions between an initial artifact-based model and observed behavior,
cross-checked independent values, and eventually succeeded. That discrepancy
does **not** prove Docker supplied the wrong application library; replacing
libraries would change benchmark conditions without a diagnosis. Trial 1 also
misread a single receive as all output, then recovered by draining the response
(`44d7061b562c72c8`). Trial 2 invoked an unavailable object attribute
(`88190f4957bceb1c`); trial 1 had a nested quoting edit failure
(`a5b1ea87dabf8845`). These are generated-script issues, not evidence of a broken
shell tool. Initial `checksec` commands suppressed stderr across the pwn runs,
making absent output harder to explain; the traces do not establish whether the
cause was CLI syntax or installation.

**Interpretation:** validation, receive handling and diagnostic visibility recur.
No evidence here justifies relaxing Docker permissions or restoring terminal
sessions, and no failed solve is attributable to the repaired listener.

### 3. Reversing

All six succeeded. `rev-a-walk-through-x86-part-2` used 7/7/5 calls and 48.4/45.0/
38.1 seconds. Missing `ndisasm` in trials 1/2 was recoverable through installed
alternatives. Raw-binary disassembly settings needed correction. A verified
capability list / early availability check is a smaller change than adding a
large toolkit. Successful extraction was checked before submission.

`rev-gibberish-check` took 22/17/18 calls and 260.0/225.8/231.8 seconds. Across
trials, a reconstructed scoring model disagreed with the original executable.
Trial 1 committed to long searches before testing that agreement, incurred two
30-second command timeouts (`9adb6758c2b6bbd0`, `4bc7ac8acf5ded41`), then spent
more time calibrating an inaccurate model. A later repeated search reused a
deterministic candidate instead of obtaining distinct samples. Trial 2's first
large search timed out at 120 seconds (`4d722b0efdd02085`), then inexpensive
structured probes found a working input. Trial 3 checked the original early,
noticed disagreement and used direct bounded validation, without a restart.

Only one disassembly preview overflowed (80,891 bytes); all three trials still
carried considerable disassembly through subsequent requests. Large requests
were expensive but no context cap was reached. All three restarts in the entire
36-attempt baseline occurred here. Saved files survived and the agent recovered,
supporting the existing restart/workspace design. Long computations should set
their own shorter stop/checkpoint interval, keeping controller timeout as a last
bound. Raising every timeout would let incorrect searches run longer.

**Interpretation:** repeated premature commitment to a reconstructed model and
poor search sizing; no demonstrated loss of process/file state or need for more
capabilities. Existing validation instructions were not reliably followed.

### 4. Web

All six succeeded in 4–5 calls. `web-poem-collection` was consistent at four calls
and 11.6–15.3 seconds. `web-shreeramquest` used 5/4/4 calls and 35.8/17.8/16.4
seconds. The agent interpreted observed HTTP responses, adjusted requests within
the allowed endpoint, and submitted observed values. The first shreeramquest
trial spent an extra round on authentication/route behavior; this is a small
efficiency issue, not an infrastructure outage.

Publicly served application text mentioned an internal port, but these trials
stayed in scope. This is positive evidence that current endpoint guidance was
followed here; it does not independently prove enforcement or explain a historical
scope incident. HTTP 403/404 responses are task behavior, not automatically
infrastructure or agent failures.

**Interpretation:** no web-specific change warrants priority from these traces.
Do not add mandatory notes or extra discovery steps to four-call tasks without
measuring their overhead. One selected web task is labeled Easy.

### 5. Forensics

All six succeeded. `for-1black0white` used 7/7/6 calls. Each trial installed a QR
decoder; early capability checks would avoid failed imports, and one small
general decoder could be considered if repeated installation becomes material.
Installation itself took only about 1.7–3.9 hosted tool seconds, so it does not
explain the trial-2 latency outlier. Trials 2/3 initially interpreted a newline
count as record count, then corrected it by parsing the file. This is a concrete
example of checking data structure instead of trusting a shell summary.

Trial 2 has a timing inconsistency: model observation `26c613faea59aecc` spans
132.723 wall-clock seconds, the root spans 156.343, while local active time is
83.346 seconds. Runtime intervals/deadlines use `time.monotonic()`; hosted spans
use wall-clock timestamps. A host sleep or clock adjustment is plausible but
unconfirmed. Do not call this a demonstrated 90-second timeout bypass or blame
the package install. Preserve both clocks and investigate using benign timing
checks before interpreting precise latency effects.

`for-whyos` used 20/16/14 calls and 194.3/151.4/130.9 seconds. Broad matches and
disassembly repeatedly crowded the previews: five truncated outputs over the
three trials, with raw captured totals of roughly 1.34 MB, 1.44 MB and 0.13 MB.
All captures report complete; the capture system did not lose those bytes.
Some output contained historical errors from the supplied log: those are artifact
contents, not errors of this run. The agent later improved its filtering and
connected a narrow observation to relevant context.

Trial 1 submitted two weakly supported candidates (`8214996903e0cce3`,
`127757f646c48df8`) before finding supported evidence. Other trials succeeded
without rejected submissions. Multiple submissions remain legitimate feedback;
the avoidable problem is candidate quality, not the existence of that tool.
Trial 3 also expected radare2 analysis state to persist across new processes and
needed an explicit reanalysis (`c6e9000887cad092`, `9ff65616fc364fc2`). Workspace
files persist; a tool's in-memory analysis does not automatically persist.

**Interpretation:** strongest evidence for selective output, explicit file-backed
analysis state, and supported submissions. Reversing plus forensics account for
about 62% of this baseline's local estimated cost. One selected forensic task is
Easy; the two tasks have very different workload profiles.

### 6. Misc

All six succeeded. `msc-algebra` used 10/9/9 calls and 72.0/59.1/70.2 seconds.
In every trial the agent initially carried an answer from an old connection into
a fresh session, whose question differed. Correct same-connection parsing fixed
the mistake. Several iterations expanded parsing/format handling after observed
rejections; later scripts handled degenerate inputs and finished. This is
**session-state reasoning**, not missing support for persistent terminals:
one script already maintained a full multi-step connection successfully.

`msc-quantum-leap` used 5/5/14 calls and 68.6/34.3/335.7 seconds. Trial 3 broadened
its search substantially. Tool `1edff1c5aa3c7373` materialized and sorted a growing
Cartesian product of candidate combinations and returned `Killed`, exit 137,
after a 97.846-second hosted span. Resource exhaustion is plausible; OOM is not
confirmed by this record. It is not a controller command timeout and did not
restart the solver. A later smaller alternative succeeded. Bounded sampling,
streaming top-k candidates and a small scaling estimate are preferable to a
blanket RAM or time increase.

**Interpretation:** recurring connection-state mistakes plus one expensive search
outlier. Strategy variance is large even when all runs succeed; assess tail time,
calls and cost in addition to success.

## Context and budgets

The largest individual input is **170,959 reported tokens**, in whyos trial 2.
Forensic peaks are 148,811/170,959/140,918; gibberish-check peaks are
97,228/82,663/72,241. These were accepted calls, not aggregate-token counts. This
review does not infer the model/gateway's advertised maximum from accepted input
or claim that long-context quality is unaffected.

Reconstructing the request fields used by `make_responder` from exported inputs
and recorded settings gives a largest serialized request of **567,894 bytes**,
about **27.1% of the current 2,097,152-byte cap**. This is an audit reconstruction,
not a newly instrumented pre-request byte measurement. The old 524,288-byte guard
would bind for five exported requests in this baseline. Keep the current raised
cap; these data do not justify raising it again. More raw output would increase
replay cost rather than necessarily improve evidence quality. Try selective
output first; compaction remains a separate lossy mechanism to evaluate later.

No attempt reached 600 seconds, 40 model calls, 80 tool calls, a model-input stop
or an incomplete-model-response stop. The largest model/tool count is 22/22;
maximum active time is 335.65 seconds; maximum reported output per generation,
including reasoning, is 3,962 tokens. This is headroom evidence on these tasks,
not proof the limits suit all tasks. There is no top-level API timeout among these
36. Apart from the clock-anomalous span, the largest hosted generation duration
is 40.802 seconds. Do not estimate request p95 or gateway performance from that
one anomalous span without reconciling clocks.

## Prioritized candidates

P1 = address first; P2 = next / conditional; P3 = defer. Ease describes the full
change and meaningful verification, not merely editing a prompt/config line.
These are proposals, not approved implementations or measured gains.

| Rank | Priority | Candidate and simplest proposal | Support / likely value | Ease | Verification and limits |
| --- | --- | --- | --- | --- | --- |
| 1 | P1 | Diagnose service initialization and disconnect behavior; record safe lifecycle/readiness evidence | Sole failed attempt has repeated remote JSON errors while container stays running | Moderate diagnosis; fix unknown | Generic delayed-initialization/early-close tests first. No universal active probe: connecting can mutate state. No auto-reset or task-private inspection. |
| 2 | P1 | Clarify same-session buffered reading: distinguish delayed data, idle timeout, EOF and complete response | Repeats across crypto, pwn and all algebra trials | Easy prompt/tool-contract clarification; moderate optional helper | Synthetic delayed/split-response and randomized-session examples using existing tools. Prefer scripts first; add helper only if clarification fails. No new terminal framework. |
| 3 | P1 | Make small independent validation and bounded search operational: test scale, cap iterations/memory, checkpoint before expensive work | Gibberish-check timeouts, pilot revisions, quantum-leap Cartesian-product kill; recovery currently works | Easy small workflow experiment; moderate reliable measurement | Revise existing validation instructions rather than duplicate them. Measure contradictions caught before search, command timeouts/137, calls/time/cost; do not add task-specific algorithms. |
| 4 | P1 | Audit required export payloads separately from structural evidence; retain safe local failure categories | Six fields absent despite complete counts; a separate later recheck lacked its final error/export | Moderate | Synthetic missing-payload and failed-export fixtures; preserve original exports, distinguish behavioral visibility from outcome verification. No raw exception bodies or false claim that all event nulls are errors. |
| 5 | P2 | Reduce printed noise; save/search files, print counts and bounded relevant excerpts with diagnostics | Whyos 5 preview truncations; reversing/forensics dominate cumulative context/cost | Easy prompt refinement; moderate generic output change if later needed | Track peak input tokens/bytes, repeated excerpts, overflow/retrieval and verification success. Current capture already works; do not raise preview cap as first remedy. |
| 6 | P2 | Check imports/tool interfaces early; keep `/bin/sh` diagnostics visible; optionally add one repeatedly needed general dependency | Missing decoder/reedsolo, unavailable disassembler/API, quoting/Bash-only errors | Easy checks; moderate image/dependency maintenance | Verify exact interfaces; compare saved install time with image cost. No broad toolkit expansion or guarantee a command succeeds because outer exit is zero. |
| 7 | P2 for measurement | Reconcile monotonic durations with hosted wall-clock spans; add safe duration metadata if needed | One 132.7-second model span inside 83.3 active seconds | Easy discrepancy detection; moderate diagnosis | Benign clock/sleep checks; retain both intervals. Do not change deadlines or infer provider SLA from mismatched clocks. |
| 8 | P2 conditional | Brief revisable plan; optional notes recording facts, hypotheses, artifact paths and next test only when complexity warrants | Useful candidate for model drift in long runs; direct evidence of forgetting is weak | Easy behavior edit; benefit unproven | Existing tools and per-attempt files only. Measure note overhead/accuracy and whether it changes choices. A joint plan/validation/notes edit measures the package, not notes alone. |
| 9 | P3 | Improve visible purpose sentences only if needed for trace usability | 12 returned function-call generations lacked requested visible purpose text | Easy prompt; enforcement adds complexity | Low priority: tool inputs/results remain available. Avoid forcing extra calls or treating missing narration as solve failure. |
| 10 | P3 / defer | Automatic continuation, larger budgets, stronger model, compaction, new framework or relaxed isolation | No bound exhausted; justified service blocker; existing tools solved long tasks | Config edits easy, full validation/cost potentially substantial | Revisit with a specific binding limit or demonstrated lost opportunity. More budget/permissions would not by itself repair server JSON, read logic or unbounded search. |

Recommended next behavior experiment: a **small session/validation/output
clarification**, with brief optional planning if desired, using the existing
tools and budget. Optional file notes are most credible for long, branching
attempts; mandatory notes on every short task add overhead. If the user wants a
notes-only comparison, isolate notes from the other changes and label the
hypothesis accordingly. Infrastructure/export repairs should be separately
verified and versioned so their effects are not credited to prompt changes.

## Comparison limitations and a defensible follow-up

1. **Baseline only.** There is no planning/notes treatment result yet. This review
   generates hypotheses; it cannot estimate improvement caused by any proposal.
2. **Ceiling and sample size.** 35/36 is 97.2% observed success, not a precise
   deployment rate. There are only 12 distinct tasks, repeated three times;
   trials sharing task structure are not 36 independent problem samples. Two
   tasks per category cannot establish category-wide effects. Published Hard
   labels did not imply uniformly difficult agent runs.
3. **Service blocker is not censored away.** Keep 35/36 in the original outcome
   table, separately annotate the service-observed blocker, and report any fresh
   reproduction as another condition. Do not treat it as a proven agent failure
   or adjust the denominator after seeing it.
4. **Tuning reuse.** The user authorized development and original test-list tasks
   as practice. Human/assistant inspection and future tuning make them unsuitable
   as fresh holdout evidence. Original scored results are unchanged. No reviewed
   solution details should enter the generic prompt.
5. **Visibility.** Six missing fields in one successful trace prevent complete
   reconstruction of its tail. Encrypted reasoning replay is not readable
   reasoning; this review assesses observable decisions, not internal thought.
   Count-complete traces do not guarantee payload completeness.
6. **Timing and environment.** One wall/monotonic discrepancy is explicit. Host
   sleep/load, AMD64 emulation, changing package downloads and gateway/cache
   state were not experimentally controlled. Identical recorded images/source
   help, but do not eliminate those factors. Active, attempt-total, launch-total
   and span times must stay distinct.
7. **Costs.** Use the same local rate calculation or native generation costs in
   both conditions and retain complete/known-usage labels. Cached input and cache
   writes vary; estimates are not invoice reconciliation. A lower token count
   need not imply an equal percentage latency improvement.
8. **Separate incidents.** The later `scored-recheck` stop is not one of these
   36. Its durable error/export gap informs observability work, not this solve
   denominator. No automatic retry or replacement was performed during review.
9. **Human review status.** These are assistant-assisted, trace-supported labels.
   A teammate should spot-check consequential claims, especially service cause,
   kill cause and causal improvement claims; none is established by keyword
   counting alone.

For an approved follow-up, keep all 12 tasks and all three trials; freeze source,
prompt, model settings, dataset and images for each condition. Record any common
infrastructure repair in both conditions, or rerun a fresh matched baseline if it
changes conditions materially. Keep failures and planned stopping policy. Report
per-task outcomes plus calls, peak context, estimated/native cost, command
timeouts/restarts, unsupported submissions, notes overhead and median/tail active
time. Pair by task and show every trial; trial numbers do not imply matched random
seeds. Use a later unreviewed set for generalization. A simple before/after remains
exploratory because time/order/cache and host state are not randomized controls.

## Per-trial coverage

The following table records the principal behavioral observations for every
attempt. Observation IDs above and in the table identify the relevant entries in
the original trace. Full source paths, hashes and trace links are in review.json.

| Challenge | Trial | Run | Outcome | Model/tool calls | Active seconds | Review finding |
| --- | ---: | --- | --- | ---: | ---: | --- |
| cry-lupin | 1 | `98e5ac9ca868` | success | 7/7 | 66.03 | Saved response and parsed its structure; missing dependency triggered repeat computation (2e33d2289ee326af). |
| cry-lupin | 2 | `b291028aaa4f` | completed_without_success | 7/6 | 47.89 | Remote JSON-load error persisted across retries; container remained running; final stop explained blocker (0cf0c4317acc5c59). |
| cry-lupin | 3 | `339dd07d8012` | success | 7/7 | 70.39 | Saved response; missing dependency discovered late, then corrected (afb385f452ca9d09). |
| cry-open-ellipti-ph | 1 | `185b0ecc36f8` | success | 9/9 | 93.75 | Initial short read and numeric-conversion error recovered; final two generations/tool payloads incomplete in export. |
| cry-open-ellipti-ph | 2 | `96c820e46c74` | success | 11/11 | 144.72 | Empty short reads led to unsupported process-lifetime inference; later type/shell diagnostics recovered (4d1395ae70ebd9fe). |
| cry-open-ellipti-ph | 3 | `fb9fa5e1d1bd` | success | 14/14 | 167.68 | Same-socket incremental reads eventually received delayed banner; saved samples; backend/index errors corrected (064504ef2c59fb08). |
| pwn-pilot | 1 | `4373f926e73d` | success | 7/7 | 34.77 | Initial construction exceeded known size; compact correction worked (bb3f69b66eb35272). |
| pwn-pilot | 2 | `62c62407c81c` | success | 18/18 | 154.77 | Partial banner plus several unvalidated assumptions; component/local tests eventually corrected them (472e4a486ba15c20). |
| pwn-pilot | 3 | `8f0b8d86a0f4` | success | 5/5 | 26.96 | Available library primitives and short script gave efficient completion; no significant tool/infrastructure issue observed. |
| pwn-roppity | 1 | `e9d24da3da06` | success | 16/16 | 170.05 | Independent measurements resolved a mismatch; quoting error and single-read output assumption recovered (44d7061b562c72c8). |
| pwn-roppity | 2 | `de19c0726c74` | success | 15/15 | 175.43 | Revised mismatched assumptions; unsupported library attribute and repeated variants added work (88190f4957bceb1c). |
| pwn-roppity | 3 | `5c1190692c19` | success | 16/16 | 200.49 | Invariants and component probes supported recovery; several model revisions/variants before success (58f84c70bd25fb14). |
| rev-a-walk-through-x86-part-2 | 1 | `05d5dcc29926` | success | 7/7 | 48.42 | Missing disassembler and incorrect raw-binary settings; installed alternative worked (f768d490079d43f4). |
| rev-a-walk-through-x86-part-2 | 2 | `8fccf5cf92e6` | success | 7/7 | 45.05 | Missing disassembler, then addressing adjustment needed; recovered with existing tools (c695583625c1ad08). |
| rev-a-walk-through-x86-part-2 | 3 | `013730a57a0b` | success | 5/5 | 38.15 | Used available disassembler; concise successful path with observed-result validation. |
| rev-gibberish-check | 1 | `4ed5c5203c6d` | success | 22/22 | 259.98 | Large dump; unvalidated model; two search timeouts/restarts; repeated deterministic candidate; later direct validation recovered (9adb6758c2b6bbd0). |
| rev-gibberish-check | 2 | `dfd4e9e69e20` | success | 17/17 | 225.81 | Long disassembly context; 120-second search timed out; cheaper structured probes then worked (4d722b0efdd02085). |
| rev-gibberish-check | 3 | `c648f18c4fe6` | success | 18/18 | 231.83 | Original checker contradicted reconstruction early; direct bounded checks recovered without timeout (f267c21089171c50). |
| web-poem-collection | 1 | `cd84bec2d6a6` | success | 4/4 | 15.31 | Four-call completion; relevant HTTP warning guided checks; no significant agent/runtime problem observed. |
| web-poem-collection | 2 | `d6affadbbfb0` | success | 4/4 | 13.66 | Four-call completion; some routine negative route checks; no significant runtime problem observed. |
| web-poem-collection | 3 | `c9269ce55025` | success | 4/4 | 11.63 | Four-call completion; supported submission; no significant runtime problem observed. |
| web-shreeramquest | 1 | `00b24d636143` | success | 5/5 | 35.78 | HTTP authentication/route distinction cost one extra round; all work stayed at allowed endpoint. |
| web-shreeramquest | 2 | `59aeb000aff5` | success | 4/4 | 17.78 | Short observed-response-driven recovery; no infrastructure issue or scope incident observed. |
| web-shreeramquest | 3 | `e9d590d43641` | success | 4/4 | 16.43 | Short observed-response-driven recovery; no infrastructure issue or scope incident observed. |
| for-1black0white | 1 | `f7ccc5d7e114` | success | 7/7 | 31.03 | Early import inventory; decoder installed; alternative rendering checked (70c20c42634e0ce9). |
| for-1black0white | 2 | `fd8707a7237b` | success | 7/7 | 83.35 | Newline-count interpretation corrected; missing decoder installed; hosted clock span conflicts with active duration (26c613faea59aecc). |
| for-1black0white | 3 | `646ee8d792fe` | success | 6/6 | 21.20 | Record count corrected by parsing; missing decoder installed; shorter six-call completion. |
| for-whyos | 1 | `04dc1fa5c1b9` | success | 20/20 | 194.34 | Three noisy preview overflows, two weak rejected submissions, then selective search recovered (8214996903e0cce3). |
| for-whyos | 2 | `ea4c42ebf234` | success | 16/16 | 151.36 | Two broad preview overflows and binary-tool invocation errors; later narrow evidence/context check supported submission (6b21013a9c6ff7b4). |
| for-whyos | 3 | `1be076c681aa` | success | 14/14 | 130.91 | One preview overflow; in-memory tool analysis assumed persistent; reanalysis/narrowing recovered (c6e9000887cad092). |
| msc-algebra | 1 | `fc2817b9ddca` | success | 10/10 | 72.05 | Answer carried to new randomized connection; format/parser revisions; same-session automation eventually completed. |
| msc-algebra | 2 | `7efb161a344d` | success | 9/9 | 59.15 | Answer carried to new randomized connection, then corrected; handled later degenerate input; finished. |
| msc-algebra | 3 | `a6ad9c70d544` | success | 9/9 | 70.21 | Answer carried to new randomized connection; decimal format and identity handling corrected; finished. |
| msc-quantum-leap | 1 | `e24e5567c15d` | success | 5/5 | 68.56 | Several bounded transformations; small alternative completed; no runtime issue observed. |
| msc-quantum-leap | 2 | `2255ac8e6474` | success | 5/5 | 34.29 | Short bounded experiments and successful observed-result submission; no runtime issue observed. |
| msc-quantum-leap | 3 | `b95a2f974f81` | success | 14/14 | 335.65 | Broad search materialized candidate product; command killed with 137 after 97.846 hosted seconds; later smaller alternative worked (1edff1c5aa3c7373). |
