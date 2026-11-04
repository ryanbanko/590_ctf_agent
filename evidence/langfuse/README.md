# Langfuse migration and local SDK verification

November 3, 2026 (America/New_York).

**37 fast tests and all 19 synthetic Docker checks passed.** Detailed tracing now
uses the real Langfuse SDK exclusively. No model calls, CTFTiny attempts, pilots,
scored runs, improvement experiments, or hosted trace uploads occurred.

The user explicitly chose to finish SDK/local verification before creating a
Langfuse Cloud project. No real Langfuse credentials were configured or used.

## Implemented architecture

- `run_agent(public_task, respond, call_tool)` receives public task text and bounded
  functions. It has no runner dictionary, SDK client, evaluator answer, or container
  control handles. Full public history still passes between responses.
- The trusted runner's closures enforce deadlines/turn/tool budgets and dispatch
  the existing three tools. Exact `submit_flag` verification stays inside that
  scope; the expected answer is absent from state/results and SDK inputs.
- A small `AttemptStopped` exception carries only the termination reason, allowing
  expected stops to cross the function boundary while unrelated errors propagate.
- Langfuse root/generation/tool observations capture safe inputs/outputs and native
  timing. Guard, stopping, and cleanup evidence uses native events attached to the
  root explicitly, including background-thread events.
- The custom JSONL writer/module, sequence numbers, and trace-file lock are removed.
  There is no application fallback logger, tracing interface, or dual backend.
- `summary.json` retains outcome/resource information plus trace ID and SDK flush
  timing. Configuration, source hashes, resolved image IDs, suite results, and JUnit
  reports remain normal reproducibility artifacts.
- Direct runtime dependency `langfuse==5.1.0` and all transitive dependencies are
  locked. Model access still has no SDK/backend implementation.

The main loop is now 80 lines including prompt, envelope validator, and stop
exception. Lifecycle/budget/tracing work is concentrated in the trusted runner.
The dependency/service setup cost of Langfuse is explicit; the change does not
claim every file or test became shorter. No application object model, provider
registry, generic exporter, or self-hosted observability stack was introduced.

## Verification method

Tests initialize the actual `Langfuse` client with dummy test project keys, a
separate standard OpenTelemetry `TracerProvider`, and the SDK-supported
`span_exporter=InMemorySpanExporter()` argument. This substitutes only transport.
All observations/events, attributes, timings, parent IDs, and flush behavior come
from the installed SDK. No hosted API, project, or external telemetry destination
is contacted.

Test support saves `otel-spans.json` using each SDK `ReadableSpan.to_json()`.
These are native OpenTelemetry JSON snapshots of the SDK output, not a custom
runtime event stream or a claimed Langfuse server export. The application writes
only the normal result file; hosted runtime uses the client supplied by its owner.

Fast checks retain validation/recovery/stopping/context behavior and additionally
verify the narrowed public loop interface, SDK export failure leaving stopping/
cleanup/results intact, and disabled tracing preventing solver startup. Callback
errors retain exception type rather than sensitive exception text. Oversized and
late outputs are omitted with rejection/discard metadata. Evaluator tests verify
exact equality and that the expected answer never appears separately in root input/
metadata/results. Candidate/verdict tool evidence remains.

## Reproduce

```sh
uv sync --frozen
uv run python -m pytest -q --disable-plugin-autoload --junitxml=runs/langfuse-fast.xml
uv run python -m ctf_agent build-images
uv run python -m ctf_agent self-check --output runs
```

Actual verification used the synchronized `.venv/bin/python`. One self-check
discovers all 19 Docker cases; no Langfuse account is needed. Docker suites should
run sequentially because cleanup verification uses the shared project label.
The existing project images were available; no Dockerfile/image-policy change or
rebuild was needed during this verification.

## Retained records

- [Fast-test JUnit report](pytest-fast.xml): 37 passed, zero failures/errors/skips.
- [Combined suite](self-check-867a5677094f/suite.json): 19 passed, exit code zero,
  cleanup verified, settings, source hashes, image IDs/ARM64 architecture, and run IDs.
- [Docker JUnit report](self-check-867a5677094f/pytest.xml): per-case outcomes with
  properties linking each case to its run ID.
- Each attempt directory contains `summary.json` and a test-captured native
  `otel-spans.json`; none contains a new `trace.jsonl`.
- [Post-run audit](verification.json): current source hashes match; all previous
  19 Docker identities and configuration limits are preserved; unchanged Docker/
  worker/firewall/configuration sources match the preceding milestone.

The audit checked all 19 native trace/summary ID links, parent relationships,
completed span timestamps, root outcomes, one tool span/output per counted tool
request, and all six independent NFLOG packet-denial checks. Every rejection has
an observation rather than silently disappearing. The test secret key is absent
from exported spans. Correct-submission candidates are absent from root observation
input/metadata/output; they appear only in permitted tool/conversation evidence.

[Synthetic success](self-check-867a5677094f/9a6ef700a39a/summary.json) retained five
scripted responses and five tools. It recovered from exit code 7, wrote/ran a script
in the solver, retrieved the generated flag through the permitted target, observed
a wrong verdict, then submitted the observed candidate successfully. No later
sibling command executed. Native generation inputs retain history lengths
**2, 4, 6, 8, 10**; tools and generations are children of the same attempt root.

[Late response](self-check-867a5677094f/e636e7154af5/summary.json) retained one
generation, zero tools, and `wall_limit`. The watchdog stopped the solver during
the callback wait; its eventual response was discarded and not exported as output.
Packet-denial, guard loss, worker loss, command timeouts, resource limits,
interruption, setup failure, and cleanup scenarios all retained their identities.

Pytest recorded **0.127 seconds** for fast tests and **54.421 seconds** for Docker
checks. The encompassing launcher recorded **54.895693 seconds**. These are setup
verification timings, not a performance experiment. Total attempt time now includes
SDK flushing, separately recorded as `trace_flush_seconds`. Root outputs precede
export; final local totals include that flush overhead.

The launcher verified no project containers/networks remained. Earlier JSONL and
milestone evidence are unchanged as historical records. Gateway/model usage and
cost remain zero, and token usage remains inapplicable for scripted checks.

## Limits and next step

Hosted authentication, ingestion, querying/export, availability, and account/service
settings remain unverified. A successful local result, native trace ID, or normal
`flush()` return does not certify hosted trace completeness. The SDK's default
export-failure behavior preserves application execution; missing detailed evidence
would prevent treating a future run as complete benchmark evidence. Hosted checks
remain a separate step when the user is ready.

No live model/gateway compatibility, pricing/account limits, token-aware context
fitting, AMD64 execution, or CTFTiny integration was established. Python callbacks
still cannot be forcibly interrupted; the independent watchdog attempts solver
stopping while an uncooperative callback can delay host cleanup. Stop for review
before the next milestone.
