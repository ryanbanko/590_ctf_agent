# Task-preface assessment — November 17, 2026

**Worth a small experiment; prefer operational characteristics over six category
checklists. Start with a stateful-network preface.** This is a read-only runtime
assessment and a proposal, not a new prompt implementation or performance result.
The original `0395835` agent/tools/default settings remain selected. The current
manual HTB integration remains offline-verified only.

## Evidence checked directly

Read current status/working agreement, assignment, setup, design, reference
authority, relevant history/experiments, evidence index, baseline/change/pilot/
latest-batch summaries, configuration and agent/tools/attempt/challenge/launch
code. Also checked sandbox/firewall implementation. Prior review conclusions
were used to locate cases, then checked against original local exports.
[review.json](review.json) records source identities, record/export hashes,
coverage and selected observation references without payloads or candidate values.

Rechecked all 71 run-record hashes across the original baseline (36), partial
full validation rerun (23), and planning/notes trial (12). All match prior inventories;
all 68 available export hashes match too. Separately checked the pilot/expanded
review inventories, which include historical controls and overlap the baseline.
Those inventory rows must not be counted as additional independent attempts.

The baseline has eight null required request/action fields in one successful
trace. The partial full rerun lacks its API-incident export; its wall-limited
run's final generation output is null with explicit `Request timed out.` status,
not evidence of a missing successful reply. Planning/notes has two absent exports
and six null fields in a third successful run. Expanded validation has six null
fields in one success. Existing structural completeness does not certify payloads.
No hosted refresh was performed. Connection-pilot raw records are external; only
the retained derived summary was available here. Timing discrepancies remain.

Selected chronological trace checks, including both successes and failures:

| Public workload | Direct observation | Implication |
| --- | --- | --- |
| Misc, stateful network | `fc2817b9ddca` tools 2–4 read one question, open fresh sockets, then send fixed answers derived from an earlier question. The current prompt visibly differs. The same stale-session pattern is visible at tool 3 in `7efb161a344d` and `a6ad9c70d544`. Later scripts parse/answer within one session. | A concrete session-lifetime reminder has an observable target. |
| Crypto, delayed network reads | `fb9fa5e1d1bd` tools 2–7 move from an empty short read to buffering/startup explanations; tool 7 receives data after five short timeout results on one connection. The newline and waiting changes do not isolate the cause. | Distinguish idle timeout, EOF and protocol completion; do not claim a diagnosed server mechanism. |
| Pwn, local and remote checks | `62c62407c81c` has partial banner recovery and repeated payload corrections before component checks. `ebc08728e106` tools 5–8 progressively check separate assumptions and narrow subsequent work. | Operational guidance can span categories, but cannot guarantee correct low-level programs. |
| Large forensic artifact | `04dc1fa5c1b9` has three preview overflows, two rejected submissions, then a focused contextual search supporting the successful submission. The public handout inventory includes a 23,695,720-byte file. | Selective inspection has a stronger connection to workload than the Forensics label alone. |
| Small forensic artifact/control | `f7ccc5d7e114` inspects a 283-byte handout, checks structure and decodes successfully in seven calls. | Mandatory large-file rituals would be unnecessary here. |
| Reversing, computation | `c648f18c4fe6` checks an early model prediction against the original executable, observes rejection, changes approach and succeeds. `4fbd9b2b538b` instead consumes two command allowances on diagnostic/search work, with timeout/restart feedback. | Original-artifact checks and bounded computation matter, although the input executable is only 39,016 bytes. |
| Pwn, failed diagnostic interpretation | `61bf8e65e52b` repeatedly changes tests; tool 24 acknowledges a layout error after earlier external-restriction hypotheses. Tools 36–40 expose further diagnostic corrections before the 40-call stop. | A category label or more generic persistence is unlikely to fix test construction by itself. |
| Reversing, artifact integrity | `f739906d33da` tool 17 modifies the supplied filename, then fails before its restoration statement. Tool 18 reads those remaining bytes into a variable named `orig`. Tool 10 captures 527,861 output bytes; tool 24 usefully benchmarks throughput. | Preserve original artifacts and distinguish modified measurements; this is not evidence of an infrastructure defect. |
| Tiny input, expensive search | `b95a2f974f81` has a 21-byte handout yet a search returns `Killed`/137. Its cause is unconfirmed; it is not a command timeout. | File size alone cannot route guidance about computational scaling. |
| HTTP control | `cd84bec2d6a6` follows HTTP response evidence and succeeds in four calls. | An endpoint does not imply a raw TCP dialogue or a need to hold one transport connection open. |

These are assistant-assisted observations, not human labels, hidden reasoning,
new solutions, or estimated failure-class prevalence. No recorded commands were
executed. No private dataset source/answer/write-up was consulted.

## Precedents and what they establish

