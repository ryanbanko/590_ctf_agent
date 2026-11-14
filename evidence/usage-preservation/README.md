# Usage preservation and cost review — November 14, 2026

The user asked to proceed with usage preservation and investigate the Langfuse
cost display, model costs and possible Daybreak issues. This milestone changes
only local usage accounting and focused tests. No prompt, plan/notes mechanism,
continuation policy, model, limit, dependency, batch scheduler or hosted setting
was changed. No model generation or real challenge attempt ran.

## Implemented contract

`make_responder()` adds `known_usage` to its existing usage dictionary. It contains
`model_calls` (responses with usage), `tokens` and `cost_usd` at the configured
gateway rates. A later failed request no longer destroys these known subtotals.
If a valid response lacks usage, later usage-bearing responses still contribute.

Existing whole-attempt fields retain their meanings. Any failed/unknown-usage
request leaves `tokens` and `cost_usd` null and `usage_complete` false. A known
subtotal of zero does not mean the attempt was free. Total `model_calls` includes
failed requests; the nested count includes only usage-bearing responses.
Known usage reaches result/summary and root-span output through the existing
`result.update(model_usage)` path. No retries or alternative aggregation were added.
Historical records and report artifacts are unchanged; the existing reporting
tools do not automatically treat the new partial subtotal as complete usage.

## Verification

The installed environment ran:

```sh
.venv/bin/python -m pytest tests/test_model.py tests/test_agent.py \
  tests/test_agent_controls.py tests/test_hosted_tracing.py tests/test_batch.py \
  -q --disable-plugin-autoload --junitxml=evidence/usage-preservation/pytest.xml
```

**58 passed, two Docker-marked cases deselected.** The HTTP transport, Docker and
trace exporter are offline substitutes. Tests cover a successful call followed
by a timeout (one known call, two total, no retry), missing usage at the first,
middle or last response, later reported usage accumulation, unchanged complete
totals and native attempt-span output. Existing terminal stopping/batch checks pass.

The first focused test run had nine passes and one test assertion error: the
trace-test helper already decoded output, and the new assertion decoded it again.
The assertion was corrected; accounting assertions had passed. An initial `uv`
invocation could not access its sandboxed cache, so the installed `.venv` was used
without dependency changes. Whitespace and local link checks were also performed.

## Langfuse cost display

[Filtered live readback](langfuse-cost-check.json) queried only core/basic/model/
usage fields for the two completed listener-fixed traces via the Langfuse CLI.
Both returned HTTP 200 with all observations on one page:

| Trace | Generations with native cost | Sum of native generation cost, USD |
| --- | --- | ---: |
| [roppity](https://us.cloud.langfuse.com/project/cmw17lafc0745ad0eekgn9a7j/traces/12a2422a87bf028848fc54ce9acc9409) | 17/17 | 0.015578494998 |
| [baby-boi](https://us.cloud.langfuse.com/project/cmw17lafc0745ad0eekgn9a7j/traces/0ebc50da6a9d81ce5868d97bf4677beb) | 26/26 | 0.019064114996 |

Both root `attempt` observations are SPANs with `totalCost: null`. The native
cost fields are on child `model-response` GENERATIONs. Our local `cost_usd` lives
inside root output JSON; it is not a native root-cost field. This explains a
blank cost on the selected root span, while confirming cost ingestion works.
The user's UI was not inspected, so a particular hidden column, filter or rounding
cause cannot be confirmed. No hosted data/model definition was changed.

Native total is approximately $0.03464261; local total was $0.03304781.
The difference is the cache-write premium omitted by the existing local
three-rate estimator: 63,792 writes times ($0.125 - $0.10)/million = $0.00159480.
This correction preserves that estimator; it does not claim to reconcile billing.
See [Langfuse cost documentation](https://langfuse.com/docs/observability/features/token-and-cost-tracking).
The first CLI parser read the envelope's top level instead of `body.data`;
corrected readback supersedes that apparent empty result. No empty-cost conclusion
was used. Credentials, headers and trace input/output were excluded from evidence.

## Current model-price comparison

[Duke metadata](gateway-model-costs.json) was queried read-only, with no generation;
its two model rates match the checked
[official standard pricing](https://developers.openai.com/api/docs/pricing).
Both are advertised with reasoning/function support; metadata is not a live
Responses or Daybreak compatibility check.

| USD per million tokens | GPT-6 Luna | GPT-6.1 Sol | Ratio |
| --- | ---: | ---: | ---: |
| Uncached input | 0.10 | 2.00 | 20x |
| Cached input read | 0.01 | 0.10 | 10x |
| Output, including reasoning | 0.50 | 10.00 | 20x |
| Cache write at the observed rate | 0.125 | 2.50 | 20x |

[Fixed-volume illustration](model-cost-comparison.json) reprices the same 43
historical generations, including exclusive cache-write/reasoning buckets:
approximately **$0.03464 Luna versus $0.62840 Sol (18.14x)**. This is not a forecast:
models may use different numbers of calls/tokens and caching, and neither source
establishes actual billing or the remaining account allowance. Stay with Luna
unless a small separate Sol comparison is approved.

Planning/notes, continuation and Daybreak considerations are recommendations in
[the improvement review](../../docs/IMPROVEMENT_OPTIONS.md#usage-cost-and-workflow-follow-up--november-14),
not new implemented behavior. `audit.json` pins this milestone's source/evidence;
earlier listener audits retain their historical hashes.
