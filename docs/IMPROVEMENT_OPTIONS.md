# Agent improvement options

**Historical decision record, November 7–11.** Several proposals below have since
been implemented. Use [current status](../PROJECT_STATUS.md) for selected settings,
active issues and next work; [project history](PROJECT_HISTORY.md) and
[experiments](EXPERIMENTS.md) record what was approved, implemented and verified.
Priorities and feasibility judgments below describe their dated review, not a
new implementation plan or authorization. No proposal text is discarded here.

November 7, 2026. Decision review requested by the user after discussion of the
latest development traces, prompt structure, output handling, solver information,
models/reasoning, the NYU reference prompt, and plans/notes. These are proposals,
not implemented changes or authorization for live comparisons.

**November 11 infrastructure handoff:** repeated target container/listener exits
remain unresolved. See [TARGET_PROCESS_ISSUE](TARGET_PROCESS_ISSUE.md) for the
four-attempt evidence, generic native/emulated checks, resource audit and suggested
next steps. Missing init, emulation and insufficient target quotas are unproven
causes; no service fix is selected or implemented. This later issue is separate
from the dated agent-behavior proposals below.

**November 8 implementation update:** the user-approved combined first fix is now
implemented and synthetically verified. See [milestone evidence](https://github.com/ryanbanko/590_ctf_agent/blob/aedfd62cf8379adee73a30546592036af6f82a42/evidence/agent-first-fix/README.md).
The dated proposals below preserve the decisions before implementation. The
[subsequent eleven-ID development rerun](../evidence/agent-first-fix-batch/README.md)
completed on `e7e366c` with 6/11 successes, matching the historical baseline total.
Summary/export checks are complete, including a supplemental export recovering
missing `rev-tablez` payloads. Detailed behavioral review remains pending; this
single rerun does not establish a causal improvement.

The [user follow-up](#user-follow-up-explanations-and-current-recommendations)
below records later preferences, successful read-only Duke model discovery and
the more detailed output-capture proposal. It supersedes the earlier unavailable-
gateway finding and revisits the full-output priority without erasing this matrix.
The latest [initial-change versus experiment classification](#initial-baseline-changes-versus-separate-experiments)
also clarifies existing connection guidance and published reasoning-token advice.

## Basis and interpretation

The [eleven-attempt review](../evidence/development-trace-review/README.md) found
six verified successes and five voluntary unsuccessful endings. The failures
used 5–9 model requests and 26.9–46.4 active seconds under a 40-request/600-second
profile. No tool output was runtime-truncated, and no scope-denial, outer command
timeout or cleanup failure was recorded in that batch. Earlier failures remain
historical evidence, not observations under every part of the current runtime.

Settings at the November 7 review were `gpt-6-luna`, low reasoning, 4,096 generated tokens/request,
60-second requests, 512 KiB serialized model input and 64 KiB tool output. The
agent already receives full public conversation history and native response-item
replay. Workspace files are available through tools but are not automatically
inserted into model context. A text-only assistant response ends the attempt.

Potential benefit below means a plausible gain, not an established effect size.
Observed mistakes establish a behavior gap, not that a prompt edit will fix it.
Priority balances that evidence with implementation, verification, ongoing
maintenance, API overhead and the class-project schedule. Ease includes useful
verification, not merely the number of edited lines. No numerical scoring or
performance predictions are warranted by one attempt per selected task.

**P1:** first candidate or inexpensive preparation. **P2:** separate small
experiment if warranted. **P3:** optional/conditional. **Defer:** weak current
evidence relative to its cost or complexity.

## Prompt, information and working method

| Change | Potential benefit and evidence | Ease / maintenance | Overhead and main risk | Priority |
| --- | --- | --- | --- | --- |
| Independent validation and diagnosis before stopping | High plausible value; supplied checker unused, copied data reused in self-checks, and unverified blocker conclusions recur. Strongest direct behavioral evidence. | Easy prompt edit; very low maintenance. Actual model effect needs live follow-up. | More diagnostic actions can help or waste calls; preserve justified stops and all enforced limits. | **P1, first behavior experiment** |
| Concise verified solver description | Moderate plausible value; new toolkit is poorly advertised in the system prompt. NYU defaults illustrate clear environment/tool information. No proof that missing awareness caused these five failures. | Easy; maintain a short verified capability list when the image changes. | Extra prompt tokens; stale or overbroad tool claims can mislead. | **P1, inexpensive preparation** |
| Clear prompt sections and less duplication | Small-to-moderate plausible clarity gain; current prompt is already short and contains useful recovery rules. Formatting alone is not a demonstrated fix. | Easy; preserve original rules while reorganizing. | A large rewrite may create contradictory requirements and make attribution difficult. | **P1 as part of drafting, keep small** |
| Focused output and file-based intermediate data | Moderate plausible value; bulky dumps and manual transcription appeared in traces, including a concrete transcription error. | Easy prompt/tool-description guidance using existing commands and files. | Over-filtering can hide useful evidence; preserve errors, anomalies and completion output. | **P1 alongside validation guidance** |
| One-script stateful interactions and internal network deadlines | Moderate targeted value; stale connection state and a newline-delimiter error occurred, then recovered. Existing tool description already covers much of this. | Easy clarification; no session service needed. | Excessively short internal timeouts can cause unnecessary failures. | **P1 clarification, avoid duplication** |
| Short, revisable plan for multi-stage tasks | Moderate plausible value; may keep an unresolved contradiction connected to its next test. Current traces do not isolate a planning failure. | Easy prompt experiment; no new tool/schema. | Tokens and rigid planning can slow simple tasks or anchor a bad approach. | **P2, optional initially** |
| Optional per-attempt notes file | Moderate potential for longer attempts; limited evidence of actual forgetting in these short runs. | Easy with existing tools; no application memory system. | Writes/reads consume calls, file contents are not automatically in context, and incorrect assumptions can become entrenched. | **P3, use when complexity warrants** |
| Safe remaining-time/call feedback | Moderate possible value; could support more informed stopping. No evidence the agent stopped because it misunderstood its budget. | Moderate: source values from trusted existing state, expose only public counters, and test boundaries/tracing. | Extra observation content and another maintained interface; budget availability alone does not make a next action useful. | **P3** |

Keep notes as concise facts with evidence references, labeled hypotheses, attempts
and results, unresolved contradictions and the next test. Update at meaningful
discoveries or strategy changes. Keep them inside one disposable attempt. Do not
introduce cross-attempt memory into independent evaluation trials.

Keep operational contracts in tool descriptions and stable overall guidance in
the system prompt. The public task already contains files and endpoints. A
category-specific template system is unnecessary to communicate a few verified
tools. Preserve the existing short visible purpose sentence and evaluator-only
success confirmation; they already work.

## Models, budgets and continuation

| Change | Potential benefit and evidence | Ease / maintenance | Overhead and main risk | Priority |
| --- | --- | --- | --- | --- |
| Same model, low to medium reasoning | Potentially high; mathematical mistakes and weak diagnosis make it a credible hypothesis. No controlled result yet. | Easy configuration change; low maintenance. Verify gateway acceptance before a challenge comparison. | Increased reasoning tokens/latency; may encounter existing per-request bounds. | **P1 separate experiment after prompt review** |
| Stronger model at a supported effort | Potentially high, possibly larger than a prompt gain; entirely unmeasured on this setup. | Small config edit, moderate operational verification: access, Responses/tool compatibility, prices and usage. | Unknown gateway availability, cost/latency and changed behavior. | **P2** |
| More extreme effort settings | Possible value on hard tasks; no evidence that medium is insufficient yet. | Easy config, but each setting adds evaluation work. | Higher latency/output use with uncertain marginal gain. | **P3 after medium results** |
| Increase generated-token allowance or request timeout | Enables a valid reasoning/model comparison if current bounds constrain it; not an independent remedy demonstrated by this batch. | Easy config; moderate budget/termination verification. | Greater potential cost and waiting; changing bounds alongside effort confounds a single-variable claim. | **Conditional prerequisite** |
| One bounded continuation after a text-only unsuccessful reply | Moderate-to-high possible effect on premature endings; NYU's reference loop continues. Benefit remains speculative. | Moderate: change loop policy and verify terminal events, call accounting, trace export, and legitimate final responses. | Can turn a justified stop into repetition; must never bypass success, incident or resource stops or reset the deadline. | **P2, isolate from prompt/model changes** |
| Larger total wall/call/input limits | Low demonstrated value now; latest failures did not reach these guards. | Easy config, but makes comparisons and maximum resource exposure larger. | More spending/context without necessarily improving decisions. | **Defer until a measured limit binds** |

OpenAI documents [Luna's supported reasoning settings](https://developers.openai.com/api/docs/models/gpt-6-luna).
Its [reasoning guide](https://developers.openai.com/api/docs/guides/reasoning)
states that the generated-token allowance includes reasoning and visible output;
an exhausted allowance can produce an incomplete response. Our current adapter
stops on incomplete model responses. Therefore, a more capable configuration
must have enough room to answer, and its 60-second request timeout also needs
attention. This is a feasibility check, not a recommendation to adopt a large
generic allowance automatically. If bounds need adjustment, record the combined
configuration change or use common adequate bounds in both comparison conditions.

[Official model-selection guidance](https://developers.openai.com/api/docs/guides/model-selection)
supports comparing models on representative tasks rather than assuming a winner.
GPT-6.1 Sol is a candidate, not a selected replacement. The preceding read-only
Duke listing attempt was unreachable; current gateway availability and rates are
unverified for alternatives. No new gateway request or model call was needed for
this decision review. Models have not been changed.

## Output/runtime mechanisms and larger alternatives

| Change | Potential benefit and evidence | Ease / maintenance | Overhead and main risk | Priority |
| --- | --- | --- | --- | --- |
| Explicit omission marker and retained/omitted byte information | Moderate clarity when truncation happens; current flag/count exist but head/tail text is joined. No latest-batch truncation. | Easy-to-moderate bounded-reader change and focused output checks. | Markers must fit a clearly documented observation bound and remain distinct from actual process output. | **P2, useful small runtime improvement** |
| Reserve some diagnostic stderr space | Potential value if stdout overwhelms a combined budget; an older milestone had missing diagnostic output. Current reader differs and latest batch does not show this failure. | Moderate stream-allocation policy and meaningful mixed-stream checks. | Reserving space may discard useful stdout; cannot reconstruct complete chronology. | **P3 if reproduced on current reader** |
| Automatically save full command output | Useful if omitted sections repeatedly need retrieval; ordinary redirection already works. | Moderate-to-hard for robust solver-side capture, bounded storage, failure handling, ownership and cleanup. Avoid restoring the old artifact/RPC machinery. | Disk growth and new process/output behavior; source-command truncation still cannot be recovered. | **Defer; use explicit workspace logs first** |
| Raise the 64 KiB tool-output cap | Low demonstrated value; no latest-batch tool truncation. | Requires code and config change: current validation explicitly caps output at 64 KiB. Then verify capture and downstream bounds. | More repeated context and cost, possibly earlier model-input stops. | **Defer** |
| Context compaction or automatic file/notes injection | Potential value for long histories; historical input-limit failures occurred under much smaller settings. Current batch does not show input exhaustion. | Moderate-to-hard: preserve native replay/tool links and public-data boundaries. | Lossy summaries, duplication, unsupported assumptions, larger trace audits. | **Defer until measured** |
| Dedicated planner, extra tools, restored interactive sessions or a new framework | No demonstrated need for the current failure pattern; existing scripts/tools solved multi-step tasks. | High total system/verification/maintenance burden compared with prompt/config changes. | More state, dependencies and control paths; distraction from independent validation. | **Defer** |
| Move prompts to Langfuse / copy NYU's template infrastructure | Versioning or templating may help at greater scale; current code prompt already has Git/source-hash provenance and native tool schemas. | Moderate integration and maintenance; little immediate behavior benefit. | Another configuration source and synchronization problem. | **Defer; retain code prompt** |

The [NYU source comparison](REFERENCES.md#nyu-baseline-prompt-comparison--november-7)
is complete. Use its clarity as reference, adapting facts to this runtime. Its
permissions, private-derived flag-format assumptions, paths and extra servers
are not requirements or compatible defaults to copy.

## Recommended sequence and evidence

1. **Draft and review a compact prompt candidate.** Prioritize independent checks,
   calibrated blocker claims, accurate environment information, focused output and
   avoiding manual transcription. Keep optional planning/notes explicit and small;
   for cleaner attribution, test their additional effect separately. Preserve all
   scope, verification and stopping boundaries. This is the best first investment
   because implementation is small and the behavior target is concrete.
2. **Run a separately authorized small development follow-up.** Include relevant
   failures and at least one simple success to watch overhead/regression. Freeze
   images, source/settings and attempt counts within a condition; retain failures.
   If the prompt includes several refinements, describe it as a combined prompt
   candidate rather than attributing the result to one sentence.
3. **Compare medium reasoning with a fixed prompt.** Keep other settings common
   where feasible, check incomplete responses/timeouts, and record changed bounds.
   Consider a stronger model next if the quality gain warrants the operational cost.
4. **Select a further intervention from new evidence.** A bounded continuation,
   concise plan or omission marker is a small separate option. Full output capture,
   memory systems and larger execution changes need stronger evidence of need.

For prompt/plan/continuation experiments, inspect independent checker use,
evidence-based revisions, duplicate actions, unexplained endings and valid stops,
alongside trusted success, model/tool calls, active/launch time, available tokens,
estimated cost and evidence/cleanup completeness. For output changes, use focused
synthetic checks of exact bounds, clear omission, stderr behavior, invalid UTF-8
and timeout diagnostics; a full benchmark campaign is not needed to establish
the mechanical contract. Model changes additionally need provider compatibility
and accounting checks. New live checks require authorization.

One trial per condition is exploratory. These development comparisons support
choosing the one eventual frozen configuration described by the later course
guide; they do not require a second full scored campaign. Keep the ten held-out
IDs untouched, original failures intact and report/demo work separate.

Documentation synchronization, trace review and the generic NYU prompt review
are already complete. This options review adds no runtime/prompt/model changes,
new dependencies, new tests or model calls. The publication-history follow-up
remains separate before public sharing.

Verification: all 69 local links/heading targets across this document and the
updated status passed; runtime/configuration/test hashes still match the reviewed
batch; `git diff --check` passed. No runtime tests were rerun for this design review.

## User follow-up: explanations and current recommendations

November 7. The user supports prompt/environment improvements, wants concrete
explanations of validation, networking and output, favors retaining full command
output if practical, requests guidance on planning/notes, and asks about stronger
models and larger token allowances. Implementation remains separate from this
research/design discussion.

Independent validation means checking the derivation against evidence that can
expose its mistakes: a supplied public checker, original artifact bytes or an
independently sourced round-trip test. Reusing a wrong copied table in both a
solver and its test does not provide that protection. Use inexpensive checks when
available; evaluator submission remains the authority on actual success. The
prompt should generalize these habits rather than encode challenge-specific fixes.

Describe the verified Linux AMD64/Python environment, representative tools,
writable files/packages, per-attempt reset and process/connection reset on outer
command timeout. A new shell invocation does not resume a previous socket client.
Read the current server prompt and solve its transaction in the same script when
state matters. Internal connect/read timeouts allow the script to diagnose a
stalled operation; they differ from the outer 120-second command allowance and
600-second attempt deadline. Exact timeout values should fit the interaction.

For output and intermediate data, save a large result once in a workspace file
and inspect selected sections or compute summaries. Parse/carry data through
files or program variables instead of manually copying long values. Preserve
stderr and unexpected/completion output. Runtime truncation currently keeps a
bounded beginning/end within a shared 64 KiB raw-byte budget, reporting a flag and
observed byte count. It does not save the missing middle. Commands that filter
their own output can discard information before the controller ever receives it.

### Planning and notes

Anthropic's [agent architecture guidance](https://www.anthropic.com/research/building-effective-agents)
distinguishes fixed workflows from agent-directed decisions and favors simple
patterns before more orchestration. OpenAI's older, model-specific
[GPT-5.1 prompting examples](https://developers.openai.com/cookbook/examples/gpt-5/gpt-5-1_prompting_guide)
use concise milestone plans for complex work and permit skipping them for simple
work. These are design references, not requirements for Luna or this course.

For this agent, planning would mean a short provisional sequence of outcomes,
revised when observations change the approach. It helps coordinate multiple
dependencies and makes the next discriminating test explicit. It is less useful
for a straightforward three-call task; an overly detailed upfront plan can anchor
the wrong hypothesis. Start with brief plan text alongside an ordinary tool call,
not a separate planner model or a mandatory new tool. The existing loop already
adapts action by action; a plan would add explicit task organization.

Notes hold established observations, evidence references, labeled hypotheses,
attempts/results, unresolved contradictions and next tests. A plan is forward-
looking; notes preserve what was learned. Anthropic's
[context-engineering article](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents)
describes structured notes retrieved later to support extended work. In our
implementation, an optional workspace notes file can help after several
approaches, but it must be read to re-enter model context. It does not reduce
context size while the full history is still replayed. Update it at useful
checkpoints; keep it disposable per attempt. No compaction is proposed now.

### Model candidates and tokens

Read-only Duke `/v1/models` and `/v1/model/info` requests succeeded, listing
41 models including the three candidates below. Their advertised reasoning and
function support do not prove actual Responses compatibility. Metadata rates match
the official standard prices checked during this research. No generation calls.
[Filtered metadata and calculation assumptions](../evidence/development-trace-review/gateway-candidates.json).

| Candidate | Input / cached input / output USD per million | Same observed eleven-attempt token counts |
| --- | --- | ---: |
| GPT-6 Luna | 0.10 / 0.01 / 0.50 | $0.01823 |
| GPT-6.1 Sol | 2.00 / 0.10 / 10.00 | $0.34725 |
| GPT-6 Astra | 10.00 / 1.00 / 50.00 | $1.82337 |

These are fixed-volume illustrations, not forecasts or account-balance checks.
Actual models/efforts change usage, caching, latency and outcomes. Official pages:
[Luna](https://developers.openai.com/api/docs/models/gpt-6-luna),
[Sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol),
[Astra](https://developers.openai.com/api/docs/models/gpt-6-astra).
Luna medium is the inexpensive incremental experiment; Sol medium is a reasonable
stronger-model candidate for this project. Astra is a premium comparison option.
No model or configuration is selected or changed by this document.

The current 4,096 generated-token cap is **per response**, including reasoning and
visible output. It is not an aggregate per-attempt token limit. Model input has
a separate 512 KiB serialized-byte bound; attempts have wall/call limits and no
aggregate token or local spending cap. These are project choices. An experimental
8,192-token response allowance is reasonable to consider for medium effort, with
16,384 a further option if incomplete responses show a need. Allocated capacity
is not automatically consumed, but it permits greater usage. The request timeout
can also constrain higher effort. Keep other guards initially and record changed
bounds honestly in comparisons; more room alone does not explain the latest
voluntary early stops.

### Full command-output retention and continuation

Full-output retention is feasible and has value for trace review as well as agent
retrieval. Two requirements differ: private retained artifacts for the human
reviewer, and files the solver agent can inspect during the attempt.

| Approach | Human review after cleanup | Agent can retrieve omitted sections | Integration |
| --- | --- | --- | --- |
| Explicit stdout/stderr redirection into workspace files | Requires preserving selected files before cleanup | Yes, through existing commands | Simplest; agent must choose it before output is lost |
| Stream Docker stdout/stderr into private run files while retaining bounded observations | Yes, including received timeout output | Not automatically; host files remain outside solver | Small extension to current bounded reader |
| Automatic solver-side command logs, paths in tool results, trusted export before cleanup | Yes if export succeeds | Yes, through existing commands | Moderate wrapper/capture/export work; preserve exit, stdin, timeout and background-process behavior |

For the first implementation proposal, automatic host capture plus existing
workspace-file guidance is the smallest useful addition. If automatic in-attempt
retrieval is also a goal, solver-side logs should be designed explicitly instead
of implying a host path is accessible. Keep raw artifacts attached to existing
records, not a second detailed trace backend. Use safe per-call paths and bounded
capture storage, keep draining after a retention cap, and mark truncation,
write errors and timeout/incomplete capture. A file called "full output" must not
silently be partial. Preserve the bounded model observation and explicit omission
marker; files cannot recover bytes that a command never printed.

Text-only continuation remains secondary. A possible experiment permits one
budgeted re-evaluation after a voluntary unsuccessful final reply. It must leave
success, incidents, failure handling and resource stops terminal, preserve the
deadline/counters, and avoid treating every justified stop as wrong. It addresses
stopping policy separately from reasoning quality, planning and memory.

Next: review the prompt draft scope, model/response-budget candidate and desired
output-retention behavior as concrete milestones. No implementation, challenge
attempt, new test or compaction work occurred in this follow-up.

Follow-up verification passed for 72 local links/heading targets, the three
filtered gateway metadata records and cost calculations, unchanged reviewed
runtime/configuration/test hashes, and `git diff --check`. Raw account credentials
and unfiltered gateway configuration were not copied into the evidence.

## Initial baseline changes versus separate experiments

The user requested a concrete separation of initial improvements from experiments.
This classification is a proposal, not implementation approval or a live-run plan.

**Initial baseline package:** concise verified-environment/prompt organization;
specific validation and diagnostic habits; clearer connection/deadline guidance;
focused output and programmatic intermediate data; an unambiguous truncation
contract; and, if adopted, bounded raw stdout/stderr retention in private run files.
Use existing functions and tools. No planner, notes subsystem, session service,
extra model or new detailed tracing backend is required for this package.

Independent validation would be agent behavior inside the solver: use a supplied
public checker, compare a transformation against original input, or independently
re-extract artifact data, then report a relevant assertion/mismatch. The controller
cannot universally verify arbitrary reasoning. No new generic validation tool or
host-side challenge execution is proposed; the trusted evaluator keeps its current
role. Contradictions should trigger a focused diagnostic rather than simply more
repetition. An available inexpensive check is preferred, not mandatory proof of
every candidate before submission.

Connection guidance was partly present already: `run_command` states that each
call starts a new shell, cross-call terminal sessions are unavailable, and shorter
internal network deadlines should be used. The missing explicit link is that
randomized prompts/session state belong to the current connection, so their
read/compute/respond sequence should stay in one client script. Earlier interactive
session machinery was deliberately removed in the approved simplification. The
trace demonstrates a misuse despite partial documentation, not a newly discovered
need to rebuild that machinery. Clearer instructions still require behavioral
verification; they cannot guarantee compliance.

For truncation, retain bounded previews but explicitly distinguish beginning,
omitted middle and end, with raw byte counts and unchanged exit/timeout semantics.
Never imply separated excerpts were contiguous. Private raw stream files are the
smallest automatic archive option; they improve human review but do not make host
files readable by the solver. Existing workspace redirection supplies agent-readable
files. Automatic solver-side logs with export remain a possible later engineering
milestone if in-attempt retrieval without prior redirection is required. Test
capture limits, mixed streams, invalid UTF-8, timeout partial output and storage
failure without adding a benchmark campaign to prove the mechanical contract.

**Separate behavioral/configuration experiments:** model/effort with adequate
common request bounds; optional short plans; optional per-attempt notes; and one
bounded no-tool continuation. Hold unrelated changes fixed for each. Prompt
changes in the initial package also need a small authorized development check;
calling them baseline improvements does not establish their effect. If bundled,
report the package effect rather than attributing gains to one component.

There is no universal standard response-token allowance. OpenAI's
[reasoning guide](https://developers.openai.com/api/docs/guides/reasoning#allocating-space-for-reasoning)
recommends reserving at least 25,000 tokens for reasoning plus output when first
experimenting, then adjusting from observed usage. Our 4,096 cap is conservative
relative to that advice; the earlier 8,192 proposal is also a conservative project
choice, not a standard. Neither number is a course requirement. The latest batch
did not exhaust its cap. For a reasoning comparison, consider common generous
bounds such as 25,000 tokens if the approved resource allowance fits, verify the
request timeout is adequate, then right-size from actual usage. This remains a
configuration decision for that experiment, not an automatic expansion of every
limit. Larger limits permit consumption; they do not force it.

Compaction, cross-attempt memory, restored interactive sessions, a dedicated
planner and broadly expanded limits remain deferred. Preserve the same evaluation
boundaries and original attempts. No runtime source, configuration or model was
changed and no test/model generation was run for this classification.

## Consolidated first-fix implementation proposal — November 8

This consolidates the later discussion and supersedes the earlier host-archive-only
starting proposal. The intended outcome is a clearer solver contract and recovery
of output omitted from the model preview, using the existing three tools and
function-based controller. This is an implementation plan, not evidence of a
behavioral improvement. No runtime change or experiment has been performed.

1. **Environment and prompt:** update `agent.py` with verified solver facts,
   workspace/package persistence, available specialist tools and allowed package
   installation. Replace overlapping working-method instructions with concise
   evidence, independent-check, contradiction-diagnosis and stopping guidance.
   Prefer original artifacts or supplied public checkers over repeated manual
   transcription; no mandatory checker tool, planner or notes file.
2. **Command contract:** update `tools.py` descriptions to specify `/bin/sh`, new
   shells without interactive sessions, same-connection read/compute/respond
   scripts, shorter internal network deadlines, and timeout restart effects.
   Keep actual configured timeout values injected rather than duplicated. Explain
   ordinary nonzero exits, preview omission, returned paths and capture status.
3. **Automatic output files:** extend the existing bounded reader in `docker.py`.
   Keep the current combined 64 KiB raw-byte beginning/end preview, with an explicit
   omitted-middle marker and counts. On overflow, write the buffered prefix and
   stream subsequent bytes to separate stdout/stderr files in private run records.
   Short outputs need no retained files. Preserve raw bytes; decode only previews.
4. **Agent retrieval and lifecycle:** transfer captured files into generated solver
   workspace paths through a safe non-root writer, without host mounts or a new
   service. Return a solver path only when delivery succeeds. Use collision-safe,
   no-follow file handling and the existing deadline/terminal-stop controls;
   delivery must not restart an attempt that has stopped. Private controller copies
   survive solver cleanup. Keep existing command execution semantics and expose
   delivery/capture failures without changing the command's exit status.
5. **Bound storage explicitly:** proposed defaults are 10 MiB per command and
   100 MiB per attempt, shared across stdout/stderr. Make these ordinary validated
   limits. Continue draining after a retention limit; clearly distinguish preview
   truncation, complete capture, partial timeout capture, retention-cap exhaustion
   and storage/delivery failure. These caps remain proposed implementation choices.
   Files can preserve only bytes received by the controller, not unprinted or
   unflushed output. No inter-stream ordering guarantee is added.
6. **Verify and document:** focused offline tests for threshold boundaries,
   beginning/middle/end integrity, mixed streams, long lines, invalid UTF-8, storage
   errors and cap exhaustion. Synthetic Docker checks for non-root retrieval,
   safe paths, timeout/restart persistence, stop/deadline precedence and retained
   copies after cleanup. Replace the old test's explicit no-output-file expectation.
   Check actual prompt/schema/export consistency; update README, DESIGN, status and
   evidence with results. No paid model call or real challenge is needed to verify
   this mechanical contract. Stop for review before a development pilot.

Implement the prompt/contract edits first, followed by capture and retrieval as
one consistent contract; do not advertise automatic files before they work. Keep
model, reasoning effort and response-token settings unchanged in this milestone.
A later authorized development comparison can assess the bundled behavior; it
cannot identify the causal contribution of each prompt/output component.

Separate experiments remain stronger model or more reasoning with suitable common
request limits; a larger response-token allowance; short revisable plans;
per-attempt notes; and one bounded continuation after an unsuccessful text-only
ending. Defer compaction until measured context pressure. Before cost-based model
comparisons, reconcile the two existing estimates described in the
[cost check](../evidence/development-trace-review/README.md#estimated-cost-check--november-8).

The user subsequently preferred doing prompt/contract and output work in one
initial milestone, with one review after mechanical verification. The
[combined hypothesis and primary-source review](EXPERIMENTS.md#combined-prompt-tool-contract-and-output-recovery--hypothesis-recorded-november-8)
record expected behavior, possible regressions, acceptance checks and later
comparison limits. The earlier prompt-only comparison remains historical;
a bundled result supports the package rather than its individual components.
