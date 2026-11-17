# Manual HTB fallback — November 16, 2026

Authorized milestone: create a feature branch and implement the manual fallback
with offline verification. Branch `feat/htb-manual` started from clean main.
No commit/push, real challenge attempt, model spending, Docker/VPN operation or
hosted mutation was performed. MCP implementation and live checks remain later
milestones. Existing experiment/scored records were not changed.

## Implemented behavior

- `setup-manual` prompts for public description, name/category, downloaded ZIP/
  folder and explicitly assigned IPv4 TCP/UDP endpoints. It saves a reusable
  public task, copied handouts and a list of withheld paths under Git-ignored runs.
- Imports are bounded and validate paths, file types, duplicates and sizes.
  Python's standard ZIP reader supports the documented `hackthebox` password;
  unsupported formats require an extracted folder. Imported content is not
  executed on the host. Known private/build/credential paths stay out of the solver;
  this is not general secret-content detection.
- `run-manual` shares CTFTiny's agent, tools, isolated solver, guard and model/
  Langfuse integration. Remote target spawning/reset/expiry is operator-managed;
  the launcher owns only the local bridge/guard/solver.
- Trusted flag verification can use either a private local answer or a callback.
  Manual verification binds the challenge/candidate and accepts y/n/cancel/error.
  No HTB token or local answer key is needed for the manual mode. Human-relayed
  acceptance is explicitly distinguished from automated HTB verification.
- Pending/final submission records preserve IDs, exact candidate, source and UTC
  timestamps locally and keep candidate/verdict in the existing tool span. The
  root summary does not receive the candidate or a private answer. Both modes
  receive submission records; raw records are Git-ignored.
- Input polling, the existing watchdog, and post-verification checks preserve the
  original attempt deadline. Human waiting counts. Invalid input reprompts;
  cancellation, EOF, Ctrl-C, unavailable verification and late verdicts cannot
  manufacture success. An interrupted process may leave a pending submission,
  rather than a fabricated final verdict.
- `configs/htb-manual.toml` raises the HTB profile to wall_seconds=1800,
  max_model_turns=100 (adapter max_requests=100) and max_tool_calls=120.
  CTFTiny development limits remain unchanged. Larger allowances are not evidence
  of better performance or a guarantee of staying within a dollar budget.

## Verification

The final command was:

```sh
.venv/bin/python -m pytest -q --junitxml=evidence/htb-manual/offline-tests.xml
```

**204 passed, 49 Docker cases deselected, 2.10 seconds.** See the retained
[JUnit record](offline-tests.xml) and [checks/provenance](checks.json).

Coverage includes ZIP/folder roundtrip, encrypted synthetic ZIP, unsafe paths,
symlinks/special files, duplicate/oversized imports, task schema/file/endpoint
validation, cancelled setup, partial pipe input/deadline, accepted/rejected/invalid
input, cancellation/EOF/Ctrl-C, verification unavailable, late acceptance and
non-boolean verifier output, durable submissions, bridge cleanup failure and
separate configuration limits. A real subprocess CLI setup check removes
credentials and Docker from PATH. Existing CTFTiny controller/agent/model/export
tests remain in the full suite.

The manual trace integration check uses the actual pinned OpenAI/Langfuse SDKs,
local HTTP response transport and in-memory span exporter. It verifies a model
generation, parent-linked submit_flag tool with candidate/verdict, native
usage accounting, root answer separation and ordinary export/completeness logic
through a substituted observation-read API. Trace URLs and Docker are substituted.
The synthetic accepted candidate is not evidence of a real HTB solve.

Earlier checks, retained as part of the verification history:

1. Initial focused suite: **93 passed**.
2. First broad suite: **201 passed, one failed, 49 deselected**. The newly added
   trace-export test had not substituted `Langfuse.get_trace_url`, whose project
   lookup produced ConnectError before the export callback. There was no working
   hosted connection or mutation; run.json retained that error. Corrected the
   offline test substitution and supplied the sandbox_cleanup event required by
   the standard export check. No runtime export behavior was weakened to pass.
3. Corrected manual suite: **33 passed**. Two additional integration checks then
   covered bridge cleanup failure and the actual CLI setup path; the final broad
   suite above contains them.

CLI help and whitespace checks passed. Baseline identity checks cover the agent,
tools, default settings, guard/sandbox, Docker files, dependencies and dataset
selection; detailed hashes are in checks.json. No raw benchmark flag, solution,
private target build file or recorded model command was consulted or replayed.
The first provenance inventory mistakenly included ignored Python cache files;
the corrected inventory uses tracked Docker files and passed. This did not
change runtime source or historical evidence.

## Remaining limits and next step

This is offline verification. The inherited Docker controls, actual target
reachability under Duke VPN, remote HTB verdicts, gateway/model access, hosted
Langfuse ingestion/readback and MCP are not newly verified here. The local span
substitute is not proof of hosted payload completeness. ZIP formats unsupported
by Python need local extraction; only IPv4 endpoints are supported. Remote
instance state is not reset by a fresh local attempt, and saved endpoints must
be updated after respawn. Input polling targets Linux/macOS hosts.

Stop for user review. Next proposed milestone: an authorized Docker-to-assigned-
endpoint readiness check, followed by one bounded ordinary Try Out attempt with
manual submission and actual hosted trace readback. The user will need to supply
the public challenge description/handouts/current endpoint and have Duke network
access ready. Credentials stay in the existing local environment, not chat or
the solver. MCP can later supply the same task and trusted verification callback.
