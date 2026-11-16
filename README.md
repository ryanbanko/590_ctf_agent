# CTFTiny agent — CYBERSEC 590 Assignment 4

Setup and run instructions for the agent. [DESIGN](docs/DESIGN.md) describes the
current architecture; [EXPERIMENTS](docs/EXPERIMENTS.md) records tests and results.
The [Part 1 report](docs/REPORT.md) is the preserved submission snapshot; later
development updates are recorded in the current status and linked evidence.

For development or agent handoff, start with [current status](PROJECT_STATUS.md)
and the [working agreement](AGENTS.md). [Project history](docs/PROJECT_HISTORY.md)
preserves milestones; [experiments](docs/EXPERIMENTS.md) holds detailed test records.
The [historical development guide](docs/DEVELOPMENT_GUIDE.md) preserves our longer
November 11 README; use this README for current setup and commands.
The [target-listener handoff](docs/TARGET_PROCESS_ISSUE.md) records the implemented
listener correction and its verification.

## Requirements

- **Docker:** Linux or macOS with Docker Engine or Docker Desktop (Linux containers,
  Compose v2).
  - The `docker` command must work for your user without `sudo`.
  - The image evaluation passed with 8 GiB of memory assigned to Docker.
  - The solver image is about 11.5 GB; challenge target images are pulled as needed.
