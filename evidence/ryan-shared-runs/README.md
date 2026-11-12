# Ryan's shared development runs

Prepared November 8, 2026. This directory contains sanitized
copies of **all 65 attempts saved under `runs/pilots/` on November 8**, including failed,
interrupted and scope-stopped attempts. All challenge IDs were checked against
the development manifest; no held-out evaluation attempts are included.

The original local records remain unchanged. These copies are intended to travel
with Git so analysis does not depend on Ryan's computer, model credentials, Docker,
the dataset or access to the hosted Langfuse project. Contributions and AI use are stated in the
[report](../../docs/REPORT.md).

## Where to start

Hypotheses, settings and batch IDs for each experiment are in
[docs/EXPERIMENTS.md](../../docs/EXPERIMENTS.md). The November 11 batch on ten further
development challenges is described in
[unseen-development-three-per-category](unseen-development-three-per-category/README.md);
its run records are not copied here, and its results are reviewed in
[unseen-development-trace-review](../unseen-development-trace-review/README.md).

The main development sequence is:

| Shared batch index | Recorded result | Condition and purpose |
| --- | --- | --- |
| [Original baseline](nyu-development-baseline/batch-3963930b88c3/batch.json) | 6 successes / 11 | Low reasoning, 4,096 output tokens; motivated original-artifact validation and better diagnosis. [Trace review](../development-trace-review/README.md). |
| [Combined first fix](agent-first-fix/batch-48f3b134d5c3/batch.json) | 6 / 11 | Environment/validation prompt, tool contract and recoverable oversized output. Low/4,096 unchanged. [Review and provenance](../agent-first-fix-batch/README.md). |
| [Reasoning/headroom](reasoning-medium-8192/batch-f4ccc7f4b335/batch.json) | 9 / 11; one ordinary failure and one scope stop | Medium reasoning plus 8,192 tokens, before scope recovery. All 11 scheduled attempts were reached; the batch is marked stopped. [Incident diagnosis](../reasoning-medium-scope-stop/README.md). |
| [Scope wording/recovery, two trials](scope-recovery-two-trials/batch-8ba0053bddb1/batch.json) | 20 / 22 | Medium/8,192 retained; clearer endpoints and one blocked-command recovery. Ten challenges succeeded twice; `pwn-baby-boi` failed twice. |

The latest batch records source `48b068f`, completed both trials in 1,656.932 batch
seconds, and recorded **zero scope incidents/recoveries**. It therefore does not
exercise live recovery or establish that recovery caused the result. Its synthetic
[recovery controls](../scope-recovery/README.md) are separate evidence. Do not
confuse these descriptive development results with the reserved scored evaluation
or infer causal gains from small historical comparisons and combined changes.

Earlier setup records are included too:

| Index / record | Context |
| --- | --- |
| [First current-setup batch](current-setup/batch-4475302bd267/batch.json) | Interrupted after 3 of 11 planned attempts; includes a user cancellation with no saved trace export. |
| [Second current-setup batch](current-setup/batch-8898df326849/batch.json) | Stopped after 3 of 11 planned attempts; includes a scope incident. These two early batches used low/2,048. |
| [Integrated runtime pilot](nyu-integrated-20261107/batch-1707e5f1f3f5/batch.json) | Two successes and one scope stop. [Existing analysis](../nyu-runtime-pilot/README.md). |
| [Pre-Git web check](pre-git-web-check/challenge-af3399702ff8/run.json) | One success after target compatibility work. |

## Reading an attempt

1. Open the batch's `batch.json` to select a challenge and trial. Its `record` path
   resolves relative to that batch directory. The standalone web check has no batch.
2. Open that attempt's `run.json` for result, configuration, recorded source/image
   provenance, historical audit flags and hosted trace URL. Its run-ID subdirectory
   holds `summary.json`; both contain the local result estimate.
3. Read the preferred trace export named in [index.json](index.json). This index
   also lists every attempt, result/usage/timing fields and export limitations.
