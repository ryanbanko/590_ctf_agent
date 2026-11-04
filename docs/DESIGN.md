# Design choices and alternatives

The [assignment](../ASSIGNMENT.md) requires adaptive behavior, isolation, trusted
verification, enforced limits, and complete evidence. It does not prescribe a
class architecture, agent framework, trace format, or provider. CTFTiny is the
benchmark goal; [the original resources](REFERENCES.md) preserve how reviewed
NYU conventions support it. The user's preference is understandable code and
minimal maintenance across runtime, setup, dependencies, tests, and configuration.

## Runner, loop, and tools

The trusted runner owns containers, the deadline/watchdog, counters, evaluator
answer, and Langfuse root observation. The loop receives only public task text and
bounded `respond` / `call_tool` functions. It has no lifecycle-state dictionary,
answer key, SDK client, or container control handles. Both functions are ordinary
closures created by the runner; they retain access to resources without sending
those resources to the model or SDK observation inputs.

`submit_flag` remains one of the three tools. Its dispatcher branch verifies exact
equality inside the trusted runner. There is no extra verifier interface exposed
to the loop. `tools.py` holds schemas, validation, and command/file dispatch; it no
longer receives the expected answer. The answer is absent from state/results and
is never separately traced. Candidate submissions and verdicts remain observable.

The runner yields an operator/controller record containing functions, result
metadata, output directory, and container identifiers for trusted inspection.
`run_agent(public_task, run["respond"], run["call_tool"])` receives only the two
functions. That record is not a second public/private copy of execution state.
Private control state holds the lock, deadline, watchdog event, sandbox, root
observation, and reference to result counters. The answer stays in lexical scope.

`AttemptStopped` is one small `RuntimeError` subclass carrying a reason string.
It gives bounded functions a precise way to report enforced termination without
exposing private state. The loop catches only that exception; unrelated runtime
errors propagate. This is a concrete exception boundary, not an application class
model. Ordinary functions/dictionaries remain preferable to a controller class or
provider/dispatcher registry at the present scale.

A context manager owns attempt lifetime: prepare, yield the bounded functions,
then stop/clean up and write the result even on exceptions or interruption.
This is Python's standard resource-lifetime pattern. Replacing it with repeated
manual setup/finally blocks would duplicate cleanup. The model loop and tools do
not own container lifetime. Target staging/reset for CTFTiny remains separate work.

<a id="context-passed-between-turns"></a>
<a id="what-remains-after-the-loop"></a>

## Context and return values

Each response receives full public history: common system prompt, public task,
previous accepted assistant replies, and matching tool results. Tool schemas are
passed separately. The loop copies history/schemas so a callback cannot mutate
those input objects. The bound response function supplies the remaining timeout
to the trusted scripted source or live Responses adapter.

The user chose Responses and Langfuse's automatic OpenAI integration. Chat
Completions would require fewer format changes, but Responses supports the
reasoning/tool flow of the selected model. `model.py` translates the existing
message contract into native input items. A live assistant reply carries its
original `response_items` alongside the tool/text projection used by the loop.
On the next request the adapter replays those original items, including any
encrypted reasoning, then links tool results through `call_id`. This avoids a
second hidden conversation store and keeps scripted fixtures compatible.
`store=False` keeps conversation management explicit in our process.

For one tool per turn:

```text
Request 1 = system + task
Request 2 = system + task + assistant tool request + matching tool result
Request 3 = the same history + next assistant request + matching result
```

Several tools in one response run sequentially before another response is requested.
The runner validates the envelope and unique call IDs, parses/validates tool inputs
at their boundary, and enforces model-turn/tool/time caps. Malformed JSON becomes
a validation observation and consumes tool budget. Final text stops without
verified success; a correct `submit_flag` stops immediately with no extra model
request. Bounded functions reject all later requests after stopping.

The solver workspace/process state persists between tools in an attempt. Files are
not automatically included in the conversation; content enters through supplied
public text or tool observations. Each attempt starts fresh. There is no context
compaction, cross-attempt memory, retrieval store, or token-aware fitting. Byte and
turn bounds make records finite. The live adapter now rejects requests above a
32 KiB serialized-input bound; it does not compact history or implement a general
token-aware context-fitting system.

