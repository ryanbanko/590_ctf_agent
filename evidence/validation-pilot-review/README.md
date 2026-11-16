# Validation-prompt pilot review — November 15, 2026

The user ran the approved candidate on cry-lupin and msc-algebra, three fresh
trials each, using the ordinary sequential batch runner. Batch `bfa61beea669`
completed **6/6 verified successes**. All six evidence checks/exports and cleanup
records passed; no scope incident, solver restart, target restart/OOM or command
timeout was recorded. This is an encouraging pilot, not a confirmed improvement.

## Comparison with the original prompt

| Task | Baseline successes | Candidate successes | Baseline mean active seconds | Candidate mean active seconds | Baseline / candidate estimated cost |
| --- | --- | --- | --- | --- | --- |
| cry-lupin | 2/3 | 3/3 | 61.44 | 164.03 | $0.00652700 / $0.02276431 |
| msc-algebra | 3/3 | 3/3 | 67.14 | 69.06 | $0.01418644 / $0.01212598 |
| Total | 5/6 | 6/6 | 64.29 | 116.55 | $0.02071344 / $0.03489029 |

The baseline includes its early service-blocked failure; it is not omitted from
resource accounting. Its short duration makes success/time comparisons especially
important to interpret separately. The candidate used 699.29 active seconds
versus 385.72, about 81% more; estimated model cost rose about 68%. Median active
seconds across all six decreased from 68.12 to 62.49, while one 374.69-second run
raised mean/tail resource use. Do not select only the metric that favors a condition.
Costs are local gateway-rate estimates, not complete native cache-write billing.

## Each candidate trial

| Task/trial | Active seconds | Model/tool calls | Estimated cost | Review |
| --- | --- | --- | --- | --- |
| [Lupin 1](https://us.cloud.langfuse.com/project/cmw17lafc0745ad0eekgn9a7j/traces/e36da668045fced077d245464ed3531d) | 374.69 | 22/22 | $0.01679070 | Recovered from cheap parser failures, but followed a long route and repeated some preparation/search work. |
| [Algebra 1](https://us.cloud.langfuse.com/project/cmw17lafc0745ad0eekgn9a7j/traces/f2513f8198ce511fc7e3c77c96961923) | 50.87 | 8/8 | $0.00248653 | Checked an exceptional case before completing; initial session confusion remained. |
| [Lupin 2](https://us.cloud.langfuse.com/project/cmw17lafc0745ad0eekgn9a7j/traces/bd671b2b93c98beb15edaea0d95435d3) | 74.11 | 8/8 | $0.00400896 | Used a local encoded sample to check interpretation after an initial prediction failed. |
| [Algebra 2](https://us.cloud.langfuse.com/project/cmw17lafc0745ad0eekgn9a7j/traces/f2b7861e6b929fbdfbcc76539f6fae19) | 121.39 | 11/11 | $0.00537291 | Repeated fresh connections with answers from earlier observations before correcting the interaction. |
| [Lupin 3](https://us.cloud.langfuse.com/project/cmw17lafc0745ad0eekgn9a7j/traces/6f943d638da7e6d2be670d06cf72ce7e) | 43.29 | 7/7 | $0.00196465 | Cheap parser error recovery; the first correction missed an assertion and repeated the error. |
| [Algebra 3](https://us.cloud.langfuse.com/project/cmw17lafc0745ad0eekgn9a7j/traces/fafb2a0d697fd25796ad3186ce962f26) | 34.94 | 6/6 | $0.00426654 | Fast recovery/completion, but one command printed 44,928 characters. |

## Behavior findings

- **Some desired validation behavior occurred.** Lupin 2 tool 6 tested an encoded
  local sample after a failed prediction, before changing strategy. Algebra 1
  tool 6 checked an exceptional expression separately. Comparable checking also
  existed in original-prompt traces, so these are not proof of a new capability.
- **The long run still made avoidable mistakes.** Lupin 1 tools 6–11 encountered
  six parser/import failures, each returning within four seconds. The errors
  stopped dependent work cheaply, but validation was incomplete. Tools 12–14
  returned nonzero because bounded searches left unresolved work; those exits
  must not all be mislabeled implementation failures. Some later passes repeated
  roughly 20-second computations. Saving/reuse remains a separate opportunity.
- **The prompt is not a correctness guarantee.** Lupin 3's claimed dimension check
  missed a vector case and its first patch missed a second assertion. Algebra 2
  tools 3–5 opened new sessions but sent fixed answers from earlier observations,
  leading to incorrect protocol interpretations before eventual recovery.
- **Output/context efficiency is unresolved.** Algebra 3 tool 5 printed 44,928
  characters. The following generation's input rose from 7,493 to 31,813 tokens.
  No tool output was truncated. The largest request was 33,736 input tokens;
  aggregate attempt input counts are replay totals, not individual context size.
- **Infrastructure was healthy in this sample.** No repeated remote JSON error
  occurred. The original baseline's one failure was a service issue, so the
  success-count increase cannot be credited to the validation instructions.
  Scope-recovery relocation was not exercised because no scope denial occurred.

## Provenance, checks and limits

[Derived review](review.json) contains all six candidate and six baseline metrics,
observation IDs/step references, source/export hashes and comparison conditions.
[Checks](checks.json) records the metadata/provenance audit. The exact candidate
prompt appears in every one of the 62 model requests. Tool descriptions match the
baseline. Only `ctf_agent/agent.py` differs in recorded runtime source hashes;
settings, limits, dataset identity and per-task image provenance match. All 62
candidate generation inputs/outputs and 62 tool inputs/outputs are present.

The review read existing local exports, with no hosted writes, model call,
container operation, private source/state/answer consultation, or command replay.
Raw runs stay Git-ignored. This evidence contains derived metadata, not flag
values, solve scripts or full trace payloads. No runtime code changed during review.

There are three trials per task, two categories, fresh unpaired randomized
instances and a historical baseline. Prompt wording, paragraph placement and
sentence splitting changed together. Different solution paths, model/cache
variability and reused practice data further limit inference. Compare with the
original baseline, not only the previously rejected connection-description pilot.

**Recommendation:** keep this candidate unchanged for a reviewed broader test,
rather than claim it improved efficiency or add another prompt rule immediately.
A proposed expansion would run the other ten tasks from the original 12-task
practice set, three trials each, preserving these six results. A fresh original-
prompt control would strengthen inference but costs additional trials. Neither
expansion nor control is launched or authorized by this review itself.
