# Experiment record

One entry per agent change tested on development challenges, in order. Each entry
gives the hypothesis as written before the runs, the settings that changed, the
batch, the result and where the records are. The report explains these results. Run
records and traces for the pilot, baseline, A, B and C batches are in
[evidence/ryan-shared-runs](../evidence/ryan-shared-runs/README.md). Raw records for the
other batches are not in the repository; their linked reviews summarize them.

Settings below are reasoning effort / output tokens per request / request size cap /
request timeout. Every batch used `gpt-6-luna`, a 600 s attempt limit, 120 s commands,
40 model calls and 80 tool calls, except Experiment 1 (see its entry).

## Experiment 1 — evidence-use and recovery prompt

- **Date / code:** November 4; prompt in commit `f566057`. Settings: low / 2,048 /
  256 KiB / 30 s, with a 300 s attempt limit, 30 s commands and 20 model calls.
- **Hypothesis:** "explicit guidance to distinguish assumptions from observations,
  check corrections, preserve diagnostic/completion output, and investigate a blocker
  before stopping will reduce avoidable early exits after recoverable errors and
  unsupported progress claims."
- **Runs:** `cry-ecxor`, `msc-algebra`, `pwn-baby-boi`, `rev-checker`,
  `web-poem-collection`, one attempt each.
- **Result:** 3/5 solved; 32 model calls, 31 tool calls; 181.2 active seconds;
  estimated cost $0.00944938.
- **Records:** [prompt-recovery/trial-review.json](../evidence/prompt-recovery/trial-review.json).

## Experiment 2 — solver libraries and output limit

- **Date / code:** November 4, commit `f566057`.
- **Observed:** missing Python libraries, and outputs of about 17 KiB truncated by the
  16 KiB limit, in the Experiment 1 traces.
- **Change:** installed pwntools, SymPy, NumPy, PyCryptodome, requests and Pillow in
  the solver; raised the output limit to 32 KiB; added guidance on network read deadlines.
- **Hypothesis:** "supplying established libraries will avoid the observed
  missing-import detours; 32 KiB will retain the roughly 17 KiB outputs observed in the
  previous trials; clearer command guidance may reduce unbounded network reads and
  stale-session assumptions."
- **Result:** synthetic checks only (64 offline tests, 23 Docker checks); no live
  comparison.
- **Records:** [solver-libraries](../evidence/solver-libraries/README.md).

## Experiment 3 — writable environment, pip, larger limits

- **Date / code:** November 4, commit `a6d3bf0`.
- **Observed:** "a missing dependency leading to a scope stop, blocking reads ending an
  entire attempt, and connections mistakenly treated as persistent between commands."
- **Change:**
  - writable Python environment and home directory, with pip downloads over HTTPS;
  - a command timeout no longer ends the attempt. At first child processes were cleaned
    up; since November 6 the solver container is restarted;
  - limits raised to 600 s attempts, 120 s commands, 40 model calls, 512 KiB requests,
    4,096 output tokens and 64 KiB output.

  The interactive terminal sessions added here were removed on November 6 and replaced
  by one shell per command.
- **Result:** synthetic checks only (82 offline tests, 27 Docker checks).
- **Records:** [agent-usability](../evidence/agent-usability/README.md),
  [execution-simplification](../evidence/execution-simplification/README.md).

## Pilot — batch `1707e5f1f3f5`

- **Date / code:** November 7, commit `00e6a41` plus the uncommitted solver-image
  integration, later committed as `616b5f2`. Settings: low / 4,096 / 512 KiB / 60 s.
- **Purpose:** check the integrated solver image and run workflow before further agent
  changes.
- **Runs:** `msc-algebra`, `rev-checker`, `web-shreeramquest`, one attempt each.
- **Result:** 2/3 solved; `web-shreeramquest` stopped on a scope violation (blocked
  connection to port 4999).
- **Records:** [nyu-runtime-pilot](../evidence/nyu-runtime-pilot/README.md).

## Baseline — batch `3963930b88c3`

- **Date / code:** November 7, commit `616b5f2` (NYU solver image). Settings: low /
  4,096 / 512 KiB / 60 s.
- **Runs:** eleven development challenges, one attempt each.
- **Result:** 6/11 solved; 63 model calls, 58 tool calls; estimated cost $0.01823374.
- **Records:** [development-trace-review](../evidence/development-trace-review/README.md).

## Experiment A — prompt, tool contract and output capture

- **Date / code:** November 8, commit `e7e366c`. Settings unchanged: low / 4,096 /
  512 KiB / 60 s.
