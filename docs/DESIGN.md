# Design choices and alternatives

The [assignment](../ASSIGNMENT.md) requires adaptive tool use, solver/evaluator
separation, enforced limits, trusted verification and complete records. CTFTiny
is the active benchmark. [Original references](REFERENCES.md) explain how the
NYU package and conventions informed this setup. Functions, dictionaries and
resource-owning context managers keep the implementation understandable without
an agent framework or application class hierarchy.

This document describes implemented behavior. The approved
[simplification plan](SIMPLIFICATION_PLAN.md) separates execution replacement
from the completed target/network checkpoint and the independent image evaluation. Our agent, three
tools, model integration, native SDK export, complete TOML and batch wrapper remain.

The [November 6 instructor reply](REFERENCES.md#november-6-course-guide-and-professor-confirmations)
accepts our target Compose/private controller verification, native Langfuse JSON
exports and held-out CTFTiny selection. Keep the current boundaries and record
formats. The course guide's references to separate components do not require a
course-runtime adapter, JSONL layer or NYU development migration for this project.

Solver-image selection remains independent of execution. Following the successful
[8 GiB evaluation](../evidence/nyu-solver-image-evaluation/retry-8g/README.md), the
[production integration](../evidence/nyu-solver-integration/README.md) uses one
Dockerfile with the supplied NYU release installation body and small project
additions. The unused HTTP entrypoint is omitted. The normal build/default tag
now selects this image; no NYU agent framework, parent-build wrapper or second
execution backend was added. All 100 offline tests and 34 normal Docker cases
passed. The larger toolkit costs roughly 11.5 GB; optional installer failures
remain documented. The lean image and its archive remain historical baselines.
Agent, tools, guard, evaluator, model/SDK and batch behavior are unchanged.

## One challenge path

`run-challenge --challenge ID` loads an indexed challenge through the installed
`nyuctf` package and uses the same lifecycle, agent, tools and evaluator for every
selected ID. The existing manifest supplies the development/scored result label.
A separate scoring agent or CLI mode would duplicate behavior; separation belongs
in the challenge selection and experiment records. The ten reserved IDs remain
held out from development solving.

`run-batch` is one additional function in the existing launcher. It invokes
`run-challenge` in a fresh process for each ID/trial, sequentially, and copies the
experiment settings into the batch directory. Fresh processes avoid reusing
Langfuse client state between attempts. A small `batch.json` indexes existing
records and run IDs; it is not another trace backend or an aggregation framework.
Ordinary failed attempts continue; incomplete records, cleanup/scope/infrastructure
incidents and response-source failures stop the batch for review. Missing usage
on an otherwise valid reply leaves totals unknown and does not stop the agent.
On interruption it signals the child launcher and waits for its cleanup before
recording the partial index. No parallelism, automatic retries, resumption or
extra batch-budget subsystem is introduced.

`challenge.py` owns trusted loading, public-data construction, file staging and
target lifetime. `launch.py` owns host clients, orchestration, provenance and native
trace export. `agent.py` keeps the conversation loop and Responses adapter together.
Splitting those responsibilities into separate model/target/records/budget modules
added navigation without a current maintenance benefit. No provider registry,
generic benchmark adapter or campaign ledger is needed.

The loader verifies the pinned Git revision, canonical index hash, clean checkout
and complete disjoint split, with ten reserved IDs. Missing local challenge files
fail with an actionable preparation error. Setup now downloads the full pinned
dataset once; existing sparse checkouts use Git's `sparse-checkout disable`.
This avoids per-challenge path lookup or maintaining an automatic downloader.
`CTFChallenge` includes private metadata and the
answer key; its package object stays on the trusted host. Only name, category,
description, listed filenames and allowed endpoints form the public task.
The workspace has all fifty directories; the live serialized-input cap is now 512 KiB.

## Supplied targets and contestant files

File-only entries create one fresh ordinary Docker bridge. Service-backed entries
use the supplied Compose definitions, canonicalized by Docker itself, with fresh
project-owned networks and volumes. This keeps commands, dependencies, aliases,
backend membership, DNS, capabilities, temporary storage, users and supplied
resource settings. A small integration function retains image-ID pinning,
bounded startup/teardown, recorded adjustments and actual container/volume IDs.
It does not reimplement the NYU framework. Installed `nyuctf==1.1.1` lifecycle
helpers invoke the original file without our project/exposure/deadline controls,
so calling Compose directly remains the smaller explicit integration.

Concrete changes to supplied settings: remove host port publishing, build directives
when using supplied prebuilt images, global container/resource names and shared
Docker socket binds. Global `ctfnet` becomes project-local; backend definitions
are preserved rather than reconstructed. `target.json` records service adjustments.
The 27-file infrastructure inventory accepts 26 configurations; `msc-showdown`
remains unsupported because of privileged operation. Seventeen socket omissions
are explicit exceptions, not proof that all challenge behavior is unchanged.
A demonstrated need for Docker administration would require a separate engine;
a read-only socket bind still permits Docker API writes and is not a solution.

One demonstrated CPU exception is explicit: on ARM64/aarch64 **Docker engines**,
the exact supplied MongoDB 7.0.9 AMD64 reference
`mongo:latest@sha256:7b88befc893008d7139ce3276c093b3efd435023af8bb76a9d79fa90be1eaeb6`
is replaced by its same-release native sibling
`mongo@sha256:8ff69162926750978451697274dc3c93eac609894b9cff7ed977e76e6bcabcbe`,
with platform `linux/arm64`. AMD64 engines and all other references remain supplied.
Both are MongoDB **7.0.9-jammy** in the same official manifest index. This is a
recorded compatibility adjustment, not a generic image resolver. Application,
environment, commands, backend graph and endpoint scope are preserved.
[Evaluation](../evidence/mongo-arm64-evaluation/README.md) and
[normal integration](../evidence/mongo-arm64-integration/README.md) record the checks.

Compose `up --wait --wait-timeout 20` uses its standard running/healthy handling
within the existing 30-second CLI timeout. A shared small function records only
status/running/restarting, restart count, exit code, OOM and health status. It
rejects exited/restarting/OOM-killed or non-healthy declared-healthcheck states;
old restart counts alone do not reject a currently healthy service. Normal startup
and preparation's post-probe phase use it, retaining failure states before cleanup.
Environment values and healthcheck command/log bodies are excluded. There is no
new daemon, readiness framework, per-challenge application probe or configuration
field. Services without healthchecks still have no universal application-health
guarantee, and failures after these snapshots are possible.

Standard Compose `down --volumes` resets project/anonymous volumes. Read-only
server-file binds/configs/secrets must resolve inside the challenge directory;
Docker Desktop must share those host paths. Writable host binds and external/
custom volumes fail with a fresh-state error instead of silently persisting state.
Current CTFTiny definitions have no non-socket host binds, so no storage-copy or
nested-engine subsystem is added. Host namespace/device/privileged access is
rejected. Ordinary supplied mounts never enter the solver environment.

The previous forced target capability/DNS/tmpfs/log/resource policies disappear.
Targets now use normal Docker capabilities and network access unless the supplied
Compose says otherwise. They no longer receive the imposed 256 MiB resource cap;
solver CPU/RAM/PID/time/call limits remain. The solver still has zero effective
capabilities, no credentials/private mounts/socket, and no target admin tool.

The guard joins the exposed service's network directly and shares its namespace
with the solver. One ordinary bridge supplies both challenge connectivity and NAT
for approved package downloads; Docker chooses routes and resolves supplied service
names/aliases. Public descriptions retain hostnames while endpoint IP/port policy
is constructed from inspected containers. The extra egress bridge, gateway argument,
manual route replacement, forced internal/isolation settings and hostname rewriting
are gone. Backend networks retain service membership; a synthetic two-service case
checks frontend-to-backend DNS and denied direct solver access to the backend.

Only explicitly listed contestant files are transferred. Validation rejects
traversal, private metadata names, duplicate paths and symlinks. Listed Dockerfiles
remain outside the solver, with the omission recorded. Standard `docker cp`
transfers each file; trusted pre-agent setup creates parents and assigns UID/GID
1000. Source executable permissions and file hashes are preserved and verified.
The read-only-root/tmpfs copying workaround, in-memory tar and extractor are gone.

## Runner, agent and tools

The original Python-only solver omitted ordinary CTF utilities. A synthetic probe
also confirmed that Docker mounted `/workspace` with `noexec`, preventing even
a copied `/bin/true` from running. A conventional writable solver now permits workspace execution with non-root
commands and no effective capabilities. Numeric memory/time settings are project choices,
not assignment-prescribed values; the assignment requires enforced bounds and scope.

The normal build selects Linux AMD64 for the solver to match CTFTiny's x86
executables, while guard/fixture images remain native. Docker Desktop provides
emulation on Apple Silicon; native AMD64 Linux is preferable for speed and live
debugging (see [Docker platform guidance](https://docs.docker.com/build/building/multi-platform/)).
NYU's Ubuntu 22.04 recipe supplies its Python 3.10 environment and broad toolkit,
including SageMath, radare2, angr and multilib compilation. The installation body
is copied from release `20250206`, revision `112cfa3`; the MIT notice is retained
in [docker/NYU-LICENSE](../docker/NYU-LICENSE). This reuses their provisioning,
not their host setup or HTTP server. Our additions are writable `/workspace`,
non-terminal/unbuffered settings, NumPy 2.2.6, Pillow 12.3.0, installed-package
inventories and idle startup. All six previously supported Python capabilities
passed; host dependencies and agent interfaces are unchanged. The old requirements
input/lock are archived as [historical evidence](../evidence/solver-libraries/README.md),
with no active lock-regeneration workflow. Dockerfile/license enter source provenance.

The upstream recipe still uses floating downloads, including an external installer
that ignored some optional failures. Hashcat, John, steghide and Cutter were
absent; Sherlock failed. We do not maintain repairs for these unverified extras.
Source rebuilds are not exact artifact reproduction: the checksummed frozen image,
RootFS and OS/Python inventories identify the tested installation. Installed
versions are also embedded in `/opt/os-packages.txt` and `/opt/python-packages.txt`.
No workspace tmpfs or portable per-attempt disk quota remains. Docker's writable
layer persists across restart and disappears when the container is removed.

The professor approved runtime package downloads. Existing nftables/independent
NFLOG monitoring still permits assigned endpoints, Docker DNS and public IPv4 HTTPS;
other private/reserved destinations and unapproved ports are denied, recorded and
terminal. The guard installs enforcement before starting the solver, which lacks
NET_ADMIN and cannot change it. Normal Docker networking supplies connectivity;
it does not replace the guard. Internet purpose relies on instructions and trace
review, not a package-only proxy/domain firewall.
[Clarification](REFERENCES.md#authority-and-professor-clarification).

NYU's image prepares a writable isolated venv at `/home/ctfplayer/.ctfenv`; PATH
selects it. Normal home `/home/ctfplayer` and `/tmp` are writable. No environment is
created during attempt startup. The live profile retains 1 GiB RAM and 64 PIDs;
`workspace_mb` is removed because ordinary Docker writable storage provides no
portable per-container disk quota. The Docker host's available disk is a practical
limit. All additions disappear at final container removal, not at command restart.

`docker exec` starts `/bin/sh` in `/workspace` as UID/GID 1000. A bounded Python
selector loop drains stdout/stderr, including final output and closed-output
hangs. It keeps a combined beginning/end byte excerpt without accumulating full
output. The host never evaluates command text. A one-shot Python writer retains
existing descriptor-relative no-follow traversal checks; stdin carries path/text.
There is no worker daemon, Unix socket/RPC, PTY, session registry, supervisor,
subreaper, automatic output file or artifact-transfer protocol.

Ordinary nonzero exits return observations. A command timeout kills the local
Docker client, then restarts the same solver with Docker's SIGKILL restart. Killing
the client alone is insufficient: Docker owns the command. Restart kills all
solver processes, including detached children and unrelated background activity.
Files/pip installs survive; connections and memory do not. Targets and guard stay
running. The run ID, counters and original attempt deadline remain unchanged.
No command is automatically retried. The result explicitly reports the reset;
partial output is traced even if recovery fails.

A small lifecycle lock serializes startup/recovery with terminal stopping. A
terminal flag is set before waiting for that lock; recovery checks the deadline
and independent network-denial audit before and after restart. Scope/guard loss,
interruption, failed recovery and whole-attempt expiry remain terminal. Final
removal of the solver prevents a late lifecycle operation retaining the attempt.
Docker's standard init handles reaping; no per-command descendant cleanup is
claimed on normal exit. Background tasks can survive until reset/final cleanup.

Output up to 64 KiB raw bytes is returned whole; larger output retains head/tail
and explicit truncation/counts. UTF-8 decoding replaces invalid bytes. To retain
omitted output, commands can redirect it to files. Automatic artifact retrieval
is deliberately removed. The recorded tool observation is exactly what the model
receives. Initial package inventory uses ordinary Python metadata; an optional
final inventory records availability, commonly unavailable after terminal stop.
There are no repeated per-tool scans; installation activity remains in the trace.
Historical records and output files remain unchanged.

GDB permissions and debugging support are unchanged and further work is deferred.
Static inspection works; live debugging failed in the recorded Apple Silicon
probe. Removing terminal sessions does not change that separate limitation.

The trusted response boundary copies the public tool definitions and inserts the
active command timeout maximum/default before tracing and invoking the model.
It shares no other private runner state and leaves the static definitions intact.
Commands use `/bin/sh`; Bash syntax requires an explicit `bash` invocation.

`run_attempt()` owns resources, the deadline/watchdog, counters, answer key,
Langfuse root observation and final result. It yields a small operator record;
`run_agent(public_task, respond, call_tool)` receives only public text and two
bounded functions. Closures keep private state outside model messages and trace
inputs. The answer is used only by trusted exact-equality verification.

`submit_flag` is one of the three existing tools, not a separate evaluator API.
Candidates and verdicts are recorded; the expected answer is never separately
exposed. The other tools run commands and write files only inside the solver.
Their [contracts](../README.md#architecture-and-tool-contracts) cover validation,
outputs, timeout and error behavior. Host validation and one-shot filesystem checks
protect distinct boundaries and remain separate.

The agent retains the system prompt, public task, assistant replies and matching
tool observations. Calls execute sequentially; the next model request sees their
results. Verified success prevents later actions, including remaining sibling calls.
The current prompt asks the model to revise contradicted assumptions, diagnose
recoverable errors, verify corrections, preserve diagnostic/completion output,
and investigate a blocker before ending. [Experiment 1](EXPERIMENTS.md) records
the hypothesis and pending comparison. This changes guidance, not loop behavior;
its effect on live persistence and cost is unmeasured.
Wrong submissions and ordinary command errors permit continuation. Text-only replies
end without verified success. Hard attempt/model limits, scope denial, guard loss
and infrastructure failures stop the attempt. `AttemptStopped` is a small exception that
carries the enforced reason; unrelated errors propagate.

Context is public history plus workspace files, which are not automatically inserted
into prompts. There is no compaction, cross-attempt memory or planning subsystem.
The Responses adapter replays native output items, including encrypted reasoning,
and links function results by call ID. The serialized-input bound stops oversized
requests. Add context-fitting behavior only when development evidence warrants it.

A context manager owns resource cleanup even on exceptions/interruption. The
independent watchdog stops the solver while a response is pending. A Python callback
cannot be forcibly interrupted; live HTTP calls disable retries and have bounded
transport timeouts. Remote cancellation and billing cancellation are not guaranteed.

## Limits and accounting

The same existing hard limits cover wall time, model turns, tool calls, command
runtime, output bytes, file writes and container resources. Live settings come from
the complete `configs/development.toml`. `config.py` only loads and validates
values; missing/unknown fields fail clearly. Alternative experiments copy that
file and use `--experiment`. One `max_model_turns` value also supplies the
model adapter's internal `max_requests` guard. The current live profile permits
600 seconds per attempt, ordinary commands up to
120 seconds, 60-second model requests, forty model turns/requests and eighty tool
calls. Model input is bounded to 512 KiB serialized data and output to 4,096 tokens.
Synthetic controls and preparation use the same complete file; the optional
paid model check applies small explicit test bounds inside `tests/check_model.py`.
The redundant `configs/initial.toml` and application fallback dictionaries are
removed. All values are project choices; the assignment requires enforced limits,
not those particular numbers.

Preparation now loads the selected experiment through the same loader as live
runs. The trusted run record exposes a remaining-time callback for ordinary file
copying; transfer shares the original attempt deadline.

The user approved removing the local spending cap and all reservation accounting.
`make_responder()` still returns a function and per-attempt usage dictionary.
API usage supplies token counts and estimates from configured gateway rates;
cached/reasoning subsets are not double counted. Missing usage sets aggregate
token/cost totals to null and marks
usage incomplete, while valid replies continue. Per-response usage remains in
native observations where supplied. Provider/account limits are separate.

## Tracing and evidence

Langfuse is the sole detailed tracing system. Native OpenAI instrumentation creates
live generation observations; scripted tests use manual generations. Tool results,
incidents, stopping and cleanup are root-linked observations/events. Trusted setup
functions are not automatically decorated: package objects, expected answers,
credentials, locks and controller state must never become trace arguments.

`summary.json`, `run.json`, source hashes and image IDs are ordinary results and
provenance, not another detailed log backend. SDK flushing happens after solver
cleanup; the application owner shuts down the client. The existing Python SDK
exports hosted observations to `observations.json` using cursor pagination,
including empty pages with continuation cursors. Page size is 100, not a total
record cap. Readback retains its 90-second deadline and completion polling.
The launcher audits counts, completion, parentage,
credentials and cleanup. Missing evidence prevents marking the launch complete.
No fallback tracing backend or custom durable exporter is introduced.

Rejected arguments are not traced as accepted input. Late replies execute no tools;
automatic live instrumentation may retain their bounded provider output/usage with
an explicit discard event. A normal HTTP hook removes raw provider error bodies
before automatic tracing sees them. Secret credentials stay host-side; the SDK's
public project identifier appears in native instrumentation metadata.

`reasoning.summary: auto` uses native response replay/capture without another call.
The one approved benign compatibility request returned an empty summary; a later
development run returned readable summaries in three of seven generations. Their
presence is not guaranteed. Tool arguments/results and visible assistant text remain
available for inspection. The user subsequently approved one system-prompt sentence
asking for a brief visible action explanation with each tool call
in the same response. The existing native generation output captures that text;
no schema, tool, parser, extra turn or control-flow change was needed. This requests
an action explanation, not private internal reasoning. The current wording asks
for the purpose or what the action will test, without requiring an expected result.
Prompt wording can affect
model behavior and token use. The reviewed development run included visible
explanations in all seven generations; performance equivalence is unverified.

## Verification scope

Fast tests check contracts, loop recovery/context, trusted verification, model
transport and split labeling with substitutes. Synthetic Docker tests establish
resource/isolation/incident boundaries. The preparation command separately checks
real contestant staging and target startup without model calls or solving. These
layers protect different boundaries; repeating the entire suite for every routine
edit is unnecessary.

The selected ten and `pwn-baby-boi` each passed two fresh preparation cycles with
file hashes/ownership, private boundaries, permitted TCP connect-and-close,
independent packet-denial evidence, solver stopping, reset and cleanup. Native SDK
spans use the established local in-memory exporter; no hosted credentials or uploads
are needed. Invoke each preparation through a separate CLI process: repeatedly
creating/shutting down the same Langfuse project client in one diagnostic process
reused SDK state and produced empty later exports. No application workaround was
needed for the normal one-invocation lifecycle.

Four later development preparations passed, bringing runtime coverage to fifteen
challenges. All fifty file inventories were checked; the remaining thirty-five
environments have not passed runtime preparation. `msc-showdown` is a known
unsupported privileged target. Subsequent [solver checks](../evidence/solver-readiness/README.md)
cover baseline utilities and benign executable handling, separately from challenge
preparation. Preparation is not a solve, pilot, scored evaluation or improvement
comparison. [Status](../PROJECT_STATUS.md) and [readiness evidence](../evidence/benchmark-readiness/README.md)
record the completed scope and the Section 2 handoff.
