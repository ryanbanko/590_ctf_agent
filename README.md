# CTFTiny agent — CYBERSEC 590 Assignment 4

Setup and run instructions for the agent. Architecture, experiments and results are in
the report, [docs/REPORT.md](docs/REPORT.md).

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

## Selected configuration

The configuration used for the scored runs and the competition is
[configs/development.toml](configs/development.toml), the default, with the code at commit
`aedfd62`:

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

## Choosing a challenge

[configs/ctftiny.json](configs/ctftiny.json) splits the 50 challenges into two lists:
- `development` (40): use these for testing.
- `scored` (10): held out. Never run them during development.

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
