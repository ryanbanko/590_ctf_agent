# Planning/notes and 50-turn candidate — November 16, 2026

Historical implementation checkpoint: the user later ran the candidate, reviewed
its limited adoption and selected the original prompt/40-turn configuration.
See the [trial review and rollback](rollback/README.md). The exact pre-wrapper
version of this document is preserved as
[implementation-README.txt](rollback/implementation-README.txt); prior hashes and
offline results retain their original checkpoint meaning. Statements below about
no live trial describe implementation time, not current status.

The user approved restoring the original practice-baseline system prompt, adding
the agreed brief-planning/optional-notes paragraph, and raising the default model
turn allowance from 40 to 50 to accommodate note reads/writes. This is a combined
prompt-and-budget candidate. No live attempt has run with this condition.

## Hypothesis and exact condition

Brief plans and optional notes may help complex attempts maintain direction,
reuse valid work and avoid repeating rejected approaches, with limited overhead
on straightforward tasks. Ten additional model turns provide room for note
operations within the original wall and tool limits; they do not establish that
extra persistence improves decisions or guarantees completion.

The prompt is the exact original `0395835` value plus the
[agreed paragraph](planning-notes-paragraph.txt), placed after its original
validation/recovery/scope guidance. The earlier validation/readability revision
is withdrawn from the active prompt. Its observations and original artifacts
remain unchanged in [prompt-validation](../prompt-validation/README.md),
[initial pilot](../validation-pilot-review/README.md),
[expanded pilot](../validation-expanded-review/README.md) and
[partial full batch](../validation-full-review/README.md).

The default `configs/development.toml` now sets `max_model_turns = 50`; the
existing loader derives `model.max_requests = 50` from that value. The original
allowance was 40. Note reads/writes consume ordinary model/tool calls and time.
The 600-second wall deadline, 80-tool-call cap, 120-second command maximum,
90-second request timeout, model/effort/output/input settings and all other
settings stay fixed. Historical configuration snapshots are not rewritten.

Plans accompany tool calls. The existing text-only stopping policy remains.
Notes use the existing `write_file` and `run_command` tools inside the solver;
files are not automatically inserted into model context. Notes are optional,
per-attempt and fallible. Overwriting a note does not remove earlier note text
from conversation replay. No new tool, planner model, controller state, note
schema, injection, compaction, continuation, dependency or Docker change is added.

## Preserved artifacts

- [Original prompt](system-prompt-original.txt) and
  [original settings](settings-original.toml), verified against `0395835`.
- [Previous validation candidate](system-prompt-previous-candidate.txt), verified
  against its existing preserved snapshot before editing.
- [New prompt](system-prompt-candidate.txt) and
  [new settings](settings-candidate.toml).
- [Prompt diff from original](system-prompt.diff),
  [diff from previous candidate](previous-candidate-to-planning-notes.diff) and
  [complete runtime/config diff from baseline](runtime.diff).
- [Pre-edit hashes](before-edit-sha256.json) for 70 runtime/config/test and
  selected historical evidence files, allowing preservation checks.

## Actual verification

All **41 existing focused offline checks passed** (`pytest.xml`):

```sh
.venv/bin/python -m pytest -q tests/test_agent.py tests/test_model.py tests/test_contracts.py::test_complete_configuration_has_one_model_call_limit tests/test_contracts.py::test_configuration_rejects_invalid_limits tests/test_development.py::test_invalid_model_cap_is_rejected_before_launch --junitxml=evidence/planning-notes/pytest.xml
```

The [test record](pytest.xml) reports zero failures/errors/skips. Tests use local
SDK exporters, mocked HTTP transports and substituted Docker operations. They
cover public prompt propagation, recovery, native text/tool replay, verified
success, text-only/terminal stopping, usage and limits, and configuration sharing/
validation. No new test cases were added for prompt wording.

[Checks](checks.json) verifies the exact original-plus-paragraph transformation,
identical non-prompt AST, original snapshot identity, sole parsed setting change
of 40 to 50, derived API cap of 50, source/evidence preservation, local links and
whitespace. The first source-diff inspection caught an accidentally removed blank
line between the network and evidence-use paragraphs; it was restored before the
exact transformation check and tests. An inspection command also initially named
nonexistent test_config.py/test_attempt.py; actual test locations were then found
under tests/ before selecting checks. Neither was a runtime test failure.
The [initial audit](checks-initial.json) rejected an existing Markdown link to a
directory because its checker required every target to be a file. The checker
was corrected to accept existing directories as valid link targets, and the
completed audit was rerun; the initial result is preserved.

No live model call, challenge attempt, Docker operation, hosted change,
recorded-command execution, commit or push occurred. This milestone does not
authorize those later stages.

## Interpretation and next stage

Offline checks establish integration and preservation, not model behavior.
Any comparison with the 40-turn original measures planning/notes **plus** the
larger turn allowance. Isolating the prompt effect would require an original-
prompt control at the same 50-turn allowance. Prior trials sharing task/trial
labels are historical, unpaired comparisons; they are not matched random inputs.

After review, a separately approved small practice pilot could include complex
tasks and a short-task control. Assess evaluator-confirmed success, repeated
approaches, reuse, active time, calls/tokens/cost, note reads/writes, stale claims,
planning-only endings and actual note adoption. Extra available turns alone are
not evidence that notes help. If notes are rarely used, report limited adoption.
Keep failures and API/export incidents; do not replace historical results.
