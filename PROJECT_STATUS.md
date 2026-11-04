# Project status

Last reviewed: November 4, 2026 (America/New_York). Documentation review only;
the approved CTFTiny readiness milestone remains unfinished.

## Current state

The isolated solver, trusted evaluator, conversation/tool loop, Responses model
connection, and Langfuse tracing are implemented. One live synthetic attempt
succeeded. **No real CTFTiny challenge has been loaded, started, or solved.**

Latest recorded verification:

- **53 fast tests passed** on November 3. Four added cases cover the preliminary
  CTFTiny loading boundary and file-staging archive; actual Docker transfer and
  benchmark loading remain unverified.
- The earlier model milestone passed 49 fast tests and one live synthetic attempt:
  **2 model requests, 2 tools, 837 input/100 output tokens**, estimated
  **$0.0001337**. Hosted usage/cost readback and cleanup passed.
- The last full synthetic Docker suite passed **19 cases** in the Langfuse SDK
  milestone. It was not repeated for the later hosted/model/readiness work.
- Native ARM64 execution is verified. Actual AMD64 execution remains untested.

Start with [How to use](README.md#how-to-use) for installation, environment
variables, and available commands. Use [DESIGN.md](docs/DESIGN.md) for current
architecture and [REFERENCES.md](docs/REFERENCES.md) for the five original resources,
the professor's clarification, and subsequent integration references.
[ASSIGNMENT.md](ASSIGNMENT.md) is authoritative.

## Approved milestone in progress: CTFTiny readiness

The user approved a minimal readiness check for one development challenge:
create a local Git baseline; obtain a pinned dataset and loader; record the
development/scored split; load public task data and stage contestant files;
verify target connectivity, reset, and cleanup; document the preparation command.
This approval includes metadata-only scored selection. It includes **no model
calls or challenge solving**.

Completed workspace work:

- Saved the public 50-entry index in
  [index-metadata.json](evidence/ctftiny-readiness/index-metadata.json).
- Recorded ten scored IDs and the remaining 40 development IDs in
  [configs/ctftiny.json](configs/ctftiny.json). Selection uses the first ten IDs
  ranked by SHA-256 of the UTF-8 string `ctf590-v1:<id>`; it uses metadata only.
  `pwn-baby-boi` is the readiness candidate, chosen as the first development
  pwn ID in lexical order. No scored challenge contents have been opened.
- Added `ctf_agent/challenge.py` with development-only loading, explicit public
  task fields, listed-file validation, and binary staging through Docker tar input.
  Four new offline cases bring the recorded fast-test total to 53.

Remaining acceptance checks:

- [ ] Create the local Git baseline. No commits or repository publication exist yet.
- [ ] Obtain the CTFTiny checkout, pin its revision, and validate the recorded index.
- [ ] Install and lock the reviewed `nyuctf` dependency.
- [ ] Inspect only the selected development setup and decide on necessary Compose
  changes, endpoint/name mapping, and any required solver tools.
- [ ] Verify real contestant-file staging and the public/private boundary.
- [ ] Verify permitted connectivity, a focused denial check if networking changes,
  fresh target reset, and cleanup.
- [ ] Add and document the readiness command, retain evidence, and stop for review.

The manifest's revision is intentionally null. The loader rejects unpinned data
and scored IDs. `nyuctf` is not installed or locked, and there is no real CTFTiny
preparation/solver CLI command yet. No target-specific compatibility layer has
been added before inspecting the selected setup.

[Partial evidence](evidence/ctftiny-readiness/README.md) records what was actually
checked. It does not establish benchmark readiness.

## Last execution blocker

On November 3, automatic approval review could not process the already-authorized
local Git baseline commit because its review service reported an exhausted usage
limit. The command did not execute. The service identified this as a **review
failure, not a safety determination**.

The user checked account usage and reported both a five-hour limit and available
credits. Whether the review service can use those credits is unresolved. Review
capacity has not been retried during the November 4 documentation work. Do not
assume the old error describes the account's current capacity, and do not bypass
the review check.

Once protected operations are available, continue the approved readiness scope
above without asking for the same task approval again.

## Settled design decisions

- Target CTFTiny through its explicit index; NYU documentation and package APIs
  provide compatible conventions. Preserve supplied Compose definitions wherever
  compatible with assignment controls; inspect before changing them.
- Use ordinary functions, dictionaries, closures, and resource-owning context
  managers. Keep the system understandable across runtime, dependencies,
  configuration, setup, and tests. No agent framework or custom application
  class hierarchy is planned.
- `run_attempt()` owns resources, limits, trusted verification, and final results.
  `run_agent(public_task, respond, call_tool)` receives only public data and
  bounded functions. `submit_flag` checks exact equality in trusted lexical scope.
- Model-controlled commands run only in the non-root solver. No host mounts,
  Docker socket, credentials, private metadata/source/build files, evaluator
  storage, or answer key enter the solver. Candidate submissions and verdicts
  are recorded; the expected answer is never separately exposed.
- A separate trusted guard shares the solver's network namespace and enforces
  endpoint restrictions with independent denial logging. Scope violations,
  guard loss, command timeout, and hard limits stop the attempt. Unexpected
  solver-stop failure records infrastructure failure; cleanup still attempts
  both removals.
- Langfuse is the sole detailed tracing system. Automatic OpenAI integration
  creates live generations; scripted fixtures retain manual generations. Normal
  summaries/provenance remain local. Historical JSONL records are preserved.
- Use Responses with full public history and native output-item replay, including
  any encrypted reasoning context. There is no compaction or cross-attempt memory.
  The live adapter rejects requests above its 32 KiB serialized-input cap.
- Keep synthetic support and checks under `tests/`. Prefer basic focused checks.
  Repeat the full Docker suite when changed behavior or unresolved concerns
  justify it, rather than routinely for unrelated changes.
- Runtime dependencies are pinned/locked: Langfuse 5.1.0 and OpenAI 3.44.0.
  Pytest 9.2.0 is a development dependency.
- Solver defaults remain 60 seconds, 20 tools, 20 response turns, a 10-second
  command cap, 16 KiB command output, 64 KiB writes, 1 CPU, 256 MiB memory,
  64 PIDs, and 64 MiB workspace. Accepted assistant messages are capped at 1 MiB.
- The completed model check used `gpt-6-luna`, low reasoning, four requests,
  1,024 output tokens/request, no client retries, and a $0.10 cap. These are
  setup-check settings, not a frozen real-challenge configuration.
- The user confirmed a $1/day Duke allowance. This does not authorize spending
  the full allowance or additional paid attempts. Account throughput/remaining
  quota and actual invoices were not independently checked.
- Results retain scripted/model counts, available API usage, estimated cost,
  conservative reservations, timing, incidents, and cleanup. Unknown usage is
  not reported as free. Transport timeout does not guarantee remote cancellation
  or billing cancellation; the independent watchdog stops the solver.

## Completed milestone history

All completed milestones below ran on November 3, 2026. Evidence directories are
historical snapshots; their commands, dependencies, source hashes, test counts,
and then-pending work describe that point in time. Follow the main README for
current usage. Original evidence has not been rewritten.

| Milestone | Actual verification | Historical evidence |
| --- | --- | --- |
| Isolated tools/lifecycle | 17 Docker + 5 contract tests; no model calls. | [milestone1](evidence/milestone1/README.md) |
| Organizational refactor | 17 Docker + 6 contract tests; no model calls. | [refactor](evidence/refactor/README.md) |
| Pytest/tool cleanup | 17 Docker + 6 fast tests; no model calls. | [pytest-refactor](evidence/pytest-refactor/README.md) |
| Scripted conversation loop | 30 fast + 17 controls + 2 loop Docker cases; no model calls. | [agent-loop](evidence/agent-loop/README.md) |
| Complexity cleanup | 34 fast + 19 Docker cases; no model calls. | [complexity-cleanup](evidence/complexity-cleanup/README.md) |
| Langfuse-only SDK tracing | 37 fast + 19 Docker cases; no model calls or hosted uploads. | [langfuse](evidence/langfuse/README.md) |
| Hosted Langfuse check | 42 fast; one scripted hosted trace with 16 observations; no model calls. | [langfuse-cloud](evidence/langfuse-cloud/README.md) |
| Responses/automatic tracing | 49 fast; one synthetic success with 2 model requests and 10 observations. | [model-integration](evidence/model-integration/README.md) |

### Responses and automatic Langfuse integration

The approved model-integration milestone completed on November 3. The user chose
Responses and automatic instrumentation, requested basic verification, supplied
host-only Duke credentials, and confirmed a $1/day allowance. Read-only gateway
metadata authenticated and listed 41 models. The approved check selected
`gpt-6-luna` at gateway rates of $0.10/M input and $0.50/M output tokens, with low
reasoning, no client retries, 1,024 output tokens/request, at most four requests,
and a $0.10 cap.

One live synthetic attempt succeeded: two model requests and two tools, first
fetching through the permitted endpoint and then submitting the observed candidate
to trusted verification. It used 837 input/100 output tokens and an estimated
$0.0001337. Automatic hosted cost agreed within numeric precision. The ten hosted
observations included two automatic generations with no duplicate manual live
generation. Cleanup passed. The attempt took 5.580838 seconds including cleanup/
flush; the complete check including CLI readback took 17.213709 seconds.

`model.py` translated public history into Responses items and preserved native
outputs, including reasoning, for replay. The runner retained bounded `respond`/
`call_tool` interfaces. Counts/usage were retained for discarded replies; missing
usage was classified as unknown rather than free. OpenAI 3.44.0 was pinned/locked,
and Langfuse 5.1.0 remained the pinned tracing SDK. Request-byte and conservative
cost reservations preceded dispatch. A standard HTTP response hook kept raw
provider error bodies out of automatic traces while retaining status.

Verification passed 49 fast tests. The previous 19-case Docker suite was not
repeated because the user requested basic checks and isolation implementation
was unchanged. The initial credential audit and its correction are described
below and preserved in [model evidence](evidence/model-integration/README.md).
No real CTFTiny challenge was attempted. At that stopping point, CTFTiny readiness
was proposed; the user subsequently approved the current milestone.

### Hosted Langfuse synthetic verification

The approved hosted check completed before live model integration. The official
Langfuse skill was installed and its instrumentation/readback guidance followed.
Host-only `.env` credentials authenticated; one existing isolated scripted flow
was uploaded and retrieved through the SDK, then independently through the
official CLI. Both readbacks contained the same 16 observations: root, five
scripted generations, five tools, and stopping/cleanup events. All 13 trace-audit
checks passed.

Verification passed 42 fast tests. The hosted check took 13.607838 seconds and
confirmed Docker cleanup. Source hashes, images, configuration, raw SDK/CLI
exports, and trace links remain in [hosted evidence](evidence/langfuse-cloud/README.md).
The runner, loop, tools, sandbox, Docker helpers/images, dependencies, and limits
were unchanged from the preceding milestone; its 19-case suite was not repeated.
Missing image tags were rebuilt from unchanged Dockerfiles.

No model API calls or real CTFTiny attempts occurred during this milestone.
Scripted generations established delivery/readback for the configured project,
not model adaptation, token/cost reporting, or general service reliability.
Gateway integration was the next proposed milestone at that time and was later
authorized and completed above.

### Langfuse-only tracing and narrowed loop interfaces

The approved SDK/local migration pinned and locked Langfuse 5.1.0. The custom
JSONL tracer/module, event sequence counter, and trace-file lock were removed.
Native root/generation/tool observations and explicit incident events became the
sole detailed trace system; ordinary results/provenance stayed local.

`run_agent(public_task, respond, call_tool)` received public data and bounded
functions rather than the attempt dictionary. Runner closures owned deadlines,
budgets, containers, and exact `submit_flag` verification. The expected answer
remained in trusted lexical scope, outside state/results and SDK inputs.
`AttemptStopped` carried only a reason so the loop could distinguish enforced
termination from unrelated bugs. The operator received a controller record, and
`run["result"]` was finalized after context exit.

Verification passed 37 fast tests and all 19 synthetic Docker checks. Native SDK
spans retained full tool outputs, trace/parent links, the five-turn recovery/
success flow, late-response discard, and six independent packet-denial checks.
Limits, Docker helpers/images, and cleanup behavior were preserved. The launcher
took 54.895693 seconds. [Langfuse evidence](evidence/langfuse/README.md) retains
the tested source hashes, summaries, and native span snapshots.

At the user's request, this stage verified the SDK locally before a Cloud project
was configured. Tests used the real SDK with its supported OpenTelemetry
in-memory exporter; no hosted credentials/uploads or model calls were used.
Hosted authentication, ingestion, readback, and export were still unverified at
that stage. The later hosted milestone resolved that separate setup question.
Neither this migration nor the hosted check attempted a real CTFTiny challenge.

### Complexity cleanup

The approved cleanup moved request/checking responsibility into
`request_response()`, leaving the loop focused on history and tools. Pure envelope
tests stopped constructing mocked attempts. Trace reading was shared, and standard
pytest exception assertions replaced manual equivalents. `self-check` discovered
all Docker-marked cases and retained one combined suite record without a fixed
test count. An unused Docker stdin parameter and one redundant adjacent deadline
check were removed.

Unexpected solver-kill errors/timeouts retained `solver_stop_failed` evidence and
classified the attempt as infrastructure failure. Known missing/already-stopped
containers remained harmless. Cleanup still attempted both removals, and monitor
join time covered its bounded kill operation. Focused regressions distinguished
these cases and an unrelated RuntimeError during concurrent stopping.

Verification passed 34 fast tests and all 19 synthetic Docker cases in one
combined run. The launcher took 54.194444 seconds. Previous case identities,
all six packet-denial checks, tool-result records, limits, and scripted context
flow were preserved; cleanup passed. Source hashes and historical JSONL records
remain in [cleanup evidence](evidence/complexity-cleanup/README.md).

The increased fast-test count covered stopping behavior; eight existing envelope
cases were moved to direct validator tests. No live model calls, real challenges,
or later assignment stages occurred. The subsequent Langfuse milestone replaced
this stage's state/tracing interfaces while retaining its evidence unchanged.

### Scripted-response conversation loop

The approved loop milestone added `agent.py` with public conversation history,
sequential tool dispatch, returned observations, existing terminal conditions,
final-text stopping, and a configurable turn cap. It used functions/dictionaries
and added no runtime dependency. Model access and CTFTiny target integration were
not implemented at that stage.

Verification passed 30 fast tests, the existing 17 Docker controls cases, and
two new scripted-loop Docker cases. The success flow recovered from a failed
command, wrote and ran a solver script, fetched a generated candidate through
the permitted endpoint, observed a wrong submission, and then submitted the
observed correct candidate. Verified success prevented the remaining requested
sibling tool from executing.

The late-response case confirmed that the watchdog stopped the solver during a
response wait and that the eventual reply executed no tools. The callback could
not be forcibly interrupted by Python; an uncooperative source could delay host
cleanup even though the independent solver stop remained enforced. Real API
timeouts, retries, pricing, settings, credentials, and account limits were still
future gateway work at that point.

The controls launcher took 43.406439 seconds, and pytest reported 7.76 seconds
for the two loop cases. [Agent-loop evidence](evidence/agent-loop/README.md)
retains source, trace, cleanup, and initial missing-image failure records.
Scripted turns were distinguished from actual model calls, which remained zero.
No real challenge, pilot, scored selection/run, or improvement experiment occurred.

### Pytest and tool cleanup

This approved refactor consolidated host argument validation, made tool schemas
and local names clearer, and adopted pinned pytest 9.2.0 as a development
dependency. Standard discovery, fixtures, parameterized probes, and exception
assertions replaced custom unittest discovery and case-running loops. Application
runtime dependencies were still empty at that historical stage.

All six fast tests and the same 17 container checks passed. The launcher took
44.393378 seconds. Packet denials and cleanup were verified. The change preserved
container helpers, isolation policy, limits, evaluator semantics, and trace
formats. No model loop or model access was added. Original source hashes and
verification records remain in [pytest evidence](evidence/pytest-refactor/README.md).

### Organizational refactor

Synthetic target support and checks moved from the application into `tests/`.
Attempt results acquired one shared logging path, and fixture cleanup attempted
both container and network removal after a cleanup failure. The existing public
build/self-check commands were retained.

All 17 real-container cases and six contract tests passed. The suite took
46.626560 seconds, verified cleanup, and retained one result event per executed
tool. No containment policy, resource limit, evaluator behavior, container helper,
or expected-answer boundary changed. [Refactor evidence](evidence/refactor/README.md)
preserves the historical records and source paths. No model calls or real
challenge attempts occurred.

### Initial isolated execution tools and lifecycle

The initial approved milestone established non-root solver command/file tools,
exact trusted synthetic verification, separate solver/target/guard lifetimes,
endpoint restrictions, resource limits, incident stopping, and cleanup. It used
the Docker CLI with bounded communication; model text was never executed in a
host shell or an administrative target shell.

The original verification passed 17 real-container checks and five contract
tests in 45.279662 seconds. Checks covered allowed target access, validation,
symlinks, host-file/credential boundaries, zero solver capabilities, output bounds,
wrong/correct submissions, stopping after success, deadlines, detached children,
guard/worker loss, interruption, setup failure, and six independent prohibited
IPv4 probes. IPv6 failure demonstrated absence of an external route, not an NFLOG
denial. Cleanup left no project containers or networks.

Implementation diagnostics included isolated networks omitting normal gateway
metadata, tcpdump's need for account-drop capabilities in the trusted guard,
host-probe metadata collection, and commands that close output streams while
continuing to run. Those fixes and the original startup failures remain in
[initial evidence](evidence/milestone1/README.md). They were setup diagnostics,
not the course's controlled agent-improvement experiment.

The initial environment was an Apple Silicon Mac with Python 3.13.2, uv 0.12.8,
Docker Engine 28.3.2, and Compose 2.39.1. Native ARM64 execution was verified;
Docker advertised AMD64 support, but actual AMD64 execution was untested.
The workspace started empty, no Git commit existed, and model calls/cost were zero.

### Historical acceptance checks

These completed checklists record milestone acceptance; they do not authorize
reruns or change the current readiness scope.

**Responses/model integration**

- [x] Confirm gateway authentication, model availability, pricing metadata, and approved cap.
- [x] Pin OpenAI 3.44.0 and connect Responses with automatic Langfuse generations.
- [x] Preserve bounded loop/tool interfaces and native output/linked result replay.
- [x] Enforce request/input/output/cost limits and retain late/unknown usage correctly.
- [x] Pass 49 fast cases and one live synthetic attempt using two model requests.
- [x] Read back the trace with the official CLI; review parentage, credentials, usage, and cost.
- [x] Preserve source/config/image provenance, cleanup, evidence, and review stopping point.

**Hosted Langfuse**

- [x] Install/read the official skill and review integration guidance.
- [x] Keep host credentials Git-ignored and provide a blank example.
- [x] Authenticate and upload one existing scripted synthetic flow.
- [x] Retrieve complete observations and audit IDs, parentage, history, outputs, and verdicts.
- [x] Confirm the secret key is absent and the answer is not separately exposed in the root.
- [x] Independently compare SDK and official-CLI observation IDs.
- [x] Pass 42 fast cases, confirm cleanup, retain provenance/exports, and stop before model work.

**Langfuse migration and narrow interfaces**

- [x] Replace custom JSONL runtime tracing with native SDK observations/events.
- [x] Keep answers, credentials, and controller objects outside trace inputs.
- [x] Give the loop public task data and bounded callables only.
- [x] Retain `submit_flag` inside trusted runner scope and preserve all limits.
- [x] Verify native span relationships, inputs/outputs, verdicts, and packet records.
- [x] Check exporter failure preserves cleanup/results and disabled tracing prevents startup.
- [x] Pass 37 fast and 19 Docker cases, preserve evidence, and defer hosted setup for review.

**Complexity cleanup**

- [x] Extract response-request responsibility and narrow unexpected-error handling.
- [x] Test pure envelope validation directly and retain representative integration checks.
- [x] Share trace inspection and use ordinary pytest exception assertions.
- [x] Discover and record all 19 Docker scenarios in one launcher.
- [x] Retain solver-stop failure evidence and attempt both cleanup removals.
- [x] Remove the unused Docker input argument and redundant deadline check.
- [x] Document context ownership/return values; pass 34 fast and 19 Docker cases.

**Scripted loop**

- [x] Pass copies of public history and schemas; keep runner state private.
- [x] Demonstrate observation-driven recovery and subsequent tool choices.
- [x] Count invalid arguments against tool budget and return validation observations.
- [x] Continue after a wrong submission and stop after trusted success.
- [x] Enforce final-text, turn/tool caps, malformed envelopes, duplicate IDs, and size limits.
- [x] Reject late actions and later sibling tools after termination.
- [x] Verify real-container success/recovery and watchdog stopping during a response wait.
- [x] Preserve original controls, source provenance, traces, and cleanup records.

**Isolated tools/lifecycle and early refactors**

- [x] Execute commands and UTF-8 writes only inside the solver.
- [x] Validate arguments, reject symlink traversal, and bound command output.
- [x] Verify non-root execution, zero solver capabilities, and protected host files/secrets.
- [x] Permit the synthetic endpoint and block a live unapproved target port.
- [x] Retain independent internet/direct-IP, DNS, host, and unrelated-container denials.
- [x] Stop on scope violation, guard loss, deadlines, tool caps, and command timeout.
- [x] Record wrong/correct candidate verdicts without separately exposing the answer.
- [x] Verify interruption/setup-failure cleanup and preserve image/dependency provenance.
- [x] Move synthetic support under tests and consolidate tool-result logging.
- [x] Adopt pytest while retaining the original 17 case identities and controls.

The model check's initial audit counted Langfuse's native public project identifier
as a secret. The corrected review of the same trace passes all 12 checks: the
gateway token and Langfuse secret key are absent; the public identifier appears
only in SDK scope metadata. Original check/export records are preserved. No extra
model calls were made for that correction.

Tested source/image/configuration hashes belong to their recorded snapshots.
The [model verification](evidence/model-integration/verification.json) documents
the subsequent test-only credential-audit correction.
[Readiness progress](evidence/ctftiny-readiness/progress.json) records the newer
loading/staging work as incomplete. The repository is not frozen for scoring.

## Assignment work still ahead

The metadata-only development/scored split is recorded. Dataset revision validation,
real target readiness, and all empirical agent evaluation remain unfinished.

After readiness review, later stages require separate authorization:

1. Agree on real-attempt settings and spending limits; run one or two development
   attempts and inspect their traces.
2. Annotate a failure and write a hypothesis before testing a controlled change.
3. Run a small development pilot and check behavior/resource projections.
4. Freeze code, dependencies, dataset revision, and configurations, then compare
   them on the same ten held-out challenges with fresh resets and 2–3 trials
   as the approved budget permits.
5. Aggregate pass@k, solve rate and variance, time, calls, available tokens, and
   measured/estimated cost, including failures. Explain changes using trace steps
   and disclose prior exposure.
6. Select the competition configuration and prepare the approximately three-page
   report plus a fresh successful-run video/live demo. Videos are limited to
   three minutes; contribution and AI/reuse attribution are required.

The original assignment sets November 4 as an initial-system planning checkpoint
with no separate submission. Repository/report/demo are due **November 11, 2026,
11:59 p.m. Eastern**. Practice changes are planned for November 12–17; the final
competition is November 18. Team composition and contribution ownership remain
to be confirmed; Ryan is the current project contact.

## Next action and handoff

Finish the already-approved CTFTiny readiness milestone when execution review is
available. Inspect the development target before deciding on Compose/tool changes.
Do not begin a real solve, paid check, pilot, scored run, improvement experiment,
aggregation, or report/demo work from this handoff.

Suggested prompt for a fresh chat:

> Continue `/Users/ryanbanko/590_final`. Read `AGENTS.md` and its required documents,
> plus `evidence/ctftiny-readiness/README.md`. The CTFTiny readiness milestone is
> already approved and partly implemented: 53 fast tests recorded, ten scored IDs
> reserved by metadata only, and `pwn-baby-boi` selected for readiness. Dataset
> revision, loader installation, real staging/target/reset checks, CLI, and Git
> baseline remain unfinished. The last protected Git operation failed because the
> automatic review service hit a usage limit; no fresh capacity check has occurred.
> Continue the existing scope when review is available. Preserve the assignment
> boundaries and keep checks basic. No new model calls or solving are authorized.

## Documentation review

The November 4 review checked current documentation against source, configuration,
environment-variable requirements, saved verification records, and local links.
It changed documentation only. No tests, model requests, hosted uploads, challenge
activities, container operations, or Git writes were run. Completed historical
evidence and the original assignment remain unchanged.
