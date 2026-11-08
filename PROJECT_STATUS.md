# Project status

Last reviewed: November 8, 2026 (America/New_York).

**Scope clarification and one blocked-command recovery implemented: 149 offline tests and all 47 synthetic Docker cases passed; final focused checks and cleanup passed. Firewall/image/model settings remain unchanged. No real challenge retry or paid model call was made. Implementation awaits review.**

Use the [current plan](#latest-course-clarification-and-current-plan),
[Git checkpoint](#current-git-checkpoint) and [assignment checklist](#assignment-checklist)
for remaining work. Dated milestone sections preserve their completion state and
next-step recommendations at the time; later completed work supersedes those
historical pending-stage notes.

## One prevented-connection recovery — implemented November 8

The user approved both explicit target address/protocol/port instructions and one
corrective response after confirmed firewall prevention. This is the user's
interpretation of the assignment, not an explicit instructor confirmation. Current
profiles add `max_scope_recoveries = 1`; 0 preserves strict first-denial stopping.
Guard rules/images/permissions and all model/existing resource limits are unchanged.

The existing selector cancels a blocked command, and the controller resets the
same solver before acknowledging the trusted cumulative drop counter. The agent
receives `scope_denied`, allowed endpoints, recovery count and reset flags within
the same deadline/call budget. Files persist; old processes/connections end; no
command is automatically retried. Repeated incidents, strict/idle denials,
invalid/decreasing counters, lost guard, failed reset and terminal races still stop.
Delayed NFLOG entries reread the counter and do not re-count old drops. Summaries
preserve incident/recovery/denied-packet counts after the monitor joins cleanup.

Verification: **149 offline tests and 47 full synthetic Docker cases passed**.
Final focused offline checks (77) and four Docker recovery cases cover the last
capture-delivery and counter-snapshot hardening. They overlap the full suites.
A live forbidden synthetic listener accepted zero connections; feedback reached
the scripted agent, permitted work continued, and repeated/idle/failed-reset
incidents stopped. Guard/deadline/strict controls and cleanup passed. One
intermediate post-recovery proof assertion failed; the broad PID check was
tightened and diagnostic messages added. The original failure is retained and
all four final checks passed; PID reuse is the likely cause, not independently
confirmed from the original generic assertion. No managed containers/networks
remain. [Evidence and exact scope](evidence/scope-recovery/README.md).

The readiness helper now tests the configured recovery allowance before terminal
denial; real challenge readiness was not rerun. No real challenge/model call,
hosted write, new dependency, image rebuild, extra agent tool or service was used.
The original medium scope-stopped trial and prior evidence remain unchanged.
Implementation/evidence are uncommitted for review. Next: review, then separately
authorize one fresh web development check before any broader behavioral claims.

## Medium/headroom batch scope-stop diagnosis — November 8

The user ran `batch-f4ccc7f4b335` with medium reasoning and 8,192 generated tokens.
All eleven scheduled attempts were reached: nine verified successes,
`pwn-baby-boi` ended without success, and final `web-shreeramquest` stopped for a
scope violation. Its public endpoint was `172.20.0.2:80`; its third tool command
included other target ports after a proxy rejection. Independent guard evidence
records a blocked connection to `172.20.0.2:4999`. The internal listener mentioned
in served public source did not authorize that connection.

The controller stopped the solver and retained final trace/results. Target and
solver cleanup passed. The batch wrapper intentionally marks scope incidents
stopped-for-review and raises the displayed RuntimeError, even on the last attempt.
No scheduled attempts are missing and earlier successes remain valid records.
[Incident evidence and hashes](evidence/reasoning-medium-scope-stop/README.md).

Run provenance records `c80b61a` with a dirty working tree and explicit source/
configuration hashes. This diagnosis read the final saved trace and public scope
metadata without executing trace commands. No new model request, challenge
attempt, hosted write, Docker operation or runtime/configuration change occurred.
Full behavioral comparison remains pending; do not infer a causal reasoning effect
or rerun/relax the scope incident automatically. Prior private-history publication
follow-up and export payload-completeness work remain separate.

## Reasoning/headroom experiment activated — November 8

The user requested increased reasoning and then explicitly doubled the token
allowance before any experimental calls. After preparing a separate profile, the
user requested applying the change: the active `configs/development.toml` now uses
Luna effort `medium` and per-response generated-token allowance 8,192, up from
low/4,096. The named `configs/reasoning-medium.toml` experiment profile has the
same values, so the existing default batch command selects this condition too.
All other values and application code remain fixed. The previous low/4,096
configuration is preserved in the prior batch's evidence snapshot and Git.
The hypothesis and limitations
are recorded before calls in [EXPERIMENTS](docs/EXPERIMENTS.md#reasoning-and-token-headroom-experiment--preregistered-november-8).

The normal loader and parsed-value comparison passed; 27 existing model/config/
contract tests passed with the new profile using offline SDK transports. This
checks request propagation, not actual gateway acceptance. No new model calls,
real attempts, Docker operations or hosted writes occurred in preparation.
[Configuration, verification and batch command](evidence/reasoning-medium-preparation/README.md).

After activation, the same 27 checks passed with the active default. Both profile
values match, and comparison with the saved low snapshot confirms exactly the
effort/token changes. Application Python is unchanged; initial preparation
evidence is preserved with a separate activation addendum. No live batch was
started and no commit/push was made by this configuration change.

The intended exploratory cohort is the same eleven development IDs, one fresh
attempt each, compared with low-effort `batch-48f3b134d5c3` (6/11). This measures
effort plus headroom together; it cannot isolate effort. The 8,192 cap includes
reasoning/visible output and is not automatically consumed. Keep the 60-second
request and 600-second attempt limits; record incomplete/capped responses rather
than discarding them. No reliable improvement claim follows from one trial per
task against a historical baseline. Save/review this preparation before live use.

## First-fix live batch and documentation audit — November 8

The user ran `batch-48f3b134d5c3` after committing the combined improvement as
`e7e366c`. All eleven development IDs completed one fresh attempt. **6/11 succeeded**,
equal to the earlier batch's total: `rev-tablez` changed to success and
`web-shreeramquest` changed to an ordinary unsuccessful ending. The other outcomes
match. The result is exploratory; no causal improvement/regression is established.
[Batch evidence, trace links and provenance](evidence/agent-first-fix-batch/README.md).

Saved records contain 65 model requests/60 tools, 309.737431s summed active time,
450.202408s batch elapsed time and $0.02025106 summed local configured-rate estimate.
Existing model/settings/limits, images, dataset and handouts match the historical
baseline; the two capture settings are the only added configuration fields.
No recorded command timeout, solver restart, truncation/output capture, scope/guard
incident or cleanup error occurred. This batch did not exercise automatic output
recovery. All attempts recorded clean source provenance; source hashes match the
current application/configuration/tests.

All saved run audits and export counts/end times passed, but the original
`rev-tablez` export lacked input/output payloads on five observations despite
`evidence_complete: true`. A read-only Langfuse CLI fetch recovered all 18
observations with payloads into `observations-refreshed.json`, preserving its
original export and audit flags. All eleven selected exports now contain their
root/generation/tool payloads. Tightening payload-completeness checks is a separate
engineering follow-up; the missing original payloads' cause is unconfirmed.

This follow-up updates documentation and filtered evidence only. No runtime or
configuration change, new model request, challenge attempt, container operation
or hosted write occurred. No benchmark answer files or held-out contents were
consulted. Detailed behavioral trace review, later experiments, scored evaluation
and report work remain separate. Original hypotheses, runs and synthetic evidence
are preserved. These documentation updates were subsequently saved in `c80b61a`.

Documentation checks passed: 186 local links/heading targets, JSON/TOML parsing,
eleven record/export/baseline hashes, current source hashes, credential/candidate
patterns and `git diff --check`. Raw runs, `.env` and datasets remain ignored and
untracked. No runtime test reruns were needed for this documentation-only audit.

## Combined first fix — implemented and verified November 8

The user authorized the planned combined improvements after documentation checkpoint
`4620032`. The prompt now describes verified solver capabilities/persistence and
adds original-evidence validation/contradiction diagnosis. The command contract
clarifies shells, connections, deadlines, reset effects and capture metadata.
Oversized output retains marked 64 KiB raw-byte head/tail previews plus bounded
separate stdout/stderr files, private retained artifacts and acknowledged solver
paths. New capture settings are 10 MiB per command and 100 MiB per attempt; all
existing settings, including model/effort/token bounds, remain unchanged.

**Verification:** 132 offline tests; full 42-case Docker suite, then ten focused
output cases after close-error hardening and one added actual-10-MiB test. These
cover 43 distinct Docker cases with overlapping focused reruns. The audit checked
52 summaries and 19 overflow observations/artifacts; all have zero model calls and
no cleanup errors. No managed containers/networks remain. One fault-injection test
mock was corrected; its initial failure record is preserved. Documentation links
and whitespace are checked separately. [Evidence and reproduction](evidence/agent-first-fix/README.md).

Capture keeps draining after storage limits/errors. Complete/partial status and
delivery errors are explicit; safe non-root file delivery uses at most five seconds
within remaining attempt time. A timed-out internal writer stops the attempt
rather than leaving a Docker exec alive or restarting unrelated processes. Host
artifacts survive cleanup; arbitrary solver-file storage still has no disk quota.
No new dependencies, images, tools, sessions, planner, notes or continuation policy.

At the end of implementation, changes were uncommitted for review and no real
development/held-out attempts, paid requests or hosted writes had been run by that
milestone. The package was subsequently committed as `e7e366c` and the user-run
development batch above followed. Synthetic checks verify the mechanical contract;
the live rerun does not establish a solve-rate gain. The preregistered hypothesis
and historical records remain intact; cost-pricing reconciliation is still separate.

## Earlier first-fix proposal and cost check — November 8

Recorded before implementation; the completed milestone above supersedes its
pending implementation status.

The discussion is consolidated into an [implementation proposal](docs/IMPROVEMENT_OPTIONS.md#consolidated-first-fix-implementation-proposal--november-8):
verified solver/environment instructions; concise command/connection/deadline
semantics; independent validation and diagnosis guidance; and bounded beginning/end
previews with automatic recoverable output files on overflow. The file proposal
preserves all received output up to explicit storage limits, supplies actual
solver-readable paths during the attempt, and retains private copies after cleanup.
Model/effort/token settings, planning, notes and continuation remain separate
experiments. No runtime/configuration/test change or new challenge run occurred.

Estimated cost is still recorded locally and in the Langfuse attempt span output;
native generation costs are also present in the saved export. A read-only check of
`rev-checker` found $0.00053867 locally versus $0.00058457 summed native generation
cost. The exact $0.00004590 difference is the native cache-write premium absent
from our local formula. These are estimates, not independently verified billing.
[Cost evidence and interpretation](evidence/development-trace-review/README.md#estimated-cost-check--november-8).
Reconcile the pricing sources before a model-cost comparison; no cost logic or
Langfuse settings were changed. Verification used existing records, current source,
the installed SDK and official Langfuse documentation, without model calls or
hosted writes. Implementation remains the next reviewable milestone.

The user prefers one combined implementation milestone. Before implementation,
the [combined hypothesis and source review](docs/EXPERIMENTS.md#combined-prompt-tool-contract-and-output-recovery--hypothesis-recorded-november-8)
record expected behaviors, possible regressions, mechanical acceptance checks and
later comparison limits. Primary OpenAI, Anthropic, Langfuse and Pi sources support
the principles; they do not certify our capture/delivery design or demonstrate a
solve-rate gain. This follow-up changed documentation only, with no model calls
or runtime tests.

## Latest development-batch trace review — November 7

At the user's request, reviewed messages and tool arguments/results from all eleven
attempts in `batch-3963930b88c3`, newer than the integrated-runtime pilot and separate
web retry. All are development IDs; six succeeded, five ended without success.
All exports/audits completed; no recorded denial/timeout incidents or cleanup
errors. The failed attempts stopped after 5–9 requests and 26.9–46.4 active seconds,
well before configured limits. No held-out contents or expected-answer files were
consulted. [Detailed findings, trace links and proposal](evidence/development-trace-review/README.md).

The clearest gaps were untested mathematical proposals, self-checks sharing copied
data with the derivation, and blocker explanations stronger than the observations.
The successes also show effective error recovery, dependency use and immediate
stopping after trusted verification. These findings support a narrow independent-
validation/diagnosis prompt experiment, not a claim that higher limits or more
infrastructure are needed. Proposed wording and a small development comparison
remain unimplemented and require review/authorization before proceeding.

Verification matched exported generation/tool counts to all eleven result records,
confirmed development membership and existing audit results, and checked shared
source/settings/solver/guard provenance. The saved source hashes match current
application/configuration/test files. The review index retains source record/export
hashes and observation IDs without copying candidate values or commands. Historical
attempts remain unchanged. Review artifact checks passed for 91 local links/heading
targets, all eleven record/export hashes, candidate omission and whitespace. This
review made no model calls, container operations,
hosted writes or runtime changes. User assessment of the assistant's findings is
the next step; scored evaluation, aggregation and report/demo work remain separate.

## Final pre-Git validation — completed November 7

Ran the full current offline/Docker suites with **111/111 and 36/36 passing**, no
retries, cleanup verified. Refreshed all ten reserved environments plus the repaired
web development target: **22 fresh readiness cycles passed**, including final
code's dependency checks and private/scope/reset boundaries, with no solving or
model calls on reserved challenges.

After VPN confirmation, one fresh `web-shreeramquest` development attempt ended
in **trusted evaluator success**: 4 model requests/4 tools, 14.879s active,
27.184s complete launch/export, estimated $0.00085533. Automatic records/privacy/
parentage/cleanup audits passed. At user request, detailed trace review is deferred.
Original unsuccessful pilot is preserved. No agent/prompt/settings/runtime-code
changes were needed during this validation. [Complete validation evidence](evidence/pre-git-validation/README.md).

Two tracked historical Compose snapshots with private target environment values
were backed up byte-for-byte under ignored `runs/`, then redacted in the working
tree. No current host account-key matches were found in the publication scan.
Two prior committed file versions still contain private deployment data; history
was not rewritten. Review the publication/history approach before public sharing.
No commit or push was performed during that validation. The runtime and evidence
were subsequently saved in `616b5f2`; agent-focused work and later scored evaluation
remain separate stages.

## MongoDB compatibility and dependency readiness — completed November 7

The normal launcher now substitutes the **exact supplied AMD64 MongoDB 7.0.9
reference** with its matching pinned ARM64 sibling on ARM64/aarch64 Docker engines.
AMD64 engines and other image references stay supplied. Both are 7.0.9-jammy from
the same official release index; `target.json` records original/replacement,
platform, version and reason. No dataset edit, dependency/configuration file,
registry resolver, application change, solver or endpoint expansion.

Startup uses bounded native Compose `--wait` for supplied healthchecks. One small
safe state checker detects restarting, exited/OOM and health failures, including
when a frontend is running; records exclude environment/health logs. Preparation
checks dependencies again after its probes. Failure states survive cleanup in
`target.json`; prior restart counts alone do not reject a healthy service.

**111 offline cases passed.** Two new Docker failure cases passed; an existing
network/reset case hit an intermittent local fixture-image lookup error, then
passed its focused rerun after the image was verified present. Both initial
failure and retry remain recorded. Normal CLI preparation passed two fresh cycles;
normal-lifecycle registration/login/own-profile checks passed two more, preserving
supplied service fields, fresh DB state, stable services, boundaries and cleanup.
No model calls, live retry, changed model/agent/tools/guard/evaluator/batch settings,
commit or push. [Exact substitution, source and evidence](evidence/mongo-arm64-integration/README.md).

The daemon image-lookup anomaly and older tracked private Compose publication
cleanup remain separate follow-ups. Services without supplied healthchecks still
have no universal application-health guarantee. Stop for review; a single fresh
web pilot can be authorized next, with its original failed attempt retained.

## Earlier independent MongoDB ARM64 check — passed November 7

Historical evaluation; the production integration above supersedes its pending recommendation.

The supplied database is AMD64 **MongoDB 7.0.9**. Its matching official ARM64
manifest is a sibling of that exact AMD64 artifact in the same release index.
After the user disconnected VPN, pull/version probes passed. Two fresh temporary
deployments replaced only Mongo's image/platform: authenticated database ping,
registration/login/own-profile on port 80, stable services after 35s, fresh reset,
private boundaries, port-4999 denial and cleanup all passed. **Zero model calls**,
no solving/submissions, dataset/source/default configuration changes or live retry.
[Artifact, complete checks and recommendation](evidence/mongo-arm64-evaluation/README.md).

Recommend a narrow recorded substitution of this exact Mongo digest on ARM64
Docker hosts, keeping the supplied image on AMD64 hosts, plus preparation checks
for restarting/exited/unhealthy dependencies and restart counts. No general image
resolver or network expansion. Review before implementing that integration; original
failed pilot and AMD64 diagnostic remain preserved. No commit or push.

## Final-runtime readiness and pilot — November 7

The ten held-out environments passed the normal zero-model preparation command:
**20 fresh cycles**, exact contestant files, private boundaries, permitted
connect-and-close, denied-traffic/independent incident evidence, reset and cleanup.
No solving, model calls or held-out answer review. [Readiness evidence](evidence/final-runtime-readiness/README.md).

The three development pilot selections also passed the existing preparation
checks, then ran after VPN confirmation with unchanged settings: `msc-algebra`
and `rev-checker` succeeded; `web-shreeramquest` stopped on a scope violation.
All three exports/evidence audits completed and cleanup passed. Total 18 model
requests/18 tools in 140.75s; estimated model cost $0.00596. No retry or agent/
prompt/tool/settings/image/scope change. [Pilot results](evidence/nyu-runtime-pilot/README.md).

The web attempt used the correct port 80, received 502 responses, then probed
4999/3000/8080; 4999 on the frontend IP was blocked. The supplied proxy forwards
internally to `nodeserver:4999`. A fresh zero-model diagnostic reproduced MongoDB
restarting with exit 132/AVX-unavailable warnings, followed by Node exit/database
connection errors. Opening a port does not repair this target CPU incompatibility.
Existing TCP-only preparation passed its stated connectivity/isolation checks but
missed dependency health (`Running=true` can coexist with `Restarting=true`).
Do not interpret the ten passing control checks as full application readiness.
Review a narrow readiness/compatibility fix before another pilot; keep agent
behavior changes separate. Detailed conversation review remains primarily with
the user; only the relevant web tool sequence was inspected when requested.

Generated Compose snapshots can contain private target values. New ones remain
local and Git-ignored; older tracked snapshots need a separate publication cleanup.
An unfiltered Compose inspection included private deployment values in local
assistant tool output; subsequent diagnostic output is filtered and no such values
were added to new agent/model inputs or reports. No further model calls followed
that inspection. No commit, push or Git-history rewrite was performed.

## Production solver integration — completed November 7

One [solver Dockerfile](docker/solver.Dockerfile) reuses the supplied release
installation body, adds the tested workspace/environment settings and pinned
NumPy/Pillow, and omits the unused HTTP entrypoint. The two former active solver
requirements files are archived, not used for installation. MIT attribution is
included. Five evaluation-only toolkit checks now run in the normal Docker suite.
Only the provenance file list changes in application Python; no agent/tool/model/
SDK/evaluator/guard/batch behavior or numeric limits changed.

The existing `build-images` command passed in **14.03s using cached upstream
layers**. First combined-image create/start was **0.73s**, first Python exec
**0.17s**; this is not a clean-machine cold test. No new preflight subsystem or
startup allowance was added. **100 offline tests and 34 Docker cases passed**,
including controls, restart persistence, fresh state and functional toolkit checks;
cleanup was verified. The default `ctf590-solver:m1` now matches the tested image.
The lean baseline image/archive remain preserved; a separate verified archive
freezes the new default. Images/archives have not been published to teammates.

[Integration evidence and artifact identities](evidence/nyu-solver-integration/README.md).
The roughly 11.5 GB footprint, floating upstream downloads, unsupported optional
tools and unestablished live GDB support remain explicit limitations. README now
covers source builds and loading the shared artifact. No model calls, uploads,
challenge attempts, commit or push. Stop for review; the final-runtime environment
readiness refresh and small live pilot are later stages.

## Earlier supplied-image retry — passed November 7

Historical evaluation; the production integration above supersedes its pending recommendation.

After applying the user's saved 8 GiB setting with a normal Desktop restart, the
unchanged AMD64/UID-1000 NYU release built in **17m 17s**. Minimum recorded host
free space during the build was about **25.2 GiB**; no resource bound triggered.
VM memory samples showed substantial available RAM and unused swap. Eight GiB
was sufficient here; Mac swap alone did not establish a Docker memory shortage.

An **eight-line child recipe** adds writable `/workspace`, the existing output
environment settings and missing NumPy/Pillow. Its build and `pip check` passed.
All **29 existing Docker compatibility/control cases plus five additional cases
passed** under existing solver limits. Functional checks cover SageMath arithmetic/
linear algebra, radare2 binary analysis, angr symbolic execution, ELF32 compilation/
execution and denial of supplied sudo elevation. Two portable offline pip/home
tests also passed against the current image. No application/agent/model/guard/SDK
or normal configuration change; only test adaptations and evaluation inputs.

Recommend this tested NYU-based image with its small adapter for broader CTF
tooling, accepting roughly **11.5 GB** Docker image footprint versus **1.16 GB**
for ours. It does not establish every upstream tool works: the external installer
ignored Kali-package/Sherlock/Cutter errors. Those extras remain unsupported.
The first raw-image probe exceeded 60 seconds, while its repeat completed in
1.405s; plan a one-time zero-model image preflight, not a claim about the cause.

The tested adapter has a verified **2.94 GB local archive**, image identity and
OS/Python inventories. It is not published/distributed yet. Original solver image/
RootFS and defaults remain unchanged; all test resources cleaned up. No model
calls or real challenge attempts. [Results, tradeoffs and next integration](evidence/nyu-solver-image-evaluation/retry-8g/README.md).
Stop for review before changing defaults or running a live pilot.

## Earlier November 7 storage review

November 7 follow-up: the build stopped at our chosen 10 GiB Mac-space reserve,
not an observed Docker/host filesystem-full error. Docker's sparse disk has a
1 TiB virtual ceiling and about 931 GiB available internally; the Mac had about
24 GiB physically available before cleanup. Raising Docker's disk ceiling would
not help. At that review Docker was configured for 16 GiB RAM on a 16 GiB Mac;
the subsequent 8 GiB retry is recorded above. Host swap was about 6.6 GiB; historical
build swap/peak storage were not sampled. The build context was only 2,704 bytes.
The user approved removal of the unrelated 10.9 GB fMRIPrep image; it was removed
without changing the solver image. Host free space rose from **24.29 to 34.46 GiB**.
[Storage measurements](evidence/nyu-solver-image-evaluation/storage-review.json)
and [authorized removal](evidence/nyu-solver-image-evaluation/fmriprep-removal.json).
Do not settle the image comparison from the reserve-triggered cancellation.
The then-pending allocation/retry/checks are now recorded above.

Supplied Compose services now retain commands, dependencies, aliases, DNS,
permissions, storage and resource settings. Fresh project-local bridges/volumes
replace network reconstruction. The guard joins the challenge-facing bridge;
extra egress networks, manual routing, gateway arguments and hostname rewriting
are removed. Socket/port/global-name adjustments are explicitly recorded.

**100 offline tests and 29 synthetic Docker cases passed**, with cleanup verified.
Two fresh zero-model preparation cycles each passed for `pwn-baby-boi`,
`web-shreeramquest` and `cry-ecxor` (six cycles total). Those infrastructure
checks made no model calls. A subsequent approved live synthetic smoke test
passed with two requests; details below. No CTFTiny solving or performance
comparison ran.
[Current checkpoint evidence](evidence/target-network-simplification/README.md).

Material changes: targets regain supplied/default capabilities, resource settings
and normal network connectivity; the previous blanket target hardening is gone.
Solver limits, evaluator separation, firewall/independent denial evidence and
restart behavior remain. The infrastructure inventory accepts 26 of 27 Compose
setups; privileged `msc-showdown` remains unsupported. Seventeen socket omissions
are recorded, not claimed to preserve every challenge's functionality.

Read-only challenge-directory binds have offline validation only: Docker Desktop
rejected both temporary-directory and repository binds. Named-volume freshness
and backend DNS/scope passed real Docker checks. Current CTFTiny definitions have
no non-socket binds. Writable host binds/external storage require an explicit
reset strategy. No host-sharing or storage-copy workaround was added.

The [separate plan](docs/SIMPLIFICATION_PLAN.md) records both completed checkpoints
and supplied-image evaluation. The initial build was canceled at our host reserve;
the subsequent adapted candidate passed the compatibility/control checks above. Our
agent/prompt/model, three tools, Langfuse SDK export, TOML and batch workflow remain.
Baseline commit `64f6385`, checkpoint evidence and previous solver/guard images are
preserved. The current image is also archived locally; GDB/context/agent behavior remain
separate. The direct course clarifications and next steps are recorded below.
Live pilot remains a separately authorized stage.

## Bounded solver-image evaluation — November 6

The user authorized the independent build and synthetic comparison. Pinned NYU
release `20250206` (`112cfa3`) was built unchanged for AMD64 with UID 1000, under a
separate candidate tag. Initial Docker Hub EOF errors cleared after the user
disconnected the VPN. Ubuntu packages, radare2/JADX and the Python venv/pip steps
completed. The external `ctftools` installer was canceled after **567.92 seconds**
when host free space fell below **10 GiB**; the 20-minute time limit did not trigger.
These are evaluation-only bounds, not agent settings or assignment requirements.

No completed candidate image exists. Candidate tools, pip, privilege boundaries,
restart persistence and fresh-state compatibility were therefore **not tested**.
The 1,068-package initial apt step estimated 5,097 MB of added filesystem data;
the completed evaluation cache chain occupied 6.742 GB before scoped cleanup.
Neither number is a final candidate-image size. Do not describe this as a broken
upstream Dockerfile or a failed runtime compatibility test.

**November 6 recommendation, reopened by the November 7 storage review:** retain our current lean image. It already supports the current
workflow; adoption has not demonstrated a net reduction in maintenance. A future
retry needs adequate build storage and the same synthetic compatibility gate.
Workspace/environment adaptations remain proposals, not implemented changes.

Eleven existing synthetic Docker cases passed against the current image, including
all three tools, trusted verification, private filesystem/privilege boundaries,
timeout recovery, hard limits and six denial cases. Its AMD64 identity and RootFS
are unchanged. A preservation tag and checksummed 266,362,880-byte local image
archive were created under Git-ignored `runs/frozen-images/`. Only the canceled
build's 19 identified cache records were removed (6.742 GB); unrelated cache and
images remain. Managed-container/network cleanup passed. No runtime, tests,
dependency/configuration, agent, SDK or batch change; no model calls or challenge
attempts. [Build, controls and preservation evidence](evidence/nyu-solver-image-evaluation/README.md).

## Live synthetic smoke check — passed November 6

The user approved the existing bounded `model-check` and confirmed VPN readiness
before model requests. On clean committed runtime `00e6a41`, the model fetched
JSON from the isolated synthetic target, then submitted its observed candidate;
trusted verification accepted it. Two real model requests and two tool calls
produced 12 complete hosted Langfuse observations. All check/privacy/parentage/
usage audits passed; cleanup was verified with no scope incidents or errors.

Run `b2ce1cd44ed6`: 1,585 input and 191 output tokens (including 7 reasoning),
$0.000254 estimated model cost matching hosted totals, 5.72 active seconds and
22.25 seconds for the complete check/readback. The initial model input excluded
the answer. The observed candidate appeared only after tool output.
[Evidence and trace](evidence/live-simplification-smoke/README.md).

No runtime, prompt, normal model setting, dependency or image changed. This smoke
check covered real provider/command/submission/export behavior; live file writing,
restarts, broader challenge behavior and solve rate were not exercised. Previous
100/29 control evidence remains valid. That review preceded the bounded image
evaluation above; a broader live development pilot remains separately authorized.

## Latest course clarification and current plan

**Current next step:** review the completed
[scope clarification/recovery milestone](evidence/scope-recovery/README.md), then
separately authorize a fresh web development check. Preserve the original medium
scope stop; no automatic retry or scope expansion occurred. Full medium versus
low behavioral review remains pending and is separate from this controller change.
Detailed first-fix behavioral interpretation and export payload-completeness
handling remain open; the latter is a separate engineering task.
The following paragraphs preserve earlier decisions and milestones; pending
proposal wording is superseded by the latest results above.

The professor [explicitly accepted](docs/REFERENCES.md#november-6-course-guide-and-professor-confirmations)
repository Compose files/private controller verification, Langfuse JSON exports,
and developing on separate CTFTiny IDs while holding ten out. Keep all three;
no JSONL conversion, NYU development-data migration or separate course-runtime
adapter is required. This confirms the approach, not every compatibility/control
claim. Existing evidence and known exceptions remain.

The image evaluation/production integration, same-release MongoDB compatibility
fix, final-runtime readiness refresh, development pilot and fresh web retry are
complete and saved in `616b5f2`. The latest [validation evidence](evidence/pre-git-validation/README.md)
records 111 offline tests, 36 Docker cases, 22 fresh readiness cycles and verified
web success. These are infrastructure/development results, not scored evaluation
or a measured agent-improvement effect.

The separately authorized [latest development-trace review](evidence/development-trace-review/README.md)
is complete. Review its findings and proposed narrow prompt change, then agree on
a small development comparison before implementation or new live attempts. Record
the hypothesis before calls and hold other settings/images fixed. The current
prompt already requests recovery, so another generic persistence paragraph is
unlikely to add much; independent validation and diagnostic checks are the specific
proposed focus. No prompt, tool, model, runtime or SDK change was made by the review.

The user also requested a [generic NYU baseline prompt comparison](docs/REFERENCES.md#nyu-baseline-prompt-comparison--november-7).
Pinned default templates support a concise verified-environment description and
clear task/file/endpoint information. Existing task/submission handling already
covers much of their structure. Their no-tool continuation behavior is a separate
controller-policy experiment; sudo, file paths, extra servers and debugger claims
must match our own runtime. The reference does not replace the trace-supported
independent-validation proposal. Source links and limits are recorded in REFERENCES;
no upstream application code, prompt change or live test was introduced.

The user requested a consolidated [improvement-options evaluation](docs/IMPROVEMENT_OPTIONS.md)
covering prompt/environment guidance, output, reasoning/models, plans/notes,
budget feedback and continuation. It ranks potential benefit, evidence, ease,
maintenance and overhead. Recommended next work is a compact prompt candidate and
a separately authorized small development follow-up, then a fixed-prompt reasoning
comparison. No candidate is implemented or tested by this design review; larger
output/memory/execution mechanisms remain conditional on evidence.

The [follow-up design discussion](docs/IMPROVEMENT_OPTIONS.md#user-follow-up-explanations-and-current-recommendations)
explains validation, stateful connections/deadlines, planning/notes, truncation,
full-output retention and per-response versus per-attempt budgets. Read-only Duke
listing/metadata requests now succeeded for Luna, GPT-6.1 Sol and Astra; filtered
rates/capabilities and fixed-volume cost illustrations are saved with the review.
No candidate generation compatibility was tested. Environment/prompt updates are
supported in principle; full-output retention merits a concrete capture design,
and an 8,192-token per-response allowance is proposed for consideration with a
medium-effort model. None is implemented; continuation remains secondary and
compaction is deferred until evidence warrants it.

The latest [initial-change/experiment split](docs/IMPROVEMENT_OPTIONS.md#initial-baseline-changes-versus-separate-experiments)
proposes prompt/environment/connection clarity, independent-check habits, explicit
truncation and optional bounded raw-output archives as the initial baseline package.
Model/effort, plans, notes and continuation remain separate experiments. Existing
connection guidance was partial, not absent. Published 25,000-token starting advice
is now distinguished from our conservative 4,096/8,192 project choices; common
adequate bounds belong in the reasoning-comparison design. No implementation or
live-run authorization is inferred from this design discussion.

A [command-description comparison](docs/REFERENCES.md#command-tool-description-comparison--november-7)
checked NYU's actual callable/parameter documentation and OpenAI/Anthropic guidance.
The proposed long description can be condensed to roughly the existing length
while preserving operational caveats; system policy and parameter defaults should
stay in their respective places. This remains wording review, not implementation.

Evaluation freezing, scored trials, aggregation and report/demo work remain later,
separately authorized stages. The private-data history/publication decision is also
still open before public sharing; current-file redaction did not rewrite history.

The newer guide states one configuration with three fresh attempts per challenge,
per-challenge success/sample-SD/token/time metrics, and a demo that need not solve.
These are recorded as **guide statements**, distinct from the three email approvals.
The working checklist below reflects that guide; original Canvas requirements
remain unchanged in ASSIGNMENT.md and their differences are preserved in REFERENCES.
The earlier documentation audit did not run models. The subsequently approved
synthetic check, development pilot and web retry are setup/development evidence,
not scored evaluation or report work.

## Current Git checkpoint

Latest saved HEAD is `b6ec0e5` ("increased reasoning experiment"). Local `main`
and `origin/main` matched with a clean working tree before this recovery milestone.
That checkpoint includes the reasoning settings, attribution and prior batch
documentation. The low-effort live rerun recorded clean `e7e366c` source;
`4620032` preserves the earlier review and hypotheses. The scope instructions,
bounded recovery, tests and accompanying evidence/documentation are uncommitted
for review. No commit, push or history rewrite was performed in this milestone.

The runtime baseline is `616b5f2d854f58b2e305697cee21d5f739e81d03` (`616b5f2`),
“integrated NYU solver image with expanded tooling, ready for testing.” The working
tree was clean before this documentation synchronization. The preceding commit,
`00e6a41`, already contains execution/network simplification and the earlier
SDK-export/configuration cleanup.

The following changes and evidence are now committed in `616b5f2`:

- Integrated the evaluated NYU installation body into one solver Dockerfile,
  retained MIT attribution and removed the two active solver requirements files
  (archived copies preserved). Original lean image/archive remain available.
- Added the exact same-release MongoDB 7.0.9 ARM64 substitution and recorded
  adjustment on ARM64 Docker engines; AMD64 and other references stay supplied.
- Added native Compose health waiting and safe dependency-state checks at startup,
  on startup failure and after readiness probes. Added focused tests and
  consolidated toolkit checks into the normal Docker suite.
- Updated source provenance to include the NYU license instead of obsolete
  requirements files. Agent, prompt, three tools, model settings, evaluator,
  guard, native SDK export and batch behavior are unchanged.
- Added image evaluation/build/freeze, smoke/pilot, final validation and privacy
  evidence; updated README, status, design, references, experiment log and plan.
  Recorded verification: 111 offline/36 Docker cases, 22 readiness cycles and a
  fresh verified web success. Detailed trace review was deferred at that checkpoint;
  the later eleven-attempt review is recorded above.
- Ignored new private Compose snapshots and redacted private fields in two old
  tracked public copies, preserving exact originals under ignored `runs/`.
  Historical committed versions still need a publication/history decision.

Image archives, `.env`, dataset checkout, live run records and private originals
remain Git-ignored. Historical run provenance retains the original source/image
hashes and dirty-working-tree status; committing the checkpoint does not change
those records. This synchronization makes no commit, push or history rewrite.

### Documentation synchronization — November 7

Updated this status file to match the committed runtime checkpoint, completed
validation and remaining assignment work. Preserved the original assignment,
professor/guide distinctions, historical milestone evidence and publication
follow-up. Verified HEAD and the clean pre-edit working tree; all 63 local links
(including heading targets) and `git diff --check` passed. Saved evidence confirms
111 offline/36 Docker cases passed and 22 fresh readiness cycles across 11
environments. Only this status file changed. No runtime/configuration changes,
test reruns, container operations, hosted trace review or model calls were made.
That documentation milestone stopped for review; the subsequently authorized
development-trace review is recorded above. That review subsequently added evidence
and an experiment-log entry; runtime source remains unchanged.

### Documentation checkpoint — November 8

At the user's request, checkpoint the completed trace review, generic reference
comparison, improvement options, combined implementation plan/hypotheses and
estimated-cost findings before runtime implementation. The local and live remote
`main` tips both matched the runtime baseline before this checkpoint. Include only
the documentation and filtered review evidence; preserve ignored original runs.
This checkpoint changes no runtime/configuration/test files and runs no model or
challenge attempt. Verification covers documentation links, filtered artifact
structure, credential/candidate-pattern checks and whitespace. This is a local
commit; pushing and runtime implementation are subsequent actions.

### Earlier November 6 pre-commit audit

November 6 audit: local `main`, local `origin/main` and read-only GitHub `main`
all point to `64f6385fb788f2c54e2a4f0ca6a661fd8d1c51d1` (`64f6385`). There are no
staged changes or committed ahead/behind differences. Execution/target-network
simplification, updated tests/docs and both new evidence directories are saved
in the working tree but uncommitted. This audit changes documentation only;
no commit or push is performed. The original assignment and historical evidence
are preserved unchanged.

Documentation checks passed: 122 local links and 23 heading links resolve;
`git diff --check` is clean. Runtime/configuration/test hashes still match the
last passing 100-offline/29-Docker verification. No tests, containers or model
requests were rerun for this documentation-only audit.

## Historical November 5 Git audit (subsequently committed as `64f6385`)

On the November 5 documentation audit, local `HEAD` and GitHub `main` both point
to `a6d3bf0563bd3565a9967a52468757f9d2ac07a3` (`a6d3bf0`). At that audit the changes below were
saved locally but uncommitted; no commit or push was performed by that audit.
They are now included in `64f6385`; the execution checkpoint is subsequent work.
That commit already included writable Python/home, runtime pip access,
interactive sessions, timeout recovery, larger limits and removal of the local
spending cap. Those are not new changes since the checkpoint.

| Local change | What changed | Verification or status |
| --- | --- | --- |
| Worker reliability | Guaranteed exceptional cleanup, final-output draining, automatic finished-session reaping and partial-input byte reporting. | [Reliability evidence](evidence/agent-reliability/README.md). |
| Missing usage and preparation | Valid replies without usage continue with unknown aggregate totals. Preparation uses the selected experiment; staging checks available space and shares the remaining deadline. | 91 fast tests, 31 Docker cases and two preparation cycles at that milestone. |
| Configuration cleanup | Complete normal settings in `configs/development.toml`; no fallback value dictionaries; one configured model-call limit; `configs/initial.toml` removed. | Resolved live values match the pre-cleanup profile exactly. |
| Trace export and package writes | Existing Langfuse Python SDK replaces CLI export and retrieves all cursor pages. Package scans still run; identical inventories skip rewriting `packages.json`. | [Cleanup evidence](evidence/config-sdk-cleanup/README.md): 95 fast tests, 31 Docker cases and matching readback of an existing synthetic trace. |
| Documentation and planning | Current commands/settings/evidence documented, stale README verification counts corrected, and the proposed infrastructure simplification recorded separately. | Documentation-only audit; the proposal has no implementation or runtime verification yet. |

The completed milestones add evidence under `evidence/agent-reliability/` and
`evidence/config-sdk-cleanup/`. Runtime/configuration/test source hashes still
match the final passing cleanup verification. This audit did not rerun those
tests or make model calls. Historical evidence remains unchanged.
Documentation checks passed: 102 local links resolve and `git diff --check`
reports no whitespace errors.

## Assignment checklist

### Section 1 — build the agent and check the environment: complete

- [x] Implement a multi-turn agent that observes tool results and chooses subsequent
  actions. Recorded evidence includes a live synthetic success and the user's
  six-turn development attempt.
- [x] Document the architecture and each tool's inputs, outputs, validation,
  timeout and error behavior in [README](README.md#architecture-and-tool-contracts).
- [x] Identify Ryan Banko's contributions in README as initial agent design, solver
  environment implementation and development-testing setup; retain AI assistance
  disclosure and external-source citations.
- [x] Enforce hard attempt/model/tool limits and solver resource limits in code.
- [x] Verify candidate submissions in trusted code and record candidates/verdicts
  without separately revealing the expected answer.
- [x] Keep commands in the isolated solver and keep private metadata, answers,
  evaluator files, credentials, host mounts and Docker socket outside it.
- [x] Restrict solver connections to assigned endpoints plus professor-approved
  package-download connectivity; retain independent
  blocked-request evidence and stop the solver on a scope violation.
- [x] Support challenge selection, public-file staging, fresh target/network reset
  and cleanup for the selected ten plus the development example.
- [x] Retain traces, results and source/configuration/image provenance.

Initial handoff verification: **63 fast tests; eleven preparation checks with 22 fresh cycles**.
[Evidence](evidence/benchmark-readiness/README.md). This establishes setup readiness
for those challenges; it does not establish real challenge-solving success.

### Section 2 — use testing to improve the agent: started, comparison pending

Current checkpoint: the combined first fix and synthetic evidence are committed
in `e7e366c`; the eleven-ID development rerun completed with 6/11 successes.
Summary/provenance and supplemental export checks are recorded above. Detailed
behavioral review remains pending; the historical entries below preserve earlier
experiments and do not imply a reliable improvement effect.

Earlier development attempts informed the environment correction below. Five
subsequent trials used the revised prompt and updated solver: **3/5 verified
successes**, 32 model calls, 31 tool calls and **$0.00944938 estimated cost**.
All recorded exports were complete, with no recorded scope-denial events or
cleanup errors. One exploratory `cry-ecxor` before/after pair has matched settings
and images; both attempts failed, although the revised prompt recovered from
more errors. This does not establish a reliable prompt effect or complete pilot.
[Experiment 1](docs/EXPERIMENTS.md#experiment-1--evidence-use-and-recovery-prompt)
records the approved prompt change, observed failures and proposed next changes.
The [original toolkit review](docs/EXPERIMENTS.md#toolkit-review--original-proposal)
maps public challenge categories, file types and development-handout imports to
potential solver packages. [Experiment 2](docs/EXPERIMENTS.md#experiment-2--solver-libraries-output-visibility-and-network-guidance)
records the approved six-library subset (without reedsolo), 32 KiB live output,
and internal network-deadline guidance. Dependencies are installed at image-build
time; at that milestone runtime access remained limited to assigned endpoints.
That configuration used a 30-second command limit and 300-second wall limit
with terminal timeout handling. The current usability milestone below supersedes
those controls.
This setup milestone passed **64 fast tests and 23 synthetic Docker controls**.
After the final pwntools non-terminal setting, four focused final-image checks
passed for library/network workflows, output limits, private filesystem boundaries
and curl denial. The combined library probe took about 1.35 seconds; its internal
read deadline returned in about 0.22 seconds without ending the attempt.
[Build, pinned versions, provenance and verification](evidence/solver-libraries/README.md).
No real attempts or model calls ran; model API spending was $0. Stop for review
before the next live comparison.
Verification: **45 existing agent/contract/model-adapter tests passed** for the
initial candidate ([evidence](evidence/prompt-recovery/pytest.xml)). The visible
sentence now asks for the action's purpose or what it will test, without requiring
an expected result; both existing prompt propagation/tracing cases passed after
that refinement ([evidence](evidence/prompt-recovery/purpose-only.xml)). No live
calls or API spending.

- [x] Annotate the reviewed development trace failures using tool calls, inputs, results and
  subsequent actions, including blocked requests and stopping behavior.
- [x] Record Experiment 1's hypothesis before its live comparison.
- [x] Implement the approved evidence-use/recovery system prompt.
- [x] Add sequential batch launching with a small index of existing attempt records.
- [x] Implement and verify the approved package/session/timeout/output usability changes.
- [x] Complete the focused worker/usage/preparation reliability follow-up.
- [x] Consolidate normal settings and use native SDK export (historical write-on-change inventories).
- [x] Replace execution machinery and verify solver restart recovery; remove per-tool scans.
- [x] Review execution, then simplify supplied targets/networking and verify scope/reset.
- [x] Review the target/network checkpoint and record professor confirmations.
- [x] Verify one bounded live synthetic command/submission/hosted-export cycle after simplification.
- [x] Complete image comparison and production integration: 100 offline/34 Docker checks passed; new default frozen and lean baseline preserved.
- [x] Recheck the intended ten environments under the final runtime without solving: 20 fresh cycles passed.
- [ ] Support the chosen improvement with trace evidence and small follow-up checks.
  The earlier exploratory pair is preserved; the new guide does not require a second full evaluation.
- [x] Integrate and verify the same-release native MongoDB adjustment and dependency-state readiness checks.
- [x] Complete the separately approved fresh web retry: verified success after the MongoDB fix; original scope incident retained.
- [x] Complete the authorized assistant review of the latest eleven development
  traces, including messages/tools/results and proposed improvements. Findings
  await user assessment; new changes/comparisons remain separately authorized.
- [x] Record the combined first-fix hypothesis before implementation and verify the
  package with 132 offline and 43 distinct synthetic Docker cases.
- [x] Record the user-run eleven-ID development rerun on clean `e7e366c`, preserve
  original exports, recover missing `rev-tablez` payloads and audit provenance.
- [ ] Review the new batch's messages/tool results against the hypothesis and assess
  changed outcomes before choosing the next experiment.
- [ ] Freeze code, dependencies, images, dataset and settings for evaluation.
- [ ] Following the new guide, run one fixed configuration for three fresh trials
  on each of the ten reserved challenges; preserve failures, missing usage and
  incomplete incidents. Actual counts remain honest if course limits prevent completion.

### Sections 3–4 and submission: remaining

- [ ] Report per-challenge success rate, sample SD (percentage points), mean input/
  output/total tokens and launch-to-termination time across all three trials.
  Calls/cost remain useful recorded extras; older Canvas pass@k/variance wording is preserved separately.
- [ ] Explain trace-supported findings, changes, follow-up checks and prior exposure.
- [ ] Select the competition configuration and explain its tradeoffs.
- [ ] Prepare the guide's 1–3 page report with contributions, reused-code
  citations and AI disclosure.
- [ ] Record an identified autonomous-run video or live demo showing tools/results;
  the guide does not require a solve. If a solve is shown, include submission and
  evaluator confirmation. Preserve identifying configuration/commit/challenge/run records.
- [ ] Finalize the repository package, aggregation script, frozen commit and
  reproducible launch instructions; submit by November 11 at 11:59 p.m. Eastern.

## Current implementation

The production image integration above supersedes earlier image/requirements/home
settings in the dated implementation history below. Current commands are in README.

### Target/network simplification — checkpoint complete

[Evidence](evidence/target-network-simplification/README.md) records 100 offline
tests, 29 Docker cases, the 27-definition infrastructure inventory and six fresh
development preparation cycles. A two-service synthetic target verifies frontend/
backend DNS, denied direct backend access, within-trial volume persistence and
fresh state after `down --volumes`. Host bind execution was blocked by Docker
Desktop sharing; read-only bind policy is verified offline only.

The supplied Compose definitions and standard project networking/lifecycle replace
our blanket service normalization, backend reconstruction and egress/router setup.
Small existing orchestration remains for private loading, image identity, exposure/
freshness checks, bounded lifecycle and adjustment/results records. New code adds
narrow mount/storage/host-administration checks and explicit adjustment records;
no new persistent subsystem or runtime dependency. Runtime Python decreases from
1,575 to 1,561 lines (14 fewer); the main reduction is mechanisms and assumptions,
not line count. The agent, resolved settings, solver image and SDK export are unchanged.

Targets now inherit ordinary Docker/supplied capabilities and resource settings.
Solver controls still enforce scope, CPU/RAM/PIDs/time/calls/output/write/model
limits. The known privileged target and storage needing bespoke reset fail
explicitly. Neither preparation nor socket omission proves solving compatibility.
The then-pending image review is recorded above; a live pilot remains separate.


### Previous execution simplification — checkpoint complete

The [checkpoint evidence](evidence/execution-simplification/README.md) records
baseline/new source and image identities, 93 offline tests, 28 complete synthetic
Docker cases and two fresh development preparation cycles. The complete Docker
run checked denied-traffic incidents, guard loss, resource/isolation controls,
trusted submissions, actual ownership/mode-preserving copying, writable home/pip,
restart persistence, detached/background process reset and clean removal. Offline
checks cover failed recovery and terminal-stop races, trace output and SDK export,
and batch interruption/incident records. Fault tests use substitutes, not a daemon
stress test; no solve-rate or live-reliability improvement is established.

The old 354-line worker service and its host RPC are gone. Standard Docker and
Python replace the mechanisms; small custom code remains for bounded capture,
one-shot writing, restart coordination and initial inventory. Existing guard,
evaluator and tracing code are reused, not relabeled as NYU-supplied functionality.
The current solver image is adapted independently of the NYU image decision.
`workspace_mb` and session/artifact contracts/tests are removed rather than kept
as dormant fallbacks. CPU/RAM/PID/time/call/model/output/write controls remain.

The former package write-on-change and per-command descendant-cleanup milestones
below are historical. New inventories are initial plus optional final readback;
terminal stopping often makes final inventory unavailable and records that fact.
That checkpoint was reviewed; the target/network checkpoint above completes the
next infrastructure step. Its original counts remain historical evidence.


### Previous configuration, SDK export and package snapshots — complete

Approved November 5: `configs/development.toml` contains every normal model/run
value. `config.py` loads and validates without fallback values; the old
`configs/initial.toml` is removed. `max_model_turns` also supplies the adapter's
request guard, so there is one configured model-call limit. The resolved live
values exactly match the saved pre-cleanup settings. Alternative profiles must
copy the complete file. Synthetic controls now use this profile too; the optional
paid model check retains small explicit test bounds under `tests/`.

The existing Langfuse client exports all cursor pages to `observations.json`,
with the same completion/privacy audits and bounded readback. Node/npm is no
longer needed for normal runs. Historical `cli-observations.json` files remain.
Package scanning is unchanged; identical inventories skip the file rewrite.
Output files still copy as before. No new dependency, tool, image change, model
setting change or benchmark attempt is included.

Verification: 95 fast tests passed, including complete-config validation and one
shared call limit, package first/change-only writes, SDK pagination beyond 100
records, empty continuation pages, delayed completion and readback deadline.
Hosted readback of the existing benign trace matched historical and current CLI
content for ten observations. All 31 Docker cases passed under the consolidated
normal profile, with cleanup verified. Full details are recorded in
[cleanup evidence](evidence/config-sdk-cleanup/README.md). These are maintenance
checks, not a measured benchmark improvement. Stop for review before another pilot.

### Reliability follow-up — complete; stop for review

Worker resources now share guaranteed cleanup on exceptional exits. Completed
sessions drain final output and are reaped automatically, retaining their bounded
final result for later retrieval. Partial input reports `input_bytes_sent`.
Broken supervisor protocols remain terminal infrastructure failures; ordinary
command timeouts still permit continuation after confirmed cleanup.

Valid model replies without usage metadata continue. Aggregate token/cost totals
become null and remain unknown; native observations retain available per-response
usage. Preparation accepts the same `--experiment` as live runs, checks free
workspace after Python setup, and stages files within the remaining attempt time.
The API still selects at most one tool per response, so forty responses normally
permit at most forty tool actions despite the separate eighty-tool guard.

Verification passed: **91 fast tests and 31 synthetic Docker cases** in a complete
suite, including fault handling, automatic reaping, partial-input reporting,
zero-wait final-output capture, timeout recovery, isolation and cleanup. Two
zero-model preparation cycles passed for `pwn-baby-boi`; recorded attempt settings
exactly match `configs/development.toml`. The solver image is rebuilt locally.
No model/numeric-profile, network-policy, dependency, tool-count or GDB change is
included. [Final evidence](evidence/agent-reliability/README.md). No live model
requests or challenge-solving attempts ran. Stop for review before another pilot.

### Previous usability milestone — complete

Approved November 4: live limits are 600 seconds, 120-second ordinary commands,
60-second model requests, forty model turns/requests, eighty tool calls, 512 KiB
model input, 4,096 output tokens and 64 KiB tool output. Solver RAM/workspace are
1 GiB/512 MiB. Local spending caps/reservations are removed; usage remains recorded.

`HOME`/`TMPDIR` use `/workspace`; a fresh system-site-packages venv accepts runtime
pip installs. The guard now has separate NAT egress and allows Docker DNS/public
HTTPS. Internet is permitted by agent instructions only for pip dependency
installation, with answer lookup prohibited; purpose is not enforced by the
firewall. Private-network isolation, trusted verification and scope-stop records
remain. Interactive sessions use the existing command tool; per-command
supervisors clean up detached descendants. Ordinary timeouts permit continuation
after confirmed cleanup. Larger output returns beginning/end excerpts and a file
path; package versions and bounded output copies survive in attempt records.

Verification: **82 fast tests and 27 distinct Docker cases passed**, including
pip install/import, writable home/space, fresh Python reset, PTY interaction,
independent commands, session close, timeout recovery with detached descendants,
output excerpts/files, private boundaries, scope incidents and cleanup. The initial
three-second deadline probe expired during venv startup; it now allows eight
seconds to reach runtime expiration. A later missing-image check found the egress
network did not yet exist; cleanup now accepts Docker's absent-network wording.
Those failed records remain; the corrected case and remaining checks passed.

`prepare-challenge --challenge pwn-baby-boi` also passed two fresh cycles with the
new venv/output directories excluded from contestant-file inventory. The benign
pip install/import command took about 1.66 seconds in the main run. Solver and
guard images are rebuilt locally. No GDB change, real model call or challenge
solving occurred. [Evidence and final provenance](evidence/agent-usability/README.md).
Stop for review before another live development pilot. Performance improvement
and compatibility with every package/challenge are not established.

### Historical runtime package policy and course clarification

The following describes the preceding temporary offline milestone, superseded by
the usability change above. Its incident and verification evidence are retained.

The professor has now confirmed that runtime package downloads are acceptable;
the concern is looking up CTFTiny answers. See [the recorded clarification](docs/REFERENCES.md#authority-and-professor-clarification).
The user explicitly prefers minimal networking machinery. The current plan keeps
the six preinstalled libraries, removes the temporary offline pip default, supplies
a writable per-attempt installation location, permits practical internet egress,
and tells the agent to use it for dependencies and never published answers.
No proxy, mirror, CTF blacklist or custom installer is planned. This relies on
model instructions and trace review for internet purpose, not package-only network
enforcement. Solver isolation, private-data boundaries and hard limits remain.
Package installation and imports need benign verification under actual resource
limits before further live trials. No runtime changes have been made for this plan.

The first gateway-timeout batch was moved intact to
`runs/archive/batch-be87c5be7ce7`; it remains historical setup-failure evidence.
The later batch with a verified success and scope incident remains under
`runs/pilots/current-setup/`. Raw run records are local and Git-ignored.

All eleven selected pilot environments passed the user's preparation checks.
Batch `batch-8898df326849` then recorded `cry-ecxor` without success,
`cry-describeme` with verified success, and `for-1black0white` with a scope stop.
The third attempt lacked a QR decoder and ran `pip install opencv-python-headless`;
the guard recorded and blocked DNS requests for `pypi.org`. Records were complete
and cleanup passed. The remaining eight IDs were not attempted in that batch.

Pending professor clarification, a marked, removable Dockerfile ENV line makes
pip ignore package indexes and skip its version check at runtime. Build-time
installation still works. The tool description tells the model downloads are
unavailable. An ordinary missing-package request should return a local error and
permit recovery; actual out-of-scope network requests still stop the run/batch.
No new library, network permission or installer framework was added. This change
does not supply the missing QR decoder or establish that the challenge can solve.
Verification: **81 fast tests and 24 Docker controls passed**, with cleanup
verified. A missing-package pip request returned a local error in about 0.42
seconds; a second command succeeded in the same attempt. The solver was rebuilt
locally. [Evidence and reversal instructions](evidence/runtime-package-policy/README.md).
No real attempts/model calls ran during this fix. Stop for review before the
next live pilot attempt.

### Batch launcher

`run-batch --challenges ID ... --trials N` now repeats the existing launcher in
fresh processes, preserves every attempt's records, and writes a small batch
index with existing run IDs and trace links. The experiment file is copied into
the batch folder. It adds no parallelism, retries, resume system or batch-cost
gate. The user requested two different development challenges per category;
only one development forensics ID exists, allowing eleven total without using
reserved challenges. Those eleven IDs have now been selected and preparation
passed; completing the live pilot remains pending after the recorded scope stop.
Verification: **17 offline batch cases passed; 81 fast tests passed overall**.
[Evidence](evidence/batch-wrapper/README.md). These checks simulated child results;
no real challenge attempts or model calls were made. Stop for review before
selecting/running the pilot.

The record audit confirmed tool activity, submissions/verdicts, resolved
configuration, commit, challenge ID and `result.run_id` are already captured.
Existing source hashes and the dirty-working-tree flag identify uncommitted
changes. See [README](README.md#read-results). Demo work is deferred at the user's
request; the current focus is the batch wrapper and development pilot.

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
existing workspace. At that milestone the live input-size cap became **262,144 bytes (256 KiB)**;
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
At that review, persistence after contradictory results remained an unapplied
prompt hypothesis; the later approved change is recorded in
[Experiment 1](docs/EXPERIMENTS.md). No new attempt was run then. The local `review.md` beside the raw records
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

## Historical profile expansion (superseded)

The following records an earlier change; current settings are listed in README
and `configs/development.toml`.

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

## Earlier environment correction and remaining assignment work

The environment-correction notes below are historical. Use the current checkpoint
and README for active execution/storage behavior and verification scope.

### Historical solver environment and timeout-contract correction

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
was added in that milestone. The subsequently approved prompt-only change is
recorded in [Experiment 1](docs/EXPERIMENTS.md); real model comparisons remain pending.

### Remaining scope

The shared command can select any indexed ID whose files are materialized and
whose supplied setup fits the reviewed conventions. **Earlier infrastructure preparation covered
the ten reserved IDs and five development IDs, not all fifty entries.** The new
execution checkpoint has separately prepared only `pwn-baby-boi` so far. More complex
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

The remaining work is trace-supported agent analysis, the held-out runs, guide
success/sample-SD/token/time metrics, report and autonomous-run demo. The older
Canvas pass@k/variance/successful-demo wording is preserved in REFERENCES. Section 1 being ready does not complete the entire assignment. Repository,
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
| Live synthetic smoke after simplification | [live-simplification-smoke](evidence/live-simplification-smoke/README.md) |
| Target/network simplification | [target-network-simplification](evidence/target-network-simplification/README.md) |
| Execution simplification | [execution-simplification](evidence/execution-simplification/README.md) |
| Configuration, SDK export and package snapshots | [config-sdk-cleanup](evidence/config-sdk-cleanup/README.md) |
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
