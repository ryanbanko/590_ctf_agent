# Original resources and design context

These are the five technical resources the user supplied at the start of this
project. They informed the design and should be reviewed when working on the
corresponding integration. Findings below describe the November 3, 2026 review;
verify current package/API details when implementing them.

Current completion status is tracked in the
[assignment checklist](../PROJECT_STATUS.md#assignment-checklist). The initial
review and milestone notes below preserve their historical context; the historical
[shared-launcher preparation](#shared-ctftiny-launcher-and-selected-ten-preparation)
verified the ten reserved CTFTiny challenges plus the development example. Current
execution/target checkpoints and the November 6 professor confirmations appear
below and in PROJECT_STATUS.

## Authority and professor clarification

[ASSIGNMENT.md](../ASSIGNMENT.md) preserves the original assignment and is the
original source for course requirements. Read it alongside the later course guide
and specific instructor clarifications recorded here; keep those sources distinct.
The user's initial approach was
tentative; examples, defaults, dependencies, prompts, and permissions in external
resources are not additional requirements or automatically approved choices.

The user asked the professor whether the referenced Implementation Guide meant
the CTFTiny and NYU CTF Bench documentation rather than a separate class guide.
The professor replied, as reported by the user:

> Thanks. Yeah it is basically the implementation guide there.

On November 4, 2026, the user reported a further professor clarification about
runtime package downloads:

> Yes. The intention of that statement is more along the lines of you don’t want
> the agent looking up the ctf tiny answers and submitting them. But access to
> download packages is perfectly acceptable

This authorizes package-download access; the prohibition on looking up benchmark
answers remains. The user prefers a simple implementation rather than airtight
package-only filtering. The approved implementation uses public HTTPS egress and
Docker DNS needed by pip, clear model instructions and trace review, preserving solver
isolation, private-data boundaries and hard limits. Internet connectivity is
technically available to tools generally; command-name-only enforcement is not
claimed. See the current design and [usability evidence](../evidence/agent-usability/README.md)
for verification. Preserve this clarification alongside the original assignment; it is not a request to rewrite that source.

Use the resources below as that setup/operation guidance while checking them
against the assignment, especially its solver/evaluator and access boundaries.

## November 8 blocked-connection recovery — user direction

The original assignment says to stop if an action reaches outside the permitted
environment and to retain/analyze blocked requests. The user explicitly selected
the interpretation that a connection prevented by enforcement can receive a
corrective response and continue in scope. This is user direction, not an explicit
professor confirmation or a change to the original assignment wording.

The approved implementation allows at most one confirmed blocked-command recovery
per attempt, preserving the firewall, exact target endpoints, incident evidence,
original deadlines/counters and terminal behavior for repeat incidents, failed
guard/audits, failed recovery and detections outside active commands. It resets
solver processes before returning feedback; actual out-of-scope access is not
authorized. The earlier scope-stopped experiment remains recorded under its
original policy. No professor email is reinterpreted as granting this behavior.

## November 6 course guide and professor confirmations

The user supplied the seven-page PDF **Assignment 4 mplementation Guide.pdf**,
headed *Appendix A Implementation Guide*. The original file remains with the user;
its external Downloads path is not a teammate setup dependency. The professor's
announcement said the guide draws on the CTFTiny/CTFBench GitHub repositories.
The PDF references a separately released `course-compose.yaml`, private verifier
and helper scripts; those references alone did not establish their availability.

The user asked about three concrete differences. The professor replied, as
reported by the user on November 6:

> 1. Using the challenge repository’s compose files and checking flags privately in your controller is fine. I had originally intended to provide a subset of the dataset, but that hasn’t been created yet.
> 2. JSON trace exports from Langfuse are fine.
> 3. Your approach of developing on separate CTFTiny challenges and holding ten out for evaluation works.

These specific confirmations settle our implementation choices:

- Keep repository target Compose files and trusted controller verification. No
  separate course configuration/verifier is a prerequisite to continuing.
- Keep native Langfuse JSON exports; JSONL conversion is not required for compliance.
- Keep the recorded CTFTiny development/held-out split. No NYU development-dataset
  migration or replacement selection is required. Existing development exposure
  stays recorded; the ten held-out IDs remain protected.

Approval of the approach is not proof of every challenge's compatibility or of
our individual socket/mount exceptions. Scope enforcement, limits, private-data
boundaries, fresh trials and complete records still need actual verification.
Pip approval above remains in effect. No helper-kit API or download is assumed;
available helpers can be evaluated later without blocking infrastructure work.

### Evaluation guidance stated in the PDF

The following are guide statements, **not additional confirmations in that email**:

- Pages 1/5: one fixed configuration and three fresh attempts per selected challenge;
  no second full evaluation or mandatory five-challenge/paired pilot.
- Page 6: per-challenge success percentage, sample SD in percentage points using
  denominator `3 - 1`, mean input/output/total tokens and launch-to-termination time.
  Include failures and keep unavailable usage null; incomplete/incident results
  must not be silently replaced or omitted.
- Page 7: trace-supported improvement with small follow-up checks, a 1–3 page
  writeup and an identified autonomous demo; a successful solve is not required.
- Pages 4/5 describe result records/helper scripts. Our accepted JSON trace format
  does not establish that those helper scripts are present or that our result
  schema/timing fields already match their interface.

These differ from the older Canvas comparison/pass@k/successful-demo wording.
Keep the original assignment unchanged. The working evaluation plan follows the
newer guide's explicit scope, with its provenance noted here; the professor's
three-part reply should not be cited as separately resolving every discrepancy.
Actual evaluation/report/demo implementation and authorization remain later work.

## 1. CTFTiny — required benchmark target

Original link: <https://github.com/NYU-LLM-CTF/CTFTiny>

- The README explicitly says CTFTiny follows NYU CTF Bench's structure and refers
  to NYU's usage guidance. This is why the NYU documentation and loader apply.
- We inspected the index metadata and repository filenames: 50 indexed challenges,
  with category/challenge/event/path/year fields. We did not open individual
  challenge answers or solutions.
- Design consequence: later use `nyuctf` with an explicit path to `ctftiny.json`.
  The assignment's scored set must come from CTFTiny, with 10 challenges kept
  separate from development. The current manifest reserves 10 scored IDs and 40
  development IDs using metadata only; the pin and index validation were subsequently completed.

## 2. NYU CTF Bench — dataset conventions and Python package

Original link: <https://github.com/NYU-LLM-CTF/NYU_CTF_Bench>

- Its `nyuctf` package provides `CTFDataset`, `CTFChallenge`, contestant-file and
  endpoint metadata, and Compose lifecycle helpers. Its NYU development/test
  splits are not CTFTiny selections.
- We reviewed generic loader/lifecycle code and the published wheel in memory.
  At review time PyPI published 1.1.1 while repository main declared 1.1.2;
  relevant APIs existed in the published wheel. Version 1.1.1 was subsequently installed and locked.
- `CTFChallenge` holds the expected flag alongside public metadata. The lifecycle
  helpers invoke the supplied Compose file directly and do not enforce all course
  controls. Package objects must remain trusted host data; construct public task
  messages explicitly rather than serializing whole objects.
- Design consequence: reuse package conventions and supplied target Compose files
  wherever compatible. Inspect actual target configuration before deciding that
  an override or additional lifecycle code is needed. Subsequent target compatibility checks are recorded below.

Supporting sources:
[dataset loader](https://github.com/NYU-LLM-CTF/NYU_CTF_Bench/blob/main/python/nyuctf/dataset.py),
[challenge/lifecycle implementation](https://github.com/NYU-LLM-CTF/NYU_CTF_Bench/blob/main/python/nyuctf/challenge.py),
[published package](https://pypi.org/project/nyuctf/).

## 3. NYU documentation — setup and operation guide

Original link: <https://nyu-llm-ctf.github.io/docs/>

- Reviewed dataset setup, framework installation/operation, and configuration.
  Some pages describe NYU's complete reference agent framework, not just the
  challenge loader package.
- Design consequence: follow benchmark data/target conventions without assuming
  we must adopt that agent architecture, its hint features, tools, default model,
  default network, or example budget. Course controls take precedence.

## 4. Reference agents — architectural examples, not challenge solutions

Original link: <https://github.com/NYU-LLM-CTF/nyuctf_agents>

- Reviewed generic baseline startup, conversation, environment, tools, setup
  script, and solver Dockerfile. The separate solver container and copying of
  listed contestant files support our basic host/solver/target arrangement.
- The command, file-creation, and flag-checking tools motivated our small tool set.
  The baseline flag checker prints the expected answer; that behavior must not be
  copied. Its ordinary shared network and solver image privileges are not proof
  that the assignment's stronger controls are satisfied.
- Design consequence: use the reference implementation to understand interfaces
  and responsibilities. Our implementation uses a small function-based loop
  (now verified with scripted responses) and explicit controls, rather than
  vendoring the full agent framework. The trusted runner supplies bounded model/tool
  functions; Langfuse now owns detailed tracing. Live model integration was pending
  at that review and is now verified synthetically below.

Supporting sources:
[baseline entry point](https://github.com/NYU-LLM-CTF/nyuctf_agents/blob/main/run_baseline.py),
[environment](https://github.com/NYU-LLM-CTF/nyuctf_agents/blob/main/nyuctf_baseline/environment.py),
[tools](https://github.com/NYU-LLM-CTF/nyuctf_agents/blob/main/nyuctf_baseline/tools/tools.py).

## 5. Duke AI Gateway guide — model access

Original link:
<https://ai.colab.duke.edu/colab-ai-blog/all-blogs/getting-started-with-dukes-ai-gateway-a-developers-guide/>

- The guide describes OpenAI-compatible access, model discovery, authentication,
  and gateway usage management. It informed the proposed use of the OpenAI Python
  client through Duke's LiteLLM gateway.
- At the initial review that approach was not implemented. Confirm available models, tool calling,
  API flavor, compatible settings, actual pricing, and account allowance before
  selecting a model or performing an approved live check.
- At that stage the approximately $1/day allowance was the user's unverified planning assumption,
  not a confirmed account limit or a requirement inferred from this guide.
- Credentials remain in trusted host configuration, outside solver environments
  and application trace inputs. No gateway model calls had occurred at that stage.

Subsequent approved model milestone: the user chose Responses and automatic
Langfuse integration and confirmed a $1/day allowance. Read-only gateway model
metadata authenticated and listed 41 models. One approved synthetic attempt with
`gpt-6-luna` used two requests and succeeded, with native hosted usage/cost readback.
Gateway pricing matched the [official model page](https://developers.openai.com/api/docs/models/gpt-6-luna).
The [Responses function-calling guide](https://developers.openai.com/api/docs/guides/function-calling)
and [reasoning guide](https://developers.openai.com/api/docs/guides/reasoning)
informed native output replay and linked function results. This is setup evidence;
model selection for real challenge performance remains future work.

## Subsequent approved reference: Langfuse

The user later selected Langfuse as the sole detailed tracing system and asked for
narrow runner/loop interfaces using normal SDK patterns. SDK **5.1.0** was resolved
from PyPI, pinned, installed, and inspected locally. Integration follows the
[SDK overview](https://langfuse.com/docs/observability/sdk/overview),
[native instrumentation](https://langfuse.com/docs/observability/sdk/instrumentation),
and [client/exporter reference](https://python.reference.langfuse.com/langfuse).
It removes custom JSONL tracing while retaining normal result/provenance files.
The real SDK's supported in-memory exporter enables local synthetic verification.
Hosted setup and verification followed as a separate milestone. No individual challenge
material or model API calls were needed for this migration.

The user then requested installation of the
[official Langfuse skill](https://github.com/langfuse/skills). Its instrumentation
and CLI references, current [best practices](https://langfuse.com/docs/observability/best-practices),
and [query documentation](https://langfuse.com/docs/api-and-data-platform/features/query-via-sdk)
guided the hosted verification. The pinned SDK's own OpenAI integration confirmed
our messages/tools generation input shape. One synthetic hosted trace was read
through the current observations API and independently through `langfuse-cli`;
[evidence](../evidence/langfuse-cloud/README.md) records the result. This verifies
hosted delivery/readback for that project, not real model usage or general service
reliability. The CLI was used for review, not added as an application dependency.

The later [automatic OpenAI integration](https://langfuse.com/integrations/model-providers/openai-py)
now owns live generations. OpenAI 3.44.0 is pinned; Langfuse 5.1.0 remained current
when checked against PyPI. The installed SDK's documented behavior and offline
transports verified native model/token observations. The normal SDK includes its
public project identifier in instrumentation scope; secret credentials remain
excluded. A response hook keeps raw provider HTTP error bodies outside tracing.
The CLI retrieved the live synthetic trace and usage/cost totals agreed with
the local estimate. See [model evidence](../evidence/model-integration/README.md).

## Initial readiness milestone (historical)

November 4 package/target verification: the sparse CTFTiny checkout is pinned to
`f1c9531672c45b24b7fb5f3aa44a7ac33d3602f8`; its index matches the preserved hash.
Installed/locked the published `nyuctf==1.1.1` and reviewed its installed generic
loader/lifecycle code. Its declared `pathlib` dependency is retained rather than
forking the package. The [NYU dataset usage guide](https://nyu-llm-ctf.github.io/docs/usage/dataset/)
supports an explicit dataset index; CTFTiny remains the chosen dataset.
The first readiness milestone inspected the selected development setup. Its Compose definition mounts
the Docker socket and publishes a host port. Runtime JSON keeps the supplied
image/alias while removing those exposures, adds target limits, and uses the
existing isolated network/guard policy.
[Docker Compose service controls](https://docs.docker.com/reference/compose-file/services/)
and [bridge networking](https://docs.docker.com/engine/network/drivers/bridge/)
informed that arrangement. The target image is pinned by digest, and actual AMD64
target response is verified on the ARM64 host. No target solver/write-up/flag file
was inspected; trusted `nyuctf` loading holds the answer programmatically. At that first milestone, no held-out challenge contents were opened.
See [readiness completion evidence](../evidence/ctftiny-readiness/COMPLETED.md).

All original links are retained here; external repositories/sites have not been
vendored or fully archived. Local code, assignment, decisions, status, and
verification evidence are saved in this workspace. External contents can change.

Generic reference-agent/infrastructure review is permitted. The assignment's
restriction on consulting held-out evaluation flags, solutions, and write-ups
during development/scoring remains in force. Trusted evaluation can load expected
answers programmatically without exposing them to the model or separately in logs.

Use [DESIGN.md](DESIGN.md) for decisions and alternatives and
[PROJECT_STATUS.md](../PROJECT_STATUS.md) for current scope, findings, and open work.


November 4 launch setup: the existing Responses integration was consolidated into
`agent.py`; trusted target handling into `challenge.py`; and ordinary provenance
and native trace export into `launch.py`. Current official Responses/function-call
and Langfuse CLI documentation was reviewed. The official CLI package name is
now `@langfuse/cli`; at that milestone the application pinned
`@langfuse/cli@1.3.1` for native exports. The later SDK cleanup below supersedes that path.
No SDK migration or agent framework was added. Gateway metadata still reports
the existing model prices. The user requested setup only and will check the
system themselves; no new live model calls or challenge solving occurred.

Subsequent approved reasoning-summary check: the current
[OpenAI reasoning-summary guide](https://developers.openai.com/api/docs/guides/reasoning#reasoning-summaries)
documents `reasoning.summary: "auto"` as an opt-in readable summary, distinct from
raw internal reasoning. Installed OpenAI/Langfuse SDK code supports that parameter
and native output capture. One benign request through Duke accepted it, but its
summary array remained empty. The
[Langfuse best-practices guidance](https://langfuse.com/docs/observability/best-practices)
informed the native observation/usage/parentage/credential audit. The official
CLI read back the same response. No additional provider/model experiment was run.

## Shared CTFTiny launcher and selected-ten preparation

The later user-approved setup milestone reuses `CTFDataset(dataset_json=...)` and
`CTFChallenge` from the installed package. The public index and setup/file inventory
were used to materialize the selected ten directories, without consulting evaluation
solutions, write-ups or answer values. Trusted package loading retains answer keys
programmatically; only listed contestant files and explicit public fields reach the
solver. Both result labels use the same command and implementation.

The [NYU dataset guide](https://nyu-llm-ctf.github.io/docs/usage/dataset/) and installed
package code confirm the common loader conventions. Docker's existing Compose
canonicalization and service controls support the supplied image/service/alias/port
arrangement. Nginx startup diagnostics demonstrated that the disposable target needs
writable log/temp storage and CHOWN; solver permissions were unchanged. Eleven
zero-model preparation commands passed, with two fresh cycles per challenge.
[Current evidence](../evidence/benchmark-readiness/README.md) records scope, setup
diagnostics and remaining limits. CTFTiny is the active dataset; additional NYU
dataset setup was deferred at the user's request.


## November 5 configuration and SDK export cleanup

The approved cleanup follows the current [SDK query guide](https://langfuse.com/docs/api-and-data-platform/features/query-via-sdk)
and [public API guide](https://langfuse.com/docs/api-and-data-platform/features/public-api).
The installed Langfuse 5.1.0 already provides `client.api.observations.get_many`;
its typed response supports aliased JSON serialization and cursor pagination.
Keeping the pinned version avoids an unrelated dependency migration. The
application now reuses that client and saves every page to `observations.json`,
removing its Node/npm/CLI requirement while retaining the existing audits.

Offline checks cover pagination beyond 100 rows, empty continuation pages, delayed
completion and timeout. Readback of the existing synthetic trace matched its
historical export and a fresh official CLI readback for IDs, parentage, inputs,
outputs, metadata, model and usage/cost. No new model calls or traces were created.
The CLI was used only for independent verification. Complete TOML settings and
package write-on-change checks are recorded with this milestone's
[evidence](../evidence/config-sdk-cleanup/README.md).

## November 5 NYU infrastructure comparison — proposal only

The follow-up review checked installed `nyuctf==1.1.1` loader/lifecycle source and
the baseline [release 20250206](https://github.com/NYU-LLM-CTF/nyuctf_agents/releases/tag/20250206),
commit `112cfa33f5c0a06a20e49af525ac8eb07ec98457`. The reviewed files include its
[environment](https://github.com/NYU-LLM-CTF/nyuctf_agents/blob/112cfa33f5c0a06a20e49af525ac8eb07ec98457/llm_ctf/environment.py),
[tools](https://github.com/NYU-LLM-CTF/nyuctf_agents/blob/112cfa33f5c0a06a20e49af525ac8eb07ec98457/llm_ctf/tools/tools.py),
[conversation](https://github.com/NYU-LLM-CTF/nyuctf_agents/blob/112cfa33f5c0a06a20e49af525ac8eb07ec98457/llm_ctf/conversation.py),
Dockerfile, entrypoint, setup and requirements. This was the baseline, not D-CIPHER.
It uses a writable solver, normal Docker copying/execution and thin Compose
lifecycle methods. Its timeout handler kills the local Docker client; its checker
prints the expected answer. Neither behavior should be copied unchanged.

Docker's [copy documentation](https://docs.docker.com/reference/cli/docker/container/cp/)
supports ordinary transfer once our restrictive layout is removed, with ownership
and mount behavior checked. [Restart](https://docs.docker.com/reference/cli/docker/container/restart/)
and [storage](https://docs.docker.com/engine/storage/) documentation support the
proposal to reset solver processes while retaining its writable layer. The then-current
tmpfs workspace would not survive that reset. [Bind-mount documentation](https://docs.docker.com/engine/storage/bind-mounts/)
explains that socket binds refer to the daemon host: under our current Docker
Desktop deployment they expose the engine managing trusted resources, not a
separate challenge daemon.

The source review and read-only Compose configuration inventory did not build the
NYU image, prototype recovery or solve challenges. The
[implementation proposal](SIMPLIFICATION_PLAN.md) records what would be reused,
removed, newly integrated and verified. It supersedes earlier conversational
suggestions to remove the file writer/batch wrapper or require terminal command
timeouts. Current runtime behavior remains documented in DESIGN and README.


## Execution simplification checkpoint — November 6

The first approved checkpoint uses Docker's standard
[exec](https://docs.docker.com/reference/cli/docker/container/exec/),
[copy](https://docs.docker.com/reference/cli/docker/container/cp/) and
[restart](https://docs.docker.com/reference/cli/docker/container/restart/) behavior.
Copying preserves file modes but normally creates root-owned files; trusted
pre-agent CHOWN assigns solver ownership. Restart with SIGKILL resets all solver
processes while retaining its writable layer. These details were verified locally,
not assumed from the baseline. The retained structured writer and bounded reader
are adaptations of existing project code, not NYU-provided tools. No full NYU
agent framework or supplied-image build was introduced.

The existing [Langfuse instrumentation](https://langfuse.com/docs/observability/sdk/instrumentation)
conventions retain root-linked tool results and add timeout/restart/inventory events;
SDK version/export and native model integration are unchanged. Verification uses
the actual SDK with local transport plus synthetic Docker targets; no new hosted
trace or model call ran. The [checkpoint evidence](../evidence/execution-simplification/README.md)
records results and the capability tradeoffs. Target/network and image decisions
in the earlier proposal remain pending.


## Target/network simplification checkpoint — November 6

Rechecked installed `nyuctf==1.1.1` lifecycle code: it invokes the original Compose
file without project/exposure/readiness/deadline integration, so the loader remains
reused while the existing small trusted Compose orchestration is retained.
Docker's [Compose networks](https://docs.docker.com/reference/compose-file/networks/),
[service definition](https://docs.docker.com/reference/compose-file/services/) and
[down/volume cleanup](https://docs.docker.com/reference/cli/docker/compose/down/)
documentation support ordinary project-local names, DNS/service relationships and
fresh named/anonymous volume cleanup. Those replace our manual network/route
arrangement; the custom firewall/denial collector is still required and retained.

The 27-definition read-only infrastructure inventory accepts 26 configurations;
privileged `msc-showdown` remains unsupported and 17 socket omissions are recorded.
No flags, solutions or write-ups were consulted. Six zero-solving development
preparation cycles and synthetic multi-service DNS/volume/scope checks passed.
Docker Desktop rejected read-only host bind execution; that policy has offline
coverage only. No host-sharing workaround was added. No model calls or new hosted
traces ran. [Evidence](../evidence/target-network-simplification/README.md) preserves
provenance, failures, scope and capability/resource tradeoffs. Supplied image
selection is still independent and pending.


## Live synthetic smoke check — November 6

The existing bounded check was exercised on clean runtime commit `00e6a41` after
user approval and VPN readiness. Current
[OpenAI function-calling guidance](https://developers.openai.com/api/docs/guides/function-calling)
and [Langfuse trace guidance](https://langfuse.com/docs/observability/best-practices)
were consulted; the unchanged implementation used native response replay, linked
tool observations and installed SDK hosted readback. Two model calls and two tools
ended in trusted synthetic success, with usage/cost/privacy/parentage/cleanup
audits passing. [Evidence](../evidence/live-simplification-smoke/README.md) records
limits, source/images, the trace and the untested scope. No CTFTiny challenge,
source/image change, dependency migration or broader live pilot was included.

## Bounded supplied-image evaluation — November 6

The approved evaluation used the exact [release Dockerfile](https://github.com/NYU-LLM-CTF/nyuctf_agents/blob/112cfa33f5c0a06a20e49af525ac8eb07ec98457/Dockerfile)
and entrypoint from `20250206`. The baseline Dockerfile at current revision
`612190f298ae9e604f00370019beed4ba1f372f6` had the same hash. The external
[ctftools installer](https://raw.githubusercontent.com/c3-ctf/ctftools/master/install.sh)
is mutable and adds repositories/tooling; a review snapshot does not freeze what
the unmodified build fetched. No full NYU host setup or agent framework was used.

The unchanged AMD64 build progressed after the user disconnected the VPN, then
was canceled for host storage during the external installer. No completed image
or NYU runtime compatibility result exists. The current image is retained,
reverified and archived; its eleven focused control checks are baseline evidence,
not candidate results. [Evidence](../evidence/nyu-solver-image-evaluation/README.md)
records source hashes, build logs, storage bounds, scoped cache cleanup and limits
on the conclusion. Neither the guide nor professor confirmations require adopting
that toolkit. No source defect or incompatibility is inferred from cancellation.

November 7 storage follow-up uses measured APFS/raw-file/Linux filesystem figures
and Docker's [Mac disk-accounting guidance](https://docs.docker.com/desktop/troubleshoot-and-support/faqs/macfaqs/)
and [resource defaults](https://docs.docker.com/desktop/settings-and-maintenance/settings/).
The chosen reserve triggered cancellation; Docker's virtual ceiling was not the
constraint. The image decision is reopened. Only the explicitly approved unrelated
fMRIPrep image was removed; actual host free space increased by about 10.2 GiB.
Memory changes and a fresh candidate build remain proposed, not performed.

## Completed supplied-image retry — November 7

After the user saved 8 GiB and a normal Desktop restart applied it, the unchanged
release recipe built successfully. Actual resource samples and 34 synthetic
candidate checks support the recommendation to use the supplied base with a small
workspace/NumPy/Pillow adapter. Generic additional tests exercise SageMath,
radare2, multilib and angr function analysis; angr's
[state/call-state API](https://docs.angr.io/en/latest/core-concepts/states.html)
informed the benign symbolic-function test. No benchmark solution code or answer
content was reviewed. Installed SDKs and existing local spans verify controls;
no new hosted/model call was part of this checkpoint.

[Evidence](../evidence/nyu-solver-image-evaluation/retry-8g/README.md) records the
successful build, earlier diagnostic timeout, ignored optional installer errors,
all checks, inventories and checksummed local artifact. The existing image/defaults
remain unchanged. Exact frozen artifact loading is distinguished from rebuilding
the upstream recipe with its mutable external downloads. No NYU agent framework,
host setup script, extra Docker administration or new runtime backend was adopted.


## Production supplied-recipe integration — November 7

The approved checkpoint reuses the verified release installation body in the
single production [Dockerfile](../docker/solver.Dockerfile). The
[MIT notice](../docker/NYU-LICENSE) accompanies the copied source. The project
adds workspace/environment settings, pinned NumPy/Pillow, inventories and idle
startup; the unused upstream HTTP entrypoint is omitted. Source/license provenance,
100 offline tests, 34 normal Docker cases, first-start measurements and a separate
frozen default artifact are recorded in [integration evidence](../evidence/nyu-solver-integration/README.md).
The existing lean artifact remains historical comparison evidence. No agent
framework, startup subsystem or live pilot was added. The source revision does
not freeze external downloads; exact reproduction uses the verified archive.


## Same-release MongoDB ARM64 compatibility — November 7

A zero-model [local evaluation](../evidence/mongo-arm64-evaluation/README.md)
verified official MongoDB 7.0.9 ARM64 as a working sibling of the supplied AMD64
manifest. Docker's release manifest records the Docker Official Images source
revision and Ubuntu Jammy build. MongoDB's
[production platform requirements](https://www.mongodb.com/docs/manual/administration/production-notes/)
state the x86 AVX and ARM architecture requirements. This motivated testing native
ARM, not downgrading the server or modifying the challenge application. Two fresh
functional/control cycles passed; production adoption remains a reviewed next step.
No challenge solution/write-up, live model call or expected-answer disclosure was
needed in this evaluation. Private runtime configs remain local/Git-ignored.


## MongoDB compatibility/readiness integration — November 7

The approved integration uses the exact ARM64 MongoDB 7.0.9 sibling on ARM64
Docker engines and preserves the supplied AMD64 reference elsewhere. Both are
pinned by digest in the existing target integration; no dataset edits or dynamic
registry resolution. `target.json` records the exact original/replacement and
reason. Compose's installed `up --help` confirmed native `--wait`/`--wait-timeout`;
that standard behavior handles supplied healthchecks. A safe state snapshot
adds detection/reporting of restarting/exited/health failures before paid work and
after preparation probes. [Exact source/verification](../evidence/mongo-arm64-integration/README.md).
No solver/agent/model/endpoint change or new dependency; no live model retry.


## Final pre-Git verification — November 7

The completed local setup passed 111 offline tests, all 36 synthetic Docker cases
and 22 fresh final-code preparation cycles covering the ten reserved IDs plus the
web development target. A separately authorized fresh live web attempt achieved
trusted success in four requests/four tools; automatic record/privacy/cleanup
audits passed. Detailed conversation review is deferred at the user's request.
[Validation and source evidence](../evidence/pre-git-validation/README.md).
Current private deployment copies were redacted with originals preserved locally;
older committed copies remain a separate publication/history decision. No source
behavior change, version migration, commit, push or history rewrite was part of
that final verification. These results supersede earlier pending-stage notes while
preserving the historical checkpoints and the original failed pilot.

## NYU baseline prompt comparison — November 7

At the user's request, reviewed the generic default prompt templates and prompt
loading/conversation code at the same release `20250206`, revision
`112cfa33f5c0a06a20e49af525ac8eb07ec98457`, used for solver provenance. This is a
review of pinned defaults, not a claim about every configuration override or the
current main branch. No challenge demonstrations, hints, solutions or write-ups
were opened; no upstream code was executed or copied into the application.

The [system template](https://github.com/NYU-LLM-CTF/nyuctf_agents/blob/112cfa33f5c0a06a20e49af525ac8eb07ec98457/llm_ctf/prompts/templates/default/system.md.jinja2)
sets the CTF role, objective and container context. The
[initial task template](https://github.com/NYU-LLM-CTF/nyuctf_agents/blob/112cfa33f5c0a06a20e49af525ac8eb07ec98457/llm_ctf/prompts/templates/default/initial_message.md.jinja2)
separates public task/endpoint/file information and adds small category-specific
tool notes. The
[tool-use template](https://github.com/NYU-LLM-CTF/nyuctf_agents/blob/112cfa33f5c0a06a20e49af525ac8eb07ec98457/llm_ctf/prompts/templates/default/tool_use.md.jinja2)
requests evaluator checking. Our task construction and submission tool already
cover much of this. A compact description of verified solver capabilities is the
clearest useful addition; their custom formatting/template infrastructure is
unnecessary for our native function tools.

Their assumed `~/ctf_files` path, sudo/system-package installation, extra HTTP
server and live GDB behavior do not describe our verified runtime. Our prompt
should use `/workspace`, pip-only external access and established capabilities.
Any flag-format guidance must come from public task information, not be inferred
from the trusted expected answer merely because the reference exposes a format.
Reference defaults remain technical examples, not course requirements.

The [conversation loop](https://github.com/NYU-LLM-CTF/nyuctf_agents/blob/112cfa33f5c0a06a20e49af525ac8eb07ec98457/llm_ctf/conversation.py)
sends a continuation message after a turn with no tool calls, within its own
limits. Our text-only reply ends an attempt. That difference could affect early
stopping, but it is a separate controller-policy hypothesis, not evidence of a
superior prompt or a reason to combine loop and prompt changes. A bounded
continuation experiment would require explicit stopping behavior and review.

The inspected default templates do not supply the independent-validation
guidance motivated by our recent traces. Keep that evidence-based proposal and
consider the reference's environment/task clarity alongside it. No prompt,
runtime, model/settings or dependencies changed; no model calls or attempts ran.

## Command-tool description comparison — November 7

Reviewed the pinned NYU [CommandExec source](https://github.com/NYU-LLM-CTF/nyuctf_agents/blob/112cfa33f5c0a06a20e49af525ac8eb07ec98457/llm_ctf/tools/tools.py),
including its callable docstring and separate command/timeout annotations. The
docstring alone is ten whitespace-separated words; this is not the total rendered
tool schema or surrounding prompt. Existing local description is about 95 words;
the conversational draft was about 176; a condensed alternative is about 92.
Length comparisons are descriptive, not evidence of better model performance.

[OpenAI function-calling guidance](https://developers.openai.com/api/docs/guides/function-calling)
supports explicit purpose, parameter formats and output meaning, with overall
usage guidance in the system prompt. Anthropic's
[tool-writing article](https://www.anthropic.com/research/writing-tools-for-agents)
emphasizes making implicit operational assumptions explicit. Its
[Claude tool-definition documentation](https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools)
suggests at least three to four sentences and more for complex tools. This is
provider guidance, not a universal size target or a course requirement.

Recommendation: shorten through separation of responsibilities, preserving shell,
connection, restart and output behavior. Keep pip/network policy in the system
prompt and timeout defaults/remaining-time clipping in the parameter description.
Do not advertise output archival/retrieval until implemented. No tool/runtime or
prompt changes were made by this comparison.
