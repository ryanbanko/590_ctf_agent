# New development capability batch — November 11

**Execution update:** user-run `batch-8c98b0fc7e14` reached all 20 attempts,
with 14 verified successes. Its final response-source error stopped the batch.
[Detailed failure review](../../unseen-development-trace-review/README.md) and
[filtered result inventory](../../unseen-development-trace-review/review.json)
are prepared for Git sharing. Full new-batch transcripts have not been sanitized
or copied here; originals remain local. The original plan/configuration below
remain unchanged as pre-run records.

**Original preparation status: planned, not run by this preparation.** The user requested previously
untested challenges, taking the hardest available supported development entries,
up to three per category, and two fresh trials per challenge. This tests the
existing agent without changing its prompt, model, tools or held-out split.

[plan.json](plan.json) records the ten IDs, difficulty labels, selection rule,
two trials, 20 planned attempts, original split hash and configuration hash.
[experiment.toml](experiment.toml) snapshots current medium reasoning/8,192-token
settings. No model attempt on these IDs was found in saved local records at
preparation time; prior exposure elsewhere is not established.

| Category | Challenges | Upstream difficulty |
| --- | --- | --- |
| Crypto | `cry-lupin`, `cry-open-ellipti-ph`, `cry-beyond-quantum` | Hard |
| Pwn | `pwn-roppity`, `pwn-pilot`, `pwn-got-milk` | Hard |
| Reverse engineering | `rev-gibberish-check`, `rev-a-walk-through-x86-part-2`, `rev-the-big-bang` | Hard |
| Misc | `msc-android-dropper` | Easy; only remaining supported unattempted misc development entry |

No unattempted development web/forensics IDs remain. The only other unattempted
misc entry, `msc-showdown`, is Very Easy and has a separately documented unsupported
privileged setup. It is excluded pending review. Held-out IDs are unchanged.
Labels come from the public README at our
[pinned CTFTiny revision](https://github.com/NYU-LLM-CTF/CTFTiny/blob/f1c9531672c45b24b7fb5f3aa44a7ac33d3602f8/README.md#challenge-list).
There is no published ranking within the Hard tier; the existing ID hash breaks
ties. These target environments have not yet passed our readiness checks.

## Run from the repository root

This command makes live model requests. It runs every challenge once, then repeats
the list for trial two, including successes. Use the recorded configuration:

```sh
uv run --frozen --env-file .env python -m ctf_agent run-batch \
  --experiment evidence/ryan-shared-runs/unseen-development-three-per-category/experiment.toml \
  --challenges \
    cry-lupin cry-open-ellipti-ph cry-beyond-quantum \
    pwn-roppity pwn-pilot pwn-got-milk \
    rev-gibberish-check rev-a-walk-through-x86-part-2 rev-the-big-bang \
    msc-android-dropper \
  --trials 2 \
  --output runs/pilots/unseen-development-three-per-category
```

The existing runner prints a fresh `batch-<id>` directory. It records a settings
snapshot and `batch.json` with each started attempt, trial, outcome, run ID and
Langfuse URL. Per-attempt `run.json`, `summary.json` and native observation exports
retain usage, estimated costs, timing, verification and incident results. Unknown
usage remains unknown. Do not change code/images during the batch. Ordinary
unsuccessful endings continue; terminal incidents, infrastructure/export failures
or cleanup failures stop for review. Preserve partial and failed attempts.

## Publish results for teammates after the run

Raw records under `runs/` remain local and Git-ignored. Langfuse traces require
project access. **Running the batch does not automatically publish results to Git.**
This directory currently contains only the plan/configuration, not future results.

After the batch finishes or stops, review its actual `batch-<id>` folder and create
a sanitized copy under this directory using that same batch name. Follow the
parent guide's [sharing checks](../README.md#sharing-checks-and-changes): retain
the batch index, configuration, result/provenance records and available trace
exports; exclude target/evaluator files and credentials; scrub candidates, opaque
reasoning, HTTP headers and host identity fields. Do not blindly copy the raw
folder. Handle retained raw command-output files through a separate content review.

Record source/shared hashes and check every actual attempt's metrics, trace links,
call counts and payload availability. Keep missing exports/payloads explicit;
prefer an existing supplemental refreshed export while retaining its original.
Add a results index linking all copied attempts, including failures and partial
batches, and update this guide with the actual status. Preserve
`plan.json` as the pre-run plan; do not rewrite it as though all planned attempts
ran. Commit and push the reviewed evidence/docs so teammates receive them on pull.

For teammates/agents: begin with the plan and parent guide, then inspect the actual
batch records and chronological tool/results. Never execute recorded commands on
the host. This is development exposure, not final scored evaluation. The historical
cost-estimate discrepancy and export gaps described in the parent guide still apply.
