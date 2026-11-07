# CTFTiny agent benchmarking

A bounded model/tool agent for [the assignment](ASSIGNMENT.md), using `nyuctf`
for CTFTiny loading, an isolated solver, trusted verification and Langfuse tracing.
The ten scored challenges are reserved; use the forty development IDs in
[configs/ctftiny.json](configs/ctftiny.json) for practice and Section 2.

[Project checklist](PROJECT_STATUS.md#assignment-checklist) ·
[Design](docs/DESIGN.md) · [Section 2 experiments](docs/EXPERIMENTS.md) ·
[References and attribution](docs/REFERENCES.md)

The [infrastructure simplification plan](docs/SIMPLIFICATION_PLAN.md) tracks
reviewable checkpoints. Execution now uses ordinary Docker copy/exec and a
writable disposable solver. Targets now retain supplied Compose behavior on fresh
project networks/volumes; image selection remains independent. Re-run `build-images`
after pulling these changes (both solver and guard startup changed).

The professor has [confirmed](docs/REFERENCES.md#november-6-course-guide-and-professor-confirmations)
that repository Compose files/private controller verification, Langfuse JSON
exports and our CTFTiny development/ten-held-out split are acceptable. No separate
course runtime, JSONL conversion or NYU development-data migration is required.
The next infrastructure task is the bounded upstream solver-image evaluation;
adoption depends on compatibility and lower maintenance. It has not started.

## One-time setup

**Each teammate completes this section once after cloning the repository.** If
you already have the dependencies, Docker images, `.env` and full dataset installed,
skip to [Choose and run a challenge](#choose-and-run-a-challenge). If you previously
downloaded only selected challenges, complete the sparse-checkout step below first.

Clone the repository into any folder and open that folder in your IDE. Run all
commands from its **repository root**: the folder containing `README.md`,
`pyproject.toml` and `ctf_agent/`. The checkout's name and location do not matter;
paths such as `configs/` and `datasets/` are relative to that folder.

Use Python **3.13.2**, uv, Docker Desktop/Engine with Linux containers and
Compose v2. Trace export uses the installed Langfuse Python SDK. Start Docker before
running the build command:

```sh
uv sync --frozen
uv run --frozen python -m ctf_agent build-images
cp -n .env.example .env
```

Dependencies are locked: Langfuse 5.1.0, OpenAI 3.44.0, nyuctf 1.1.1, and pytest
9.2.0 for development. Start Docker before building or preparing challenges.

The build command creates a **Linux AMD64 solver**, including on Apple Silicon
(Docker Desktop uses emulation there). It includes Python, Bash, `file`, binutils
(`strings`, `readelf`, `objdump`), `xxd`, `curl`, `nc`, OpenSSL, ZIP/unzip, GCC,
make, GDB and 32-bit x86 C/C++ runtime libraries. `/workspace` permits executing
contestant files and programs the agent creates. Re-run `build-images` after
pulling solver-image changes. On ARM Linux hosts, Docker needs AMD64 emulation;
native AMD64 Linux avoids the emulation overhead and debugger limitations.
On the verified Apple Silicon Docker setup, 64-bit and 32-bit execution pass;
GDB static inspection works, but live debugging fails with register/ptrace errors.

The solver also includes **pwntools, SymPy, NumPy, PyCryptodome (`Crypto`), requests
and Pillow**. These are installed in the image, separate from the host runner's
dependencies. [Requested versions](docker/solver-requirements.in) and
[resolved dependencies](docker/solver-requirements.txt) are committed; the image
records installed versions in `/opt/python-packages.txt`. Reedsolo is not included.

The solver has a writable `/workspace`, home at `/home/solver`, normal `/tmp`
and an image-prepared Python environment at `/opt/venv`. Python/pip select it
automatically: `python -m pip install PACKAGE`. Files and installed additions
survive a command-timeout restart, but are discarded after each attempt.
The live profile allows 1 GiB RAM; writable storage uses Docker's disk space,
with **no per-attempt disk quota**. Monitor Docker's available storage.

The professor [approved runtime package downloads](docs/REFERENCES.md#authority-and-professor-clarification).
The agent's rule permits external internet **only for pip dependency installation**,
never looking up benchmark answers or write-ups. The guard allows Docker DNS and
public HTTPS, plus assigned challenge endpoints; other private-network access is
blocked. HTTPS connectivity is technically usable by other commands: package-only
purpose is an instruction and trace-review policy, not an enforced domain filter.
Native system dependencies still need image updates; pip cannot install every tool.

If `.env` does not exist, copy `.env.example` to `.env`. Each teammate uses their
own Duke key and the team's intended Langfuse project. Fill these host-only variables:

| Variable | Source |
| --- | --- |
| `LITELLM_TOKEN` | Your Duke AI Gateway key from the [Duke dashboard](https://dashboard.ai.duke.edu/). |
| `LANGFUSE_PUBLIC_KEY` | Intended Langfuse project's API key settings. |
| `LANGFUSE_SECRET_KEY` | Same project's key pair. |
| `LANGFUSE_BASE_URL` | Project's regional URL, e.g. `https://us.cloud.langfuse.com`. |

Keep `.env` private and Git-ignored. The configured Duke gateway does not require
a separate `OPENAI_API_KEY`. Preparation and local tests need no keys.

**Download the full pinned dataset.** If `datasets/CTFTiny` does not exist, run:

```sh
git clone --depth 1 --filter=blob:none --no-checkout https://github.com/NYU-LLM-CTF/CTFTiny.git datasets/CTFTiny
git -C datasets/CTFTiny fetch --depth 1 origin f1c9531672c45b24b7fb5f3aa44a7ac33d3602f8
git -C datasets/CTFTiny checkout --detach FETCH_HEAD
```

**If you already have the earlier sparse checkout**, run this once instead of
cloning again. It downloads the remaining directories at your existing revision:

```sh
git -C datasets/CTFTiny sparse-checkout disable
```

Wait for the download to finish; the full dataset may contain large files. The
long revision identifies the exact dataset version we recorded. Keep that checkout
unchanged. All dataset files remain host-side; only listed contestant files enter
the solver. Do not consult evaluation flags, solutions or write-ups.

## Choose and run a challenge

After completing one-time setup on your machine, use these steps in your IDE terminal.

**1. Start Docker and open a terminal at the repository root.** The folder should
contain `README.md` and `pyproject.toml`. Use your own checkout location; the
commands below are identical for every teammate.

**2. Choose an ID from the `development` list in
[configs/ctftiny.json](configs/ctftiny.json).** Start with `pwn-baby-boi`, which the
one-time setup downloads along with every other challenge. Replace that ID in both
commands below when you choose another challenge, for example `cry-ecxor`. You do
not need to look up or download its directory separately after full dataset setup.

**3. Check the challenge environment.** This starts fresh containers, checks files,
connections, isolation and cleanup using the same experiment settings as the run,
then exits. It makes no model requests and
does not try to solve the challenge. You do not need to repeat it before every
attempt if that environment has already passed and its setup is unchanged.

```sh
uv run --frozen python -m ctf_agent prepare-challenge --challenge pwn-baby-boi
```

**4. Run one agent attempt.** This command uses your `.env` credentials and makes
paid model requests within the configured limits:

```sh
uv run --frozen --env-file .env python -m ctf_agent run-challenge --challenge pwn-baby-boi
```

Each invocation starts a fresh environment, stages public files, runs the agent,
verifies submissions, cleans up and exports its trace. File-only challenges need
no target service; missing prebuilt service images are pulled automatically.
Run preparation on your machine before its first live attempt.

**5. Read the results.** The command prints a new directory under
`runs/challenges/`. Open its `run.json` for the outcome and Langfuse trace URL;
use the trace to follow model calls, tool arguments and results. See
[Read results](#read-results) for the saved files and field meanings.

If preparation reports missing challenge files, finish the full dataset setup above
before retrying. If preparation fails for a service, file-size or isolation reason,
inspect its saved evidence before running the model; that challenge's setup may
need a compatibility fix. All 50 IDs are selectable, but compatibility with every
target arrangement has not been verified. Keep `scored` IDs for final evaluation.
The known exception is `msc-showdown`; its privileged Docker setup is rejected by
the current controls. For `cry-describeme`, the listed Dockerfile stays with the
trusted controller, and the run record identifies that omission.

### Run a development batch

`run-batch` repeats the existing launcher sequentially, with fresh processes,
solver/target environments and attempt records. For example, this makes **live
model requests** for two development challenges, one attempt each:

```sh
uv run --frozen --env-file .env python -m ctf_agent run-batch \
  --challenges cry-ecxor msc-algebra \
  --trials 1 --output runs/pilots/current-setup
```

Add more IDs after `--challenges`; `--trials 2` repeats every selected ID twice,
including challenges solved on the first trial. Keep pilot and scored batches in
separate output folders. The command rejects mixing development/scored IDs.

The printed batch folder contains a copied `experiment.toml` and `batch.json`.
The index lists each started attempt's challenge, trial, outcome, evaluator
success, existing run ID, trace link and relative `run.json` path. `completed`
means the scheduled attempts and records finished, not that every task was solved.
Calls, tokens, time, cost and detailed traces remain in the existing attempt records.

Ordinary unsuccessful attempts and command timeouts permit the next trial after
cleanup. Launch failures, incomplete records, cleanup failures, scope/guard or
infrastructure incidents, and response-source failures stop the batch for review.
An otherwise valid model reply without usage metadata can continue; its token
and estimated-cost totals remain unknown. Ctrl-C forwards interruption to the
current launcher and waits for its cleanup; the partial index remains. There is no automatic retry or resume.
Do not edit code or rebuild images during a batch. The wrapper snapshots the
experiment file and otherwise uses the existing per-attempt controls; there is
no added batch-cost gate.

Two different development challenges per category would give **11 IDs**: crypto,
miscellaneous, pwn, reversing and web can each supply two, but forensics has only
`for-1black0white`. Keep the other forensics challenge in the reserved scored set.
The selected eleven-ID pilot passed preparation; an earlier batch stopped after
three attempts when pip tried to reach PyPI under the previous network policy.
Package access is now enabled; review the new setup before starting another pilot.
See [project status](PROJECT_STATUS.md) for historical outcomes.

### Optional command settings

Optional arguments: `--experiment` (default `configs/development.toml`),
`--dataset`, `--manifest`, and `--output` (default `runs/challenges`).
`prepare-challenge` also accepts `--experiment` (the same development default),
`--dataset`, `--manifest`, and `--output`; it saves under `runs/` by default.
Use the same `--experiment FILE` for preparation and the subsequent run. The
top-level `--config` applies to image builds and synthetic checks.

### Limits and estimated cost

| Limit | Current live settings |
| --- | --- |
| Whole attempt | 600 seconds, including solver preparation; cleanup/export add time. |
| Ordinary command | Up to 120 seconds, clipped to remaining attempt time. |
| Model request | Up to 60 seconds; no client retries. |
| Model / tool calls | 40 / 80 maximum. |
| Model input / output | 512 KiB serialized input; 4,096 output tokens per request. |
| Solver resources | 1 CPU, 1 GiB memory, 64 PIDs; writable disk has no per-attempt quota. |
| Tool output / file write | 64 KiB combined stdout/stderr; 64 KiB UTF-8 write. |

Edit `[attempt]` and `[model]` in [configs/development.toml](configs/development.toml),
the single complete file for normal run settings. `config.py` loads and validates
it; there are no hidden value overrides. Copy the whole TOML file to compare a
different configuration and pass it with `--experiment FILE`. All fields are
required. `max_model_turns` supplies both the runner and model-adapter call limit;
there is no separate `max_requests` setting. Preparation uses the same file.
Local synthetic controls also use it; the paid `model-check` explicitly applies
smaller test bounds in `tests/check_model.py`. The old `configs/initial.toml` is
retired. Both model-turn/request limits are 40. The current API setting selects at most one
tool per model response, so the live agent normally has at most 40 tool actions;
the separate tool-call guard remains 80.
There is no local spending cap or reservation system; token usage and estimated
cost are still recorded. Provider/account limits remain outside this application.
Larger allowances permit more work but do not force the agent to use them.

A command timeout returns `timed_out: true`, `solver_restarted: true` and
`process_state_reset: true` after restarting the **same solver container**.
Files and pip installs survive; **all solver processes and connections end**,
including unrelated background commands. Target services remain running. The
run ID, call counts and original deadline remain unchanged; no command is retried
automatically. Failed recovery, scope/guard failures and the whole-attempt deadline
are terminal. Use shorter internal network deadlines to avoid unnecessary resets.

Contestant files are copied with standard `docker cp` before agent execution;
trusted setup assigns solver ownership and records hashes/modes. Staging uses the
remaining attempt deadline. There is no startup venv or custom archive transfer.

### Commands and output

`run_command` accepts `command` and optional `timeout_seconds`, up to the configured
maximum (120 seconds). Each call starts a new `/bin/sh` in `/workspace` and returns
bounded stdout/stderr, exit code, timeout status and observed output-byte count.
Use `bash` explicitly for Bash syntax. There are no PTYs, session IDs, polling or
cross-call input. A script can perform a complete target interaction within one
command; the model cannot inspect and respond midway through that same process.
Background processes may continue until a timeout reset or final cleanup.

Output up to the configured raw-byte limit is returned whole. Larger output keeps
the beginning/end and sets `truncated: true`; invalid UTF-8 bytes render as
replacement characters. No automatic output files/copies are created. Redirect
output to a workspace file when later inspection matters. Traces preserve exactly
the observations returned to the model; they do not claim to retain omitted output.
A timeout event retains captured partial output even if recovery fails.

### Read results

Each invocation prints a fresh record directory:

| Artifact | Meaning |
| --- | --- |
| `run.json` | Settings, dataset/source/image provenance, split label, result, trace URL, export audit, total time. |
| `<run-id>/packages-initial.json` | Initial installed Python versions. An optional final inventory may be unavailable after terminal stop; availability is traced. |
| `<run-id>/summary.json` | Stop reason, verified success, counts, available tokens/cost, timing, solver restart count, cleanup errors. |
| `observations.json` | Complete native hosted trace export containing model/tool inputs and outputs; older records use `cli-observations.json`. |
| `public-task.json`, `target/` | Public task and trusted target runtime configuration/lifecycle record. |

`verified_success` means trusted verification accepted a candidate.
`evidence_complete` means the launch's hosted trace audit passed. They describe
different outcomes. Historical records may contain `cost_reserved_usd`; new runs
retain usage/cost estimates without reservations. Cached/reasoning tokens are
subsets of input/output totals. Unknown usage
is not reported as free: if any response lacks usage, `usage_complete` is false
and aggregate `tokens`/`cost_usd` are null. Native generation observations still
retain usage from responses that supplied it. Records under `runs/` are Git-ignored; preserve the runs
you use in your report.

The launcher uses the existing Langfuse Python client to retrieve every cursor
page, then checks observation counts, completion, parentage, secrets and cleanup.
No Node/npm installation is needed. Package inventories are captured at startup
and attempted at final cleanup; per-tool scans are removed. Installation activity
remains in tool traces. Historical runs retain their old package/output artifacts.

The `.venv/`, `.env`, Docker images, `datasets/` and `runs/` are local setup or
outputs, not files supplied by a GitHub clone. Historical evidence under `evidence/`
can contain paths from the original verification machine. Those paths document
the old runs; teammates do not need to recreate them or run the archived Compose
files. Use the current commands above to create fresh local records.

The first user-run development attempt had six model calls and six tool calls,
cost an estimated $0.00118394, and stopped at the 10-second command cap. Attempt
time was 51.8 seconds; launch time was 59.8 seconds. It had complete saved trace
evidence and no verified success. See [status](PROJECT_STATUS.md).

If a solver/guard image is missing, rerun `build-images`. If contestant files are
missing, materialize their indexed directory. Unsupported Compose arrangements
fail before model execution and need review. A model/CLI error is recorded in
`run.json`; inspect that record before repeating paid calls.

Existing identifiers are in `run.json`: `challenge_id`, `result.run_id`,
`provenance.commit` and `provenance.working_tree_dirty`. Resolved settings are in
`provenance.config` and `model_settings`. Tool activity, candidate submissions and
evaluator responses are in the Langfuse trace/export; the final verdict is
`result.verified_success`. No additional attempt-ID or logging system is needed.

## How the dataset and challenge selection work

CTFTiny contains **50 challenges**. We use the `nyuctf` Python package to load
them; you do not need a separate NYU dataset. Each challenge has an ID, such as
`pwn-baby-boi`, and a directory containing its files and any service setup.

Three files have different jobs:

| File | What it tells you |
| --- | --- |
| `datasets/CTFTiny/ctftiny.json` | The dataset's public index: every challenge ID, category and directory. |
| [configs/ctftiny.json](configs/ctftiny.json) | Our selection: which IDs are `development` and which are `scored`. |
| [configs/development.toml](configs/development.toml) | How the agent runs: model, time limits, request limits and token allowances. |

**The split is already set for you.** Open `configs/ctftiny.json` and look under:

- **`development` — 40 challenges:** use these to practice, inspect failures and
  test changes during Section 2. `pwn-baby-boi` is in this list.
- **`scored` — 10 challenges:** save these for the later frozen evaluation.

We have **not selected a separate set of ten development challenges**, and the
assignment does not require one. You can start with one or two from the development
list. The agent and command are the same for both groups; the challenge ID determines
the result label automatically. The name `development.toml` does not choose the group.

Both groups contain all six categories:

| Category | Development | Scored |
| --- | ---: | ---: |
| Crypto | 10 | 2 |
| Forensics | 1 | 1 |
| Misc | 4 | 2 |
| Pwn | 8 | 3 |
| Reverse engineering | 15 | 1 |
| Web | 2 | 1 |

The ten scored IDs were selected by a fixed hash of their IDs, without reading
answers or solutions. **The selection is not balanced by difficulty**: the index
has no difficulty ratings, and we have not established how hard each challenge is.

The setup below downloads **all 50 challenge directories once**. After that, choose
challenges by ID without a separate download step. Dataset files are local to each
teammate's machine and are not included in this repository. Downloading the files
does not run or solve them, and does not change the development/scored split.
The recorded setup now has all 50 directories and validated file inventories.
Environment checks passed for the ten scored challenges and five development IDs:
`pwn-baby-boi`, `cry-ecxor`, `cry-describeme`, `msc-algebra` and `web-shreeramquest`.
`msc-showdown` remains unsupported because its supplied setup requires privileged
Docker access. Other environments still need their preparation checks.

## Architecture and tool contracts

The trusted host loads `CTFChallenge`, owns the answer key and target lifecycle,
and passes only public description, listed file names, and allowed endpoints to
the agent. `run_agent(public_task, respond, call_tool)` retains public conversation
history, executes tool requests sequentially, adds observations, and asks the
model again. Native Responses output items are replayed between requests. A
verified submission stops immediately; text-only replies end without success.

| File | Responsibility |
| --- | --- |
| `__main__.py`, `launch.py` | CLI, host clients, one real attempt, provenance and trace export. |
| `challenge.py` | Package loading, explicit public fields, file staging, supplied target/network lifetime. |
| `agent.py` | Conversation loop, Responses adapter, request limits and usage. |
| `attempt.py` | Trusted evaluator, hard limits/watchdog, tool/response bounds, final summary. |
| `tools.py` | Three tool definitions, validation, solver dispatch. |
| `sandbox.py`, `docker.py` | Solver/guard lifecycle, denial monitoring, bounded Docker communication. |
| `config.py` | Non-secret settings and validation. |
| `docker/guard.py` | Independent namespace firewall; the solver needs no custom daemon. |
| `tests/` | Test substitutes, synthetic targets, controls and preparation checks. |

| Tool | Input and validation | Output, timeout, errors |
| --- | --- | --- |
| `run_command` | Nonempty `/bin/sh` command up to 16 KiB; optional finite positive timeout within the configured maximum. | Bounded head/tail stdout/stderr, exit code, observed byte count and truncation/timeout status. Timeout restarts all solver processes; files survive. |
| `write_file` | Workspace-relative path without traversal/NUL; UTF-8 content at most 64 KiB. One-shot solver Python code rejects symlinks/races. | Path/bytes-written or error observation; bounded by command/attempt time; timeout resets solver processes. |
| `submit_flag` | Nonempty candidate, at most 4,096 UTF-8 bytes. | Candidate/verdict recorded; exact host-side equality. Wrong submissions permit continuation; success stops. No subprocess, bounded by attempt deadline. |

Unknown tools/invalid arguments return validation observations and consume tool
budget. The model's tool schema includes the actual configured timeout maximum
and default (currently 120 seconds for ordinary live commands); validation errors repeat that cap.
Docker/recovery failures are terminal; ordinary program exits remain observations. The evaluator never separately
reveals the expected answer in prompts, results, or traces.

Commands execute only in the non-root writable solver with no effective
capabilities, host mounts, socket, credentials, evaluator files, or private
challenge/build metadata. Only CHOWN remains in the capability ceiling for trusted
file ownership setup; model commands have no effective capabilities and cannot
gain them (`no-new-privileges`). The separate trusted guard restricts connections to
assigned endpoints, Docker DNS and public HTTPS for the approved pip policy;
independent packet-denial evidence triggers solver stopping.
Targets retain supplied Compose commands, permissions, service relationships and
resource settings on fresh project-owned ordinary bridges/volumes. We remove host
port publishing and shared-daemon socket mounts, recording adjustments in
`target/target.json`. Supplied hostnames work through Docker DNS; descriptions are
not rewritten to IPs. The guard joins the challenge-facing bridge directly; there
is no extra egress bridge, manual route or synthetic gateway.

Targets regain normal Docker network/capability defaults; the previous forced
256 MiB/CPU/PID/tmpfs/permission policy is removed. Solver limits remain unchanged.
Read-only binds/config files inside the challenge directory are accepted but require
Docker host file sharing. Writable host binds and external/custom storage need an
explicit reset strategy and fail clearly. Privileged/shared-daemon administrative
setups remain unsupported; no model tool provides a target administrative shell.
The guard still restricts direct solver traffic and retains denial evidence.

Langfuse is the sole detailed tracing system. Native model generations, tools,
incidents, stopping and cleanup are recorded; ordinary local result/provenance
files remain. SDK flushing alone does not establish delivery; the launcher reads
back and audits hosted observations. Tool results and visible assistant text show
the observable decisions. `reasoning.summary: auto` is requested, but the approved
benign check returned no readable summary. Encrypted reasoning is not readable.
A later user-run development trace returned native readable summaries in three
of seven replies; their presence can vary between requests.
See [reasoning evidence](evidence/reasoning-summaries/README.md).

The system prompt also asks for one brief visible sentence alongside each tool
call stating its purpose or what it will test. Look for that sentence in the
`model-response` generation's output in Langfuse. Existing instrumentation captures
it as normal assistant text in the same request; no extra model turn, tool or
response format was added. This is a requested action explanation, not private
internal reasoning. The wording can affect responses and adds a small amount of
text. The latest reviewed development run included visible explanations in all
seven model replies; future compliance is not guaranteed.

## Verification and Section 2 handoff

```sh
uv run --frozen python -m pytest -q
uv run --frozen python -m ctf_agent self-check
```

The current target/network checkpoint passed **100 offline tests and 29 synthetic
Docker cases**, with cleanup verified. Preparation passed two fresh cycles each
for development `pwn-baby-boi`, `web-shreeramquest` and `cry-ecxor`, including
supplied hostname resolution, private boundaries and denied traffic.
[Current evidence](evidence/target-network-simplification/README.md).
The infrastructure-only inventory accepts 26 of 27 supplied Compose definitions;
`msc-showdown` remains unsupported. This is not runtime readiness for all 26.
Read-only target binds have offline validation only; Docker Desktop rejected those
mounts here. The synthetic named-volume/backend checks passed in Docker.
No live model calls or hosted traces were created; SDK export remains verified
offline and its earlier hosted readback is preserved in historical evidence.

The earlier Section 1 handoff separately prepared the ten reserved challenges plus
`pwn-baby-boi`: two fresh cycles each, file hashes/ownership, permitted TCP
connect-and-close, private boundaries, denied traffic and solver stopping, reset
and cleanup. Those checks read no target response contents. Run Docker checks
sequentially because cleanup uses a shared project label. Run each preparation as
its own CLI process.

Other explicit checks: `langfuse-check` uploads a scripted synthetic trace with no
model calls; `model-check` makes paid synthetic model calls and requires a budget.
Neither is needed before each development attempt. Historical records are under
[evidence](PROJECT_STATUS.md#evidence).

Before the execution replacement, all ten reserved challenges and five development examples passed preparation
through the shared command. All 50 file inventories were checked after downloading
the full pinned dataset. The remaining 35 environments have not passed runtime
preparation, including the known unsupported privileged target `msc-showdown`.
Separate [solver checks](evidence/solver-readiness/README.md) cover baseline utilities
and benign executable handling; they do not establish compatibility with every
contestant binary or specialized tool requirement. Solve rate and longer-run
reliability are not established by preparation. Section 2
belongs to your development experiments: inspect traces, write a hypothesis, test
a change and run a small pilot before freezing the held-out evaluation setup.
The newer course guide calls for one fixed configuration, three fresh attempts
per selected challenge, per-challenge success/sample-SD/token/time metrics, a
1–3 page report and an autonomous demo that need not solve. These guide statements
are distinct from the professor's three implementation approvals; the older
Canvas wording remains preserved in ASSIGNMENT.md. See
[course guidance](docs/REFERENCES.md#evaluation-guidance-stated-in-the-pdf).
Existing records need deliberate aggregation/timing alignment before reporting;
this documentation update does not implement metrics or start evaluation.

Work so far is attributed to **Ryan Banko**. OpenAI Codex assisted with design,
implementation, review and verification. The [five original resources and citations](docs/REFERENCES.md)
include NYU's package/docs and reference agents, Duke's gateway guide, and later
Langfuse/OpenAI guidance. The reference agent framework was not vendored.
[DESIGN.md](docs/DESIGN.md) records decisions and alternatives. The original
[assignment](ASSIGNMENT.md) remains authoritative.
