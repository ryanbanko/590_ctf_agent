# Infrastructure simplification proposal

Recorded November 5, 2026. **Not implemented; pending implementation approval.**
This is a review plan, not a description of current runtime behavior. Current
commands and contracts remain in [README](../README.md) and [DESIGN](DESIGN.md).

Keep our agent, three tools (`run_command`, `write_file`, `submit_flag`), prompt
strategy, model integration, Langfuse and sequential batch wrapper. Keep unrelated
agent-message conversion, text-only termination, context and GDB changes separate.
Only update descriptions necessary to reflect changed infrastructure contracts.

The [assignment](../ASSIGNMENT.md) requires solver/evaluator separation, private
answers, trusted submissions, enforced limits, scope/incident evidence and fair
fresh trials. The [professor's clarification](REFERENCES.md#authority-and-professor-clarification)
permits dependency downloads. It does not mandate our filesystem, session,
target-hardening or network topology choices. Package-only internet purpose is
an instruction and trace-review policy, not an airtight firewall guarantee.

## Reuse and implementation accounting

**Supplied** means NYU code/components; **standard** means Docker or Python
facilities; **existing custom** means our code, not functionality NYU provides.
New wrappers remain custom code even when they use standard libraries.

### Image evaluation is independent

| Current implementation | Proposed replacement | New work required | Custom code removed | What enables removal / loss |
| --- | --- | --- | --- | --- |
| Custom solver image/toolkit coupled to worker startup and Python paths | Evaluate the supplied NYU baseline image from release `20250206`, commit `112cfa33f5c0a06a20e49af525ac8eb07ec98457`, using standard Docker builds | Clean AMD64 build and basic utility/Python/pip checks. Compare total setup burden; no adoption of its host framework or Ghidra setup | Worker-specific image startup disappears whichever image wins. Our toolkit lists disappear only if the supplied image is selected | Runtime needs a shell and Python rather than our worker environment. A failing supplied build must not force a compatibility framework |
| Locally built images and existing provenance | Selected image frozen by identity and archived/distributed, with source revision and package inventory | Small packaging/documentation task, not an image-management subsystem | Avoid maintaining multiple supported image paths after selection | A Dockerfile with floating downloads is not by itself a reproducible evaluation artifact |

The supplied image was inspected as source, **not built**. Its default entrypoint
starts an HTTP server that this runtime does not need; a standard idle command can
replace that startup. If its installers require substantial repair, a conventional
lean image may be less work to maintain. Execution replacement can be developed
and verified against either candidate; image selection must not block it.

### Writable filesystem and ordinary execution form one change

| Current implementation | Proposed replacement | New work required | Custom code removed | What enables removal / loss |
| --- | --- | --- | --- | --- |
| Read-only root, workspace tmpfs, special home/temp arrangement, startup venv | Standard writable disposable solver with an image-prepared writable Python environment | Small Docker/image integration for user, working directory, home and PATH | Startup environment creation, mount-specific accommodations and workspace free-space protocol | Writable storage handles files/caches/installations normally. The portable workspace-size quota is lost |
| Validated archive construction/transfer/extraction in `stage_files()` | Standard `docker cp` plus existing contestant selection, size/hash records | Small checked copy wrapper: parent directories, ownership and executable modes | Tar construction, streaming and extraction workaround | Revised filesystem allows ordinary copying; verify the original failure is resolved |
| Persistent worker, socket protocol, sessions, PTYs and supervisors | Standard `docker exec` with a bounded host-side wrapper | New/reworked execution helper, not a daemon: fixed Docker argument lists, non-root solver execution, deadlines and bounded capture | `docker/worker.py` as a service; host RPC path; session registry, polling/input state and per-command subreapers | Cross-call sessions and per-command descendant-cleanup guarantees are deliberately removed |
| Recovery using command process-tree cleanup | Standard restart of the same writable solver, coordinated by existing trusted runner code | Small lifecycle integration with deadline/scope checks and terminal-stop coordination | Avoids reintroducing process-tree discovery, supervisors or cleanup-confirmation protocol | All solver processes/connections reset; files and pip installations survive. Targets and guard remain running |
| Structured writer inside worker | Existing custom filesystem writer adapted to a one-shot Python invocation inside solver | Small wrapper carrying path/content as stdin data; retain size/path/symlink protections | Worker dispatch/RPC around file writing | File writing does not require a resident service; the tool interface is retained |
| Head/tail capture plus saved output IDs, artifact RPC and automatic copying | Existing capture ideas adapted to standard Python stream reading and direct trace results | One bounded reader that drains stdout/stderr and retains beginning/end excerpts | Output-ID management, artifact requests, base64 transfers and repeated file copies | No accumulating session output. Automatic retrieval of omitted output is lost |

**Proposed restart contract:** capture partial output, reset the solver and return
an explicit timeout/process-reset observation. The model chooses the next action;
there is no automatic command retry. Ordinary nonzero program exits remain tool
observations and do not trigger restart.

The run ID, counters and overall deadline do not reset. Do not rely on `--rm`:
retain the same container for recovery and explicitly remove it at final cleanup.
Serialize recovery with terminal lifecycle operations and recheck deadline/guard
health. Scope violations, guard failure and the whole-attempt deadline never
recover. Terminal removal must win over an in-flight restart. Unconfirmed or
failed recovery ends the attempt.

This relies on replacing tmpfs: current workspace contents disappear on restart.
It preserves disk state, not in-memory program state or open connections. Background
processes can survive ordinary command exit until restart/final cleanup; the new
contract must not claim per-command descendant cleanup. Docker's ordinary init
support can handle zombie reaping without our supervisors.

Memory/CPU/PID, wall-clock, model-call, command, output and write limits remain.
A normal writable layer does not automatically preserve the current 512 MiB
workspace quota. Keeping a portable hard disk cap would require a storage
mechanism; the proposed simpler layout explicitly gives up that cap.

### Supplied target behavior and simpler networking

| Current implementation | Proposed replacement | New work required | Custom code removed | What enables removal / loss |
| --- | --- | --- | --- | --- |
| Broad `target_compose()` normalization/hardening | Supplied service definitions and standard Compose lifecycle, with reduced existing orchestration | Checked startup/teardown, narrow exposure checks, readiness and actual image/container records | Forced target DNS, capabilities, temporary storage and resource policy; broad field/mount rejection; unnecessary hostname replacement | Preserve supplied operating assumptions instead of imposing a uniform target environment |
| Socket removal and rejection of other declared mounts | Preserve ordinary mounts; document justified socket exceptions | Audit generic dependencies and existing evidence. Apply narrowly verified exceptions, not silent dependency deletion | Blanket rejection of Docker-managed volumes and legitimate server-side file mounts | Target mounts are distinct from passing private files to the solver |
| Network reconstruction, egress bridge, manual routing and gateway plumbing | Standard supplied networking plus existing custom guard/denial monitoring | Adapt attachment/routing and verify hostnames, connectivity and enforcement | Extra bridge lifecycle, backend reconstruction, route replacement and obsolete gateway arguments, where the simpler topology verifies | Docker supplies connectivity; the guard supplies scope enforcement. Neither guard nor its monitor is NYU-supplied |
| Reset and cleanup verification | Standard Compose recreation/teardown plus existing checks | Verify actual mounted state. External volumes and writable binds need an explicit reset strategy if present | Redundant network-reset bookkeeping | Fresh state is required; freshly invented networks are not. Never delete unrelated external storage automatically |

The read-only inventory resolved **27** supplied Compose definitions successfully;
**17** contain actual socket mounts and **one** requests privileged operation.
Two of the four reserved service-backed IDs have socket mounts. Under our current
Docker Desktop deployment those host-socket binds would expose the same engine
managing trusted resources, not a private challenge engine.

Existing local user-run records establish verified success without any target
mounts for `cry-describeme` and `web-poem-collection`. Other preparation evidence
establishes startup/connectivity only. Neither observation proves all sockets are
unnecessary. The review inspected configuration and existing result metadata,
not evaluation flags, solutions or write-ups.

A confirmed need for Docker administration requires a separately isolated
challenge engine. **That would be a new subsystem and is outside the base plan**
unless a demonstrated requirement justifies it. A read-only bind of the shared
socket does not make Docker API operations read-only. Record unsupported cases
instead of claiming unchanged challenge compatibility.

### Keep agent interfaces and useful records

| Current implementation | Proposed replacement | New work required | Custom code removed | What enables removal / loss |
| --- | --- | --- | --- | --- |
| Agent, prompt strategy, model adapter, native history | Existing project code | Update accurate environment/tool descriptions and result handling only | Session schema/descriptions; no unrelated message-format or stopping-policy rewrite | Infrastructure remains behind the three tools |
| `nyuctf` loading, revision/split checks, public-task construction, trusted evaluator | Supplied package plus existing custom integration | Adapt changed infrastructure arguments; preserve privacy checks | Unused parameters only | Package objects/answer key remain trusted; commands execute only inside solver |
| Langfuse integration/export and result/config/source/image provenance | Existing custom integration and installed SDKs | Record restart events, active configuration, explicit truncation and unavailable snapshots | Worker/artifact-specific metadata | Useful experiment records do not require worker RPC |
| Package scanning after every tool call | Image inventory, traced installation activity, optional final snapshot | Small environment-agnostic snapshot integration | Repeated scans, hardcoded Python inventory paths and snapshot comparison logic | Exact per-action inventories are given up. Final snapshot can be unavailable after hard stop; say so |
| Sequential batch wrapper | Existing 78-line custom function using normal subprocesses | Update timeout/recovery outcomes and remove stale classifications | Obsolete outcomes, not the wrapper/index | Retains settings snapshot, fresh processes, interruption handling, missing-record checks and partial progress without another scheduler |

The tool observation saved in Langfuse must match what the model received.
Explicit truncation is not a claim that all command output was retained. No new
tracing backend, provider registry, message compatibility layer or retry system
is proposed. Failed attempts remain part of the results.

## Implementation and verification sequence

1. Preserve baseline source/configuration/evidence. Evaluate the supplied image
   independently; select and freeze the lower-maintenance working option.
2. Replace filesystem/execution together. Verify copying, executable modes,
   writable home, pip installs and one-shot writing. Remove worker mechanisms
   rather than keeping a dormant fallback path.
3. Narrow target policy and simplify networking. Verify socket exceptions,
   supplied hostname/service relationships, permitted and blocked traffic, guard
   integrity and fresh storage, including a multi-service case.
4. Finish contracts, settings, tests, documentation and records. Run offline model
   transports, synthetic Docker controls and zero-solving preparation for intended
   environments; review before a separately authorized live pilot/comparison.

Required regression coverage includes wrong/correct submissions without separately
revealing the expected answer; success stopping later actions; no host mounts,
credentials, private metadata or socket in solver; detached children disappearing
on restart while files/installations survive; subsequent command execution;
restart racing with deadline, scope failure, guard loss and interruption;
large output with late errors; setup/cleanup failure records; fresh solver/target
state between attempts; complete hosted trace readback and batch interruption/
incident behavior. Record the disk-cap loss rather than silently passing old quota
tests. An image smoke test does not establish all challenge compatibility or solve
performance.

Remove obsolete session/PTY/worker/supervisor/artifact tests and stale worker
settings/constants. Replace them with the new behavior/boundary tests. Remove
`workspace_mb` only with the explicit quota change; retain active resource and
model limits. Fix obsolete `model_usage_missing` handling if it is no longer emitted.
Do not preserve old test counts as a target. Keep all historical evidence intact.

Update README commands/contracts, DESIGN's implemented decisions, PROJECT_STATUS,
EXPERIMENTS hypotheses/results, references/attribution and new verification evidence.
No benchmark improvement is claimed from synthetic infrastructure checks.

## Expected reduction

The 354-line worker service disappears, but small writer/output algorithms survive
in simpler locations. Additional removal comes from host RPC/artifact handling,
archive staging, session schemas, topology management and obsolete tests. Net
line-count reduction cannot be claimed before implementation.

The intended mechanism reduction is concrete: no persistent command daemon,
Unix-socket RPC, session state machine, per-command Linux supervision, custom
archive transfer or automatic artifact transport. A bounded execution helper,
one-shot writer, restart coordination, existing guard, evaluator and experiment
records remain custom code. No new persistent subsystem is included in the base
plan; neither `challenge.py` nor `sandbox.py` is expected to disappear wholesale.
