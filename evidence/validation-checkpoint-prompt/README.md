# Validation and reusable-computation prompt — November 11

Implemented the user-approved prompt refinement in `ctf_agent/agent.py`:
small original-artifact checks before expensive searches, explicit independence
of validation, exact-value rechecks after contradictions, and reusable expensive
intermediates invalidated when inputs/assumptions change. Existing long-value
file/variable guidance, tools, isolation, scope, verification and stopping remain.

The [hypothesis and follow-up criteria](../../docs/EXPERIMENTS.md#original-artifact-validation-and-reusable-computation--november-11)
were recorded before implementation/testing. This adds no planner, automatic
checkpointing or new submission interface. Luna/medium/8,192 remains selected;
the separately approved 2 MiB default cap is included in the
[settings snapshot](experiment.toml). Named older profiles and original results
are unchanged. Service investigation remains pending the user's explicit go-ahead.

## Actual verification

Five existing offline cases passed in 0.40 seconds:

```sh
.venv/bin/python -m pytest \
  tests/test_agent.py::test_observations_drive_recovery_and_only_public_history_is_passed \
  tests/test_agent.py::test_wrong_submission_then_success_stops_sibling_tools_and_later_turns \
  tests/test_agent.py::test_text_claiming_success_is_not_evaluator_success \
  tests/test_model.py::test_native_reasoning_and_tool_results_reach_next_request_with_one_generation_per_call \
  -q --disable-plugin-autoload
```

These check prompt propagation, public history, recovery, rejection/success
stopping and native response replay with substituted execution/model transports.
They do not measure the model's compliance with the new wording or better solving.
Zero live model/container calls. [JUnit record](pytest.xml) omits the host-name
attribute. [Before](prompt-before.txt), [after](prompt-after.txt), and
[hashes/check metadata](checks.json) preserve exact wording and provenance.

## User-run targeted follow-up

From the repository root, run two fresh trials of the three tasks relevant to
validation/data handling and expensive computation:

```sh
uv run --frozen --env-file .env python -m ctf_agent run-batch \
  --experiment evidence/validation-checkpoint-prompt/experiment.toml \
  --challenges cry-lupin rev-gibberish-check rev-a-walk-through-x86-part-2 \
  --trials 2 \
  --output runs/pilots/validation-checkpoint
```

This makes paid model requests and six scheduled development attempts. It uses
the current source prompt and snapshot settings; it does not restore an old
prompt from the evidence files. Keep source/images unchanged while running.
This command does not include roppity/baby-boi or initiate their separate service
investigation. Preserve failures/partial attempts and inspect actual batch status.

Evaluate checks before search, response to contradiction, exact-value handling,
reuse of intermediates, verified success and resource use. Comparison against the
older 512 KiB batch is exploratory and combines prompt plus input-headroom changes.
Isolating prompt benefit requires both prompt versions at the same 2 MiB allowance
in fresh matched trials. No live follow-up has been executed by this milestone.

## 90-second request follow-up

The subsequent user-run `batch-983d82df4d2f` reached four of six planned attempts:
all three first trials succeeded, then second-trial lupin encountered an API timeout
after 60.047 seconds on model request six. It stopped the batch; the remaining two
trials were not started. No scope incident or cleanup error was recorded. The
original result and earlier 60-second snapshot remain unchanged. These outcomes
do not establish a causal prompt improvement or identify the gateway delay's cause.

The user approved a **90-second request allowance** while retaining the
**600-second whole-attempt deadline**, clipping each request to remaining time and
keeping automatic retries disabled. The default config and the new
[request-90 snapshot](experiment-request-90.toml) differ from `experiment.toml`
only in `model.request_seconds`. Local configuration comparison passed; three
existing offline cases passed in 0.42 seconds for no-retry timeout handling,
late-response action blocking and configuration call-limit consistency.
[JUnit evidence](request-90-pytest.xml) omits host-name attributes. No new model or
container calls were made by this adjustment. Its hypothesis is recorded in
[EXPERIMENTS](../../docs/EXPERIMENTS.md#subsequent-90-second-request-allowance--november-11).

For a fresh six-attempt batch under the new allowance:

```sh
uv run --frozen --env-file .env python -m ctf_agent run-batch \
  --experiment evidence/validation-checkpoint-prompt/experiment-request-90.toml \
  --challenges cry-lupin rev-gibberish-check rev-a-walk-through-x86-part-2 \
  --trials 2 \
  --output runs/pilots/validation-checkpoint-request-90
```

This starts fresh attempts, not a resume or replacement of the stopped batch.
Keep the different request allowances explicit when comparing results.
