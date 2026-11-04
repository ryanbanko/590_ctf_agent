# Native reasoning-summary compatibility check

November 4, 2026 (America/New_York). The user approved enabling native summaries
and one benign check. **Parameter acceptance and native tracing worked; no readable
summary was returned.** No CTF data, solver/container execution, or tools were used.

## Minimal change

`ctf_agent/agent.py` adds `summary: "auto"` to the existing Responses reasoning
dictionary. Reasoning effort, replay, loop behavior, limits, and SDK versions stay
unchanged. Existing Langfuse instrumentation captures the native response; no
module, dependency, tracing abstraction, or explanatory prompt was introduced.
The existing SDK test additionally checks summary request, replay, and capture.

```sh
.venv/bin/python -B -m pytest tests/test_model.py -q --disable-plugin-autoload -p no:cacheprovider --junitxml=evidence/reasoning-summaries/pytest-model.xml
```

[JUnit](pytest-model.xml): **7 passed**, pytest time 0.39 seconds. Broader fast and
Docker suites were not repeated for this request-parameter change.

## Single live request

The benign prompt asks for a maximum-benefit maintenance-activity selection under
a ten-hour limit with dependencies. It is preserved in the native generation
input. No tool schemas were supplied, and no model output was executed.

- `gpt-6-luna`, low reasoning, `summary: auto`, one request, no retries.
- At most 2,048 output tokens, 20-second HTTP timeout, and **$0.01 cost cap**.
- **120 input / 174 output tokens**, including 154 reasoning tokens in output.
- Estimated cost **$0.000099**; conservative reservation **$0.00124425**.
- Returned output included a reasoning item and final assistant message.
- The reasoning item had **zero summary entries**.
- The hosted generation's model parameters retained `reasoning_summary: auto`.
- Native trace parentage/IDs, usage, cost bounds, and credential-exclusion checks
  passed. Both summary-presence checks failed; [check.json](check.json) correctly
  retains `passed: false` for the requested summary-availability outcome.
- The complete check, including hosted CLI readback, took **20.901695 seconds**.

[Hosted trace](https://us.cloud.langfuse.com/project/cmw17lafc0745ad0eekgn9a7j/traces/6663fb84aa49df3c3ea7fea35f13393a),
[native CLI export](cli-observations.json), and [check record](check.json) retain
the prompt, settings, source hashes, SDK versions, usage, and result. The official
CLI was `@langfuse/cli@1.3.1`. No secret credentials were present in the export.

## Interpretation and stopping point

The feature is requested, but readable summaries have not been demonstrated for
this gateway/model/configuration. A single empty response cannot establish whether
the model omitted the summary or the gateway did not forward/return it. Langfuse
preserved what was returned. Earlier encrypted reasoning cannot be decoded or
retroactively summarized through this setting.

No retry, alternative model, higher-effort experiment, prompt change, or challenge
run was performed. Stop for review before any further calls.
