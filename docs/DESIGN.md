# Design choices and alternatives

The [assignment](../ASSIGNMENT.md) requires adaptive tool use, solver/evaluator
separation, enforced limits, trusted verification and complete records. CTFTiny
is the active benchmark. [Original references](REFERENCES.md) explain how the
NYU package and conventions informed this setup. Functions, dictionaries and
resource-owning context managers keep the implementation understandable without
an agent framework or application class hierarchy.

## One challenge path

`run-challenge --challenge ID` loads an indexed challenge through the installed
`nyuctf` package and uses the same lifecycle, agent, tools and evaluator for every
selected ID. The existing manifest supplies the development/scored result label.
A separate scoring agent or CLI mode would duplicate behavior; separation belongs
in the challenge selection and experiment records. The ten reserved IDs remain
held out from development solving.

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
The workspace now has all fifty directories and a 256 KiB live input-size cap.

## Supplied targets and contestant files

File-only entries create no service but retain a fresh isolated solver network.
Service-backed entries use their supplied Compose image, service name, alias and
internal port. Ordinary Compose canonicalization supplies dictionaries rather than
requiring a YAML dependency. The runtime removes published host ports and Docker
socket mounts, rejects other mounts/unsupported arrangements, and attaches services
to a fresh isolated internal bridge. Supplied backend networks stay private and
internal. Docker-managed target volumes are removed and checked during cleanup;
host bind mounts remain prohibited. Privileged targets are rejected. Supplied
build directives are not executed when using prebuilt images. The original dataset
files stay unchanged.

Package lifecycle helpers would run the original Compose configuration directly.
A small controlled runtime configuration is required to retain the assignment's
access boundaries. A per-challenge adapter would add unnecessary code for the
selected services, which all use the same conventions. Missing images are pulled;
resolved local IDs and architecture are recorded and fixed within the attempt.
Tags may resolve differently after a later pull; freeze recorded images alongside
code/settings before comparison. This is not a bit-for-bit rebuild guarantee.

Targets have bounded CPU/memory/PIDs/tmpfs/logs, no published ports or host mounts,
no-new-privileges and capabilities limited to CHOWN/SETUID/SETGID. Targets use
normal disposable writable layers: a read-only target broke Nginx's log/temp-file
startup, and dropping CHOWN broke ownership setup. Restoring those normal startup
capabilities is simpler than challenge-specific entrypoint patches. These target
permissions do not change the solver's read-only, non-root, zero-capability setup.
The model receives no target administrative shell.

The selected alias maps to the service IP. Public task text replaces the literal
benchmark hostname with that IP; the guard permits only the recorded endpoint.
DNS stays blocked. More complex network/service arrangements fail closed rather
than silently widening access. Preparation verifies four reserved services and the
development example; the six remaining reserved challenges are file-only.

Only explicitly listed contestant files are transferred. Validation rejects
traversal, private metadata names, duplicate paths and symlinks. Listed Dockerfiles
remain outside the solver, with the omission recorded. A tar stream
goes through fixed Docker exec arguments to Python's standard data-filtered
extractor, as UID/GID 1000, into the solver's bounded `/workspace` tmpfs. Docker cp
refused the read-only solver root, including its writable tmpfs; streaming preserves
that control without another dependency or mount. Records retain names/sizes/hashes.

## Runner, agent and tools

The original Python-only solver omitted ordinary CTF utilities. A synthetic probe
also confirmed that Docker mounted `/workspace` with `noexec`, preventing even
a copied `/bin/true` from running. The solver now explicitly permits workspace
execution while retaining `nosuid`, `nodev`, a read-only root, non-root execution
and zero capabilities. Numeric memory/workspace/time settings are project choices,
not assignment-prescribed values; the assignment requires enforced bounds and scope.

The normal build selects Linux AMD64 for the solver to match CTFTiny's x86
executables, while guard/fixture images remain native. Docker Desktop provides
emulation on Apple Silicon; native AMD64 Linux is preferable for speed and live
debugging (see [Docker platform guidance](https://docs.docker.com/build/building/multi-platform/)).
Distro packages supply file/binutils/xxd, curl/netcat/OpenSSL, ZIP tools,
GCC/make/GDB and 32-bit runtime libraries. This avoids a broad analysis framework
or custom emulator integration. Installed OS versions are recorded in
`/opt/os-packages.txt`; image IDs remain part of attempt provenance. Baseline
tool availability does not guarantee arbitrary binary or specialized-package support.
Docker documents the explicit workspace option in its
[tmpfs mount options](https://docs.docker.com/engine/storage/tmpfs/).

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
outputs, timeout and error behavior. Host validation and worker filesystem checks
protect distinct boundaries and remain separate.

The agent retains the system prompt, public task, assistant replies and matching
tool observations. Calls execute sequentially; the next model request sees their
results. Verified success prevents later actions, including remaining sibling calls.
Wrong submissions and ordinary command errors permit continuation. Text-only replies
end without verified success. Hard limits, command timeout, scope denial, guard loss
and protocol failures stop the attempt. `AttemptStopped` is a small exception that
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
`configs/development.toml`, over shared defaults. After initial setup, the user
approved a 300-second live profile with 30-second command/model timeouts, twenty
model turns/requests and forty tool calls. Unspecified settings inherit defaults;
the synthetic/preparation configuration remains unchanged. Per-attempt
request/output/cost bounds remain, with ordinary usage
records instead of a persistent spending subsystem. Review costs between attempts.

`make_responder()` returns a function and non-secret usage dictionary, fresh per
attempt. Conservative input/output reservations precede dispatch and remain charged
against the cap after failures/timeouts. API usage supplies token counts and local
cost estimates from the configured gateway rates. Cached/reasoning subsets are not
double counted. Missing usage is unknown and stops the attempt. These are estimates,
not an independent invoice audit. README lists current settings.

## Tracing and evidence

Langfuse is the sole detailed tracing system. Native OpenAI instrumentation creates
live generation observations; scripted tests use manual generations. Tool results,
incidents, stopping and cleanup are root-linked observations/events. Trusted setup
functions are not automatically decorated: package objects, expected answers,
credentials, locks and controller state must never become trace arguments.

`summary.json`, `run.json`, source hashes and image IDs are ordinary results and
provenance, not another detailed log backend. SDK flushing happens after solver
cleanup; the application owner shuts down the client. The official pinned CLI
exports hosted observations, and the launcher audits counts, completion, parentage,
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
asking for a brief visible purpose/expected-result explanation with each tool call
in the same response. The existing native generation output captures that text;
no schema, tool, parser, extra turn or control-flow change was needed. This requests
an action explanation, not private internal reasoning. Prompt wording can affect
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
