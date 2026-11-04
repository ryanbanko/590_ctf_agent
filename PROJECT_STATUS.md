# Project status

Last reviewed: November 4, 2026 (America/New_York).

**Section 1 implementation and environment setup are complete for the selected
ten CTFTiny challenges and the development example.** The user will carry out
Section 2 themselves. Stop after this handoff; no further model calls, pilots,
scored attempts or performance changes are part of this milestone.

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

Verification: **63 fast tests; eleven preparation checks with 22 fresh cycles**.
[Evidence](evidence/benchmark-readiness/README.md). This establishes setup readiness
for those challenges; it does not establish real challenge-solving success.

### Section 2 — use testing to improve the agent: remaining

The existing development attempt provides a starting trace; it is not a completed
comparison or pilot. The user will carry out this section.

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
machine had all eleven checked challenge directories. See [README](README.md)
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
README now explains the dataset/index versus our split file, sparse checkout,
and the steps to prepare, run and inspect a challenge. This clarification changed
documentation only; it did not change the split, download files or launch attempts.

The structure remains function-based: model/loop code in `agent.py`, trusted
data/target preparation in `challenge.py`, and launch/provenance/export in
`launch.py`. No new runtime module, dependency, tool, campaign budget system,
provider registry or scoring runner was added for this milestone. Obsolete
single-target fields were removed from the manifest. Earlier consolidation removed
separate model/target/records/budget modules and moved controls support into tests.

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
**$0.000099**). Readable summary availability remains unconfirmed. No explanatory
prompt change or extra reasoning request was added in this setup milestone.

## Current settings and limits

`configs/development.toml`: `gpt-6-luna`, low reasoning, eight requests, 2,048 output
tokens/request, 32 KiB serialized-input cap, 20-second HTTP timeout, no retries,
120-second attempt limit and $0.10 estimated per-attempt cost cap. The inherited
command/file-operation cap is **10 seconds**; command timeout ends the attempt.
Tools are capped at twenty; solver resources remain 1 CPU, 256 MiB memory,
64 PIDs and a 64 MiB workspace. No limits changed in this milestone.

At recorded rates, eight maximum-sized requests reserve about $0.042. There is no
persistent campaign ledger; review ordinary usage records between runs. The user
previously approved discretion below $0.50 and confirmed a $1/day account allowance;
this milestone spent no model budget. Remote billing/cancellation and remaining
account quota are not independently audited.

## Limits and next steps

The shared command can select any indexed ID whose files are materialized and
whose supplied setup fits the reviewed conventions. **Infrastructure is verified
for the ten reserved IDs and `pwn-baby-boi`, not all fifty entries.** More complex
Compose arrangements fail closed. Native ARM64 solver and selected AMD64 targets
are checked; contestant AMD64 binary execution and solver tool coverage remain
unverified. Launch readiness does not guarantee solving.

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