- **Change:**
  - prompt: verified solver environment, validation against original artifacts,
    diagnosis of contradictions;
  - `run_command` description: shells, connections, deadlines, reset effects;
  - output over 64 KiB saved to files the agent can read.
- **Hypothesis:** "concise verified environment/connection instructions, specific
  inexpensive validation and contradiction-diagnosis guidance, and retrievable oversized
  output will help the agent use original evidence and resolve recoverable errors before
  ending."
- **Runs:** batch `48f3b134d5c3`, same eleven challenges.
- **Result:** 6/11 solved; 65 model calls, 60 tool calls; estimated cost $0.02025106.
  Output capture was not triggered.
- **Records:** [agent-first-fix-batch](../evidence/agent-first-fix-batch/README.md).

## Experiment B — medium reasoning and output allowance

- **Date / code:** November 8. Code as `c80b61a`, with only the configuration changed.
  Settings: **medium / 8,192** / 512 KiB / 60 s.
- **Hypothesis:** "with prompt, tools, images and other execution limits fixed, medium
  reasoning plus additional response headroom will improve independent checks and
  diagnosis of contradictions, reduce unsupported unsuccessful stopping, and potentially
  improve evaluator-confirmed success."
- **Runs:** batch `f4ccc7f4b335`, same eleven challenges.
- **Result:** 9/11 solved; 92 model calls, 91 tool calls. `web-shreeramquest` ended in a
  scope violation (blocked connection to port 4999).
- **Records:** [reasoning-medium-scope-stop](../evidence/reasoning-medium-scope-stop/README.md).

## Experiment C — endpoint wording and one scope recovery

- **Date / code:** November 8, commit `48b068f`. Settings: medium / 8,192 / 512 KiB / 60 s.
- **Hypothesis:** "explicit target address/protocol/port instructions plus one bounded
  blocked-command recovery lets the agent correct a scope mistake and continue permitted
  work without expanding access."
- **Runs:** batch `8ba0053bddb1`, same eleven challenges, two trials each.
- **Result:** 20/22 solved; `pwn-baby-boi` failed both trials. No scope incidents, so
  the recovery did not trigger live. Synthetic checks: 149 offline tests, 47 Docker cases.
- **Records:** [scope-recovery](../evidence/scope-recovery/README.md).

## Unseen development challenges — batch `8c98b0fc7e14`

- **Date:** November 11. Settings: medium / 8,192 / 512 KiB / 60 s.
- **Runs:** ten development challenges not used before, two trials each.
- **Result:** 14/20 solved. The batch stopped after its final attempt ended with a
  model API error.
- **Records:** [unseen-development-trace-review](../evidence/unseen-development-trace-review/README.md).

## Experiment D — validation and reuse prompt; request cap and timeout

- **Date / code:** November 11, commit `aedfd62`.
- **Request cap 512 KiB → 2 MiB.** Hypothesis: "additional request headroom prevents
  premature local input-limit stops for otherwise supported histories."
- **Prompt change.** Hypothesis: "small original-artifact checks before expensive
  search, exact-value rechecks after contradiction, and saved intermediate results
  reduce work based on incorrect reconstructions and repeated computation during
  recovery."
- **Runs:** batch `983d82df4d2f`, `cry-lupin`, `rev-gibberish-check` and
  `rev-a-walk-through-x86-part-2`, two trials each. Settings: medium / 8,192 / 2 MiB / 60 s.
- **Result:** all three first trials solved (52.01, 406.04 and 41.11 active seconds).
  The second `cry-lupin` attempt ended on a 60.047 s request timeout, which stopped the
  batch; two attempts did not run.
- **Request timeout 60 s → 90 s.** Hypothesis: "modest additional waiting can
  accommodate occasional slow requests without extending the 600-second attempt
  deadline." Not yet tested in a solving run.
- **Records:** [validation-checkpoint-prompt](../evidence/validation-checkpoint-prompt/README.md).

## Pwn target diagnostics

- **Date / code:** November 11. Settings: medium / 8,192 / 2 MiB / 90 s.
- **Runs:** batch `8c72ac67cab7`, then batch `bebe62296ff3` after a diagnostic change
  that records target container state before cleanup (commit `aedfd62`). Each ran
  `pwn-roppity` and `pwn-baby-boi`, two trials each.
- **Result:** 0/4 in each batch. In `bebe62296ff3` all four target containers had
  exited with code 1 before cleanup.
- **Records:** [service-lifecycle-investigation](../evidence/service-lifecycle-investigation/README.md),
  [target-snapshot-batch-review](../evidence/target-snapshot-batch-review/README.md),
  [docker-process-constraints](../evidence/docker-process-constraints/README.md).