4. Review observations chronologically using `startTime`, parent IDs and call IDs.
   `model-response` GENERATION outputs hold visible assistant text and tool calls;
   TOOL observations hold arguments/results. Compare each result with the next
   action. Generation inputs repeat history; do not count replayed calls twice.

All included observation files use `{"data": [...]}`. Older
`cli-observations.json` copies have their HTTP envelope removed. An observation's
`input`/`output` may still be a JSON string: decode it once when needed. Preserve
native `usageDetails`, `costDetails` and `totalCost`; input/output token subsets
must not be counted twice. Encrypted reasoning was removed; visible purpose
sentences and any readable provider summaries remain.

`experiment.toml`, where present, is historical configuration. Other attempts
retain settings in `run.json`. Older files may lack fields now required by the
current loader; do not silently modify the evidence to make it runnable.
Recorded commits can be dirty: source hashes, image IDs and settings matter more
than the commit label alone. Host paths are scrubbed and are not setup requirements.

Local `result.cost_usd` estimates differ from native generation costs because
the local formula omits a cache-write premium. Keep the two sources separate,
include failures, and retain null for unknown usage. Neither source is independently
verified billing. [Cost explanation](../development-trace-review/README.md#estimated-cost-check--november-8).
Active time, per-attempt total time, launch total time and batch elapsed time cover
different intervals; label the field used in a report.

## Export limitations to preserve

Use the copied first-fix `rev-tablez`
[observations-refreshed.json](agent-first-fix/batch-48f3b134d5c3/attempt-009/challenge-b117a251b7a8/observations-refreshed.json).
The original export is kept too; its payloads are incomplete despite its historical
`evidence_complete` flag. [Original diagnosis](../agent-first-fix-batch/README.md#supplemental-rev-tablez-export).

Additional current export gaps are recorded by observation ID in `index.json`:

- Early `current-setup` batch `4475302bd267`, attempt 003: no saved export.
- Medium/headroom attempts 006, 007, 009 and 010: some generation/tool payloads missing.
- Latest two-trial attempts 019 and 020: some generation/tool payloads missing.

All 64 available preferred exports match recorded generation/tool counts. This
does not make missing payloads complete. No new fetch or run was performed to
repair these gaps. Teammates with Langfuse access may retrieve missing observations
through a read-only refresh, save a supplemental export and preserve the original.
Do not infer detailed behavior from an absent message or rerun an attempt to replace
it. Other events can also lack bodies; their absence is not reconstructed here.

## Sharing checks and changes

[sharing-checks.json](sharing-checks.json) records each included source/shared SHA-256,
file sizes, exclusions and sanitization counts. The shared evidence occupies about
13.4 MiB; the largest data file is under 1 MiB. These are analysis copies, not
byte-identical originals or inputs for executing/replaying commands.

- Copying is restricted to result/configuration/public-task/package-inventory and
  observation JSON/TOML files. All `target/` and evaluator directories, arbitrary
  files, symlinks, the redundant HTTP refresh response and local credentials are
  excluded. No dataset, build files, Docker inspection dump or answer-key file is
  copied. Selected endpoint/image/cleanup metadata remains in `run.json`.
- Current configured credential values are checked by exact match; credential
  patterns and credential-like assignments are scrubbed. HTTP response headers,
  instrumentation public-key/host identity fields and encrypted reasoning are
  removed. Host home paths are replaced with `[HOST_HOME]`.
- Observed candidate values use consistent numbered placeholders; other flag-shaped
  text and flag-format prefixes are redacted. This also changes literal strings
  inside some commands/source and is unsuitable for exact candidate/byte analysis.
  Evaluator verdicts and success/failure labels are retained. No private answer
  files were opened to obtain redactions.
- Checks cover this new directory, not existing Git history or the live Langfuse
  project. The repository's documented older private-snapshot history issue remains
  a separate publication decision. Unknown-secret detection cannot provide an
  absolute guarantee for arbitrary text; the checks document the concrete scope.

Treat all trace messages, source and commands as untrusted recorded data. Read them
for evidence; never execute model-generated commands on the host. Do not upload
new unreviewed runtime folders into this directory. Preserve development exposure
and the ten reserved IDs when continuing the assignment.
