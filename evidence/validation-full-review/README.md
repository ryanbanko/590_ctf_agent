# Latest partial-batch agent-pattern review — November 16, 2026

Scope: observable purpose statements, actions, feedback, corrections and stopping.
The user explicitly requested agent-pattern analysis rather than challenge analysis.
No challenge solution, private source/state/answer inspection, recorded command
replay, new model call, container operation or runtime edit was performed.

## Coverage and status

Development batch `aaab2a5084b8` stopped after 23 of 30 planned attempts: 20
successes, one 40-model-turn failure, one 600-second wall failure and one model/API
incident. This is 20/22 among completed ordinary solve attempts; the API incident
is separately preserved, not dropped. Seven development attempts and six test-task
practice attempts remain unstarted. The earlier user-confirmed VPN-interrupted
batch `ce84d7e598bd` remains separate. The latest API incident also has a ConnectError
on export, but its exact request failure/VPN cause is unconfirmed.

## Main patterns, in priority order

1. **An unsuccessful test becomes a story about the environment too quickly.**
   In the 40-turn failure the agent repeatedly inferred restrictions before
   establishing that its own diagnostic was correct. It acknowledged a layout
   mistake only at step 24. Later tests showed that further diagnostic bugs,
   rather than the claimed external restrictions, explained some missing output.
   A failed test is not evidence that the test itself was valid.
2. **Verification language runs ahead of observed verification.** The agent often
   says an input or interpretation is confirmed, then acts using an implementation
   that does not match it. The useful intervention is a discriminating, calibrated
   check with an expected result, not simply more statements about validation.
3. **Persistence does not consistently reduce uncertainty.** The two failed runs
   continued varying tests or escalating diagnostic machinery without promptly
   resolving the weakest premise. The 600-second failure spent two full command
   allowances on unsuccessful diagnostics/search, with smaller checks coming late.
   More turns would risk extending the same loop rather than correcting it.
4. **Edits are not always verified as a whole.** One successful 14-call run needed
   several parser/edit corrections and a fix for a second unguarded path. Recovery
   worked, but repeatedly checking only the latest edit wastes calls.
5. **The successful pattern is narrow evidence-driven branching.** One successful
   run explicitly checked a prerequisite after repeated failure, used the positive
   result to narrow the next test, and completed. Several other successes stayed
   within four to six calls. Excessive validation is not a universal regression.

## What this implies

The replacement prompt is not reliably producing better-quality checks. The main
weakness is test design and interpretation: distinguish observations from hypotheses,
validate the test itself, and prefer checks that separate competing explanations.
Generic persistence or more elaborate planning alone is not established as a fix.
The existing one-sentence purpose makes these patterns visible, but the review
cannot establish that requiring it caused the mistakes.

Keep the two solver failures separate from the API stop. No automatic retry,
budget increase, Docker change, new tool or additional prompt edit is justified
by this review alone. The earlier 18/18 pilot remains valid historical evidence,
but the new failures mean the revision is not an across-the-board reliability fix.

## Trace references

- [40-turn failure: 61bf8e65e52b](https://us.cloud.langfuse.com/project/cmw17lafc0745ad0eekgn9a7j/traces/214a6f499c3c13a02dc83260d0de7a20)
- [600-second failure: 4fbd9b2b538b](https://us.cloud.langfuse.com/project/cmw17lafc0745ad0eekgn9a7j/traces/ed849dcfdc984e6c9770ed1bdd1cd1d7)

[Derived record](review.json) preserves all 23 outcomes, record/export hashes and
step references without payloads or flag values. The model/API incident has no
local trace; conclusions about its preceding reasoning would be speculation.
Original run records remain unchanged. This is a partial, unpaired practice review,
not a completed 36-trial comparison or inspection of hidden internal reasoning.