The loop returns a reason string, not its messages or final prose. Leaving the
attempt context performs cleanup, flushes the SDK, writes `summary.json`, and
updates `run["result"]`. That result records final status/counters/timing and the
Langfuse trace ID. Root output captures the result before export; final local timing
also includes `trace_flush_seconds`. Cleanup failure is surfaced after records
are written. The summary and evaluator result—not a model's success claim—support
later evaluation.

## Langfuse as the sole detailed tracing system

The user chose a full Langfuse migration rather than a hybrid/custom backend.
The prior JSONL writer, event sequence counter, trace-file lock, and application
`tracing.py` module were removed. Previous evidence remains historical. Runtime
tracing uses the official SDK directly, without another tracing interface/registry.

| Activity | Native Langfuse representation | Safe recorded data |
| --- | --- | --- |
| One complete attempt | Root observation | Public task, run/challenge IDs, configuration, image IDs, result before flushing. |
| Scripted response | Runner generation observation | Full messages/schemas, turn/timeout metadata, accepted reply. |
| Live Responses request | Automatic OpenAI integration generation | Actual native input/tools, output, model/settings, timing, and usage. |
| Tool request | Tool observation | Validated arguments, step, returned observation; rejected raw arguments omitted. |
| Guard/stopping/cleanup incidents | Events attached explicitly to root | Packet-denial evidence, stop trigger, infrastructure/cleanup failures. |

SDK observation contexts supply start/end timing and exception records. The runner
updates only application-specific inputs, outputs, and statuses. `run_attempt()` is
not automatically argument-captured: its expected answer and client stay private.
Scripted callback exceptions are sanitized inside generation scope; their rejected
or late outputs remain omitted. Live automatic generations retain provider outputs
and usage, including replies later rejected/discarded by the runner. The output-token
cap bounds generation; explicit runner events record rejection/discard and no late
reply executes tools. A standard HTTP response hook raises a status-only error before
the OpenAI/Langfuse integrations can record a raw provider error body. SDK public-key
scope metadata is a public project identifier; gateway tokens and Langfuse secret
keys stay outside trace data and solver containers.

Background guard/watchdog threads hold the root observation and create native
child events through it. They do not depend on implicit thread-local context
propagation or an application log lock. The SDK handles observation synchronization.
The controller lock remains necessary for first-stop ownership. An unexpected
solver-kill error can replace the initial trigger with infrastructure failure;
both the trigger and failed kill remain in the trace.

Runtime dependencies are pinned `langfuse==5.1.0` and `openai==3.44.0`, including their
locked transitive dependencies. This adds setup cost in exchange
for established instrumentation, trace structure, and a hosted review interface.
The user accepted that tradeoff. An agent framework, tracing wrapper framework,
self-hosted observability stack, and generic exporter are unnecessary here.

`summary.json`, suite configuration, source hashes, and resolved image IDs remain
ordinary result/provenance artifacts. They do not duplicate the detailed transcript.
SDK flushing happens after solver cleanup; the application owner shuts down its
client at process exit. Standard SDK export failures do not skip stopping/cleanup,
but a local result/trace ID alone does not prove hosted evidence is complete.
One hosted synthetic check now verifies authentication, ingestion, readback/export,
and trace completeness for the configured project. A later two-request live
synthetic check verified actual usage and automatic generation parentage.
General availability remains unverified. No custom retry, durable fallback log, or hosting
system has been introduced. Cloud setup followed the earlier SDK/local milestone.

