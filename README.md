# CTFTiny agent benchmarking

This repository implements the initial system for the [course assignment](ASSIGNMENT.md).
It provides a bounded conversation/tool loop, isolated command/file tools, trusted
synthetic flag verification, and Langfuse tracing. Responses model access through
Duke is verified with one synthetic attempt. CTFTiny loading and contestant-file
staging are partly implemented; real dataset/target verification remains pending.
No real challenge attempts have occurred.

Read [PROJECT_STATUS.md](PROJECT_STATUS.md) for current scope and the assignment
roadmap. [Original resources](docs/REFERENCES.md) preserve the user's references
and the professor's clarification; the original assignment is authoritative.

Latest recorded verification: **53 fast tests passed** on November 3, 2026.
The completed [model milestone](evidence/model-integration/README.md) used
**2 model requests**, 837 input/100 output tokens, and an estimated **$0.0001337**
for one successful synthetic attempt on native ARM64. The last full Docker suite
passed [19 synthetic checks](evidence/langfuse/README.md); it was not repeated for
the later work, which used focused checks and preserved the isolation implementation.

The approved CTFTiny readiness milestone is unfinished. Its metadata-only split
and preliminary staging code are covered by the newer fast-test record, but the
dataset revision, loader installation, real transfer/target checks, and launch
command are pending. See [current status](PROJECT_STATUS.md) and
[partial evidence](evidence/ctftiny-readiness/README.md). Completed evidence
directories preserve historical snapshots; use this README for current commands.

## How to use

Install Python **3.13.2** and uv, then run the following from the repository root:

```sh
uv sync --frozen
```

`uv.lock` pins runtime dependencies **Langfuse 5.1.0** and **OpenAI 3.44.0**,
development dependency **pytest 9.2.0**, and their transitive dependencies.
Container checks also require Docker Desktop/Engine with Linux containers and
Docker Compose v2. The live hosted check additionally uses Node.js/npm (`npx`)
for official Langfuse CLI readback.

**Set up keys for hosted use.** Local tests do not need credentials. For hosted
tracing or live model access, create a local `.env` from the example once:

```sh
cp -n .env.example .env
chmod 600 .env
```

Fill these variables in `.env`:

