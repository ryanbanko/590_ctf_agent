# Expanded validation-prompt review — November 15, 2026

Batch `10010bdf842e` completed **12/12 verified successes** across the four remaining
categories. Together with the [first six trials](../validation-pilot-review/README.md),
the unchanged revision has **18/18 successes across six task categories**, versus
17/18 in the corresponding historical baseline. The baseline's single failure
was service-related, so this is not a demonstrated causal validation improvement.

## Task-matched comparison

All four expanded-set tasks achieved 3/3 in both conditions. Times below are means
of recorded local active seconds, including every trial.

| Task | Baseline mean seconds | Candidate mean seconds | Baseline / candidate estimated cost |
| --- | --- | --- | --- |
| pwn-pilot | 72.17 | 64.73 | $0.01666764 / $0.01289659 |
| rev-gibberish-check | 239.21 | 279.14 | $0.07149670 / $0.06329163 |
| web-shreeramquest | 23.33 | 18.58 | $0.00417874 / $0.00304756 |
| for-1black0white | 45.19 | 26.27 | $0.00340241 / $0.00291756 |

For the new twelve, recorded active time was **1166.17 versus 1139.70 seconds**
(about 2.3% higher), estimated cost **$0.08215334 versus $0.09574549** (about 14.2%
lower), and model calls **118 versus 120**. Including the earlier six gives
**1865.46 versus 1525.42 active seconds** (about 22.3% higher) and estimated cost
**$0.11704363 versus $0.11645893** (about 0.5% higher). Median recorded active time
across all eighteen is 47.08 versus 62.59 seconds; the mean/tail and median tell
different stories. Preserve both, along with the timing anomaly below. Costs are
recorded gateway-rate estimates, not complete native cache-write billing.

## Every new trial

