# CTFTiny agent benchmarking

An initial agent for [Section 1 of the assignment](ASSIGNMENT.md): a model observes
tool results and chooses subsequent actions, commands run in an isolated solver,
and a trusted evaluator verifies submissions. Langfuse records model/tool activity.
CTFTiny is the active benchmark; `nyuctf` supplies the existing dataset format and
loader. No separate agent framework is used.

**Section 1 setup is complete for the selected ten challenges and the development
example.** Preparation passed for all eleven, including file staging, permitted
connections, enforced network denial, fresh reset, and cleanup. These were
zero-model setup checks, not solves. One earlier user-run development attempt
made six model/tool calls and ended on a command timeout. A synthetic autonomous
success is recorded; a real successful-run demo and Sections 2–3 remain ahead.
See the [assignment checklist](PROJECT_STATUS.md#assignment-checklist) and
[setup evidence](evidence/benchmark-readiness/README.md).

## How the dataset and challenge selection work

CTFTiny contains **50 challenges**. We use the `nyuctf` Python package to load
them; you do not need a separate NYU dataset. Each challenge has an ID, such as
`pwn-baby-boi`, and a directory containing its files and any service setup.

Three files have different jobs:

| File | What it tells you |
| --- | --- |
| `datasets/CTFTiny/ctftiny.json` | The dataset's public index: every challenge ID, category and directory. |
| [configs/ctftiny.json](configs/ctftiny.json) | Our selection: which IDs are `development` and which are `scored`. |
| [configs/development.toml](configs/development.toml) | How the agent runs: model, time limits, request limits and estimated cost cap. |

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

The public index lists all 50 even when only some challenge directories have been
downloaded. Our current checkout uses Git's *sparse checkout*, which downloads
selected directories. The ten scored directories and `pwn-baby-boi` are available
and have passed environment checks. The other 39 development directories may need
downloading before use. Those setup checks did not attempt to solve the scored set.

## One-time setup

**This setup has already been done in the current workspace.** For your next
attempt, start Docker and skip to [Choose and run a challenge](#choose-and-run-a-challenge).
The instructions here are for a fresh checkout or missing dependencies/images.

Run commands in a terminal from this repository's root. Use Python **3.13.2**, uv,
Docker Desktop/Engine with Linux containers and Compose v2, and Node.js/npm for
native Langfuse trace export.

```sh
uv sync --frozen
uv run --frozen python -m ctf_agent build-images
```

Dependencies are locked: Langfuse 5.1.0, OpenAI 3.44.0, nyuctf 1.1.1, and pytest
9.2.0 for development. Start Docker before building or preparing challenges.

Create `.env` from `.env.example` if needed. Fill these host-only variables:

| Variable | Source |
| --- | --- |
| `LITELLM_TOKEN` | Your Duke AI Gateway key from the [Duke dashboard](https://dashboard.ai.duke.edu/). |
| `LANGFUSE_PUBLIC_KEY` | Intended Langfuse project's API key settings. |
| `LANGFUSE_SECRET_KEY` | Same project's key pair. |
| `LANGFUSE_BASE_URL` | Project's regional URL, e.g. `https://us.cloud.langfuse.com`. |

Keep `.env` private and Git-ignored. The configured Duke gateway does not require
a separate `OPENAI_API_KEY`. Preparation and local tests need no keys.

For a fresh workspace, download the recorded dataset version and the first
development challenge:

```sh
git clone --depth 1 --filter=blob:none --sparse https://github.com/NYU-LLM-CTF/CTFTiny.git datasets/CTFTiny
git -C datasets/CTFTiny fetch --depth 1 origin f1c9531672c45b24b7fb5f3aa44a7ac33d3602f8
git -C datasets/CTFTiny checkout --detach FETCH_HEAD
git -C datasets/CTFTiny sparse-checkout set ctftiny/pwn/baby_boi
```

The long revision identifies the exact dataset version we recorded. Keep that
checkout unchanged. Additional challenge directories can be downloaded later,
as described below. All dataset files remain host-side; only listed contestant
files enter the solver. Do not consult evaluation flags, solutions or write-ups.

## Choose and run a challenge

For the current workspace, use these steps in your IDE terminal.

**1. Start Docker Desktop and open the project directory.**

```sh
cd /Users/ryanbanko/590_final
```

**2. Choose an ID from the `development` list in
[configs/ctftiny.json](configs/ctftiny.json).** Start with `pwn-baby-boi`, which is
already downloaded and checked. Replace that ID in the commands below when you
choose another challenge.

**3. Check the challenge environment.** This starts fresh containers, checks files,
connections, isolation and cleanup, then exits. It makes no model requests and
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

`run-challenge` replaces `run-development`. It loads the selected challenge,
starts fresh supplied services if present, stages its listed files, runs the same
model/tool loop, verifies submissions, stops at a limit or final result, cleans
up, and exports the Langfuse trace. File-only challenges follow this same path
without a target service. Missing service images are pulled for AMD64 by default;
each attempt records and uses their resolved local image IDs. Docker emulation
was checked for the selected AMD64 services on this ARM64 host.

**5. Read the results.** The command prints a new directory under
`runs/challenges/`. Open its `run.json` for the outcome and Langfuse trace URL;
use the trace to follow model calls, tool arguments and results. See
[Read results](#read-results) for the saved files and field meanings.

### Download another development challenge

Look up its ID in the public `datasets/CTFTiny/ctftiny.json` index and find its
`path`. The ID used by the agent and the directory path can differ. For example,
`pwn-bigboy` has path `ctftiny/pwn/bigboy`. Download that directory with:

```sh
git -C datasets/CTFTiny sparse-checkout add ctftiny/pwn/bigboy
```

Then use `--challenge pwn-bigboy` in the preparation and run commands above. This
is another development ID; its environment has not been verified yet. Downloading
files alone does not establish launch readiness or trigger a model request.

To download every directory instead, use
`git -C datasets/CTFTiny sparse-checkout disable`. This may download large assets;
you do not need the whole dataset to run one challenge.

### Optional command settings

Optional arguments: `--experiment` (default `configs/development.toml`),
`--dataset`, `--manifest`, and `--output` (default `runs/challenges`).
`prepare-challenge` accepts `--dataset`, `--manifest`, and `--output`; it saves
under `runs/` by default. The top-level `--config` applies to setup/check commands;
the live command uses `--experiment`.

### Limits and estimated cost

| Limit | Current live settings |
| --- | --- |
| Whole attempt | 120 seconds, including solver preparation; cleanup/export add time. |
| One command or file operation | Up to 10 seconds, clipped to remaining attempt time. |
| Model request | Up to 20 seconds; no client retries. |
| Model / tool calls | 8 / 20 maximum. |
| Model input / output | 32 KiB serialized input; 2,048 output tokens per request. |
| Solver resources | 1 CPU, 256 MiB memory, 64 PIDs, 64 MiB workspace. |
| Tool output / file write | 16 KiB output; 64 KiB UTF-8 write. |
| Estimated cost cap | $0.10 per attempt. |

Edit `[attempt]` and `[model]` in `configs/development.toml` for your Section 2
experiments; inherited defaults live in `ctf_agent/config.py`. A command timeout
currently ends the attempt. Settings were not increased during this setup work.
The conservative reservation for eight maximum-sized requests is about $0.042
at the recorded gateway rates; actual costs depend on usage. There is no campaign
budget system. Review saved usage between attempts; the user's planning ceiling
for assistant-started work is under $0.50. No paid call was made in this milestone.

### Read results

Each invocation prints a fresh record directory:

| Artifact | Meaning |
| --- | --- |
| `run.json` | Settings, dataset/source/image provenance, split label, result, trace URL, export audit, total time. |
| `<run-id>/summary.json` | Stop reason, verified success, counts, available tokens/cost, timing, cleanup errors. |
| `cli-observations.json` | Native hosted trace export containing model/tool inputs and outputs. |
| `public-task.json`, `target/` | Public task and trusted target runtime configuration/lifecycle record. |

`verified_success` means trusted verification accepted a candidate.
`evidence_complete` means the launch's hosted trace audit passed. They describe
different outcomes. `cost_reserved_usd` is a conservative reservation, not another
charge. Cached/reasoning tokens are subsets of input/output totals. Unknown usage
is not reported as free. Records under `runs/` are Git-ignored; preserve the runs
you use in your report.

The first user-run development attempt had six model calls and six tool calls,
cost an estimated $0.00118394, and stopped at the 10-second command cap. Attempt
time was 51.8 seconds; launch time was 59.8 seconds. It had complete saved trace
evidence and no verified success. See [status](PROJECT_STATUS.md).

If a solver/guard image is missing, rerun `build-images`. If contestant files are
missing, materialize their indexed directory. Unsupported Compose arrangements
fail before model execution and need review. A model/CLI error is recorded in
`run.json`; inspect that record before repeating paid calls.

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
| `docker/worker.py`, `docker/guard.py` | Operations inside the solver and independent namespace firewall. |
| `tests/` | Test substitutes, synthetic targets, controls and preparation checks. |

| Tool | Input and validation | Output, timeout, errors |
| --- | --- | --- |
| `run_command` | Nonempty command, no NUL, at most 16 KiB; optional positive timeout within the command cap. | Bounded stdout/stderr, exit code and truncation metadata. Nonzero exit is an observation; timeout stops the attempt and solver. |
| `write_file` | Workspace-relative path without traversal/NUL; UTF-8 content at most 64 KiB. Worker independently rejects symlinks/races. | Path/bytes-written or error observation; same bounded worker timeout as commands. |
| `submit_flag` | Nonempty candidate, at most 4,096 UTF-8 bytes. | Candidate/verdict recorded; exact host-side equality. Wrong submissions permit continuation; success stops. No subprocess, bounded by attempt deadline. |

Unknown tools/invalid arguments return validation observations and consume tool
budget. Worker/Docker failures are terminal. The evaluator never separately
reveals the expected answer in prompts, results, or traces.

Commands execute only in the non-root, read-only solver, with bounded tmpfs,
no capabilities, host mounts, socket, credentials, evaluator files, or private
challenge/build metadata. The separate trusted guard restricts connections to
assigned endpoints; independent packet-denial evidence triggers solver stopping.
Targets use fresh isolated internal networks, no published ports or host mounts,
resource limits, and disposable writable layers. Ordinary target startup permits
CHOWN/SETUID/SETGID; model tools have no administrative target shell. Supplied
Compose arrangements outside the reviewed image/network conventions fail closed.

Langfuse is the sole detailed tracing system. Native model generations, tools,
incidents, stopping and cleanup are recorded; ordinary local result/provenance
files remain. SDK flushing alone does not establish delivery; the launcher reads
back and audits hosted observations. Tool results and visible assistant text show
the observable decisions. `reasoning.summary: auto` is requested, but the approved
benign check returned no readable summary. Encrypted reasoning is not readable.
See [reasoning evidence](evidence/reasoning-summaries/README.md).

## Verification and Section 2 handoff

```sh
uv run --frozen python -m pytest -q
uv run --frozen python -m ctf_agent self-check
```

The fast suite has 63 cases. `self-check` runs 19 synthetic Docker cases and saves
JUnit/provenance/cleanup records. The current milestone instead ran focused real
preparation for the ten reserved challenges plus `pwn-baby-boi`: two fresh cycles
each, file hashes/ownership, permitted TCP connect-and-close, private boundaries,
independent denied traffic and solver stop, reset and cleanup. No target response
contents were read. Run Docker checks sequentially because cleanup uses a shared
project label. Run each preparation as its own CLI process.

Other explicit checks: `langfuse-check` uploads a scripted synthetic trace with no
model calls; `model-check` makes paid synthetic model calls and requires a budget.
Neither is needed before each development attempt. Historical records are under
[evidence](PROJECT_STATUS.md#evidence).

All ten reserved challenges and the development example can be prepared and
launched through the shared command. The other 39 indexed entries have not had
infrastructure checked. Solver tooling, AMD64 contestant-binary execution, solve
rate and longer-run reliability are not established by preparation. Section 2
belongs to your development experiments: inspect traces, write a hypothesis, test
a change and run a small pilot before freezing the held-out evaluation setup.
The full assignment also needs metrics, report and a real successful-run demo.

Work so far is attributed to **Ryan Banko**. OpenAI Codex assisted with design,
implementation, review and verification. The [five original resources and citations](docs/REFERENCES.md)
include NYU's package/docs and reference agents, Duke's gateway guide, and later
Langfuse/OpenAI guidance. The reference agent framework was not vendored.
[DESIGN.md](docs/DESIGN.md) records decisions and alternatives. The original
[assignment](ASSIGNMENT.md) remains authoritative.
