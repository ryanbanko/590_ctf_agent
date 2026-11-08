# Live synthetic smoke test after simplification

November 6, 2026. The user approved the bounded live model check, then confirmed
VPN connection before any model requests. No CTFTiny challenge was loaded or
solved; no image/runtime/model/prompt settings were changed.

**Passed** using the existing `model-check` command on clean committed source
`00e6a411811b9d076907f6e512fac5b97f20fc96`.

| Item | Result |
| --- | --- |
| Run ID | `b2ce1cd44ed6` |
| Model | `gpt-6-luna`, Duke gateway, low reasoning |
| Requests / tool calls | 2 / 2 |
| Tokens | 1,585 input; 191 output, including 7 reasoning tokens; 0 cached input |
| Estimated model cost | $0.000254, matching hosted cost totals |
| Active attempt / complete check | 5.72 / 22.25 seconds |
| Hosted observations | 12, complete and correctly parented |
| Scope incidents / cleanup errors | 0 / 0; cleanup verified |

The model used `run_command` to retrieve the synthetic target's JSON via Python
urllib, then submitted the observed candidate through `submit_flag`. Trusted
verification accepted it and stopped the solver. Native generation/tool records,
usage, submission verdict and cleanup were read back through the existing Langfuse
Python SDK. No CLI runtime dependency or additional model request was introduced.

The initial model input and root observation exclude the answer. The second model
request contains the candidate only after the tool observed it. The app's credential
audit passed; no expected answer is separately written to this report.

Sources and results:

- [Check/provenance](model-check-6bde4e29a918/check.json)
- [Attempt summary](model-check-6bde4e29a918/b2ce1cd44ed6/summary.json)
- [Hosted native observations](model-check-6bde4e29a918/observations.json)
- [Additional local audit](verification.json)
- [Langfuse trace](https://us.cloud.langfuse.com/project/cmw17lafc0745ad0eekgn9a7j/traces/27062c972a34e6cce9eccb280f16723b)

Local/hosted usage agrees after accounting for the native hosted split of visible
output and reasoning tokens; the local output total already includes reasoning.
Do not add those reasoning tokens again. Cost is an estimate from configured
rates, not an account-billing or quota reconciliation.

The existing check bounded this attempt to 60 seconds, four requests, 20 seconds
per request, 1,024 output tokens/request and 32 KiB serialized input; retries were
disabled. These are synthetic-check overrides from `tests/check_model.py`.
The normal run profile is unchanged.

Reproduce only when live calls are authorized and campus/VPN connectivity is ready:

```sh
uv run --frozen --env-file .env python -m ctf_agent model-check
```

This establishes the real provider → agent → solver command → private submission
→ hosted export path on the simplified runtime. It does not live-test `write_file`,
timeout recovery, every challenge, or solve rate. Those infrastructure controls
retain their separate offline/synthetic evidence. Broader development pilots and
image evaluation remain separate checkpoints. No commit or push was performed
as part of this check.
