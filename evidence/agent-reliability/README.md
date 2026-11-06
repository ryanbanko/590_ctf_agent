# Reliability follow-up — November 4, 2026

Approved scope: worker cleanup and finished-session reaping, final-output and
partial-input correctness, continuing with valid replies when usage is absent,
preparation consistency, and documentation. Numeric limits, model, network policy,
three tools and dependencies are unchanged. SDK export, context management,
broader configuration cleanup and GDB remain deferred.

## Changes

- An ExitStack guarantees command resource/descendant cleanup on exceptions,
  including failures after a subprocess starts but before output setup succeeds.
- Finished commands drain final output regardless of a short poll deadline. They
  send a final result and exit; the worker reaps them while idle and retains their
  bounded final result for later retrieval. No new service or application class.
- `input_bytes_sent` reports accepted UTF-8 bytes. Partial/failed terminal writes
  identify the unsent remainder. Unexpected supervisor protocol errors remain
  infrastructure failures rather than ordinary tool errors.
- A valid model response without usage still runs its tools. Aggregate tokens and
  cost become null with `usage_complete: false`; later known usage does not make
  incomplete totals appear complete. Native observations retain per-response
  usage when available. Transport errors and malformed/incomplete replies retain
  their existing stopping behavior.
- `prepare-challenge --experiment FILE` uses the same attempt settings as the
  subsequent run. Its default is `configs/development.toml`. Staging checks actual
  free workspace after venv creation and shares the remaining attempt deadline
  across archive preparation and transfer. The five-second staging cap is gone.
- Documentation clarifies that one tool per response and forty model responses
  normally allow at most forty live tool actions, despite the eighty-tool guard.

## Verification

[Final index](verification.json) retains source hashes, image IDs, resolved live
settings, profile matching and cleanup confirmation. No model API calls or
challenge-solving attempts ran; API model spending was $0.

| Evidence | Result |
| --- | --- |
| [Worker Docker checks](worker-checks.xml), [log](worker-checks.log) | Eight passed: existing timeout/interactive/output behavior plus automatic reaping, partial input, zero-wait output preservation and supervisor fault handling. |
| [Worker contracts](worker-contracts.xml) | Eighteen passed, including injected output-setup failure after process creation and invalid/empty supervisor replies, with process calls substituted. |
| [Model checks](model-checks.xml) | Eight passed through real SDKs and offline HTTP transports. Missing usage on the first or later response still permits two tool turns and trusted success, with unknown aggregate usage. |
| [Preparation contracts](preparation-contracts.xml) | Seventeen passed, including free-space rejection, elapsed staging deadline and default/custom experiment CLI selection. |
| [Full fast suite](fast-tests.xml) | 91 passed. |
| [Full Docker suite](self-check-d67518fdf937/suite.json), [JUnit](self-check-d67518fdf937/pytest.xml), [log](controls.log) | 31 passed in one complete run; cleanup verified. |
| [Preparation](ctftiny-readiness-d105f3a4c344/check.json), [log](preparation.log) | Two fresh `pwn-baby-boi` cycles passed: staging, connection-only checks, isolation, reset and cleanup. Recorded settings exactly match the selected development experiment. No solving. |
| [Solver build](solver-build.log) | Updated worker image rebuilt locally. The guard and dependencies were unchanged. |

The reaping probe checks `/proc` for remaining direct children of the solver's
PID 1 before retrieving the completed result. The partial-input probe fills a
non-reading terminal and verifies accepted-byte reporting. The supervisor-loss
probe deliberately kills a command supervisor inside the solver and confirms
that the attempt stops as an infrastructure error. Final-output checks recover
the complete bounded file after repeated zero-wait polls. Earlier milestone
records are retained unchanged.

Reproduce from the repository root:

```sh
uv run --frozen python -m ctf_agent build-images
uv run --frozen python -m pytest -q
uv run --frozen python -m ctf_agent self-check
uv run --frozen python -m ctf_agent prepare-challenge --challenge pwn-baby-boi --experiment configs/development.toml
```

Remaining limits are unchanged: context is not compacted, pip cannot provide every
native dependency, and a hard stop can discard output since the last read/copy.
These checks establish environment behavior, not model performance. Review before
authorizing another live pilot.
