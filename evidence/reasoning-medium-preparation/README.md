# Medium reasoning and doubled response allowance — November 8

Prepared the user-requested experiment in
[configs/reasoning-medium.toml](../../configs/reasoning-medium.toml), with the
[hypothesis recorded before calls](../../docs/EXPERIMENTS.md#reasoning-and-token-headroom-experiment--preregistered-november-8).
The user added doubled token headroom before any medium model request. The initial
effort-only draft was not run. This profile is ready for a user-run experiment;
no live attempt or compatibility-generation call was made during preparation.

**Activation update:** at the user's request, the active
`configs/development.toml` now also uses medium/8,192. Existing batch commands
without an `--experiment` option therefore use this condition. The named profile
has identical parsed values and remains an explicit experiment snapshot. The
saved low/4,096 reference is
`evidence/agent-first-fix-batch/experiment.toml` and the earlier Git checkpoint.

Exactly two parsed settings differ from the saved low-effort reference:

| Setting | Saved low-effort reference | Active / experimental profile |
| --- | --- | --- |
| `reasoning_effort` | `low` | `medium` |
| `max_output_tokens` | 4,096 | 8,192 |

Model identity, prompt/tools, prices, images, 60-second request limit, 600-second
attempt limit and all other bounds remain unchanged. The generated-token allowance
is per response and includes reasoning plus visible output. It is not reserved
spending or an aggregate attempt token limit. Only these two active settings changed.

The low reference is development `batch-48f3b134d5c3`, 6/11 successes. Its source
is `e7e366c`; the current `c80b61a` checkpoint only adds documentation/evidence.
One fresh medium attempt on each of the same eleven development IDs is an
exploratory comparison of the **combined effort/headroom change**, not an isolated
effort effect. Review capped/incomplete requests and latency as well as success;
do not discard failed attempts or reset limits. A later effort-only comparison
would need common token bounds and fresh conditions.

[Official Luna documentation](https://developers.openai.com/api/docs/models/gpt-6-luna)
lists medium support. Actual gateway acceptance has not been tested in preparation.
8,192 is a conservative project choice; OpenAI's
[reasoning guide](https://developers.openai.com/api/docs/guides/reasoning#allocating-space-for-reasoning)
recommends more initial headroom. Observe whether this cap or the unchanged
request timeout binds before drawing conclusions.

Verification: the normal loader accepted the complete profile, a parsed-value
comparison confirmed exactly the two differences above, and **27 existing
model-adapter/configuration/contract checks passed** with the experimental profile.
The checks use offline SDK transports and verify that the selected effort and
token limit reach the Responses request. No new test code, dependency, runtime
code, model call, Docker operation or hosted write in that preparation.
[JUnit report](offline.xml). The earlier effort-only preparation report remains
under ignored `runs/reasoning-medium-preparation/`; the retained report covers the
final medium/8,192 profile.

Activation verification separately passed the same 27 checks using the active
default, with exactly the two changes above relative to the preserved low snapshot.
All application Python files are unchanged. Initial preparation records remain
in `verification.json` and `offline.xml`; the activation addendum is
[active-default-verification.json](active-default-verification.json) and
[offline-active-default.xml](offline-active-default.xml).

For the same eleven-ID cohort, with Docker running and Duke access configured:

```sh
uv run --frozen --env-file .env python -m ctf_agent run-batch \
  --experiment configs/reasoning-medium.toml \
  --challenges \
    cry-ecxor cry-describeme for-1black0white \
    msc-algebra msc-ezmaze pwn-baby-boi pwn-get-it \
    rev-checker rev-tablez web-poem-collection web-shreeramquest \
  --trials 1 --output runs/pilots/reasoning-medium-8192
```

This command makes live model requests. Save a local source/hypothesis checkpoint
before running; pushing is not required. Inspect early attempts for accepted
settings and constraint failures. Preserve the batch snapshot, run records and
complete trace payloads; the previous export-payload caveat still applies.
