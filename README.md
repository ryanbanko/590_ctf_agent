# CTFTiny agent benchmarking

A bounded model/tool agent for [the assignment](ASSIGNMENT.md), using `nyuctf`
for CTFTiny loading, an isolated solver, trusted verification and Langfuse tracing.
The ten scored challenges are reserved; use the forty development IDs in
[configs/ctftiny.json](configs/ctftiny.json) for practice and Section 2.

[Project checklist](PROJECT_STATUS.md#assignment-checklist) ·
[Design](docs/DESIGN.md) · [Section 2 experiments](docs/EXPERIMENTS.md) ·
[References and attribution](docs/REFERENCES.md)

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
Compose v2, and Node.js/npm for native Langfuse trace export. Start Docker before
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

These are baseline utilities, not every specialized analysis package. Add any
needed packages to the solver Dockerfile and rebuild before a run; the solver
has no internet access to install packages during an attempt. `curl` and `nc`
can reach only assigned challenge endpoints, just like Python sockets.

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
infrastructure incidents, and response-source/missing-usage failures stop the
batch for review. Ctrl-C forwards interruption to the current launcher and waits
for its cleanup; the partial index remains. There is no automatic retry or resume.
Do not edit code or rebuild images during a batch. The wrapper snapshots the
experiment file and otherwise uses the existing per-attempt controls; there is
no added batch-cost gate.

Two different development challenges per category would give **11 IDs**: crypto,
miscellaneous, pwn, reversing and web can each supply two, but forensics has only
`for-1black0white`. Keep the other forensics challenge in the reserved scored set.
No 11-challenge pilot has been selected or run automatically.

### Optional command settings

Optional arguments: `--experiment` (default `configs/development.toml`),
`--dataset`, `--manifest`, and `--output` (default `runs/challenges`).
`prepare-challenge` accepts `--dataset`, `--manifest`, and `--output`; it saves
under `runs/` by default. The top-level `--config` applies to setup/check commands;
the live command uses `--experiment`.

### Limits and estimated cost

| Limit | Current live settings |
| --- | --- |
| Whole attempt | 300 seconds, including solver preparation; cleanup/export add time. |
| One command or file operation | Up to 30 seconds, clipped to remaining attempt time. |
| Model request | Up to 30 seconds; no client retries. |
| Model / tool calls | 20 / 40 maximum. |
| Model input / output | 256 KiB serialized input; 2,048 output tokens per request. |
| Solver resources | 1 CPU, 256 MiB memory, 64 PIDs, 64 MiB workspace. |
| Tool output / file write | 32 KiB combined stdout/stderr; 64 KiB UTF-8 write. |
| Estimated cost cap | $0.10 per attempt. |

Edit `[attempt]` and `[model]` in `configs/development.toml` for your Section 2
experiments; inherited defaults live in `ctf_agent/config.py`. Entries in `[attempt]`
override those defaults, so `max_tool_calls = 40` overrides the default of 20.
The numeric limits above are our configurable choices; the assignment requires
enforced bounds but does not prescribe those values.
A command timeout currently ends the attempt. The user approved these larger
development limits after the initial setup checks; historical attempts used the
previous settings. Both `max_model_turns` and `max_requests` are set to 20.
The command cap remains 30 seconds: recent failure evidence showed blocking
network I/O, not a computation that needed longer. Use connection/read deadlines
shorter than the command cap. Each command starts a new process; files persist
between commands, but an earlier process's connection does not automatically persist.
For a later experiment, change `command_seconds` in `[attempt]`; the tool schema
automatically advertises the new maximum/default. Synthetic checks retain their
separate 10-second/16-KiB defaults unless overridden by a specific check.
The conservative reservation for twenty maximum-sized requests is about $0.678
at the recorded gateway rates. The $0.10 cap still applies and can stop an attempt
before all twenty requests; actual costs depend on usage. There is no campaign
budget system. The existing per-attempt controls and provider limits apply;
the batch wrapper adds no separate spending gate.

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
| `docker/worker.py`, `docker/guard.py` | Operations inside the solver and independent namespace firewall. |
| `tests/` | Test substitutes, synthetic targets, controls and preparation checks. |

| Tool | Input and validation | Output, timeout, errors |
| --- | --- | --- |
| `run_command` | `/bin/sh` command, no NUL, nonempty and at most 16 KiB; optional positive timeout within the command cap. Use `bash` explicitly for Bash syntax. | Bounded stdout/stderr, exit code and truncation metadata. Nonzero exit is an observation; timeout stops the attempt and solver. |
| `write_file` | Workspace-relative path without traversal/NUL; UTF-8 content at most 64 KiB. Worker independently rejects symlinks/races. | Path/bytes-written or error observation; same bounded worker timeout as commands. |
| `submit_flag` | Nonempty candidate, at most 4,096 UTF-8 bytes. | Candidate/verdict recorded; exact host-side equality. Wrong submissions permit continuation; success stops. No subprocess, bounded by attempt deadline. |

Unknown tools/invalid arguments return validation observations and consume tool
budget. The model's tool schema includes the actual configured timeout maximum
and default (currently 30 seconds for live runs); validation errors repeat that cap.
Worker/Docker failures are terminal. The evaluator never separately
reveals the expected answer in prompts, results, or traces.

Commands execute only in the non-root solver with a read-only root and bounded,
executable workspace tmpfs,
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

All ten reserved challenges and five development examples passed preparation
through the shared command. All 50 file inventories were checked after downloading
the full pinned dataset. The remaining 35 environments have not passed runtime
preparation, including the known unsupported privileged target `msc-showdown`.
Separate [solver checks](evidence/solver-readiness/README.md) cover baseline utilities
and benign executable handling; they do not establish compatibility with every
contestant binary or specialized tool requirement. Solve rate and longer-run
reliability are not established by preparation. Section 2
belongs to your development experiments: inspect traces, write a hypothesis, test
a change and run a small pilot before freezing the held-out evaluation setup.
The full assignment also needs metrics, report and a real successful-run demo.

Work so far is attributed to **Ryan Banko**. OpenAI Codex assisted with design,
implementation, review and verification. The [five original resources and citations](docs/REFERENCES.md)
include NYU's package/docs and reference agents, Duke's gateway guide, and later
Langfuse/OpenAI guidance. The reference agent framework was not vendored.
[DESIGN.md](docs/DESIGN.md) records decisions and alternatives. The original
[assignment](ASSIGNMENT.md) remains authoritative.
