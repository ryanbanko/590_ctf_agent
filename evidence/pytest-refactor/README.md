# Pytest and tool cleanup verification

November 3, 2026 (America/New_York).

**6 fast contract tests and all 17 synthetic container checks passed.**
No model calls, real CTFTiny attempts, development pilots, or scored runs occurred.

## Changes verified

- Public `call_tool()` validates host-side arguments once; the internal dispatcher
  executes validated arguments. Worker-side path/symlink protections remain intact.
- The three handwritten tool schemas use readable formatting and a single lookup
  built at import time. Their input contracts did not change.
- Attempt dispatch uses local names for settings, sandbox, and trace while retaining
  fresh deadline checks around blocking operations.
- Pytest 9.2.0 is pinned in the development dependency group, with transitive
  dependencies locked in `uv.lock`. Application runtime dependencies remain empty.
- Standard pytest discovery, exception assertions, temporary paths, shared target/
  attempt fixtures, and parameterized probes replace custom test discovery and the
  three custom case-running loops. No custom application classes or pytest plugins
  were introduced.
- `self-check` remains a small launcher: save provenance, invoke pytest, translate
  its standard JUnit result properties into the existing suite-summary shape, and
  verify cleanup. Per-attempt JSONL traces and summary fields remain unchanged.

## Reproduce

```sh
uv sync --frozen
uv run python -m pytest -q
uv run python -m ctf_agent build-images
uv run python -m ctf_agent self-check
```

The default pytest selection runs six fast tests and deselects all 17 Docker cases.
`self-check` explicitly selects the `docker` marker and stops on the first failure,
as the previous custom runner did. No external pytest plugins are loaded by the
self-check launcher. Images were rebuilt from the unchanged, cached Dockerfiles.

## Retained records

- [Fast-test JUnit report](pytest-fast.xml): six passed, zero failures/errors/skips.
- [Suite record](self-check-b703cc48de95/suite.json): 17 passed, pytest exit code 0,
  cleanup verified, complete configuration, source hashes, and image provenance.
- [Container-check JUnit report](self-check-b703cc48de95/pytest.xml): standard pytest
  test outcomes, with check-name and run-ID properties.
- Each run-ID directory contains its complete `trace.jsonl` and `summary.json`.

Pytest reported **44.05 seconds** for its container tests; the encompassing launcher
recorded **44.393378 seconds**, including provenance/report/cleanup checks. These
are setup timings and do not establish an agent-performance improvement.

Post-run checks confirmed:

1. Exactly the same 17 check identities as the previous refactor suite.
2. Current source SHA-256 values match the tested files.
3. Sandbox/Docker helpers, configuration, tracing, Dockerfiles, and container
   worker/firewall sources have identical hashes to the previous suite.
4. Every executed tool has exactly one matching `tool_returned` event.
5. All six prohibited IPv4 probes retain independent NFLOG packet-denial evidence.
6. The suite and an independent final query found no project containers/networks.

Earlier evidence remains unchanged. Actual AMD64 execution, adaptive model behavior,
gateway compatibility/pricing, CTFTiny integration, and later assignment stages
remain unverified or pending. The next proposed milestone is `agent.py`, after
review of this refactor.
