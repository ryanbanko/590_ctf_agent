# Responses model integration and one live synthetic check

Completed November 3, 2026 (America/New_York). **49 fast checks pass**, and one
approved live synthetic attempt succeeded. No CTFTiny challenge, pilot, scored
run, improvement experiment, aggregation, or report/demo work was performed.

## Scope and decisions

The user selected **Responses** and **automatic Langfuse OpenAI integration**,
requested basic checks, supplied a host-only Duke key, and confirmed **$1/day**.
The approved attempt cap was **four generation requests**, **1,024 output tokens
per request**, **$0.10**, and one synthetic attempt. No client retries are enabled.

Read-only gateway requests authenticated (HTTP 200), listed 41 models, and supplied
capability/pricing metadata. `gpt-6-luna` reported function/reasoning support and
$0.10/M input, $0.50/M output, $0.01/M cached input. These match the
[official model page](https://developers.openai.com/api/docs/models/gpt-6-luna).
Account allowance is user-reported; remaining quota/throughput and actual invoices
were not independently checked. No model generations occurred during discovery.

OpenAI **3.44.0** was resolved from PyPI, pinned, installed, and locked. Langfuse
**5.1.0** remained current. The official Langfuse skill, current automatic
integration/best-practices guidance, OpenAI Responses/reasoning documentation, and
installed SDK code informed the implementation. No agent framework, provider
registry, custom application class, or extra tracing backend was added.

`model.py` maps the existing conversation to Responses input and preserves native
output items for replay, including any encrypted reasoning. The existing runner
still owns isolation, tool/time/turn limits, exact verification, and cleanup;
the loop receives only public data and bounded callables. Automatic integration
creates each live generation; scripted checks retain their old manual generations.
API usage updates ordinary result counters even when a reply is discarded. Missing
usage/transport errors leave cost unknown. HTTP error bodies are replaced with a
status-only exception before automatic tracing sees them. Credentials are never
model inputs, solver environment variables, or provenance inputs.

For this check, settings are a small dictionary: low reasoning, 32 KiB serialized
request bound, at most 20 seconds transport timeout clipped to remaining attempt
time, no retries, 1,024 output tokens, four requests, and $0.10. Pre-request cost
reservations use request bytes plus framing allowance and a 1.25x input-price
reserve; failures/timeouts retain reservations. No tokenizer or general context
compaction infrastructure was added. The account daily allowance is not permission
to spend the whole dollar.

## Actual verification

```sh
uv run --frozen python -m pytest -q --disable-plugin-autoload --junitxml=evidence/model-integration/pytest-fast.xml
uv run --frozen --env-file .env python -m ctf_agent model-check --output evidence/model-integration
```

Execution used `.venv/bin/python` for pytest and a temporary uv cache for the live
command. The 49 fast checks passed (19 Docker cases deselected; JUnit 0.49 seconds).
Seven new cases cover real SDK/offline HTTP translation and automatic spans,
native reasoning plus linked tool-result replay, request/input/cost rejection,
timeout without retries/unknown cost, late-response accounting without execution,
and raw provider error exclusion. Multiple Langfuse test projects required explicit
public-project selection for the automatic integration.

The unchanged image tags were missing and were rebuilt from existing Dockerfiles.
The full 19-case Docker suite was not repeated, per the user's basic-check preference.
Sandbox, Docker helpers, worker, guard, tool dispatch, fixture service, Dockerfiles,
and solver-limit configuration are unchanged from the preceding verified snapshot.

The single live attempt:

- Run `7613ca071d19`; trace `daf234b57fa82f90297a7e4b42066bca`.
- [Hosted trace](https://us.cloud.langfuse.com/project/cmw17lafc0745ad0eekgn9a7j/traces/daf234b57fa82f90297a7e4b42066bca).
- First request called `run_command` to fetch JSON with Python urllib inside the solver.
- The next request received that tool result and called `submit_flag` with its observed candidate.
- Trusted verification succeeded; there were **2 model requests, 2 tools, 0 scripted turns**.
- Usage: **837 input tokens and 100 output tokens**, including zero reported cached/reasoning tokens.
- Estimated cost: **$0.0001337** (0.01337 cents). Langfuse inferred total **$0.000133699999**.
- Conservative cumulative reservation: **$0.001834125**, below the $0.10 cap.
- Attempt including cleanup/flush: **5.580838 seconds**; full check including CLI readback: **17.213709 seconds**.
- **10 observations**: root, two automatic generations, two tools, and five control/cleanup events.
- Containers/networks cleaned up; expected answer absent from root; secret credentials absent.

The official CLI retrieved complete observations with model/usage fields. Initial
`check.json` reported false because its credential audit treated the SDK's public
project identifier as a secret. Review located that identifier exclusively in
native `metadata["scope.attributes.public_key"]`. The Duke token and Langfuse secret
key are absent. The corrected audit passes **all 12 checks**, including parentage,
model input/output, token totals, and hosted/local cost agreement. **No extra model
calls or attempts were made.** The original result, initial check, and raw CLI
response are preserved. The only post-run source change corrected the test-only
credential audit; final hashes are in the reviewed verification record.

## Records and limits

- [Fast-test report](pytest-fast.xml).
- [Reviewed verification](verification.json): final checks, source hashes, original-run comparison, and credential-file exclusion.
- [Original check](model-check-246c99c9973e/check.json): source/config/image provenance and initial audit.
- [Native CLI response](model-check-246c99c9973e/cli-observations.json): model/usage fields and complete observed context.
- [Finalized attempt result](model-check-246c99c9973e/7613ca071d19/summary.json).

Automatic instrumentation retains bounded live provider output and usage even
when the runner rejects/discards a reply; rejection/discard events identify that
case. The API callback's transport timeout is not a guarantee of remote billing
cancellation or a strict host deadline. Cost reservations assume the configured
model/rates and no additional gateway-side retries; local costs are estimates,
not an independently checked invoice. The simple synthetic check reported no
reasoning tokens; native reasoning replay is covered offline.

This establishes one model/tool/tracing integration, not real CTF performance,
general gateway reliability, AMD64 compatibility, or scored readiness. Stop for
review. Proposed next step is a separately approved CTFTiny loading/target milestone.
Another paid check requires authorization.
