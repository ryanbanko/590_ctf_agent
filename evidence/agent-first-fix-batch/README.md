# First-fix development batch — November 8

Record-only follow-up for the user-run batch
`runs/pilots/agent-first-fix/batch-48f3b134d5c3`. The eleven development challenges
each received one fresh attempt using clean commit
`e7e366c9cc2c77a45126d8d451c053bfb97abf5b`. This is the package described in the
implementation evidence, with its
[hypothesis recorded beforehand](../../docs/EXPERIMENTS.md#combined-prompt-tool-contract-and-output-recovery--hypothesis-recorded-november-8).

This document checks saved result/export metadata and preserves provenance.
Detailed message/tool-result interpretation remains pending. No challenge commands
were executed during this audit, and no new attempt or model request was made.
Held-out contents, benchmark answers and write-ups were not consulted.

## Recorded outcomes

**Six verified successes, five ordinary unsuccessful endings**, matching the
previous batch's total. `rev-tablez` changed from unsuccessful to successful;
`web-shreeramquest` changed from successful to unsuccessful. These are observed
outcome changes, not established effects of the prompt or output implementation.

| Challenge / hosted trace | Verified result | Model / tool calls |
| --- | --- | ---: |
| [cry-ecxor](https://us.cloud.langfuse.com/project/cmw17lafc0745ad0eekgn9a7j/traces/a582f64244007603e57f06cf7552c725) | No success | 5 / 4 |
| [cry-describeme](https://us.cloud.langfuse.com/project/cmw17lafc0745ad0eekgn9a7j/traces/a112e9eef1a882045b6e6efbf40224b1) | No success | 4 / 3 |
| [for-1black0white](https://us.cloud.langfuse.com/project/cmw17lafc0745ad0eekgn9a7j/traces/787cd3844a749335bd7b0f0eb9520a48) | Success | 9 / 9 |
| [msc-algebra](https://us.cloud.langfuse.com/project/cmw17lafc0745ad0eekgn9a7j/traces/4f553de11941ab86357089ea97aaf379) | No success | 11 / 10 |
| [msc-ezmaze](https://us.cloud.langfuse.com/project/cmw17lafc0745ad0eekgn9a7j/traces/41a5f9d8a596b720ce048fa6d8bfb84d) | Success | 8 / 8 |
| [pwn-baby-boi](https://us.cloud.langfuse.com/project/cmw17lafc0745ad0eekgn9a7j/traces/0c9dc4aa09c366ffcdd2930ffd034469) | No success | 7 / 6 |
| [pwn-get-it](https://us.cloud.langfuse.com/project/cmw17lafc0745ad0eekgn9a7j/traces/7c30c2659b54bbb51e964bd2161218eb) | Success | 4 / 4 |
| [rev-checker](https://us.cloud.langfuse.com/project/cmw17lafc0745ad0eekgn9a7j/traces/4c8fad0e9cd069c593fcdbfdbc7eda62) | Success | 3 / 3 |
| [rev-tablez](https://us.cloud.langfuse.com/project/cmw17lafc0745ad0eekgn9a7j/traces/7a0d04ca50e2710f52d282dc74f60766) | Success | 5 / 5 |
| [web-poem-collection](https://us.cloud.langfuse.com/project/cmw17lafc0745ad0eekgn9a7j/traces/261fc00d6f283f614e7d34eec9061804) | Success | 4 / 4 |
| [web-shreeramquest](https://us.cloud.langfuse.com/project/cmw17lafc0745ad0eekgn9a7j/traces/c546bac3fcd65888ec17668b3fcc691f) | No success | 5 / 4 |

The saved records contain 65 model requests and 60 tool calls. Summed active
time is 309.737431s; summed launch/export time is 438.529950s; batch elapsed time
is 450.202408s. These cover different intervals. Token totals are 338,143 input
and 15,711 output; 237,986 cached-input and 5,544 reasoning tokens are subsets.
The local configured-rate estimate sums to **$0.02025106**, not verified billing.
The previously identified native cache-write pricing difference remains unresolved;
do not mix pricing sources when comparing costs.

All five unsuccessful runs ended with `completed_without_success`. No command
timeouts, solver restarts, runtime truncations, automatic output captures, recorded
scope/guard incidents or cleanup errors occurred. Consequently this live batch
does not exercise oversized-output recovery; its evidence remains synthetic.

## Provenance and export checks

[summary.json](summary.json) contains filtered per-attempt metadata, trace URLs,
source paths/hashes, export hashes, recorded audit results, counts and the matched
historical baseline outcomes. [experiment.toml](experiment.toml) is the batch's
non-secret configuration snapshot. Neither artifact copies messages, command text,
candidates, target environment values or expected answers. Raw records remain
Git-ignored under `runs/` and hosted in Langfuse.

Checked all eleven records against the batch index, development manifest and
original exports: observation counts, trace identity, end times, unique IDs,
parent ancestry, cleanup events and existing privacy/cleanup audit flags. Every
record reports a clean source tree at `e7e366c`. Recorded source hashes match the
current application/configuration/tests. Compared with baseline
`batch-3963930b88c3`, model settings, existing attempt limits, image identities,
dataset revision/index and staged handout records match per challenge. The only
additional configuration keys are the two automatic-capture allowances.

### Supplemental rev-tablez export

The original `rev-tablez` export had end times and the expected observation counts,
but missing input/output payloads on five observations: the root attempt, two
generations and two tools. Its run still recorded `evidence_complete: true`.
This shows the existing count/end-time export check does not guarantee payload
availability; the cause of the missing original payloads has not been established.

A read-only Langfuse CLI `observations list` request recovered all 18 observations
with their payloads. Saved the supplemental export as
`runs/pilots/agent-first-fix/batch-48f3b134d5c3/attempt-009/challenge-b117a251b7a8/observations-refreshed.json`.
The original `observations.json` and run/index audit flags are unchanged. The
filtered summary records both hashes, the original gaps and the selected complete
export. All eleven selected exports now have their root/generation/tool input/output
payloads available, and exported root results match saved result fields.

Use the supplemental file for later `rev-tablez` trace review. Tightening the
launcher's payload-completeness check is a separate engineering follow-up, without
rerunning this successful attempt. No hosted data was modified by retrieval.

## Interpretation and next step

The user chose to rerun the prior eleven-ID development set rather than the
earlier proposed six fresh matched attempts. The baseline is historical, with
one attempt per challenge per configuration. Equal totals and exchanged outcomes
do not establish improvement, regression or a causal prompt effect. The bundled
change cannot identify which component helped. No held-out scoring or final
course metric aggregation is performed here.

Next: review messages and tool results against the recorded behavioral hypothesis,
including relevant independent checks, contradiction diagnosis, stopping claims
and changed outcomes. Preserve all originals. Decide further experiments only
after that review; model/effort/token settings, planning, notes and continuation
remain unchanged. This documentation audit made no runtime/configuration changes,
model calls or container operations.

Documentation verification passed for 186 local links/heading targets, JSON/TOML
parsing, all eleven saved record/export/baseline hashes, current source hashes,
credential/candidate-pattern checks and `git diff --check`. `.env`, raw `runs/`
and datasets remain ignored and untracked. No runtime tests were rerun for this
documentation-only follow-up. Changes remain uncommitted for user review.
