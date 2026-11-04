# Hosted Langfuse synthetic verification

Completed November 3, 2026 on native ARM64 with Langfuse **5.1.0**.
This approved milestone verifies hosted tracing with an existing scripted synthetic
flow. It performs **zero model API calls**, costs **$0 in model usage**, and uses no
real CTFTiny challenge. This is setup evidence, not a pilot or scored attempt.

## Changes and guidance

Installed/read the [official Langfuse skill](https://github.com/langfuse/skills)
at `/Users/ryanbanko/.codex/skills/langfuse/SKILL.md`, including its instrumentation
and CLI references. Reviewed current documentation and the installed SDK's native
model integration. The current generation input shape already follows the SDK's
messages/tools convention; no runtime tracing redesign was necessary.

Added the explicit `langfuse-check` command, test-only hosted readback/audit code,
five fast checks, and a blank `.env.example`. The existing scripted responder is
shared between local and hosted checks. `.env` is owner-readable/writable and
Git-ignored; credentials stay on the host and are excluded from provenance.
No new dependencies were added.

The agent, trusted runner, tools, sandbox, Docker helpers/images' source,
dependencies, and configured limits are unchanged from the previous milestone.
The [19-case Docker verification](../langfuse/README.md) remains historical and was
not repeated. Missing local image tags were rebuilt from unchanged Dockerfiles
before this one hosted attempt.

## Actual verification

```sh
uv run --frozen python -m pytest -q --junitxml=evidence/langfuse-cloud/pytest-fast.xml
uv run --frozen --env-file .env python -m ctf_agent langfuse-check --output evidence/langfuse-cloud
```

The fast suite passed **42 tests**, with 19 Docker cases deselected and no failures
or skips (JUnit time **0.182 seconds**). The hosted command passed in
**13.607838 seconds**, including successful authentication, isolated synthetic
execution, flushing, hosted readback, and cleanup verification.

- Run: `19ef08ce7a67`.
- Trace: `66c8feb838d6b983f6efaf28ab31ce64`.
- [Open the hosted trace](https://us.cloud.langfuse.com/project/cmw17lafc0745ad0eekgn9a7j/traces/66c8feb838d6b983f6efaf28ab31ce64)
  using the project's authenticated account.
- **16 observations:** one root, five scripted generations, five tools, and five
  guard/stopping/cleanup events.
- All **13 trace-audit checks** passed: trace IDs/parentage, summary agreement,
  verified success, five turns/tools, ordered tool steps, inputs/outputs, public
  history lengths `[2, 4, 6, 8, 10]`, wrong/correct verdicts, observed candidate
  verification, no answer key in the root, no secret key in observations, and
  zero actual model calls/cost.
- No managed containers/networks remained after cleanup.

Following the skill's CLI guidance, independently queried the same trace using
`npx --yes langfuse-cli api observations list` with `--trace-id`,
`--fields core,basic,time,io,metadata`, `--expand-metadata config,image_ids`,
`--all --max-items 100 --json`. Credentials were passed only through environment
variables. The HTTP 200 response contained the same 16 observation IDs as the SDK
export. The CLI was a review tool, not an application dependency.

## Retained records

- [verification.json](verification.json): source-hash/configuration comparison,
  fast-test count, SDK/CLI ID agreement, credential-file exclusion, and outcome.
- [pytest-fast.xml](pytest-fast.xml): actual fast-test JUnit results.
- [check.json](langfuse-check-c91ac6c97008/check.json): authentication, all audit
  results, cleanup, timing, trace URL, and source/image/configuration provenance.
- [observations.json](langfuse-check-c91ac6c97008/observations.json): native SDK
  serialization of the hosted observations returned by the service.
- [cli-observations.json](langfuse-check-c91ac6c97008/cli-observations.json):
  independent CLI readback, including its HTTP response envelope.
- [summary.json](langfuse-check-c91ac6c97008/19ef08ce7a67/summary.json): ordinary
  finalized attempt result.

The native hosted exports are verification artifacts, not a second application
tracing backend. The synthetic flag appears where it was retrieved and submitted;
there is no separately exported expected-answer field. Prior evidence is unchanged.

## Limits and stopping point

One successful trace verifies authentication, transport, asynchronous ingestion,
readback/export, and completeness for this configured project. It does not verify
general service reliability, every incident path in the hosted service, actual
LLM adaptation, token counts, model pricing, or account allowance. Scripted
generations remain explicitly distinct from model API calls. AMD64 and CTFTiny
integration remain pending.

Stopped for user review as requested. The proposed next milestone is Duke
gateway/model integration after agreeing on its model, API settings, pricing,
limits, and small verification scope. No live-model work or later assignment
stage was started here.