| Task/trial | Run ID and trace | Active seconds | Model calls | Estimated cost | Outcome |
| --- | --- | --- | --- | --- | --- |
| pwn-pilot / 1 | [7b008496a52b](https://us.cloud.langfuse.com/project/cmw17lafc0745ad0eekgn9a7j/traces/7dae9566e9c1518ea2e12fceea25366b) | 51.48 | 9 | $0.00378927 | success |
| rev-gibberish-check / 1 | [5d12aaf5eb8e](https://us.cloud.langfuse.com/project/cmw17lafc0745ad0eekgn9a7j/traces/34038828d7a63775953362fee49f00b2) | 144.03 | 17 | $0.01901611 | success |
| web-shreeramquest / 1 | [bd6eaf2ca41b](https://us.cloud.langfuse.com/project/cmw17lafc0745ad0eekgn9a7j/traces/d2461b6e76ee311361e9e3d79a511043) | 16.46 | 4 | $0.00092302 | success |
| for-1black0white / 1 | [f86b85403e22](https://us.cloud.langfuse.com/project/cmw17lafc0745ad0eekgn9a7j/traces/861617f5134f0709dae8fe746a9767d4) | 19.81 | 5 | $0.00100711 | success |
| pwn-pilot / 2 | [9db2200a8eae](https://us.cloud.langfuse.com/project/cmw17lafc0745ad0eekgn9a7j/traces/7f3be62d56fce9c4ee4afea97dae90e3) | 26.53 | 5 | $0.00220143 | success |
| rev-gibberish-check / 2 | [fe967b23c21b](https://us.cloud.langfuse.com/project/cmw17lafc0745ad0eekgn9a7j/traces/170cd6770e8b179f22a8c38874f65704) | 331.34 | 16 | $0.01496241 | success |
| web-shreeramquest / 2 | [a817cfb29b06](https://us.cloud.langfuse.com/project/cmw17lafc0745ad0eekgn9a7j/traces/24d426fb0928b2569f89d6cd404f15c0) | 17.42 | 4 | $0.00095877 | success |
| for-1black0white / 2 | [e0957d626a4f](https://us.cloud.langfuse.com/project/cmw17lafc0745ad0eekgn9a7j/traces/c273311bb3b579ff649c9cba9d3dcb92) | 31.74 | 5 | $0.00092511 | success |
| pwn-pilot / 3 | [e794e21ecbb7](https://us.cloud.langfuse.com/project/cmw17lafc0745ad0eekgn9a7j/traces/28034fa56ea334ac67d06c036702f21c) | 116.17 | 15 | $0.00690589 | success |
| rev-gibberish-check / 3 | [42994bf7f1eb](https://us.cloud.langfuse.com/project/cmw17lafc0745ad0eekgn9a7j/traces/4ad48aa2336428479cbc67e4fe611c67) | 362.06 | 27 | $0.02931311 | success |
| web-shreeramquest / 3 | [4ec428551a34](https://us.cloud.langfuse.com/project/cmw17lafc0745ad0eekgn9a7j/traces/7c5ee46a3eae7e3f39f68c1f74eef214) | 21.87 | 5 | $0.00116577 | success |
| for-1black0white / 3 | [b4f72c9623c9](https://us.cloud.langfuse.com/project/cmw17lafc0745ad0eekgn9a7j/traces/f11a7675fde3fa4b6be22981c404ddb0) | 27.27 | 6 | $0.00098534 | success |

## Behavior assessment

- **Pwn:** 3/3; mean time and cost lower. The short trial needed five calls. Trial 3
  recovered from several failed assumptions and eventually used a small observable
  remote test before the larger action. Trial 1 still tried an oversized generated
  input before correcting it. Final trial-1 payloads are missing, so that portion
  of the sequence cannot be fully inspected even though local records report
  evaluator-confirmed success. Local emulation complicated trial-3 interpretation;
  no new infrastructure/library diagnosis is established here.
- **Reversing:** 3/3, with lower estimated cost but higher mean time. Trial 1 checked
  predictions against the original artifact before its later bounded search.
  Trials 2 and 3 still searched using an unvalidated reconstruction: one spent
  about 84 seconds before an original-artifact rejection, and both later hit a
  command timeout/restart. Trial 3 then made repeated assumed-discrepancy adjustments
  before switching to direct original-artifact acceptance checks. The validation
  instruction is not reliably preventing this failure class.
- **Web:** 3/3; 4, 4 and 5 calls. Unexpected responses led to small focused
  comparisons and successful recovery. No obvious extra validation ritual appeared.
- **Forensics:** 3/3; inexpensive structure/layout checks and decoding. Two trials'
  initial text assumed 28 rows before inspection corrected the count to 29. These
  errors were cheap and corrected; successful recovery is not flawless extraction.
- **Output/context:** reversing remains noisy. Trial 3 tool 15 produced 500,979 raw
  output bytes; its 65,536-byte preview was marked truncated and capture reported
  complete. The agent recognized the bad diagnostic and reran cleanly. Largest
  individual reversing request was 95,997 reported input tokens, below the byte
  cap but still costly replay. Two other reversing trials also printed broad
  disassembly. Narrower output remains a separate candidate, not a shipped fix.

## Record-quality findings

**Six missing local export fields in Pwn trial 1 (`7b008496a52b`):** generation 9
input/output, tool 8 input/output, and tool 9 (`submit_flag`) input/output are null.
The run reports `evidence_complete: true` and `verified_success: true`; structural
checks do not establish payload completeness. Preserve the verified result and
flag the limited trace review. Do not reconstruct an unseen final candidate or
verdict. Hosted observations were not re-fetched, so eventual delivery versus
permanent loss remains undiagnosed. This recurs independently of the earlier
baseline export gaps. No other required input/output field is absent in the
remaining eleven expanded exports.

**Reversing trial 2 timing (`fe967b23c21b`):** tool 13 requested 120 seconds and
returned `timed_out: true`, restarting the solver. Its timestamp span is 314.303
seconds; the root span is 525.337 seconds versus 331.335 local active seconds.
The original baseline also had a separate hosted/local timing discrepancy.
Host sleep/clock effects are plausible but unconfirmed. Do not sum native spans
as controller active time or treat them as CPU time, and do not infer the command
budget was extended solely from the span duration. Trial 3 had another timeout,
with a 120.446-second span. Both attempts recovered and succeeded.

No scope incident or cleanup error occurred. Target startup/before-cleanup states
and image identities are retained in the derived review. No evidence supports a
new target crash/repair or budget relaxation from this batch.

## Provenance and limits

[Derived review](review.json) retains all twelve candidate plus twelve original
baseline records, source/export hashes, observation IDs, metrics, missing fields,
timing observations and all-trial findings. [Checks](checks.json) audits those
records and current links. All available expanded request bodies (117 of 118)
contain the exact candidate system prompt; the missing final body cannot be
verified directly. All recorded source hashes identify the same candidate, with
only `ctf_agent/agent.py` differing from baseline. The original tool description,
settings, limits, dataset and per-task images match. Combined with the first six,
179 of 180 request bodies are directly available.

Three trials per task, one task per category, historical controls, randomized
instances, reused practice exposure, timing/cache variation and the combined
validation/layout/sentence changes prevent a broad causal improvement claim.
The control set already had 12/12 successes, creating a success ceiling. Trace
payload gaps and clock discrepancies constrain detailed attribution further.

The review read existing local exports, without private answers/source/state,
command replay, hosted mutation, new model calls, containers or runtime edits.
Raw runs remain Git-ignored; this folder includes derived metadata and no flag
values or solve scripts. Original records are unchanged.

## Decision

It is reasonable to retain this small prompt revision after eighteen successful
regression trials across six categories. It has no observed solve regression,
but has not established a validation or efficiency gain. Stop expanding this
wording experiment by default; evaluate the next change separately with this
candidate frozen. Recurring priorities are checking reconstructed behavior
against original artifacts before expensive search, narrower output, and reliable
error/export records. No further run or behavior change is authorized or started
by this review. The earlier connection-description candidate remains unadopted.
