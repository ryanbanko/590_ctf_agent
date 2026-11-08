# Integrated-solver development pilot

November 7, 2026. **Three live development attempts ran: two evaluator-verified successes and
one scope stop. All records completed and cleanup passed. Detailed conversation
review remains with the user.**

[Pre-run plan](plan.json) and [unchanged configuration snapshot](experiment.toml).
Select one development challenge from each of three categories: `msc-algebra`,
`rev-checker`, `web-shreeramquest`. One fresh attempt each using existing `run-batch`,
600 seconds/40 model requests/80 tools per attempt, no automatic model retries.
The purpose is infrastructure/workflow validation before agent improvements;
solve rate is not a gate. No agent/prompt/tool/configuration edits.

[Development readiness index](readiness.json) records six passed fresh cycles.
The ten held-out environments separately passed [20 zero-model readiness cycles](../final-runtime-readiness/README.md).
The batch stopped as intended on the third attempt's scope violation. It also
stops on incomplete records, cleanup/guard/infrastructure incidents or response-source failures. Preserve unsuccessful attempts; no silent
replacement. Existing native Langfuse readback/export audits remain in use.

Executed after the user confirmed VPN readiness:

```sh
uv run --frozen --env-file .env python -m ctf_agent run-batch \
  --experiment evidence/nyu-runtime-pilot/experiment.toml \
  --challenges msc-algebra rev-checker web-shreeramquest \
  --trials 1 --output runs/pilots/nyu-integrated-20261107
```

[Results](results.json) and [batch index](batch.json) preserve all three attempts.

| Challenge | Outcome | Requests / tools | Active seconds |
| --- | --- | --- | --- |
| `msc-algebra` | Verified success | 12 / 12 | 71.76 |
| `rev-checker` | Verified success | 3 / 3 | 12.47 |
| `web-shreeramquest` | Scope violation | 3 / 3 | 23.82 |

Batch elapsed time was **140.75s**. Total: 18 requests/18 tools, 78,203 input and
4,964 output tokens (including 1,215 reasoning tokens); estimated cost **$0.00596**.
All usage was available. No time/request/tool limit was reached, solver restart
was needed or cleanup error was recorded. All three native export/privacy/parentage
checks passed; the actual observations remain under the recorded Git-ignored run
paths and linked Langfuse traces. Per-attempt summaries/run metadata are copied
under `attempts/`; no second trace exporter or tracing changes were introduced.

The web denial was **TCP port 4999 on the correct target address**, with only port
80 assigned. Relevant tools show port 80 worked initially, application operations
then returned 502, and the model tried ports 80/4999/3000/8080. The first unapproved
port stopped it. Source served by the website named a backend listener on 4999;
the supplied nginx configuration proxies from port 80 to `nodeserver:4999` on the
private backend network. This is not a reason to grant direct backend access.
A [fresh zero-model diagnostic](backend-diagnostic/README.md) reproduced MongoDB
crashing without AVX support and the Node app subsequently exiting. That is a
separate target compatibility problem, not a reason to open backend ports.
The earlier TCP-only preparation checks did not establish backend application
health; their passing control results remain accurate within that limited scope.

No retries, prompt/agent/tool/settings/scope changes, commit, push or scored attempts.
This is a small infrastructure pilot, not a controlled solve-rate comparison or
an unconditional readiness approval. The scope decision and upstream 502 need
review before proceeding. The working tree is uncommitted; recorded source hashes
and image identities identify what ran.


Private-data handling: generated `compose.json` snapshots can contain target
answers/environment values, so new snapshots are now Git-ignored and retained
locally. Some older snapshots were already tracked; they need a separate
publication cleanup. An unfiltered infrastructure inspection during this review
included private deployment values in local assistant tool output; those values
are not copied into this report or new agent/model inputs. No additional model
requests followed that inspection. Detailed native observations remain local/
hosted as already recorded; no expected answer is separately added to them.


A subsequent [same-release ARM64 Mongo evaluation](../mongo-arm64-evaluation/README.md)
passed two fresh zero-model functional/control cycles. Only the database
architecture changed temporarily; normal production integration remains pending.
The original pilot result above is not replaced, and no live retry ran.
