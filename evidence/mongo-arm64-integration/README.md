# MongoDB native-architecture and readiness integration

November 7, 2026. **Implemented and verified with zero model calls.** Normal
preparation and normal-lifecycle application checks pass two fresh cycles each.
The original pilot/diagnostic/evaluation evidence remains preserved. No live
retry, solver rebuild, dataset edit, endpoint expansion, commit or push.

## Exact compatibility adjustment

| Field | Supplied | ARM64 replacement |
| --- | --- | --- |
| MongoDB server | 7.0.9-jammy | 7.0.9-jammy |
| Architecture | AMD64 | ARM64/v8 |
| Image reference | `mongo:latest@sha256:7b88befc893008d7139ce3276c093b3efd435023af8bb76a9d79fa90be1eaeb6` | `mongo@sha256:8ff69162926750978451697274dc3c93eac609894b9cff7ed977e76e6bcabcbe` |

These are siblings in the **same official release index**, established in the
[independent evaluation](../mongo-arm64-evaluation/README.md). This is an
architecture substitution, not a version downgrade or new database build.

The existing trusted `target_compose` function applies it only for the exact
supplied image on `arm64`/`aarch64` Docker engines. It does not use the laptop's
Python architecture, so remote Docker engines select according to their own CPU.
AMD64 engines and every other reference stay supplied. No general image resolver,
new configuration file, dependency or override framework. `target.json` records
original/replacement image, platform, version and reason; existing provenance
records actual running image identities. Only the affected image is pulled when
missing through the existing pull path.

The dataset remains clean. Normal functional checks privately compared all
services' environment, command, entrypoint, dependencies, network memberships and
restart policy with the supplied Compose data; all agree. Application images and
frontend/backend boundaries are preserved. Solver access remains **port 80**.
Native architecture does not imply byte-for-byte CPU performance equivalence or
verification of every application operation.

## Readiness changes

Normal startup uses Compose's native `up --wait --wait-timeout 20` within the
existing 30-second Docker-client allowance. Its standard handling waits for running
services and supplied healthchecks. A small shared snapshot function checks
**all dependencies**, including when the frontend port is open. It records only
status/running/restarting, restart count, exit code, OOM and health status, omitting
environment values and healthcheck logs/commands. It rejects non-running,
restarting, OOM-killed and non-healthy declared-healthcheck states. Prior restart
counts alone do not reject a currently healthy service.

Startup checks are retained in `target.json` under `service_checks.startup`;
failed Compose startup captures `startup_failed` states before cleanup when
containers exist. Preparation repeats checks after its connection probes under
`after_probes`. No custom polling daemon or universal application-health framework.
Services without healthchecks still need application-specific investigation if
problems arise, and failures after these snapshots remain possible.

## Verification and honest retry record

- **111 offline cases passed**: exact-reference/architecture selection, preservation
  of service behavior, other Mongo versions unchanged, failed dependency detection,
  safe state records and healthy prior restarts. [Console](offline.log), [JUnit](offline.xml).
- **Two new Docker cases passed**: native Compose unhealthy-start failure and a
  dependency exiting after startup with the frontend still running. Failure states
  and cleanup were retained. [Initial controls](controls.log), [JUnit](controls.xml).
- The existing Compose DNS/backend scope/fresh-volume case initially hit an
  intermittent local Docker image lookup failure for `ctf590-fixture:m1`. The image
  was immediately confirmed present; both new cases used it successfully. Only
  that existing case was rerun and passed. [Preserved original failure](controls.log),
  [focused rerun](controls-retry.log), [JUnit](controls-retry.xml). No automatic
  application retry or Docker lookup workaround was added; the daemon anomaly
  remains a limitation. Thus three distinct targeted Docker cases passed, with
  one explicit test retry, not an unqualified clean first run.
- The **normal CLI** `prepare-challenge --challenge web-shreeramquest` passed both
  fresh cycles, selecting the exact ARM64 artifact without a temporary patch:
  [console](readiness.log), [complete readiness](readiness/ctftiny-readiness-d76593241d8a/check.json).
  File/private boundaries, dependency states, connect-and-close, denied traffic,
  fresh reset and cleanup passed.
- Two additional fresh **normal-lifecycle functional cycles** privately verified
  unchanged service semantics, Mongo version, benign registration/login/own-profile
  access, zero service restarts after 35 seconds, fresh database state and cleanup.
  An intentional port-4999 probe remained denied. No flag route or evaluator
  submission. [Results/local span paths](functional.json).

The other 33 previously passing Docker cases were not needlessly rerun; this
checkpoint changed only target selection/lifecycle and readiness. No solve-rate
comparison or live gateway/tracing claim is made.

[Machine-readable result/source hashes](result.json). [Prior source snapshots](baseline/challenge.py).
Runtime Compose snapshots remain private/Git-ignored. Historical tracked snapshots
still need separate publication cleanup; that work/history rewriting is outside
this checkpoint.

## Handoff

Normal challenge commands are unchanged; no manual Compose/dataset edits. README
explains the substitution and Docker Hub/VPN behavior. Review this checkpoint,
then separately authorize a single fresh development web attempt if desired.
The original failed pilot remains part of the record. Agent/prompt/model settings,
NYU solver, three tools, guard/evaluator and batch behavior are unchanged.
