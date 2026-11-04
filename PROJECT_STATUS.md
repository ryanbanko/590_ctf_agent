# Project status

Last reviewed: November 4, 2026 (America/New_York).

**Section 1 implementation and environment setup are complete for the selected
ten CTFTiny challenges and the development example.** Later development traces
revealed baseline solver-tooling and executable-workspace gaps; the approved
environment/timeout-contract correction below addresses those. The user will
carry out Section 2 experiments. Recovery changes remain a separate review;
this correction makes no model calls, pilots or scored attempts.

## Assignment checklist

### Section 1 — build the agent and check the environment: complete

- [x] Implement a multi-turn agent that observes tool results and chooses subsequent
  actions. Recorded evidence includes a live synthetic success and the user's
  six-turn development attempt.
- [x] Document the architecture and each tool's inputs, outputs, validation,
  timeout and error behavior in [README](README.md#architecture-and-tool-contracts).
- [x] Identify Ryan Banko's contribution and disclose AI assistance in README.
- [x] Enforce hard attempt/model/tool limits and solver resource limits in code.
- [x] Verify candidate submissions in trusted code and record candidates/verdicts
  without separately revealing the expected answer.
- [x] Keep commands in the isolated solver and keep private metadata, answers,
  evaluator files, credentials, host mounts and Docker socket outside it.
- [x] Restrict solver connections to permitted endpoints; retain independent
  blocked-request evidence and stop the solver on a scope violation.
- [x] Support challenge selection, public-file staging, fresh target/network reset
  and cleanup for the selected ten plus the development example.
- [x] Retain traces, results and source/configuration/image provenance.

Initial handoff verification: **63 fast tests; eleven preparation checks with 22 fresh cycles**.
[Evidence](evidence/benchmark-readiness/README.md). This establishes setup readiness
for those challenges; it does not establish real challenge-solving success.

### Section 2 — use testing to improve the agent: remaining

User-run development attempts provide starting traces; the three most recently
reviewed attempts informed the environment correction below. That correction has
synthetic verification, but no real-model comparison or completed pilot. The user
will carry out the experiments in this section.

- [ ] Annotate development trace failures using tool calls, inputs, results and
  subsequent actions, including blocked requests and stopping behavior.
- [ ] Record a hypothesis before testing a change.
- [ ] Compare the initial and changed configurations under controlled settings.
- [ ] Run a small development pilot and review readiness and projected resource use.
- [ ] Freeze code, dependencies, images, dataset and settings for evaluation.
- [ ] Run the ten reserved challenges with fresh trials, repeating 2–3 times as
  the approved budget allows; preserve failures and complete records.

### Sections 3–4 and submission: remaining

- [ ] Calculate and plot pass@k, average solve rate/variance, time, calls, tokens
  and cost, including failed attempts.
- [ ] Explain the comparison with specific trace steps and disclose prior exposure.
- [ ] Select the competition configuration and explain its tradeoffs.
- [ ] Prepare the approximately three-page report with contributions, reused-code
  citations and AI disclosure.
- [ ] Record a fresh successful autonomous-run video or live demo with evaluator
  confirmation and identifying configuration/commit/challenge/run records.
- [ ] Finalize the repository package, aggregation script, frozen commit and
  reproducible launch instructions; submit by November 11 at 11:59 p.m. Eastern.

## Current implementation

One command selects a challenge and runs the existing agent:

```sh
uv run --frozen --env-file .env python -m ctf_agent run-challenge --challenge pwn-baby-boi
```

Run it from the repository root (the folder containing `README.md` and
`pyproject.toml`) with Docker running. Each teammate must install dependencies,
build solver/guard images, obtain the pinned dataset and configure their local
`.env`; these are not supplied by a GitHub clone. The recorded verification
machine now has all fifty challenge directories (see the full-dataset update below). See [README](README.md)
for teammate setup, tool contracts, architecture, limits and result interpretation.

The portability review found personal checkout paths only in current documentation;
the application already uses repository-relative defaults. Instructions now work
from any checkout location and distinguish local setup from committed files.
Historical evidence retains its original paths as provenance. This was a
documentation-only correction, checked with a path scan and local-link validation;
it made no model calls, downloads or container runs.

`run-challenge` replaces `run-development`. It uses `nyuctf==1.1.1` to load the
selected ID, stages only listed contestant files, starts the supplied services
where present, and runs the same Responses/tool loop and trusted evaluator.
File-only challenges need no target service. Development/scored is an automatic
result label from `configs/ctftiny.json`, not a separate agent or runner.

The manifest keeps ten scored IDs separate from forty development IDs. Its
revision is `f1c9531672c45b24b7fb5f3aa44a7ac33d3602f8`; the loader verifies the index
hash, clean checkout and split. CTFTiny is the current scope. NYU setup was deferred
at the user's request; no additional dataset, adapter or agent was added.

There is no separate selected set of ten development challenges: the forty IDs
are a pool for Section 2. Both groups cover all six categories. The fixed hash
selection was not balanced by difficulty; the index has no difficulty ratings.
README now explains the dataset/index versus our split file and uses a full pinned
dataset checkout as the standard one-time setup. Existing sparse checkouts can
download all remaining directories with `git -C datasets/CTFTiny sparse-checkout
disable`, then choose any ID without further per-challenge Git commands. The
loader's missing-files error includes that recovery command for the actual dataset
location. This setup clarification does not claim that all fifty target arrangements
have passed readiness. That initial documentation update downloaded no files;
the subsequent authorized setup is recorded below.
All eight focused challenge-loader tests passed; the missing-files recovery command
and current local documentation links were checked using the project environment.

The structure remains function-based: model/loop code in `agent.py`, trusted
data/target preparation in `challenge.py`, and launch/provenance/export in
`launch.py`. No new runtime module, dependency, tool, campaign budget system,
provider registry or scoring runner was added for this milestone. Obsolete
single-target fields were removed from the manifest. Earlier consolidation removed
separate model/target/records/budget modules and moved controls support into tests.

## Full-dataset setup update

The full pinned dataset is now downloaded, with a clean checkout and matching
revision/index. All **50 contestant file inventories** validate and fit the
existing workspace. The live input-size cap is now **262,144 bytes (256 KiB)**;
the broader 600-second/40-request/$0.20 profile was not applied.

Compatibility stays in the existing loader/lifecycle: the older `port` field is
accepted, supplied prebuilt images are used, and supplied private backend networks
remain isolated. A listed Dockerfile stays outside the solver, with the omission
recorded. Docker-managed target volumes are allowed without host bind mounts and
their removal is verified after Compose cleanup. Privileged targets remain rejected.

Four additional zero-model preparation checks passed: `cry-ecxor`, `cry-describeme`,
`msc-algebra` and `web-shreeramquest`, bringing recorded runtime readiness to **15
unique challenges**. `msc-showdown` is a known exception: its registry image is
unavailable and its supplied setup requires privileged Docker. The user requested
stopping further compatibility expansion and using the supplied package/configs.
All **63 fast tests passed** after these changes. The final file-record correction
normalizes listed `./` paths so ordinary handouts are not reported as withheld
build files; all 14 focused loader/launch tests passed after that correction.
No paid calls or solving occurred. README now leads with teammate
setup and run commands; dataset details follow the quick-start instructions.
[Full-dataset record](evidence/benchmark-readiness/full-dataset.json) retains the
inventory, known exception and check references; new raw preparation evidence is
local under `runs/full-dataset-setup/`. Failed setup diagnostics remain preserved.

## Verification of Section 1

- **63 fast tests passed**, including package loading of a held-out fixture and
  the same launch/verification flow for both result labels.
- **All eleven preparation checks passed, two fresh cycles each**: six file-only
  reserved challenges, four service-backed reserved challenges, and the existing
  development example. Files/hashes/ownership and private-data boundaries passed;
  TCP connect-and-close passed where services exist. Reset, independent denied
  traffic, solver stopping and cleanup passed for every case.
- Actual native SDK spans were retained locally. Preparation made **zero model
  requests, zero flag submissions and $0 model spend**, with no hosted uploads
  or reading of target response contents. Trusted package loading holds flags
  programmatically; flags/solutions/write-ups were not inspected.
- Target compatibility fixes retain supplied image/service/alias/port conventions,
  remove host ports/socket mounts and use resolved local image IDs. Nginx needs
  writable target storage and CHOWN at startup; targets now have those normal
  permissions alongside limits. The solver stays non-root/read-only, without
  capabilities, host mounts, credentials or private metadata.
- The last full synthetic Docker suite passed **19 cases** in the earlier tracing
  milestone. It was not repeated here: solver/guard/worker controls are unchanged,
  and the changed target path received the eleven real preparation checks.

[Completion evidence](evidence/benchmark-readiness/README.md),
[suite results](evidence/benchmark-readiness/suite.json), and
[JUnit](evidence/benchmark-readiness/pytest-fast-final.xml) record verification.
Earlier failed setup/export diagnostics remain preserved in the same directory;
`suite.json` identifies the final passing runs. This is setup evidence, not
held-out solving or a course improvement experiment.

## Existing model/tracing evidence

The earlier live synthetic model check succeeded autonomously with two model
requests and two tools, 837 input/100 output tokens, estimated **$0.0001337**.
Native hosted usage/cost readback and cleanup passed.

The user's real development attempt was saved locally at
`runs/development/development-3d5f96fbcaa9/run.json`, with attempt ID `1f905c41c9a8`.
That Git-ignored record is not included in teammates' clones. It made
**six model calls and six tool calls**,
used 7,042 input/1,466 output tokens, cost an estimated **$0.00118394**, and stopped
on `command_timeout` without a submission or verified success. Attempt time was
51.797599 seconds; complete launch time was 59.837572 seconds. Saved trace audit
passed and cleanup-error lists were empty. These are historical results, not reruns.

The native reasoning-summary setting is enabled. One approved benign request
accepted `summary: auto` but returned an empty summary array (estimated cost
**$0.000099**). The later development run below returned summaries in three
generations, establishing their availability in that run. That compatibility
milestone did not add an explanatory prompt or extra reasoning request.

The user subsequently approved one system-prompt sentence requesting a brief visible
purpose/expected-result explanation alongside each tool call in the same response.
Existing native Langfuse generation output captures this normal assistant text.
Tools, response format, loop, limits and evaluator behavior were not changed, and
no extra model request is introduced. Prompt wording can affect model choices and
token use; this is not a guarantee of identical behavior or readable internal reasoning.
The existing SDK transport test now includes visible text together with a tool call
and checks native trace capture, replay, continued execution and unchanged call counts.
All 32 focused loop/model tests passed without live requests. The user's subsequent
run below included visible explanations in all seven generations.

## Latest development trace review

The newest user-run development attempt is `1f98afdc8143` on `cry-ecxor`, saved
under `runs/challenges/challenge-93992f708f7a/`. It stopped on
**`completed_without_success`**, with seven model calls, six tool requests,
zero submissions and no verified success. Estimated cost was **$0.00188724**;
active time was **31.609914 seconds**, with 48.865922 seconds for the whole launch.
Evidence audit and cleanup passed.

This run used the 256 KiB input cap. Its largest reconstructed request was 36,495
bytes; thirteen requests, thirty-four tool calls and substantial wall/cost headroom
remained. It did not hit an input, time or budget limit: the model returned final
text without another tool call, which the loop treats as termination.

The trace shows two rejected 120-second timeout requests against the 30-second
command cap; the current tool schema/error does not communicate that numeric cap.
Omitting the timeout then allowed the script to execute in about 0.205 seconds.
The model observed empty candidate sets, reused the same constraint, and stopped
without acting on a possible next direction described in its final response.
`xxd` was also missing, but the model recovered using Python. No network-denial
event appeared. Visible explanations appeared in five of six tool-bearing replies.

The user approved numeric timeout feedback after this review. Validation errors
now give the actual configured maximum and units, e.g. "at most 30 seconds".
The 30-second command cap is retained: the successful scripts completed in about
0.2 seconds, so this trace does not show a need for a longer runtime allowance.
Validation rules, timeout enforcement and stopping behavior are unchanged.
All twelve existing contract tests passed; direct validation checks confirmed
messages for 10-, 30- and 0.5-second caps and acceptance of each valid boundary.
No solver commands, model requests or hosted uploads were made for this change.
Persistence after contradictory results remains a separate, unapplied prompt
hypothesis. No new attempt was run. The local `review.md` beside the raw records
contains step references, headroom and the diagnosis. This is not a controlled
comparison with the earlier, different challenge.

## Earlier development trace review

User-run attempt `a052e07aed6f`, challenge `pwn-baby-boi`, is saved locally under
`runs/challenges/challenge-b1ad850c94af/`. It made **seven model calls and seven
tool requests**, estimated **$0.00156631**, and stopped on **`model_input_limit`**
after 44.380933 seconds (60.080358 seconds for the launch). No submission or verified
success occurred. Evidence audit and target/solver cleanup passed.

The run used the approved 300-second/30-second/20-request/40-tool profile. Before
request eight, the reconstructed serialized request was approximately **33,358
bytes**, above `max_input_bytes = 32768`. Replayed reasoning items dominate history
size, including 18,504 characters of encrypted context. The byte guard stopped the
request before dispatch; neither the overall time limit nor request/tool count
was exhausted.

The trace also shows unavailable solver utilities (`file`, `objdump`, `readelf`,
`strings`, and Python `pwn`), a rejected 10,000-second timeout followed by corrected
ten-second requests, and a final program-level socket timeout. The trace does not
establish the target's state at that final connection. No scope-denial event was
recorded. Visible action explanations appeared in all seven replies; native readable
summaries appeared in replies 2, 4 and 5. Encrypted context remains unreadable.

Proposed single-variable experiment: raise `max_input_bytes` to 65,536 while holding
other current settings fixed, then compare stopping behavior and resource use on
fresh development attempts. Missing utilities are a separate follow-up. This is a
recorded hypothesis, not an applied change or completed comparison. The local
`review.md` beside the raw records contains the sequence and size breakdown.
This review made no model calls, Docker operations or runtime/configuration edits.

## Current settings and limits

The user subsequently approved larger limits for development testing in
`configs/development.toml`: **300 seconds per attempt, 30 seconds per command/file
operation, 20 model turns/requests, 40 tool calls and a 30-second HTTP timeout**.
`max_tool_calls` is now explicit in `[attempt]`; it previously inherited 20 from
the shared defaults. The real-run loader merges this table over those defaults.

The model remains `gpt-6-luna` with low reasoning, 2,048 output tokens/request,
256 KiB serialized-input cap, no retries and a $0.10 estimated per-attempt cost cap.
Solver resources remain 1 CPU, 256 MiB memory, 64 PIDs and a 64 MiB workspace.
Command timeout still ends the attempt. The original setup evidence and user-run
attempt retain their previous 120-second/eight-request/10-second-command settings;
they were not rerun with the new limits. This change only updates the live profile
and current documentation; it does not authorize a model call or experiment.

Verification of this profile change: the real configuration loader accepted all
overrides, model-turn/request limits agree, and all other attempt defaults were
preserved. The six focused launch/configuration tests passed. No Docker runs,
model requests or hosted uploads were performed for this change.

At recorded rates, twenty maximum-sized requests reserve about $0.678, so the
unchanged $0.10 cap can stop an attempt before the request limit. There is no
persistent campaign ledger; review ordinary usage records between runs. The user
previously approved discretion below $0.50 and confirmed a $1/day account allowance;
this milestone spent no model budget. Remote billing/cancellation and remaining
account quota are not independently audited.

## Limits and next steps

### Approved solver environment and timeout-contract correction

The three most recently reviewed attempts ended without success or submissions;
none exhausted its configured limits. Missing utilities and executable failures
were environment gaps, independent of the recovery issues deferred by the user.
A fixed synthetic probe confirmed that the original ARM64 Python-only solver
mounted `/workspace` with `noexec`: even copied `/bin/true` failed with errno 13.

The normal build now selects Linux AMD64 for the solver, installs file/binutils,
xxd, curl/netcat/OpenSSL, ZIP tools, GCC/make/GDB and 32-bit runtime libraries, and
records OS package versions. Only the solver workspace gains explicit execution
permission; read-only root, non-root identity, zero capabilities, private-data
boundaries, network guard and existing numeric limits remain enforced. Curl adds
no network permission. Tool descriptions name `/bin/sh`, and the actual configured
timeout maximum/default reach the model and traces before a call is chosen.

Verification: **64 fast tests and 21 Docker controls passed**, including permitted
curl/nc connections, blocked curl with independent denial evidence, executable
and compilation checks, and complete cleanup. A separate benign probe verified
AMD64 and dynamically linked i386 execution. `cry-ecxor` preparation passed two
fresh cycles. **Zero model calls and $0 API spending.** Live GDB debugging fails
with register/ptrace errors on this Apple Silicon Docker setup; static inspection
passes. Native AMD64 Linux is recommended when live debugging is needed.

[Evidence and reproduction commands](evidence/solver-readiness/README.md).
No new runtime module, Python dependency, model tool, recovery prompt or loop policy
was added. Stop for review; recovery and real model comparisons remain separate.

### Remaining scope

The shared command can select any indexed ID whose files are materialized and
whose supplied setup fits the reviewed conventions. **Infrastructure is verified
for the ten reserved IDs and five development IDs, not all fifty entries.** More complex
Compose arrangements fail closed. The solver now builds as AMD64 with baseline
utilities; benign AMD64 and i386 executable handling passed the checks recorded above.
Arbitrary contestant-binary compatibility, specialized packages and solving remain
unproven. Live GDB debugging fails on the verified Apple Silicon Docker setup.
Launch readiness does not guarantee solving.

Section 2 can now start with development challenges: read traces, identify a
failure, record a hypothesis before changing the system, compare the change and
run a small pilot. Keep the ten reserved IDs for the later frozen evaluation.
The same command will run those IDs when that stage is authorized. Preserve
configuration, trials and failed attempts; the repository is not frozen for scoring.

The whole Part 1 assignment still needs Section 2 experiments, the held-out runs,
pass@k/solve-rate/variance/resource metrics, report and successful-run video/live
demo. Section 1 being ready does not complete the entire assignment. Repository,
report and demo are due **November 11, 2026, 11:59 p.m. Eastern**; competition is
November 18. Work so far is attributed to **Ryan Banko**, with OpenAI Codex
assistance disclosed in README. Original requirements: [ASSIGNMENT.md](ASSIGNMENT.md).

## Evidence

Historical evidence remains unchanged. Its commands and test counts describe the
recorded milestone; use README for current commands. The user requested a local
Git checkpoint of the Section 1 handoff, including code, configuration, documentation
and retained evidence: `84a5f74`. The original baseline is `028f560`; later changes
can be inspected with `git log --oneline`. This save is not a frozen scoring release. Credentials,
downloaded datasets and temporary `runs/` records remain Git-ignored.

| Milestone | Records |
| --- | --- |
| Initial isolated tools | [milestone1](evidence/milestone1/README.md) |
| Organization and pytest | [refactor](evidence/refactor/README.md), [pytest-refactor](evidence/pytest-refactor/README.md) |
| Conversation loop | [agent-loop](evidence/agent-loop/README.md) |
| Complexity cleanup | [complexity-cleanup](evidence/complexity-cleanup/README.md) |
| Native local tracing, 19 Docker cases | [langfuse](evidence/langfuse/README.md) |
| Hosted tracing | [langfuse-cloud](evidence/langfuse-cloud/README.md) |
| Live synthetic model | [model-integration](evidence/model-integration/README.md) |
| Original development preparation | [ctftiny-readiness](evidence/ctftiny-readiness/COMPLETED.md) |
| Initial live launcher setup | [development-launch](evidence/development-launch/README.md) |
| Reasoning-summary check | [reasoning-summaries](evidence/reasoning-summaries/README.md) |
| Shared challenge launcher and selected-ten readiness | [benchmark-readiness](evidence/benchmark-readiness/README.md) |