- **Python:** [uv](https://docs.astral.sh/uv/). `uv sync` installs Python 3.13.2,
  pinned in `.python-version`, if it is not already present.
- **Git**, for the dataset download.
- **Model access:** a Duke AI Gateway key. Model requests require the Duke VPN.
- **Tracing:** API keys for the team Langfuse project.

The solver image is Linux AMD64. On Apple Silicon or ARM Linux, Docker runs it under
emulation. Run every command below from the repository root.

## Setup

**1. Install dependencies.** Versions are pinned in `uv.lock`: Langfuse 5.1.0,
OpenAI 3.44.0, nyuctf 1.1.1, and pytest 9.2.0 for tests.

```sh
uv sync --frozen
```

**2. Build the images.** Start Docker first. This builds three images: the solver
(NYU's CTF Bench tool recipe plus small additions), the network guard, and a
synthetic target used by the self-checks. The first build can take tens of minutes.

```sh
uv run --frozen python -m ctf_agent build-images
```

A source build can pull newer versions of upstream tools. To use the exact solver
image from our runs instead, get the archive `ctf590-solver-nyu-integrated-20261107.tar`
(2,938,163,200 bytes) from a team member; it is not in Git. Check that its SHA-256 is
`249c1aa8a0a58744753f2d5d68febb189a3c6918e3856cef3ebfa11ee9af8979` (recorded in
[frozen-image.json](evidence/nyu-solver-integration/frozen-image.json)):

```sh
sha256sum ctf590-solver-nyu-integrated-20261107.tar
```

On macOS, use `shasum -a 256` instead. Then load it and build the two small images:

```sh
docker load -i ctf590-solver-nyu-integrated-20261107.tar
docker build -f docker/guard.Dockerfile -t ctf590-guard:m1 .
docker build -f docker/fixture.Dockerfile -t ctf590-fixture:m1 .
```

For the two affected roppity/baby-boi target images, preparation automatically
builds and caches a listener-only correction using a checksum-pinned Ubuntu socat
1.7.3.3 package. The first use needs host internet access for that small download;
startup commands, target libraries and application files stay as supplied. Other
target images are unchanged. [Details and verification](evidence/listener-update/README.md).

**3. Add credentials.** Copy the template, then fill in the four values below. `.env`
is Git-ignored and stays on the host: it is never copied into the solver container.
Each run's trace export is checked to confirm that `LITELLM_TOKEN` and
`LANGFUSE_SECRET_KEY` do not appear in it. Do not commit keys to the repository.

```sh
cp -n .env.example .env
```

| Variable | Value |
| --- | --- |
| `LITELLM_TOKEN` | Your own key from the [Duke AI dashboard](https://dashboard.ai.duke.edu/) |
| `LANGFUSE_PUBLIC_KEY` | The team project's public key, from the project's API Keys settings in Langfuse. Ask a team member with access to the project. |
| `LANGFUSE_SECRET_KEY` | The secret key from the same key pair |
| `LANGFUSE_BASE_URL` | `https://us.cloud.langfuse.com`, the team project's region |

**4. Download the pinned dataset** (all 50 challenges). The runner checks this revision
and the index hash before every attempt, so leave the checkout unchanged.

```sh
git clone --depth 1 --filter=blob:none --no-checkout https://github.com/NYU-LLM-CTF/CTFTiny.git datasets/CTFTiny
```

```sh
git -C datasets/CTFTiny fetch --depth 1 origin f1c9531672c45b24b7fb5f3aa44a7ac33d3602f8
```

```sh
git -C datasets/CTFTiny checkout --detach FETCH_HEAD
```

If you already have an older sparse checkout, run
`git -C datasets/CTFTiny sparse-checkout disable` instead.

**5. Verify the installation.** Neither command makes model calls. `pytest` runs the
offline tests. `self-check` starts real containers against the synthetic target and
checks isolation, blocked traffic, timeouts, output limits, flag verification and
cleanup. Run Docker checks one at a time.

```sh
uv run --frozen python -m pytest -q
```

```sh
uv run --frozen python -m ctf_agent self-check
```

## Current configuration and scored baseline

The current default is [configs/development.toml](configs/development.toml).
The active runtime and configuration match practice baseline `0395835`, including
the original prompt and 40 model calls. The validation/readability and planning/
notes candidates were withdrawn after review; their prompts, settings, results
and limitations remain preserved. [Latest decision and rollback verification](evidence/planning-notes/rollback/README.md).
The original Part 1 scored configuration at `aedfd62` used 40 model calls;
historical records and settings snapshots remain unchanged.

| Setting | Value |
| --- | --- |
| Model | `gpt-6-luna`, medium reasoning effort |
| Output per model response | 8,192 tokens |
| Request size cap / request timeout | 2 MiB / 90 s |
| Attempt limit / command limit | 600 s / 120 s |
| Model calls / tool calls | 40 / 80 |
| Scope recoveries | 1 |

Launch command for one challenge:

```sh
uv run --frozen --env-file .env python -m ctf_agent run-challenge --challenge <ID>
```

## Manual HTB fallback

The `feat/htb-manual` branch adds manual HTB setup and human-relayed flag
verification. It reuses the same agent, isolated Docker solver, three tools,
network guard, Langfuse tracing, usage accounting and cleanup. MCP integration
is not implemented in this milestone. CTFTiny commands/defaults remain available.

**Prepare a task.** In HTB, copy the full public description, download the
contestant files, and spawn an instance if the challenge requires one. Then run:

```sh
uv run --frozen python -m ctf_agent setup-manual
```

The prompts request a name, category, multiline description (finish with a line
containing only `.`), ZIP/folder path, and assigned IPv4 address/port/protocol.
Leave the file path blank for no files; leave the address blank when all endpoints
have been entered. Multiple assigned endpoints are supported. Public hostnames,
URLs and IPv6 are not endpoint inputs; use the assigned IPv4 address and port.

Review the displayed task and file list, then save it. This command makes no
Docker, model, gateway, Langfuse or HTB requests. It prints a path such as
`runs/htb/tasks/task-<id>/task.json`, beside a `files/` folder and `import.json`.
The task has exactly `name`, `category`, `description`, `files` and `endpoints`;
file paths are relative to its sibling `files/` folder. You can edit those public
fields before running. File-only challenges use `"endpoints": []`.

ZIP import uses Python's standard library and the documented HTB password
`hackthebox`. Unsupported encryption/compression requires local extraction and
selecting the extracted folder. Imports reject traversal, symlinks, special
files, duplicate file paths and more than 10,000 files/512 MiB. Known private,
credential and build paths (including Dockerfile/Compose, `.env`, `.git` and VPN
profiles) are withheld and listed in `import.json`. Review your selection: this
is not a general detector of secrets inside arbitrary files. Select only the
downloaded contestant files, not the repository or home directory.

**Run the saved task** after Docker, `.env`, Langfuse and Duke network access are
ready. This command makes paid model calls:

```sh
uv run --frozen --env-file .env python -m ctf_agent run-manual --task runs/htb/tasks/task-<id>/task.json
```

The default [HTB configuration](configs/htb-manual.toml) allows 900 seconds,
60 model calls and 80 tool calls. All other model/resource settings match the
CTFTiny development defaults. These are starting allowances, not a measured
performance improvement or a dollar-budget guarantee. Use `--experiment FILE`
to select another complete configuration. Human input time counts toward the
same deadline, including file staging and solver startup.

When the agent calls `submit_flag`, the terminal identifies the challenge and
prints the exact candidate as a JSON string. Submit that candidate on the HTB
challenge card and enter `y` only for acceptance or `n` only for explicit
rejection. `cancel`/Ctrl-C/closed input stop without success; `error` stops as
`verification_unavailable` when the website cannot provide a verdict. Invalid
answers reprompt. The deadline remains enforced while waiting, and late verdicts
cannot create success. This is a human-relayed HTB verdict, not an independent
automated HTB verification. No local answer key is loaded.

The operator owns the remote HTB instance: the launcher neither starts nor stops
it. Respawning may change its address/port; update and review `task.json` before
starting a fresh attempt. Attempts get fresh local solvers; remote target state
is not automatically reset. The launcher creates/removes only its own local
Docker bridge, guard and solver.

HTB's [CTF guide](https://help.hackthebox.com/en/articles/5200851-ctf-user-s-guide)
distinguishes public Docker challenges (no HTB VPN) from Machines (HTB VPN).
Gateway access separately requires Duke network access. Docker-to-target routing
with the VPN still needs a live readiness check; a Docker target's assigned port,
not ping, is the appropriate connectivity check. IPv4 endpoint scope remains
enforced by the existing guard, including explicitly permitted private endpoints.
The existing public HTTPS package-download policy is unchanged.

Manual records go under `runs/htb/attempts/`: the existing `run.json`, public task,
summary and Langfuse export, plus controller-only `submissions.jsonl` containing
pending/completed submission events, candidate, challenge/run/submission IDs,
verification source and UTC timestamp. Both local-answer and external submissions
now get these records. Raw candidates stay out of the root summary; these files
are Git-ignored and are never staged into the solver. Existing structural export
checks do not guarantee that every hosted trace payload is present.

This milestone is offline-verified only. No live HTB attempt, Docker/VPN check,
paid model call or new hosted trace has been performed. See
[verification and limits](evidence/htb-manual/README.md).

## Choosing a CTFTiny challenge

[configs/ctftiny.json](configs/ctftiny.json) splits the 50 challenges into two lists:
- `development` (40): use these for testing.
- `scored` (10): the originally held-out Part 1 selection.

On November 14 the user allowed both lists for a new planning/notes practice
comparison. Previously scored tasks reused for tuning are not fresh held-out
evaluation evidence. Keep those new practice outputs separate from the original
scored records/metrics. The manifest labels stay unchanged, and the runner still
requires separate development/scored-list batches.
[Proposed comparison and baseline freeze](docs/IMPROVEMENT_OPTIONS.md#expanded-comparison-and-baseline-freeze--november-14).

The ten scored IDs are `cry-babycrypto`, `cry-collision-course`, `for-whyos`,
`msc-quantum-leap`, `msc-weak-password`, `pwn-puffin`, `pwn-slithery`,
`pwn-unlimited-subway`, `rev-rebug-2` and `web-smug-dino`.

## Running

**Check a challenge's environment** before its first live attempt on a new machine.
This starts the target, stages the files, probes the allowed endpoints, confirms
other traffic is blocked, and cleans up. It makes no model calls.

```sh
uv run --frozen python -m ctf_agent prepare-challenge --challenge pwn-baby-boi
```

**Run one attempt.** This makes paid model calls. It prints the record directory,
the stop reason, and whether the evaluator verified success.

```sh
uv run --frozen --env-file .env python -m ctf_agent run-challenge --challenge pwn-baby-boi
```

**Run a batch.** Attempts run one after another, each with a fresh process, target
and solver. `--trials N` repeats every challenge N times. A batch refuses to mix
development and scored IDs.

```sh
uv run --frozen --env-file .env python -m ctf_agent run-batch --challenges cry-ecxor msc-algebra --trials 1 --output runs/pilots/example
```

A batch moves on after ordinary failures and command timeouts. It stops for review
on any of these:
- a scope violation, guard failure or infrastructure error;
- a model API error;
- an incomplete record or a cleanup error.

There is no automatic retry or resume. Ctrl-C stops the current attempt after cleanup.

**Run the scored challenges** (10 challenges × 3 trials), from a clean checkout of the
final commit so every run records clean provenance:

```sh
uv run --frozen --env-file .env python -m ctf_agent run-batch --challenges cry-babycrypto cry-collision-course for-whyos msc-quantum-leap msc-weak-password pwn-puffin pwn-slithery pwn-unlimited-subway rev-rebug-2 web-smug-dino --trials 3 --output runs/scored
```

**Compute the report metrics** (pass@k, solve rate per run and its variance, time,
calls, tokens and cost, failed attempts included) from one or more batch
directories; extra directories are merged as resumes. For the committed scored run:

```sh
python aggregate.py batch-3480f37c9289 batch-6f25081707a3 \
    --recovered-usage evidence/scored/trace-audit.json --json evidence/scored/final_summary.json
uv run --no-project --with matplotlib==3.11.2 python plot_figures.py \
    evidence/scored/final_summary.json evidence/scored
```

`trace_audit.py` builds `trace-audit.json` from the local (git-ignored) trace
exports: it recovers usage the agent did not record and checks every tool call for
outside hosts. See [evidence/scored](evidence/scored/README.md).

**Options:**
- `--experiment FILE` selects a settings file; the default is
  [configs/development.toml](configs/development.toml). Every field is required, so
  to compare a configuration, copy the whole file.
- `--output DIR` sets where records are written.

**Other checks:**
- `langfuse-check` uploads and reads back one synthetic trace, with no model calls.
- `model-check` makes one small paid synthetic attempt to test gateway access.

## Results

Each attempt writes a new directory `challenge-<random id>/` under the output directory
(default `runs/challenges/` for `run-challenge`, `runs/batches/` for `run-batch`):

| File | Contents |
| --- | --- |
| `run.json` | Challenge ID, development/scored label, settings, commit and dirty flag, source hashes, image IDs, dataset revision, result, Langfuse trace URL, evidence checks, total seconds |
| `<run-id>/summary.json` | Stop reason, `verified_success`, model/tool calls, tokens, estimated cost, timing, solver restarts, scope incidents, cleanup errors |
| `observations.json` | Langfuse export: model responses, tool inputs and results, flag submissions and verdicts |
| `public-task.json` | Exactly what the agent was given |
| `target/` | Target configuration and lifecycle record, including state before removal. Keep it local: it can contain private values. |

For model-backed attempts, `result.known_usage` retains reported-call token/cost
subtotals and their `model_calls` count. If any request fails or lacks usage,
whole-attempt `tokens`/`cost_usd` remain null and `usage_complete` is false;
the known subtotal is not the full attempt bill. Native Langfuse costs live on
`model-response` generations; the root `attempt` span's output contains our local
estimate, which can differ because of cache-write pricing.
[Accounting verification and cost-display check](evidence/usage-preservation/README.md).

A batch writes a `batch-<random id>/` directory containing:
- one `attempt-NNN/` folder per attempt;
- `experiment.toml`: a copy of the settings it used;
- `batch.json`: one row per attempt, with outcome, run ID and trace URL.

`runs/` is Git-ignored. Sanitized copies of development runs are in
[evidence/ryan-shared-runs](evidence/ryan-shared-runs/README.md).

**For a demo**, `run.json` holds the identifiers:
- `challenge_id` and `result.run_id`;
- `provenance.commit` and `provenance.working_tree_dirty`;
- the settings, under `provenance.config` and `model_settings`.

The Langfuse trace shows the tool activity, the submission and the evaluator's verdict.

## Troubleshooting

- **Missing images:** rerun `build-images`.
- **Missing challenge files:** finish the dataset download.
- **Model or gateway errors:** they are recorded in `run.json`; read it before
  repeating paid calls.
- **`msc-showdown`** cannot run: its setup requires privileged Docker access, which
  the controls reject.
- **`web-shreeramquest` on ARM64** uses the official ARM64 build of the same MongoDB
  release. The supplied AMD64 image crashes under emulation.
- **Docker Hub pulls failing with EOF on the VPN:** disconnect for the pull, then
  reconnect before model requests.