Directly fetched the generic NYU release templates at pinned revision
`112cfa33f5c0a06a20e49af525ac8eb07ec98457`. Its
[initial task template](https://github.com/NYU-LLM-CTF/nyuctf_agents/blob/112cfa33f5c0a06a20e49af525ac8eb07ec98457/llm_ctf/prompts/templates/default/initial_message.md.jinja2)
includes both category and server-type templates. The five category notes mostly
name installed tools; server notes distinguish netcat and HTTP/curl. Its
[prompt manager](https://github.com/NYU-LLM-CTF/nyuctf_agents/blob/112cfa33f5c0a06a20e49af525ac8eb07ec98457/llm_ctf/prompts/prompts.py)
renders these alongside a separate system prompt. This verifies implementation
precedent, not an ablation showing improved solves. Our system already advertises
most relevant tools. NYU's paths, apt/sudo, web helper and live-debugging advice
must not be assumed to describe our verified environment.

Anthropic's [Agent Skills implementation](https://www.anthropic.com/research/equipping-agents-for-the-real-world-with-agent-skills)
is a broader precedent for loading task-relevant instructions. Its
[context-engineering guidance](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
supports concise relevant context and cautions against brittle exhaustive rules.
Neither source proves effectiveness for Luna or this CTF setup. A skill loader,
retriever or agent framework is unnecessary for two short experimental snippets.

## Recommendation and alternatives

The plausible benefit is salience: present a small amount of useful procedural
knowledge when relevant, without burdening every task with all guidance. Risks
include irrelevant rituals, anchoring on one approach, duplicated instructions,
bad routing and additional replay. A preface adds context but does not reduce
the existing full history. Category is already in the public task; merely saying
the model is a category expert adds little new information.

| Option | Assessment |
| --- | --- |
| Unchanged baseline | Lowest maintenance; remains the selected runtime until evidence warrants a change. |
| Category-specific prefaces | Simple dictionary lookup and reasonable for verified category-specific capability gaps. Current traces offer weaker evidence for six separate playbooks; categories mix network, file and search workloads. |
| Operational prefaces | Best evidence fit: session handling, high-volume artifact inspection and bounded computation cross category boundaries. More precise selection is needed; begin with one profile. |
| Per-challenge solution hints or generated plans | Not recommended. Tailoring from reviewed solutions risks overfitting/leakage; an extra model selector adds cost and another source of errors. |

The connection-description pilot is cautionary but not a test of this proposal:
it changed a tool description on one crypto task, achieved 1/3 versus historical
2/3, obtained initial data each time, then failed twice during later computation.
Validation wording had 18/18 pilots followed by two ordinary failures and an API
incident in a partial rerun. Optional notes showed limited adoption. These results
reject guaranteed-benefit claims; they do not demonstrate that contextual prefaces
cannot help. The existing tool description already requests same-connection
interaction, so this experiment tests more concrete emphasis, not a new capability.

Draft network snippet for review, not installed:

> For stateful raw TCP dialogues, read the current question, compute its response, and send
> it within one script on the same connection. A short read timeout is not EOF or
> a complete message; use protocol boundaries and a bounded overall receive
> deadline. Treat values from a previous connection as unverified for a new session.
> These connection rules do not require reusing an HTTP transport connection.

A separate later artifact snippet could emphasize focused summaries/excerpts and
working on named copies while keeping originals unchanged. Computation guidance
would require its own hypothesis: measure a small sample before scaling work and
retain reusable progress. Do not bundle all three into the first treatment.

## Architecture and proposed test

Keep three tools, native replay, enforced scope/resources, evaluator verification,
and stopping unchanged. The clean integration point is `run_agent`'s initial
message construction: a separate trusted, versioned guidance block alongside the
fixed system instructions and public task. Avoid embedding trusted directions
inside the challenge JSON, which the existing prompt treats as untrusted data.
Do not derive guidance from expected answers, private target metadata or run outcomes.
The exact initial request already appears in Langfuse; record selected profile/text
hash in ordinary provenance too. No hosted prompt migration is needed.

For a first trial, explicitly freeze the profile using public task characteristics.
The public schema has category, endpoints and filenames; TCP alone cannot identify
HTTP or session semantics, and filenames do not establish file size or analysis
volume. Trusted staging knows public file sizes, but should not expose unrelated
host metadata. Unknown cases should receive no added guidance. Start with explicit
profile selection rather than an LLM router or broad name/extension heuristics.

Proposed formative comparison: three stateful-network tasks from different
categories (`cry-open-ellipti-ph`, `msc-algebra`, `pwn-pilot`) plus a short HTTP
control (`web-poem-collection`), two fresh trials per task per condition:
**16 attempts** for original versus original plus the network snippet. Apply the
same conditional snippet to the HTTP control to detect misapplication. This
tests that preface on these task types; it does not estimate automated routing
accuracy or prove superiority to category selection. Keep the HTTP distinction
explicit when finalizing wording. More trials/unreviewed practice tasks are needed
for confirmation. If the routing comparison itself is the question, a third
category-guidance arm would make 24 attempts; content and length must be controlled,
and otherwise differences measure the entire guidance policy, not routing alone.

Use the same current source/images/model/effort and 600-second/40-call CTFTiny
settings in both arms, changing only guidance. Alternate condition order through
ordinary sequential invocations; preserve fresh target state and all failures.
Do not compare CTFTiny's baseline with the manual 900-second/60-call profile.
Historical controls remain context, not the primary causal comparison. These
reviewed tasks are tuning data; original scored results stay unchanged.

Primary behavior: fewer stale-session answers and unjustified reconnect/EOF
inferences; do not grade narration as adoption. Preserve verified success, calls,
timeouts/restarts, active and launch time separately, input/output tokens, peak
context and one consistent cost basis, with partial usage retained. Check HTTP
control for unnecessary waiting or interaction changes. Stop after the pilot for
review, retain the baseline if the targeted behavior does not change, and do not
interpret a tiny success difference as statistical proof.

Before any paid trial, a separately authorized implementation milestone should
verify exact prompt propagation, profile isolation/fallback, unchanged public-data
boundaries and existing stop/replay behavior offline. This review authorizes no
implementation or spending. Operational connectivity/readiness for manual HTB
remains a separate priority before relying on that branch in competition.

## Verification of this review

The [checks record](checks.json) covers source/baseline identity, inventory hashes/counts, selected observations,
public task characteristics, new local Markdown links, JSON parsing and whitespace.
Runtime tests were not repeated because runtime/configuration/tests were unchanged.
No model call, challenge run, Docker operation, command replay, hosted write,
commit or push occurred. Remote reads were restricted to generic reference prompt
templates/code and primary vendor documentation. New assessment/evidence and
handoff links are the only repository changes.
