# Organizational refactor verification

November 3, 2026 (America/New_York).

Historical snapshot: the commands below describe the pre-pytest implementation.
For the current checkout use the [main README](../../README.md) and
[pytest refactor evidence](../pytest-refactor/README.md). Historical JSON records
and their hashes remain unchanged.

**17 container checks and 6 contract tests passed.** This is synthetic setup
evidence; no model calls, real CTFTiny attempts, pilots, or scored runs occurred.

## Changes checked

- Synthetic controls moved from `ctf_agent/self_check.py` to `tests/check_controls.py`.
- Synthetic target lifecycle moved from `ctf_agent/fixture.py` to `tests/fixtures/target.py`.
- The CLI still accepts the existing build/self-check commands; it imports test
  code only when self-check is explicitly requested.
- Attempt tool results now use one shared logging path for success and failure.
- Fixture cleanup attempts network removal even when container removal fails or
  times out. A new mocked unit check covers both failures without Docker actions.
- No changes were made to container helpers, network rules, resource limits,
  evaluator behavior, or expected-answer separation.

## Verification

Commands:

```sh
python3 -m unittest discover -s tests -v
python3 -m ctf_agent build-images
python3 -m ctf_agent self-check
```

The existing images were absent, so the same pinned Dockerfiles were rebuilt
before running the suite. Docker reused the cached implementation layers.

[Complete suite record](self-check-aaae7e8847fd/suite.json) contains all 17 check
names/run IDs, configuration, image IDs/architectures, and source hashes. Every
run directory contains its complete `trace.jsonl` and `summary.json`. Total suite
time, including synthetic target setup/cleanup: **46.626560 seconds**.

An additional trace check confirmed that the ordered `tool_called` steps match
the ordered `tool_returned` steps exactly, including infrastructure failures.
Every executed tool has one result event. Invalid calls retain their separate
`tool_rejected` events. Current source files matched the recorded SHA-256 values
after the run.

The suite and a separate final Docker query confirmed no containers or networks
with `ctf590.managed=true` remained. The original milestone's trace/provenance JSON
files have not been edited. Its evidence index now links to the moved test code
and identifies the old source paths as historical.

Remaining limits are unchanged: native ARM64 verified; actual AMD64 execution,
gateway/model integration, real CTFTiny compatibility, and later assignment stages
remain pending. This refactor is not the course's controlled improvement experiment.
