# Manual HTB description preface — November 17, 2026

The user approved adding only this sentence before the task JSON in the initial
user message for manual HTB attempts:

> Challenge descriptions vary in detail and may mix story, humor, and technical clues.

`run_manual_challenge` supplies the sentence to the common runner as an optional
preface. CTFTiny calls the runner without it. The system prompt and original task
description are unchanged. `public-task.json` and the `task_sha256` calculation
continue to use the unprefixed task JSON.

## Verification

The focused test
`tests/test_manual.py::test_manual_model_flow_exports_real_sdk_spans_without_hosted_access`
passed. Its synthetic SDK request checks the exact preface/task order and the
unchanged system message, then checks that the saved public task contains only
the original JSON plus its newline. Summary: 1 passed. See [checks.json](checks.json).

The first command could not initialize the default uv cache due to filesystem
permissions; using a temporary cache resolved that environment issue. Two early
test executions then caught mistakes in the newly added assertions (a local name
shadowed the fixture helper, then the expected saved-task path was one directory
too deep). Both were corrected before the passing run; neither indicated a
product-code failure.

No live model request, challenge attempt, Docker operation, hosted mutation,
commit or push occurred. These checks establish prompt propagation and scope, not
behavioral benefit. A controlled fresh-attempt comparison remains separate.
