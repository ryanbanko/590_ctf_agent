# Minimal development launch setup

November 4, 2026. The user's final scope is **agent setup only**. They will check
the system themselves; no actual solving or further verification was requested.

Added the real `run-development` CLI command and one TOML configuration. The
command owns host-only model/tracing clients, loads trusted CTFTiny metadata,
starts the reviewed target, stages contestant files, runs the existing bounded
agent, verifies submissions, cleans up, and saves results/provenance plus a native
Langfuse export. Real execution imports no test module.

The structure was consolidated at the user's request:

- `agent.py`: conversation loop, Responses translation, usage, and model limits.
- `challenge.py`: trusted loading, public task fields, staging, and target lifetime.
- `launch.py`: live clients, orchestration, provenance, results, and trace export.
- `tests/test_controls.py`: existing controls tests and their optional suite launcher.

Separate budget/model/target/records modules and the controls-launcher file were
removed. A persistent campaign ledger was removed before use. Existing isolation,
tool/resource limits, trusted answer separation, and per-attempt caps remain.

`configs/development.toml` uses `gpt-6-luna`, low reasoning, at most 8 requests,
2,048 output tokens/request, 120 seconds, no client retries, and a $0.10 attempt
cap. At the observed prices, eight maximum-sized request reservations total
approximately $0.041984. The user's new-work ceiling is under $0.50; estimates
and ordinary run usage records will guide any later testing. **No new model
requests, paid usage, real attempts, or hosted uploads occurred.**

[Gateway metadata](gateway-review.json) authenticated and returned the existing
$0.10/M input, $0.50/M output, and $0.01/M cached-input rates. Its recorded
`rates_match: false` is an exact floating-point comparison artifact (0.10/1e6
versus 1e-7), not a changed rate. The original diagnostic is retained.

Before the instruction to stop checking, 61 offline cases passed after code
consolidation. They include the existing 56 cases plus setting validation, a real
launch-flow check with substituted Docker/SDK transports, and native-export
transport coverage. No final live/Docker verification is claimed. The user can run:

```sh
uv run --frozen --env-file .env python -m ctf_agent run-development
```

Results go under `runs/development/`. Only `pwn-baby-boi` target compatibility is
currently supported; scored IDs remain rejected. General benchmark target
coverage, empirical improvement, scored comparisons, aggregation, report, and
demo remain future work. Earlier evidence is unchanged. New code is uncommitted
after baseline `028f560`.
