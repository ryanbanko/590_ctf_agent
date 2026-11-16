# Original baseline restored — November 16, 2026

The user chose to withdraw the combined brief-planning/optional-notes and
50-turn candidate and restore the original `0395835` prompt and 40-turn default.
This is a conservative selection after limited adoption and no demonstrated
benefit; it is not proof that the candidate caused a regression.

## What the candidate actually did

[Review metadata](review.json) preserves the original run/export hashes, local
outcomes, trace links, coverage gaps and behavior-step references without payloads,
answer values or solve scripts. The two stopped batches are:

- Initial pilot `055588a94b64`: five verified successes; the fifth run's local
  trace export failed with ReadTimeout after success.
- Breadth-development `e7f3dbb55808`: five verified successes, one ordinary ending
  after repeated service-side JSON errors and a final response-source stop whose
  trace export failed with ConnectError. A user-suspected Wi-Fi interruption is
  consistent with the last incident but is not independently diagnosed.

Together these are 12 recorded attempts across ten distinct tasks, including two
extra repeats. The two originally scored-list practice tasks did not start. This
is not a completed once-per-task 12-task comparison or a 36-attempt campaign.

Ten available exports contain 98 generation observations; all 97 available
generation inputs contain the exact candidate prompt. No explicit notes.md action
or write_file call is visible in available payloads. Initial broad intentions
appear alongside ordinary actions; they do not establish a useful maintained/
revised task-level working state or reveal hidden planning. No attempt exceeded
29 model calls, so the extra ten turns provided no observed benefit.

The review includes efficient short successes, recovery after contradictory
feedback, and inefficient successes. In `f739906d33da`, steps 4–6 return empty
inspection results before correcting the extraction assumption; step 10 emits
527,861 bytes. Steps 14–16 show an environmental explanation preceding resolution
of a contradicted model. Steps 17–18 modify an artifact, encounter an error before
restoration, then read that modified file as the purported original, undermining
later verification claims. Step 24 usefully measures throughput before expanding
work. In `ebc08728e106`, steps 5/7/8 revise an assumption and narrow the next action
with a prerequisite check. These are observations about agent evidence use and
state tracking, not challenge solutions or infrastructure diagnoses.

Two full local exports are unavailable. Successful run `317cecdc1213` additionally
lacks generation 8 input/output and tool 7/8 input/output: six missing required
fields despite local success and structural completeness. Missing actions are
not reconstructed. Historical/unpaired comparisons, variable paths, practice reuse
and the combined prompt/budget change prevent causal claims.

## Exact rollback and preservation

- Removed only the planning/notes paragraph from agent.py.
- Restored `max_model_turns = 40` and its original comment in development.toml;
  the existing configuration loader derives the API request cap as 40 too.
- Both files now match `0395835` byte-for-byte. Other runtime/config/test/Docker/
  dependency files are unchanged. The earlier validation revision stays withdrawn.
- Retained the [candidate prompt](../system-prompt-candidate.txt),
  [50-turn settings](../settings-candidate.toml), prior diffs/tests/checks, and all
  original local runs. The initial implementation README is retained
  [verbatim](implementation-README.txt) before adding its historical wrapper.

[Prompt reversal](system-prompt.diff) and [settings reversal](settings.diff) show
the exact change from the candidate. [Restored prompt](restored-system-prompt.txt)
and [restored settings](restored-settings.toml) identify the selected condition.
[Pre-rollback hashes](before-rollback-sha256.json) support preservation checks.

## Verification and remaining scope

All **41 existing focused offline tests passed** after rollback:

```sh
.venv/bin/python -m pytest -q tests/test_agent.py tests/test_model.py tests/test_contracts.py::test_complete_configuration_has_one_model_call_limit tests/test_contracts.py::test_configuration_rejects_invalid_limits tests/test_development.py::test_invalid_model_cap_is_rejected_before_launch --junitxml=evidence/planning-notes/rollback/pytest.xml
```

[Test results](pytest.xml) use local SDK exporters, mocked HTTP and substituted
Docker operations. [Checks](checks.json) verify baseline file identity, cap sharing,
preservation, source/evidence hashes, local documentation links and whitespace.
No new test cases or paid/later-stage experiment was added.

The [initial complete-documentation audit](checks-documentation-initial.json)
found relative links in the verbatim archived README resolving from its new
directory. The archive is retained as plain text so its original bytes and links
are preserved as historical text; current Markdown links point to the actual
artifacts. The completed audit checks all changed/new Markdown and evidence JSON/
XML, in addition to the focused rollback checks.

No live model call, challenge attempt, Docker operation, hosted mutation,
recorded-command execution, commit or push occurred during rollback. Stop for
review. Remaining uncommitted changes are documentation and evidence explaining
what was tested/tried; they are retained rather than discarded by a blanket reset.
