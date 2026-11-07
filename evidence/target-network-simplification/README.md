# Target/network simplification checkpoint

Completed November 6, 2026. No live models, challenge solving, new hosted traces,
pilot or scored attempts. [Plan](../../docs/SIMPLIFICATION_PLAN.md).

## What changed

Reused supplied Compose service definitions and standard Docker project networks,
DNS, volume lifecycle and routes. Retained existing `nyuctf==1.1.1` loading,
private evaluator, guard/denial collector, agent/tools, model integration, native
Langfuse SDK export, complete configuration and batch workflow.

Removed blanket target DNS/capability/tmpfs/log/resource overrides, backend network
reconstruction, the separate egress bridge, manual default-route replacement,
gateway arguments and rewriting of public hostnames to IPs. The guard now directly
joins the challenge-facing bridge. Supplied backend membership is preserved.

Small custom integration remains for private loading, image identities, bounded
startup/teardown and exposure/freshness checks. Adjustment records identify removed
host ports, shared Docker sockets, build directives and global container names.
Shared resource names become fresh Compose project names. Read-only server binds
must stay inside the challenge directory; writable host binds and external/custom
volumes need an explicit reset strategy and fail clearly. No storage-copy,
nested-engine, proxy or other new subsystem was added.

Targets regain supplied/default capabilities, resource policy and normal network
connectivity. The imposed 256 MiB/CPU/PID/tmpfs/permission policy is gone; solver
limits and scope controls remain unchanged. Runtime Python decreases from
1,575 to 1,561 lines (14 fewer). The main reduction is mechanisms and assumptions,
not line count; narrow mount/admin checks and adjustment records add some code.

## Verification

- [100 offline tests](fast-tests.xml) passed: supplied behavior preservation,
  private evaluator/model boundaries, narrow exposure/freshness errors, tracing,
  restart races, complete configuration, SDK export and batch behavior.
- [29 synthetic Docker cases](self-check-3e6b42142c52/suite.json) passed in one
  complete run, with cleanup verified. A two-service fixture exercised frontend/
  backend DNS, permitted frontend access, denied direct backend access, within-
  trial volume persistence and fresh volume state across two trials. Existing
  scope, guard loss, pip, restart, limits, isolation/submission and cleanup checks
  passed on the ordinary bridge topology.
- Two fresh zero-model preparation cycles each passed for
  [pwn-baby-boi](ctftiny-readiness-7091ee45a82b/check.json),
  [web-shreeramquest](ctftiny-readiness-7ecca9139403/check.json) and
  [cry-ecxor](ctftiny-readiness-e761b06f78d3/check.json).
  These checked service/file-only setup, real files/ownership/hashes, supplied
  hostname resolution, permitted TCP connect-and-close, private boundaries,
  independent denied traffic and cleanup. No real target response contents were
  read. Six cycles are preparation evidence, not solving results.
- [Infrastructure-only inventory](compose-inventory.json) inspected all 27
  supplied definitions: 26 pass policy; privileged `msc-showdown` remains
  unsupported. Seventeen socket omissions are recorded. No non-socket host binds
  are declared. This is configuration coverage, not runtime proof for all 26.
- [Final verification](verification.json) matches final source hashes against the
  complete Docker suite and confirms unchanged settings, agent/model code and
  solver image. All three preparations used the same solver/guard identities.
  SDK version/export is unchanged and checked offline; no new hosted readback ran.

Reproduce sequentially from the repository root:

```sh
uv run --frozen python -m ctf_agent build-images
uv run --frozen python -m pytest -q
uv run --frozen python -m ctf_agent self-check
uv run --frozen python -m ctf_agent prepare-challenge --challenge pwn-baby-boi
uv run --frozen python -m ctf_agent prepare-challenge --challenge web-shreeramquest
uv run --frozen python -m ctf_agent prepare-challenge --challenge cry-ecxor
```

## Limits, failed checks and preservation

Two initial synthetic read-only bind tests failed because Docker Desktop rejected
the source path, first under macOS temporary storage and then under the repository.
Their XML/runtime records remain in `compose.xml`/`compose-check` and
`compose-shared.xml`/`compose-shared`. No file-sharing setting or transfer workaround
was introduced. Read-only bind preservation/path validation has offline coverage
only; this environment has **no passing runtime bind test**. A teammate using
server-file binds must configure Docker host sharing. The subsequent named-volume
test passed ([focused result](compose-volumes.xml)), then the full suite passed.

Shared-daemon sockets remain removed because they expose trusted resources.
Successful preparation without them does not prove every intended challenge
operation works; a demonstrated socket requirement needs a separate isolation
decision. Privileged targets, shared-namespace arrangements and external/writable
host state requiring reset fail explicitly rather than silently widening access.

[Baseline identities](baseline.json) capture the previous execution checkpoint's
uncommitted source hashes/settings/images; commit `64f6385` remains the reproducible
pre-simplification source baseline. The old guard image is retained locally as
`ctf590-guard:before-target-network`. Original execution evidence and historical
failures remain unchanged. This checkpoint was not committed or pushed.

Supplied-image evaluation remains independent and has not been performed. Stop
for review before that checkpoint or a separately authorized live pilot. No solve-
rate improvement or compatibility with every challenge is claimed.