The explicit `langfuse-check` command delegates to test support, reuses the existing
scripted flow, and uses the normal SDK exporter. A bounded poll of the documented
observations API handles asynchronous ingestion and cursor pagination; it does not
retry model requests or add runtime tracing machinery. Raw hosted exports are
verification artifacts. The official CLI independently read back the same records.
The installed [official skill](https://github.com/langfuse/skills) guided the review.
No replacement instrumentation was needed: the current messages/tools input format
already matches the SDK's native model-integration convention. `model-check` now
performs the separately approved live synthetic check and uses the official CLI
for readback. Live requests have no surrounding manual generation observation.

## Model budget and accounting

`make_responder()` returns an ordinary function and a non-secret usage dictionary,
fresh per attempt. The runner copies that accounting into results after every
source invocation, including failure and late response. The loop receives neither
the client nor usage/controller data. No provider registry or application class
has been added. Model settings are one small dictionary for this approved check;
general model configuration and scored model selection are separate future work.

The user confirmed $1/day and approved one attempt capped at four generation
requests and $0.10. `gpt-6-luna` uses low reasoning and 1,024 output tokens/request.
Before dispatch, serialized request bytes conservatively bound byte-level token
input, with 1,024 tokens of framing allowance and a 1.25x cache-write price reserve.
Every reservation remains spent against the cap even after errors/timeouts; no
input cache discount is assumed for the reservation. The adapter stops before
dispatch if request count, input size, or cumulative reservation exceeds its limit.
Rates are a gateway metadata snapshot, not an independently verified invoice.

Token counts come from API usage, with cached/reasoning subsets distinguished to
avoid double counting. Costs are local estimates from those counts and gateway
rates; automatic hosted cost inference agreed for the verified trace. Missing usage
or failed transport leaves cost unknown and stops the attempt. Client retries are
disabled. Timeout is at most 20 seconds, clipped to the remaining attempt time;
the independent watchdog still stops the solver, but remote cancellation/billing
and a strict host transport deadline are not guaranteed by these settings.

## Testing and evidence

The approved CTFTiny readiness work starts with a metadata-only split and a small
trusted loading/staging module. It uses the existing three tools and solver controls.
Contestant files are selected from the package's explicit file list, with traversal,
private metadata names, and symlinks rejected. Docker's standard tar input copies
binary files as UID/GID 1000 before model execution in the implemented staging
path; actual container transfer remains unverified. Returned records contain file
names, sizes, and hashes rather than contents. Public task construction whitelists
description/name/category, file inventory, and permitted endpoints. Package objects
and expected answers stay trusted. Current verification is offline only; the dataset
revision/dependency and actual target lifecycle remain pending. Target-specific
Compose decisions will follow inspection rather than speculative support for all tasks.

Pytest discovers ordinary function tests and Docker-marked scenarios. One small
launcher adds source/image provenance, JUnit/suite results, and cleanup checks.
It has no hard-coded case count. Fixed synthetic targets and scripted sources live
under `tests/`; the application contains no synthetic service or control suite.

Local tests initialize the real SDK with its supported `span_exporter` argument and
OpenTelemetry's standard `InMemorySpanExporter`. No hosted credentials or network
upload is needed. Tests inspect actual native spans, link them to summary trace
IDs, and save SDK-native `otel-spans.json` for Docker verification only. This is
SDK output capture, not a second application tracing backend. Failure tests cover
an exporter reporting failure and disabled tracing preventing solver startup.
The separate hosted check requires explicit credentials and uploads only its
synthetic attempt. Five fast cases cover hosted audit/completeness, leakage
rejection, pagination/ingestion waiting, and deadline behavior using API DTOs.

Pure validation tables test the validator directly; loop checks cover context,
recovery, verification, and stopping. Docker checks establish concrete isolation,
network, resource, interruption, and cleanup behavior. These layers exercise
different boundaries; reducing repetition does not mean removing distinct probes.

## Other retained decisions

- Host argument validation and worker symlink/directory-descriptor protection
  remain separate boundaries. Sharing them across images would weaken ownership.
- Host pipe bounds and solver stdout/stderr bounds protect different processes.
  The two incremental readers have different jobs and are not a generic utility.
- The watchdog independently stops the solver during waits. Callbacks must honor
  their timeout; arbitrary Python callbacks cannot be forcibly interrupted here.
  Live transport has one successful synthetic check; interrupted remote billing is unverified.
- Solver, target, and trusted guard stay separate. Commands have no administrative
  target shell, host mounts, Docker socket, answer key, or credentials. Langfuse
  activity is host-side and grants no solver internet access.
- Docker CLI argument lists remain simpler than adding a Docker SDK; model-controlled
  text goes to the solver over stdin. Local dependency/image pins and resolved IDs
  support reproducibility without claiming bit-for-bit image rebuilds.
- CTFTiny loading should later use its explicit index through `nyuctf`; preserve
  supplied Compose definitions wherever compatible. Generic benchmark adapters,
  held-out answer/write-up access, and current real challenge solving are excluded.
- The strict response envelope now additionally permits native `response_items`.
  No speculative provider support or configuration generation was added.

Sources: [Langfuse SDK](https://langfuse.com/docs/observability/sdk/overview),
[instrumentation](https://langfuse.com/docs/observability/sdk/instrumentation),
[client/exporter reference](https://python.reference.langfuse.com/langfuse),
[Python resource context managers](https://docs.python.org/3.13/library/contextlib.html#contextlib.contextmanager).
