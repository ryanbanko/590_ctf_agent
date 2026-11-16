# Validation-prompt candidate — November 15, 2026

The user approved a small system-prompt revision after reviewing wording,
structure, preservation of meaning and experimental scope. This is an experimental
candidate in the working tree, not a demonstrated performance improvement.
No live trial was launched during this edit.

## Exact change and hypothesis

Only `ctf_agent/agent.py: SYSTEM_PROMPT` changes in runtime source:

- Replace the original expensive-search sentence with explicit cheap validation,
  a small representative case when appropriate, correction of failed preparation
  before dependent expensive work, and a cheap recheck after correction.
- Preserve the requirement to use the original public checker or artifact when
  available, and preserve the warning against circular validation.
- Move the complete `scope_denied` paragraph verbatim beside endpoint/network rules.
- Split the persistence/restart sentence and the truncated-output/capture sentence.

The intended behavior change is earlier validation and failure handling. Relocation
and sentence splits aim to preserve meaning, but can still affect model behavior.
The experiment measures this small combined revision, not validation in isolation.
No headings, planner, notes, new tool, enforced validator or additional model call
were added. Output/reuse instructions, purpose sentences, submission verification,
stopping guidance and scope policy remain. Model/settings, tool descriptions,
execution loop, Docker, dependencies, tests and original results are unchanged.

Hypothesis: cheap checks before expensive computation, stopping dependent steps
after preparation errors, and checking corrections before reruns will reduce
wasted computation without excessive checking or reduced solve success. The
model's ability to construct meaningful checks remains uncertain.

## Verification and rollback

- [Original prompt](system-prompt-original.txt): extracted from the unchanged
  runtime source before this edit; verified against commit `0395835`.
- [Candidate prompt](system-prompt-candidate.txt): exact current runtime value.
- [Source diff](system-prompt.diff): the complete application-source edit.
- [Checks](checks.json): prompt/source hashes, original/candidate transformation,
  retained instructions, non-prompt AST identity and unchanged runtime files.
  The [initial audit](checks-initial.json) checked links before creating its diff/
  checks artifacts; those two ordering failures are preserved. The completed
  rerun checks the existing artifacts.
- [Offline results](pytest.xml): 36 existing tests in `tests/test_agent.py` and
  `tests/test_model.py`. These test integration, not effectiveness of the wording.

The original is also available through `git show 0395835:ctf_agent/agent.py`.
At this milestone only the prompt differs in that file. Review the diff before
restoring it if later code changes are added. Do not discard documentation or
historical evidence merely to revert the prompt.

## Preceding investigation and rejected candidate

[Connection-pilot review](connection-pilot-review.json) preserves derived metrics,
trace links and original run/export hashes for the three user-run external trials
and their three historical baseline comparisons. The connection description was
not adopted. It is not part of this candidate.

| Connection condition | Successes | Active seconds, all trials | Estimated model cost |
| --- | --- | --- | --- |
| Original, three baseline trials | 2/3 | 184.31 | $0.00652700 |
| External connection-wording candidate | 1/3 | 1229.04 | $0.02835505 |

The candidate's first trial succeeded in 28.89 seconds; the other two reached the
600-second attempt limit during later computation/corrections. All three initial
reads completed without the earlier repeated remote JSON error. One full command
timeout restarted the solver. Another command returned Killed/137; the trace does
not establish the kill cause. Scope incidents and cleanup errors were zero.
All 38 generations included tool calls, and 37 included purpose text. No summary-
only stop occurred; the unchanged purpose instruction was not independently tested.
Fresh randomized instances, small samples, historical timing/cache conditions and
different solution paths prevent causal improvement/regression claims.

The earlier agent-started attempt `5a6bc0060000` was interrupted for user handoff:
`user_cancel`, five model calls, $0.00236938 estimated. Preserve it separately from
these three completed trials. Original raw run records remain external temporary
artifacts; this folder retains derived metadata, not private task/trace payloads.

[Service-diagnostic snapshot](service-diagnostic-summary.json) preserves 15 fixed-
probe cycles. Three four-second early closes produced persistent remote JSON
errors; three five-second closes did not. Six longer/same-connection controls
received data without the error. The target listener remained running. Interrupted
initialization/publication is consistent with synthetic evidence; actual private
state/write contents were not inspected. No target repair was adopted. This
snapshot predates the live pilot, so its pending live-comparison field is historical.
Underlying scripts and raw reports remain external temporary artifacts; this is
not a fully retained service-reproduction package.

## Proposed next experiment

Stop for review after offline verification. Proposed later paid pilot:
`cry-lupin` and `msc-algebra`, three fresh trials each, ordinary sequential runner.
Use separate output directories, preserve all failures, and retain Luna/medium,
8192 output tokens, 2 MiB request cap, 90-second requests, 600-second attempts,
120-second commands, 40 model calls and 80 tool calls, existing images and controls.
Compare evaluator-confirmed success first, then time/cost, expensive failed
commands, repeated computation, validation timing and unnecessary checking.
The historical baseline is an exploratory comparison, not paired random instances.
If warranted, review expansion to the original 12-task/three-trial practice set.
No paid pilot, broader comparison, commit or push was made by this edit.

The concise/direct wording and evaluation approach are consistent with
[OpenAI reasoning guidance](https://developers.openai.com/api/docs/guides/reasoning-best-practices)
and [evaluation guidance](https://developers.openai.com/api/docs/guides/evaluation-best-practices).
The exact wording is a trace-motivated hypothesis, not a vendor-validated Luna prompt.
