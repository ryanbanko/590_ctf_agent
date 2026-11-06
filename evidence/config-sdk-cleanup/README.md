# Configuration, SDK export and package snapshots

Approved November 5, 2026. This maintenance milestone completes three changes:

- Normal model/run values live in the complete `configs/development.toml`.
  `config.py` validates without merging fallback dictionaries. The old
  `configs/initial.toml` is removed. One `max_model_turns` value feeds both the
  runner and adapter guards. Copy the complete TOML for another experiment.
- The installed Langfuse 5.1.0 client replaces the normal launcher's pinned CLI
  subprocess. `observations.json` contains all cursor pages; the existing
  completion, parentage, credential, answer-boundary and cleanup audits remain.
  Normal runs no longer require Node/npm. Old exports remain unchanged.
- Package inventories still scan at startup and after tool calls, detecting
  changes from any command. `packages.json` is written on the first scan and only
  when its contents change. Output copying is unchanged.

No dependency, image source, tool, prompt, normal numeric profile or network-policy
change is part of this milestone. Context management, GDB and output-copy
optimization remain deferred. No model requests, new hosted traces, real challenge
attempts or scoring ran. Model API spending was $0.

## Verification

[Final index](verification.json) records source/configuration hashes, image IDs,
pinned versions, unchanged resolved settings and cleanup. The Docker suite used
the same source hashes as this final index.

| Evidence | Result |
| --- | --- |
| [Before](before-settings.json), [after](resolved-settings.json) | Resolved normal attempt/model values are exactly equal, including the adapter's derived request limit. |
| [Package writes](package-write-check.xml) | First and changed inventories write; a repeated inventory does not; private package metadata stays out of tool results. |
| [Configuration checks](config-checks.xml) | 54 focused tests passed. Complete fields are required; duplicate `max_requests` is rejected; both call guards use one value. |
| [SDK checks](sdk-checks.xml) | Eight focused tests passed, including more than 100 observations, an empty page with continuation, delayed completion and bounded timeout. |
| [Fast suite](fast-tests.xml) | All 95 tests passed with real SDKs and substituted Docker/model transports. |
| [Docker suite](self-check-d3fc4ce033dd/suite.json), [JUnit](self-check-d3fc4ce033dd/pytest.xml), [log](controls.log) | All 31 synthetic cases passed in one complete run using the consolidated normal profile. Cleanup verified. |
| [Hosted readback](hosted-readback/verification.json) | Ten observations from the existing benign trace matched both the historical export and fresh official CLI readback, including IDs, parentage, inputs, outputs, metadata, model, usage and cost. Secret credentials were absent. |

[SDK observations](hosted-readback/observations.json) and the independent
[CLI verification](hosted-readback/cli-verification.json) preserve the readback.
The source trace is the previously approved synthetic model setup check, not a
new attempt or held-out challenge. The SDK test client had tracing disabled.
The CLI was used for independent verification only, not restored as an application
dependency. Cursor-page behavior is checked offline; the hosted trace has ten rows.

The earlier [configuration check](config-first.xml) exposed a test's hardcoded
61-second expired clock after synthetic tests moved to the normal 600-second
profile. The test now derives its expired clock from the selected profile; the
corrected checks passed. Both initial Docker startup records and logs are retained:
[first](self-check-ed3e30641b94/suite.json),
[second](self-check-30246225a47d/suite.json),
[first log](controls-startup-1.log), [second log](controls-startup-2.log).
They stopped before tests because image names failed inspection, although Docker
listed their tags and could inspect the image IDs. Reapplying those same tags to
the existing IDs restored lookup; no image rebuild or source change was needed.

Reproduce normal local checks from the repository root:

```sh
uv run --frozen python -m pytest -q
uv run --frozen python -m ctf_agent self-check
```

Hosted export needs the usual host-only `.env` credentials. The comparison used
`read_model_trace` with the existing trace's start-time window and an official CLI
query of the same observations field groups. It did not invoke `model-check`.
These checks establish maintenance behavior and record compatibility, not an
improvement in benchmark performance. Review before another live pilot.