| Variable | Where to get it | Needed for |
| --- | --- | --- |
| `LANGFUSE_PUBLIC_KEY` | Intended Langfuse project's Settings → API Keys. | Hosted tracing. |
| `LANGFUSE_SECRET_KEY` | Same project's API key pair. | Hosted tracing. |
| `LANGFUSE_BASE_URL` | That project's regional URL, such as `https://us.cloud.langfuse.com` for US or `https://cloud.langfuse.com` for EU. | Hosted tracing. |
| `LITELLM_TOKEN` | Sign in to the [Duke AI Dashboard](https://dashboard.ai.duke.edu/), open AI Gateway, and create an API key. See the [Duke guide](https://ai.colab.duke.edu/colab-ai-blog/all-blogs/getting-started-with-dukes-ai-gateway-a-developers-guide/). | Live model requests through Duke. |

Use your own Duke key and the Langfuse project agreed on by the team. The example
URL is for EU; use your actual project's region. A separate `OPENAI_API_KEY` is
not required for the configured Duke gateway. `.env` is Git-ignored and is not
included in a fresh checkout. Keep credentials on the host, outside containers
and trace inputs. Commands below load `.env` explicitly with uv's `--env-file`.

**Run local checks.** Start with the fast tests; they need no Docker, keys, model
calls, or hosted trace uploads:

```sh
uv run python -m pytest -q
```

For the full synthetic Docker controls check, first start Docker and build the
images, then run `self-check`. It also needs no keys or model calls:

```sh
uv run python -m ctf_agent build-images
uv run python -m ctf_agent self-check
```

The default pytest selection contains 53 fast cases. `self-check` discovers the
19 Docker-marked cases, stops on the first failure, saves provenance/JUnit results,
and verifies cleanup. Both use the real Langfuse SDK with its supported
OpenTelemetry in-memory exporter. The Docker suite starts only synthetic targets.

**Run hosted checks when authorized.** Build the images above first. The tracing
check requires the three `LANGFUSE_*` variables and uploads one scripted trace:

```sh
uv run --frozen --env-file .env python -m ctf_agent langfuse-check
```

The live check also requires `LITELLM_TOKEN` and makes paid model requests. Agree
on its spending/request cap before running; each invocation starts a new attempt:

```sh
uv run --frozen --env-file .env python -m ctf_agent model-check
```

See [live-check settings and limits](#live-synthetic-model-check). Check your own
gateway account's allowance before paid runs. These commands verify synthetic
setup only; a real CTFTiny preparation/solver launch command is still pending.

The build command creates the solver, guard, and synthetic fixture images. The
self-check creates temporary `ctf590-*` containers/networks labeled
`ctf590.managed=true`, then removes them. Run Docker suites and hosted synthetic
checks sequentially because cleanup verification queries that shared label.
Check commands default to `runs/` and create a fresh directory beneath the output
root on each invocation. Override that root with `--output`:

```sh
uv run python -m ctf_agent --config configs/initial.toml self-check --output runs
```

Output is synthetic setup evidence, not a development pilot, scored run, or
successful autonomous CTF demo. If uv's normal cache is restricted, set
`UV_CACHE_DIR` to a writable directory. The synchronized `.venv/bin/python` also
works directly in place of `uv run python`.

## Code responsibilities

The application uses functions, closures, dictionaries, and resource-owning context
managers. `AttemptStopped` is a small exception carrying only an enforced stop
reason; it distinguishes termination from unrelated programming errors.

| File | Responsibility |
| --- | --- |
| `ctf_agent/__main__.py` | Image builds and explicit local/hosted synthetic check commands. |
| `ctf_agent/agent.py` | Public conversation history and dispatch through bounded model/tool functions. |
| `ctf_agent/attempt.py` | Trusted resources, budgets, answer verification, Langfuse observations, and final result. |
| `ctf_agent/model.py` | Responses translation, native context replay, HTTP-error handling, request/spending bounds, and usage accounting. |
| `ctf_agent/challenge.py` | Development-only CTFTiny loading and contestant-file staging; real setup verification pending. |
| `ctf_agent/tools.py` | Three tool schemas, argument validation, and solver command/file dispatch. |
| `ctf_agent/sandbox.py` | Solver/guard lifetime, network monitoring, and Langfuse incident events. |
| `ctf_agent/docker.py` | Fixed Docker invocations and bounded worker communication. |
| `ctf_agent/config.py` | Non-secret TOML settings and validation. |
| `tests/conftest.py` | Native SDK capture, test substitutes, and Docker fixtures. |
| `tests/check_controls.py` | Pytest launch, source/image provenance, suite summary, and cleanup check. |
| `tests/check_langfuse.py` | One synthetic hosted run, bounded readback, trace audit, and evidence export. |
| `tests/check_model.py` | One explicitly approved live synthetic attempt and official-CLI trace readback. |
| `tests/test_model.py` | Offline SDK transport checks for context, automatic tracing, budgets, errors, and late replies. |
| `tests/test_challenge.py` | Offline public-data, file-staging, and split checks; no real dataset or Docker transfer. |
| `tests/test_hosted_tracing.py` | Hosted audit/completeness and readback pagination/deadline checks without network. |
| `tests/test_agent.py` | Loop behavior, context, recovery, and stopping. |
| `tests/test_contracts.py` | Tool/configuration contracts and tracing/control failure paths. |
| `tests/test_controls.py` | Original 17 synthetic Docker controls checks. |
| `tests/test_agent_controls.py` | Scripted success/recovery and late-response Docker checks. |
| `tests/fixtures/` | Synthetic target/service, scripted messages, and native SDK span inspection/export. |
| `docker/worker.py` | Command/file operations inside the solver. |
| `docker/guard.py` | Namespace firewall and independent packet-denial collection. |

See [design and alternatives](docs/DESIGN.md) for responsibilities and decisions.

## Loop and context

The trusted runner yields a small controller record. The loop receives only public
task text and the two bounded callables, not that record or private runner state:

```python
# Schematic use after obtaining public target metadata and a configured SDK client.
with run_attempt(..., langfuse=client, public_task=task, respond=scripted_source) as run:
    reason = run_agent(task, run["respond"], run["call_tool"])
# run["result"] now contains the final summary, also saved as summary.json.
```

The runner's response source accepts `messages`, `tools`, and the remaining
`timeout_seconds`, and returns an assistant-message dictionary with JSON-encoded
function arguments. Sources include scripted fixtures and the live Responses
adapter. Live replies also carry native `response_items`, preserving reasoning
and function items for replay. `run_agent()` retains the system prompt, public task,
assistant replies, and matching tool observations, passing copies at each turn.
The solver workspace persists between tools; files are not automatically inserted
into prompts. There is no history compaction, cross-attempt memory, or token-aware
context fitting yet.

The runner's bound response function enforces the deadline/turn cap and checks
responses. Its tool function enforces argument validation, tool count, scope, and
trusted verification. The expected answer stays in the runner's closure, outside
state/results and model messages. The loop returns a reason string. A correct
submission ends immediately; a text-only reply ends without verified success.
[Context design](docs/DESIGN.md#context-and-return-values) explains the complete flow.

## Langfuse and result artifacts

**Langfuse is the sole detailed tracing system.** The application has no custom
JSONL writer, event sequence counter, trace-file lock, or fallback trace backend.
A root `attempt` observation contains public task input and selected configuration/
run metadata. Bounded model requests create generation observations; bounded tools
create tool observations. Live generations come automatically from
`langfuse.openai.OpenAI`; the runner creates no duplicate generation. Scripted
fixtures retain their manual generations. Guard, stopping, and cleanup incidents
are native events attached to the root, including events from background threads.

Trusted setup functions are not decorated with automatic argument capture. Their
answer key, client credentials, locks, and controller objects are never trace
inputs. Tool observations contain validated inputs and returned results, including
candidate flags/verdicts. Rejected tool inputs are omitted. Scripted rejected/late
replies are omitted; automatic integration retains bounded live provider replies
and usage even if the runner discards them. Explicit events record rejection or
discard, and such replies execute no tools. A standard HTTP response hook replaces
provider error bodies with the HTTP status before automatic tracing observes them.
Secret keys/tokens never enter trace inputs. The SDK's own public project identifier
appears in native instrumentation-scope metadata.

Each attempt still writes `summary.json`: run/challenge/trace IDs, outcome, tool
and scripted/model counts, available token/cost fields, timing, and cleanup errors.
Total time includes SDK flushing; `trace_flush_seconds` records that overhead.
The root observation's output is the result before flushing. The self-check suite
also retains configuration, source hashes, image IDs/architecture, and JUnit records.
These are result/provenance artifacts, not a second detailed tracing stream.

For checks only, the test exporter saves `otel-spans.json` using the SDK's native
OpenTelemetry serialization. It captures actual SDK output without a hosted project;
it is not an application runtime exporter. Earlier JSONL evidence remains unchanged.

The `langfuse-check` command in [How to use](#how-to-use) authenticates, runs the
five-turn scripted flow in isolated containers, flushes after cleanup, polls the
observations API until complete, and audits the
hosted data. It saves `check.json`, `summary.json`, and native service export
`observations.json`, including source/image/configuration provenance. Keys never
enter the solver or TOML. The application owner shuts down the client at exit;
disabled tracing is rejected before solver startup.

Hosted authentication, ingestion, readback/export, and cleanup passed for one
scripted run; the official CLI independently retrieved the same observations.
The later live check verified two automatically traced requests through the same
project. These checks establish the recorded trace paths, while general service
availability remains unverified. `flush()` or a trace ID alone does not prove
hosted evidence is complete.
An SDK export failure leaves controller cleanup and local results intact, but
missing detailed telemetry makes a run unsuitable as complete benchmark evidence.

## Live synthetic model check

The completed check used Responses with automatic Langfuse integration. The user
confirmed a **$1/day** Duke allowance for their account; teammates should check
their own allowance. Environment setup is in [How to use](#how-to-use).
The completed check used `gpt-6-luna`, low reasoning, four requests maximum, 1,024
output tokens/request, no client retries, and the existing 60-second attempt limit.
`ctf_agent/model.py` holds the small non-secret settings dictionary and gateway
pricing snapshot. Requests are limited to 32 KiB of serialized input; a conservative
input/output cost reservation must fit the $0.10 cap before dispatch. Reservations
are retained for failures/timeouts. Missing usage is unknown rather than zero.
Local costs are estimates from gateway rates; provider/gateway-side retries and
billing are not independently audited. Transport timeout is at most 20 seconds,
clipped to the remaining attempt time. The solver watchdog remains independent.

The `model-check` command performs a new paid synthetic attempt; it is not part
of default pytest or `self-check`. Each invocation has its own budget, so reruns require
authorization. It saves source/image/configuration provenance, the result, and
native observations retrieved through the official Langfuse CLI (`npx`/Node.js
required for this hosted check). [Evidence](evidence/model-integration/README.md)
includes the initial audit and its corrected review without repeating model calls.

## Isolation and tools

Model-controlled commands execute only in a non-root solver container, with no
host mounts, Docker socket, evaluator storage, credentials, target source/build
files, `challenge.json`, or expected-answer setting. The base filesystem is
read-only; `/workspace` and `/tmp` are bounded tmpfs mounts. Capabilities are dropped,
`no-new-privileges` is set, and CPU/memory/PID limits are enforced.

The trusted guard shares only the solver's network namespace. It installs a
firewall before solver startup and independently collects NFLOG packet denials.
A fresh internal bridge uses isolated gateway mode with no published ports or host
bridge address. DNS and unapproved endpoints are blocked. Denials, guard loss,
command timeout, and hard budget exhaustion stop the solver. Unexpected stopping
failures are recorded and classify the attempt as an infrastructure failure.

| Tool | Inputs | Behavior and bounds |
| --- | --- | --- |
| `run_command` | Nonempty `command`; optional bounded `timeout_seconds`. | Shell only in the solver's `/workspace`; bounded stdout/stderr; nonzero exit is an observation. Timeout ends the attempt and kills the solver, including detached children. |
| `write_file` | Workspace-relative `path`; UTF-8 `content`. | Rejects absolute/traversal/NUL/oversized inputs; independent worker directory-descriptor operations reject symlinks and races. |
| `submit_flag` | Nonempty `candidate`, at most 4096 UTF-8 bytes. | Exact equality in trusted host code; records only candidate/verdict. Wrong submissions allow continuation; success prevents later actions. |

Unknown tools and invalid arguments return validation observations and consume tool
budget. The runner validates once before setting trace input; worker filesystem
protections remain a separate boundary. Docker/protocol failures are terminal.
Cleanup handles exceptions and interruption and attempts both container removals.
These checks establish the listed controls, not universal container-escape prevention.

`configs/initial.toml` contains implementation defaults: 60-second attempt deadline,
20 tool calls, 20 response turns, 10-second command cap, 16 KiB command output,
64 KiB writes, 1 solver CPU, 256 MiB memory, 64 PIDs, and 64 MiB workspace.
The watchdog independently stops the solver during response waits. It cannot
interrupt arbitrary host Python callbacks; an uncooperative callback can delay
host cleanup until it returns. Live calls disable retries and set a transport timeout;
this is not proof of strict cancellation of remote generation or billing.

## Remaining work and attribution

The CTFTiny readiness milestone is already approved and unfinished. The loader
currently rejects scored IDs and an unpinned dataset. `configs/ctftiny.json` records
ten scored IDs, 40 development IDs, and readiness candidate `pwn-baby-boi`, but its
revision is still null. `nyuctf` is not yet installed or locked. Real file transfer,
target reset/connectivity/cleanup, and a preparation command remain pending.

AMD64 execution, real challenge suitability, and account throughput limits remain
unverified. Context-fitting changes should follow observed development needs. The
[status handoff](PROJECT_STATUS.md#next-action-and-handoff) includes a fresh-chat prompt.
Later pilots, scored runs, experiments, aggregation, and report/demo work need
separate authorization.

OpenAI Codex assisted with review, design, implementation, and verification.
[NYU reference agents](https://github.com/NYU-LLM-CTF/nyuctf_agents) informed tool and
solver responsibilities; their framework was not vendored. Langfuse integration
uses the [official SDK patterns](https://langfuse.com/docs/observability/sdk/instrumentation)
and [supported exporter injection](https://python.reference.langfuse.com/langfuse).
No individual CTFTiny answers, solutions, or write-ups were consulted.
