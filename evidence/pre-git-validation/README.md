# Validation before Git checkpoint

November 7, 2026. **Current local runtime validation passed.** No agent/prompt,
model/settings, solver recipe, dependency or application-code changes during this
validation. Two private historical deployment snapshots were backed up locally
and redacted in the working tree. No commit, push or history rewrite.

## Checks

| Check | Result |
| --- | --- |
| Offline suite | **111 passed** |
| Full synthetic Docker suite | **36 passed**, first run, cleanup verified |
| Final-code readiness | **11 environments / 22 fresh cycles passed** |
| Fresh web development attempt | **Evaluator-verified success**, 4 requests / 4 tools |

The full Docker suite covers isolation/evaluator boundaries, network denial,
resource/deadline controls, command restart recovery, fresh files/packages/storage,
Compose backend scope, failed-dependency handling and the additional NYU toolkit.
No test retry was needed in this validation. Earlier fixture lookup failures remain
in prior evidence and are not erased by this passing run.

[Offline console](offline.log), [offline JUnit](offline.xml),
[Docker console](docker.log), [full suite/provenance](docker/self-check-28f11af45de5/suite.json).
[Readiness summary](readiness-summary.json) and [per-environment index](readiness-index.json)
cover all ten reserved IDs plus development `web-shreeramquest`. Each had two fresh
cycles, safe dependency checks before/after probes, private/file boundaries,
connect-and-close, denied traffic, reset and cleanup. Zero model calls or solving
on the reserved set. This is not an application-health/solvability guarantee for
all fifty challenges; the known unsupported privileged target remains unchanged.

## Fresh web attempt

The user confirmed VPN readiness, then asked to test first and leave detailed
trace review for later. The unchanged normal launcher ran a **new** development
attempt with fresh target/database/solver state; it does not replace the original
scope-stopped pilot. No additional guidance or expected answer was supplied.

- Run: `d4bfacba6825`, challenge `web-shreeramquest`.
- Outcome: **success**, trusted evaluator confirmed.
- **4 model requests / 4 tools**, active **14.879s**, complete launch/export **27.184s**.
- 9,357 input / 738 output tokens; cached input 4,993; reasoning 145 is already
  included in output. Estimated configured-rate cost **$0.00085533**.
- Automatic native export/privacy/parentage and cleanup audits passed. No scope
  stop or cleanup error. No manual model/tool conversation inspection performed.

[Result](web-result.json), [run/provenance](web-attempt/run.json),
[summary](web-attempt/summary.json), [console](web-attempt.log),
[Langfuse trace](https://us.cloud.langfuse.com/project/cmw17lafc0745ad0eekgn9a7j/traces/d4ca17944c907b5c3fec70d02344a01e).
The native JSON export remains at the Git-ignored path recorded in `web-result.json`
for later user review. This single attempt validates the live path after the target
fix; it is not a measured solve-rate improvement or completed evaluation.

## Publication audit and redaction

A read-only scan of 2,264 candidate files found **no matches for current host
account secrets**, but identified two tracked deployment snapshots containing
private challenge environment data. [Original audit](publication-audit.json).
Exact originals were copied under Git-ignored `runs/private-evidence-backup/`
with byte/hash verification; only private environment fields in the tracked public
copies became `[REDACTED]`. [Redaction manifest](redactions.json) preserves paths,
original/redacted hashes and field names without private values.

[Post-redaction audit](publication-after-redaction.json) confirms those current
fields are redacted. **Two historical committed file versions still contain private
deployment data.** Current redaction does not remove Git history; it was not
rewritten or pushed. Review how the repository will be shared before a public push.
The history finding concerns challenge deployment data; no current host API-key
matches were found. Do not publish the preserved private originals.

## Review and next step

The working tree is still uncommitted. [Plan/source hashes](plan.json) identify
what ran; originals and previous failures remain. Runtime checks support saving
this code checkpoint and returning to agent-focused testing. Resolve the separate
history/publication decision before public distribution. No scored attempts,
manual trace analysis, additional model run or Git operation is included.
