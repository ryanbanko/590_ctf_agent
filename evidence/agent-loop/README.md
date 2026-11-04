# Scripted agent-loop verification

November 3, 2026 (America/New_York).

**30 fast tests, the existing 17 synthetic Docker controls checks, and 2 new
scripted-loop Docker checks passed.** No model calls, real CTFTiny attempts,
development pilots, scored runs, or improvement experiments occurred. All gateway
usage/cost remains zero; scripted turns are recorded separately.

## Changes verified

- `ctf_agent/agent.py` adds one function-based loop around the existing `call_tool()`
  boundary, with public task/history/schema copies, sequential tool requests, and
  observations matched to call IDs. No application classes, frameworks, SDKs, or
  runtime dependencies were added.
- Malformed JSON, non-object arguments, unknown tools, and invalid paths return
  validation observations and consume tool budget. Nonzero command exit results
  can inform the next scripted action.
- Invalid response envelopes, duplicate call IDs, responses over 1 MiB, and callback
  failures stop clearly. Raw malformed/late replies and callback exception messages
  are omitted from traces; rejection/discard/error events remain.
- `max_model_turns`, initially 20, bounds response turns independently of tool
  budget. Final text is unsuccessful even if it claims success. Verified success,
  deadline expiry, and incidents prevent later actions and response requests.
- Attempt summaries add `agent_mode` and `scripted_turns`; actual `model_calls`
  remains zero, `tokens` is null, and `cost_usd` is zero for these scripted checks.
- Container/process/network controls, tool implementations, evaluator semantics,
  dependency files, and the original 17 check identities are unchanged.

## Actual container observations

[Success attempt](scripted-integration/ae1f7b724e38/summary.json): five scripted
turns and five tools. A failed command returned exit code 7; the next action wrote
a Python script inside the solver. Running that script retrieved the generated
synthetic flag through the permitted HTTP interface. A wrong candidate returned
false; the next turn submitted the observed candidate successfully. A sibling
command requested after that submission never executed. The responder received no
expected-answer value; it obtained the candidate from the tool observation.

[Deadline attempt](scripted-integration/ff971f0d3079/summary.json): one scripted
turn, zero tools, `wall_limit`. A deliberately uncooperative callback waited beyond
its supplied timeout. The watchdog stopped the solver during the wait; a trusted
Docker inspection confirmed the solver was stopped before the callback returned.
The eventual command request was discarded. The attempt recorded 3.125064 active
seconds and 0.132614 cleanup seconds for a configured 3-second solver deadline.

These are synthetic controller checks, not evidence of real model reasoning,
benchmark solve rate, a performance improvement, or the assignment's successful-run
demo. Python callbacks are not forcibly interrupted: a callback that ignores its
timeout can delay host cleanup until it returns, while the solver deadline remains
independently enforced. Live transport timeout/cancellation and retry policy are
still prerequisites for the gateway milestone.

## Reproduce

```sh
uv sync --frozen
uv run python -m pytest -q --disable-plugin-autoload --junitxml=runs/agent-fast.xml
uv run python -m ctf_agent build-images
uv run python -m ctf_agent self-check --output runs
uv run python -m pytest tests/test_agent_controls.py -m docker -q --disable-plugin-autoload --ctf-output runs/scripted-loop --junitxml=runs/scripted-loop/pytest.xml
```

Do not run the two Docker suites concurrently: the controls launcher verifies
that no project containers or networks remain. Choose a fresh output directory
for each repeated invocation to keep records distinct. Actual checks used the
already synchronized `.venv/bin/python`, equivalent to the commands above.

The first controls invocation could not start because local project image tags
were absent. Its [failed startup record](self-check-7ddbbf9e03a3/suite.json) is
preserved. Rebuilding the three unchanged Dockerfiles used cached layers and
restored the image tags; no dependency pin, image source, or containment policy
changed. The subsequent complete run passed.

## Retained records and audit

- [Final fast-test JUnit report](pytest-fast-final.xml): 30 passed. The
  [earlier fast report](pytest-fast.xml) is retained from before the final response
  error-message adjustment; the final report verifies the source in the suite hashes.
- [Controls suite](self-check-e88191f0b12b/suite.json): 17 passed, pytest exit code
  zero, cleanup verified, complete settings and source/image provenance.
- [Controls JUnit report](self-check-e88191f0b12b/pytest.xml) and per-attempt
  `trace.jsonl` / `summary.json` files in the same directory.
- [Scripted-loop JUnit report](scripted-integration/pytest.xml): two passed, with
  run-ID properties linking to both complete attempt directories.
- [Post-run audit](verification.json): source hashes match current code; original
  check names/configuration limits are preserved; unchanged control/dependency
  sources match the previous milestone; all 19 trace sequences and one-result-per-
  executed-tool counts verify; all six prohibited IPv4 probes retain independent
  packet-denial events. Scripted request history sizes replay from initial history,
  accepted replies, and tool observations without duplicate full-history logs.

The controls launcher recorded **43.406439 seconds**; pytest reported **43.06
seconds** for its 17 tests and **7.76 seconds** for the two scripted-loop tests.
These timings describe setup verification, not a controlled speed comparison.
The launcher and separate final Docker queries found no project containers or
networks. Actual image IDs/ARM64 architecture are retained in controls provenance.
Earlier milestone evidence is unchanged.

Gateway compatibility, model/settings, credentials, pricing/account limits, actual
API timeout/retry/accounting behavior, AMD64 execution, CTFTiny integration, and
all later assignment stages remain pending. Stop here for user review before
proposing the next milestone.
