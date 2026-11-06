# Section 2 experiment log

Use this file for development trace findings, hypotheses recorded before live
comparisons, the exact change, run references and conclusions. Keep raw evidence
in Langfuse and run records; use `PROJECT_STATUS.md` for the overall checklist.
This is Section 2 of [Part 1](../ASSIGNMENT.md), not the later competition Part 2.

## Experiment 1 — evidence use and recovery prompt

Date: November 4, 2026 (America/New_York).
Status: **Five user-run trials reviewed; one exploratory before/after pair available.
Repeated comparison remains pending.**

### Observed problem

The three reviewed development attempts ended with `completed_without_success`,
no flag submissions, and remaining configured limits. Earlier trace reviews found:

| Development run | Trace ID | Relevant behavior |
| --- | --- | --- |
| `challenge-ab3134582f2c` (`cry-ecxor`) | `91e0d0104daffe89fdefb9f463313fe0` | Contradictory observations did not lead to a sufficiently revised approach; a later Python error was followed by a final response. |
| `challenge-c6f12d005a7b` (`msc-algebra`) | `7c44e4b3e31f2ecabb82363586d35514` | Scripts discarded service output; the model claimed progress without explicit supporting service responses and ended without a submission. This does not establish that a flag was received. |
| `challenge-3dd76ec6c9cb` (`rev-tablez`) | `6a21114e268007b68926e06b24f63984` | Missing utilities and execution failures obstructed work; the attempt later ended after another script error. Environment fixes are documented separately. |

Local records are under `runs/challenges/<run>/`; `runs/` is Git-ignored and is
not distributed by cloning this repository. Trace IDs identify the hosted records
for teammates with project access. Preserve/export the relevant tool observations
and following model actions for the final report; this summary is not a raw trace.

### Hypothesis and change

Hypothesis, recorded before the live comparison: explicit guidance to distinguish
assumptions from observations, check corrections, preserve diagnostic/completion
output, and investigate a blocker before stopping will reduce avoidable early
exits after recoverable errors and unsupported progress claims. It may increase
calls, time and cost; higher solve rate is not assumed.

The approved [system prompt](../ctf_agent/agent.py) replaces the vague recovery
instruction with those behaviors. It also accurately describes `/workspace` as
the starting directory. It preserves scope restrictions, one brief visible tool
purpose sentence, and evaluator-confirmed success. Tools, loop, limits, model,
reasoning effort, images and dependencies are unchanged by this prompt milestone.
Enforced command timeouts and other terminal stops still end the attempt.
Before live testing, the user refined the visible explanation to ask for the
action's purpose or what it will test, rather than requiring an expected result.
This keeps action explanations visible without requiring predictions that could
reinforce an unsupported assumption. The explanation remains assistant text
alongside the tool call, not an additional tool argument.

Baseline code: commit `0c7b41c94f98c427e2c06feae40acdef74609343`.
Baseline prompt SHA-256 (UTF-8):
`28234e2dd1b78bdeeb932e1cbd9759730fc10cb48143f462c7c8632981953c81`.
Initial candidate SHA-256 (before the purpose-only refinement):
`09321d02dd4f93f3e0b4d87c0410b211ca096f7e904878bf2155d384f01626cb`.
Current candidate prompt SHA-256 (UTF-8, after stripping outer whitespace):
`cea149f0c9a0d532d3e5627fcd154897503ff09f059a4bef9f2d68b3339a473d`.
Record the candidate commit with the comparison runs before interpreting results.
Git history preserves the exact earlier prompt.

### Verification and comparison plan

**45 existing offline tests passed for the initial candidate**
([JUnit evidence](../evidence/prompt-recovery/pytest.xml)):

```sh
uv run --frozen python -m pytest tests/test_agent.py tests/test_contracts.py tests/test_model.py -q --disable-plugin-autoload
```

After the purpose-only wording refinement, both existing prompt propagation and
tracing cases passed ([2-test evidence](../evidence/prompt-recovery/purpose-only.xml)):

```sh
uv run --frozen python -m pytest tests/test_agent.py -k observations_drive_recovery -q --disable-plugin-autoload
```

These tests check that the active prompt reaches the public history
and tracing, that scripted recovery can continue, and that verification and
stopping controls remain intact. They do not establish how a live model responds
to the new wording. Docker operations and model HTTP transports are substituted;
no live calls were made. No new tests or runtime components were added.

For a small, separately authorized live comparison:

1. Choose the same development challenge IDs and equal trial counts for both
   prompts; keep the ten reserved IDs untouched. Agree on the batch size within
   the existing spending/request allowance before starting.
2. Use the updated solver environment for both prompts. Hold dataset revision,
   actual image IDs, model and all settings fixed, including
   [development.toml](../configs/development.toml). Do not rebuild images between
   conditions. Record commits, settings and image IDs from each run's provenance.
   The older three runs diagnose failures but are not a fair baseline: their
   solver environment differed.
3. Start each attempt fresh. Review recoverable error → next action, repeated
   actions without new evidence, preserved service/completion output, support for
   progress claims, and the reason for stopping. A justified decision to stop
   is not automatically a failure of recovery.
4. Record verified success/submissions, scope incidents, termination reason,
   model/tool calls, time, available tokens and estimated cost for every attempt.
   Keep failures and note the uncertainty of a small stochastic sample.

### Review of user-run trials after the change

Reviewed November 4, 2026. All five trials used the current candidate prompt
(hash above), identical application source hashes, model/settings and dataset
revision, and the updated AMD64 solver image. They were development trials.
The saved generations confirm the actual prompt; the shared Git commit alone
would be insufficient because these runs used uncommitted prompt changes.

| Challenge | Run | Outcome | Model/tool calls | Active seconds | Estimated USD |
| --- | --- | --- | --- | --- | --- |
| `cry-ecxor` | `challenge-bc5088f47d97` | Completed without success | 7 / 6 | 35.07 | 0.00308961 |
| `msc-algebra` | `challenge-97b399febefe` | Verified success | 11 / 11 | 58.00 | 0.00358691 |
| `pwn-baby-boi` | `challenge-04065b43cd41` | Command timeout | 5 / 5 | 55.80 | 0.00120823 |
| `rev-checker` | `challenge-60018c066690` | Verified success | 4 / 4 | 18.26 | 0.00088861 |
| `web-poem-collection` | `challenge-2feddbeaee2d` | Verified success | 5 / 5 | 14.07 | 0.00067602 |

Total: **3/5 verified successes**, 32 model calls, 31 tool calls, 181.20 active
seconds, 172,727 input tokens (131,498 cached), 8,023 output tokens (2,512 reasoning),
and **$0.00944938 estimated model cost**. Active time excludes cleanup/export and
is not total experiment elapsed time. No recorded scope-denial events or cleanup
errors; all five exports passed the launcher's completeness checks. This is a
small selected development sample, not a scored benchmark estimate.

Turn numbers below refer to chronological model generations in each saved export.
The corresponding tool observation follows that generation.

| Evidence | Observation and implication |
| --- | --- |
| `cry-ecxor`, turns 2–5 | The model fixed an import-path error, but appended new logic after an earlier failing statement, repeating the same exception before removing it. Recovery exists but script edits are fragile. |
| `cry-ecxor`, turns 6–7 | After another diagnostic succeeded, the model ended with an explanation of its blocker. Only 7/20 model calls and about 35/300 active seconds were used. Its explanation favors one unverified assumption; alternative explanations were not exhausted. Remaining budget alone does not prove another action would succeed. |
| `msc-algebra`, turns 3–5 | An answer from a previous connection was reused on a fresh session, then corrected. `sympy` was missing; the model switched to a dependency-free approach. Each command starts a new process; network session state does not automatically persist. |
| `msc-algebra`, turns 6–9 | Verbose output exceeded 16 KiB; a failing command returned no retained stderr. Later edits introduced a `NameError`, which the model corrected. The worker's shared first-bytes budget can consume all space before a traceback arrives. |
| `msc-algebra`, turns 9–11 | A loop dropped buffered output at EOF. The model noticed completion output was missing, fixed the EOF logging, reran, obtained a candidate and submitted it successfully. This is useful observed recovery; the earlier run did not itself prove the candidate had been received. |
| `pwn-baby-boi`, turns 2–5 | `pwn` was missing; ELF utilities provided a fallback. The later script used blocking connection/line-read/receive calls without a local timeout. Turn 5 reached the 30-second command limit with no output and the controller ended the whole attempt. The export cannot locate which blocking operation stalled or establish that a longer limit would help. A claimed runtime-library discrepancy remains unverified. |
| `rev-checker`, turns 2–4 | The model identified a mistake in its transformation, corrected it and submitted a verified candidate. |
| `web-poem-collection`, turns 3–5 | The model adjusted after a failed request, obtained a candidate through the assigned endpoint and submitted it successfully. |

Visible explanations accompanied **29/31 tool-calling generations**. The two
omissions were successful submission turns, not missing command explanations;
there is little reason to add format enforcement for that now.

### Exploratory matched pair

`challenge-7ec6c0a359e0` used the original prompt on `cry-ecxor` with the updated
solver. Comparing its provenance with `challenge-bc5088f47d97` confirms the same
dataset, contestant files, image IDs and settings; only `ctf_agent/agent.py`
differs among recorded source hashes. Its traced prompt matches the baseline hash.

| Prompt | Model/tool calls | Active seconds | Estimated USD | Result |
| --- | --- | --- | --- | --- |
| Original | 5 / 4 | 39.44 | 0.00156165 | No success; the same earlier exception prevented later appended diagnostics from executing across four calls. |
| Revised | 7 / 6 | 35.07 | 0.00308961 | No success; recovered from more script errors and ran a later diagnostic, but still stopped. |

This is one sequential, stochastic pair. It supports a behavioral observation,
not a reliable effect size or improved solve rate. The other four tasks have no
matched baseline with this solver. Older environment failures remain useful
diagnoses, not fair prompt-only controls.

### Potential next changes — not implemented

1. **Network deadlines:** first test short internal I/O deadlines and stage-specific
   diagnostics, below the outer command limit. A longer global timeout would not
   address an indefinite read. Keep terminal timeout handling for now; allowing
   continuation requires verified cleanup of all descendants, including detached
   children, while preserving wall/scope stops.
2. **Output visibility:** the observed oversized outputs were about 17 KiB. A
   32 KiB development output cap is a simple configuration-only experiment that
   would fit those outputs. Alternatively, reserve bounded stderr/tail space in
   the worker; that needs code and meaningful checks. Do not implement both at
   once. Neither change fixes output discarded by the script itself, such as an
   unprinted EOF buffer.
3. **Existing libraries:** consider pinned solver-only `pwntools` because the
   missing import recurs. `sympy` is optional: the observed fallback succeeded.
   Verify Python 3.13 compatibility before adding dependencies; avoid a large
   toolkit expansion based on guessed future needs.
4. **Recovery quality:** monitor unsupported conclusions, append-after-failure
   edits and stale connection state. Prefer a complete replacement of a short
   broken script and a focused check. The current prompt already asks for
   recovery; another broad persistence paragraph is not yet justified. A later
   reasoning-effort comparison would be a separate variable.

[Machine-readable review and trace links](../evidence/prompt-recovery/trial-review.json).
This review ran no commands in challenge containers and made no new model calls
or paid requests. Runtime code/settings remain unchanged. Further comparisons,
pilot completion and scored evaluation remain unfinished.

The design follows the assignment's evidence → hypothesis → comparison sequence,
[OpenAI guidance on clear reasoning-model prompts](https://developers.openai.com/api/docs/guides/reasoning-best-practices),
and its [agent persistence/stop-condition guidance](https://developers.openai.com/cookbook/examples/gpt-5/gpt-5_prompting_guide).
Ryan Banko approved the wording, with AI assistance from another model and OpenAI
Codex during review, implementation and documentation.

## Toolkit review — original proposal

This subsection preserves the review before approval. The six-library selection
and implementation are recorded in Experiment 2 below; reedsolo was excluded.

November 4, 2026. Public index counts: 16 reverse engineering, 11 pwn, 12 crypto,
6 miscellaneous, 3 web and 2 forensics challenges. Existing file-format evidence
includes 20 x86-64 and two x86 ELF files, three Sage files, two PNGs, an APK and
a `.pt` artifact. Extensions suggest tooling needs; they do not prove a particular
package or solution is required.

A static import scan of listed **development** Python/Sage handouts found `Crypto`,
`numpy`, `reedsolo` and `sympy`. Other unresolved names, including `rsa_values`
and `sha256`, need provenance checks; they are not automatically public packages.
Listed local modules such as `rfc8032` should remain handout imports. No supplied
code was executed and no held-out solution or flag was consulted.

| Priority | Proposed solver additions | Evidence or rationale |
| --- | --- | --- |
| First | `pwntools`, `sympy`, `pycryptodome`, `numpy`, `reedsolo` | Observed missing imports or named development-handout dependencies. Pwntools also reuses established process/ELF/connection utilities. |
| Small general additions to consider | `Pillow`, `requests` | Image files and HTTP services are present. These are convenience/coverage proposals, not observed missing-import failures. |
| Specialized coverage when selected | SageMath; JADX/APKTool plus Java; CPU PyTorch | Sage, Android and likely ML artifacts exist. Verify actual format, Python/runtime compatibility and resource fit before adding these larger stacks. |
| Defer unless evidence warrants | Ghidra/angr, extra scanners, packet-analysis suites, additional compiler targets | No current trace establishes these as the next blocker. Existing binutils/GCC/GDB/curl/archive tools already cover basic workflows. Live GDB still has the documented Apple Silicon limitation. |

NYU's [reference image](https://github.com/NYU-LLM-CTF/nyuctf_agents/blob/main/docker/baseline/Dockerfile)
preinstalls a broad toolkit, including pwntools and Sage; it is a reference, not
a requirement to copy its full image or permissions. Relevant package references:
[pwntools](https://docs.pwntools.com/en/stable/install.html),
[SymPy](https://docs.sympy.org/latest/install.html),
[PyCryptodome's Crypto namespace](https://www.pycryptodome.org/src/installation),
[NumPy](https://numpy.org/install/), [reedsolo](https://pypi.org/project/reedsolo/).

Recommendation: evaluate the five existing traces first, then make a small,
separately approved solver-image change using pinned packages. Verify benign
imports/workflows under the actual Python 3.13, non-root, read-only-root and
network/resource constraints before further paid trials. Keep subsequent prompt
comparisons on identical images; do not attribute library/environment changes to
the prompt. No new runtime tools or package-manager service is needed.

Downloads from assigned challenge endpoints remain allowed. General package
registry/internet access during attempts would exceed the assignment's endpoint
restriction. Fetch dependencies during trusted image builds, then run with the
existing guard. A preloaded offline package cache is technically possible but
adds installation/state management that this project does not currently need.

## Experiment 2 — solver libraries, output visibility and network guidance

Date: November 4, 2026 (America/New_York).
Approved scope: install pwntools, SymPy, NumPy, PyCryptodome, requests and Pillow;
exclude reedsolo; raise live output to 32 KiB; clarify internal I/O deadlines and
connection lifetime. No live model comparison was authorized in this milestone.

Hypothesis before the next live comparison: supplying established libraries will
avoid the observed missing-import detours; 32 KiB will retain the roughly 17 KiB
outputs observed in the previous trials; clearer command guidance may reduce
unbounded network reads and stale-session assumptions. This is a bundled setup
change, so a later comparison cannot attribute an effect to one component alone.
The existing recovery system prompt is unchanged.

Direct solver versions are pwntools 4.15.0, SymPy 1.14.0, NumPy 2.5.4,
PyCryptodome 4.3.0, requests 2.34.2 and Pillow 13.0.0. The standard requirements
input and resolved file pin 40 packages including transitive dependencies.
Host Python dependencies are unchanged. Downloads occur during image builds;
the attempt's endpoint-only network guard remains enforced.

The live profile sets `max_output_bytes = 32768`. The command description asks
for connection/read deadlines below the outer command limit and explains that
files persist but network connections do not automatically persist between calls.
These are model instructions, not automatic socket rewriting or a session tool.

**Timeout decision: retain 30 seconds per live command.** The observed failure
used blocking operations without a local deadline. It did not show a computation
needing a longer allowance. The new library/workflow probe completed under that
cap; larger computations can justify a separate `command_seconds` experiment.
The attempt wall limit remains 300 seconds, and command timeout remains terminal.

Benign verification checks actual library workflows inside the constrained solver,
an intentionally stalled permitted socket read with its own deadline, retention
of a 17 KiB output plus stderr, and truncation above the 32 KiB bound. A local read
timeout can return while the attempt remains active; this does not establish that
the model will follow the new guidance. The output collector still keeps the
first bounded bytes, so it does not guarantee preservation of every late error.

[Verification, build and reproduction evidence](../evidence/solver-libraries/README.md).
Verification passed: 64 fast tests, 23 synthetic controls on the installed-library
image, and four focused final-image checks after disabling unnecessary pwntools
terminal setup. The final library/workflow command took about 1.35 seconds and
the intentionally stalled read returned in about 0.22 seconds, comfortably below
the 30-second command cap. These small probes do not bound arbitrary workloads.
No real challenge was solved or model API called during this milestone. Before
another comparison, record this new image/configuration and use it consistently
across both conditions. Prior results remain historical evidence.

## Batch execution support

`run-batch` now invokes the existing single-challenge launcher sequentially for
explicit IDs and trial counts. A copied experiment file and small `batch.json`
index keep each attempt discoverable through its existing run ID, verdict, trace
link and original record. Metrics remain in the individual records. The wrapper
does not change solver/model behavior and adds no batch-budget gate, automatic
retry, parallel execution or resumption feature.

The user prefers two different development challenges per category for breadth.
Only one development forensics challenge exists, so this yields eleven IDs.
Repeating a selected challenge is a separate choice through `--trials`; breadth
and repetition measure different things. The user subsequently selected and
prepared eleven IDs; the pilot started but stopped as recorded below. The existing
account/per-attempt limits and usage records remain;
the user requested no additional batch-cost management.

[Offline verification](../evidence/batch-wrapper/README.md): 17 batch cases and
81 fast tests passed. Child outcomes were simulated to test orchestration and
record handling without paid model calls. No new benchmark results are claimed.
The record audit found the required IDs and evidence already available; demo work
was deferred. At that milestone the next step was to review the wrapper, choose
development IDs, then inspect a pilot before expanding evaluation. The later
package-policy and usability sections record subsequent work; PROJECT_STATUS
tracks the current next step.

## Temporary runtime package-index default

November 4, 2026. Batch `batch-be87c5be7ce7` stopped on its first model request
with `APITimeoutError`; the user addressed gateway access. That setup failure was
later moved intact to `runs/archive/batch-be87c5be7ce7` to keep the active pilot
folder tidy; all seven files and their contents were preserved. All eleven preparation
checks passed. The next batch, `batch-8898df326849`, completed two attempts
(`cry-ecxor`: unsuccessful; `cry-describeme`: verified success) and stopped on
`for-1black0white`. Trace `c9c2d54214afdba7520255fbdfaeb213`, generation 5, ran
`python3 -m pip install --quiet opencv-python-headless` after finding no QR decoder.
The guard recorded DNS queries for `pypi.org`, stopped the solver and preserved
complete records with successful cleanup. This was a dependency-install request.

Approved temporary change: default runtime pip to `PIP_NO_INDEX=1` and disable
its version check; state in the command description that downloads are unavailable.
The ENV line is after build-time installs and is explicitly marked for reversal.
The system prompt, installed libraries, firewall and batch stop policy are unchanged.

Hypothesis before any further live trial: an ordinary missing-package install
will fail locally and become a recoverable tool observation instead of triggering
a scope stop. The model may then use existing capabilities or end unsuccessfully.
This does not guarantee every attempted download fails softly: direct URLs,
other download commands or overrides remain subject to the network guard.
No decoder was added, and no new real challenge/model attempt ran during this fix.

[Verification and reversal instructions](../evidence/runtime-package-policy/README.md).
Verification: 81 fast tests and 24 synthetic Docker controls passed. A missing
package request failed locally in about 0.42 seconds and a following command ran
successfully in the same attempt. The new solver image is built locally. No live
trial of the revised behavior has been made.


## Experiment 3 — usable sessions, package installation and recovery

Approved November 4, 2026, before any new live comparison. Prior traces showed a
missing dependency leading to a scope stop, blocking reads ending an entire
attempt, and connections mistakenly treated as persistent between commands.
Small workspace/home constraints and beginning-only output capture were additional
implementation limitations. GDB changes are excluded at the user's request.

Hypothesis: writable Python/home/temp storage and permitted pip access let the
agent obtain dependencies; terminal sessions preserve program interactions;
confirmed descendant cleanup lets it recover from command timeouts; beginning/end
excerpts and output files retain useful diagnostics. Expanded time/call/token
allowances reduce premature stops. This bundles environment and tool changes; a
later comparison cannot attribute an effect to any one component alone.

Keep the model and reasoning effort unchanged. The live profile uses 600 seconds,
120-second ordinary commands, 60-second requests, forty model responses, eighty
tool calls, 512 KiB model input and 4,096 output tokens. The local spending cap
and reservation code are removed; usage/cost estimates remain. Output is 64 KiB
with up to 1 MiB retained per command/session. Package additions reset each attempt
and installed versions are recorded. Public HTTPS is technically available to
commands generally; the prompt limits its purpose to pip, not answer lookup.

Verification uses synthetic commands and benign package installation only. It
establishes tool behavior, isolation and cleanup, not improved benchmark success.
The prior offline package milestone and old trial records remain historical.
Current verification and reproducibility evidence: [agent usability](../evidence/agent-usability/README.md).
After handoff, review before authorizing another development pilot.


Environment verification completed: **82 fast tests, 27 distinct Docker cases**
across the main run and focused completion, and two zero-model preparation cycles
for `pwn-baby-boi`. Cleanup passed. Historical startup-deadline and absent-network
cleanup failures remain in the evidence; the corrected behavior passed. The
benign package installation/import command took approximately 1.66 seconds in
the main run. No model calls or challenge-solving attempts ran, so no solve-rate
or model-behavior improvement is claimed. Stop for review before a live pilot.


## Reliability follow-up — worker lifecycle, usage and preparation

Approved November 4, 2026 after a static review of Experiment 3's implementation.
The immediate scope is worker cleanup, terminal I/O, missing usage metadata,
consistent preparation settings and documentation. SDK export replacement,
context management, broader default consolidation and GDB were deferred at that
milestone; the following cleanup completes configuration and export work.

Hypothesis before another live trial: guaranteed supervisor cleanup, final-output
draining, explicit partial-input counts and automatic reaping prevent avoidable
session failures. Missing usage should leave totals unknown rather than discard
a valid model reply. Preparation should test the selected experiment's actual
attempt settings, free workspace and remaining staging deadline. These changes
preserve the model, numeric live profile, three tools and existing isolation.

Verification uses synthetic processes, offline model transports and zero-model
preparation only; it does not measure solve-rate improvement. Historical evidence
remains unchanged. Results are recorded in
[reliability evidence](../evidence/agent-reliability/README.md): **91 fast tests,
31 Docker cases in one complete run and two zero-model preparation cycles passed**.
Preparation settings match the selected live experiment and cleanup passed. Stop for review
before a new live pilot or scored evaluation.


## Maintenance cleanup — configuration, trace export and package snapshots

Approved November 5, 2026. Normal model/run values now live in one complete
`configs/development.toml`, with one model-call setting. The loader validates
without merging hidden defaults; the previous resolved live settings are unchanged.
The installed Langfuse SDK replaces the app's CLI subprocess and retrieves all
cursor pages while preserving completeness/privacy audits. Package inventories
are still scanned; identical inventories no longer rewrite `packages.json`.

This reduces maintenance and redundant writes; it is not a performance hypothesis
or a benchmark comparison. Checks and hosted readback use substitutes and an
existing synthetic trace, with no new model requests. See
[evidence](../evidence/config-sdk-cleanup/README.md): 95 fast tests, 31 synthetic
Docker cases with cleanup verified, and matching readback of the existing ten-row
synthetic trace passed. Context management remains
a possible later hypothesis. GDB and output-copy optimization remain deferred.

## Proposed infrastructure simplification — not implemented

The November 5 source review led to a
[consolidated implementation proposal](SIMPLIFICATION_PLAN.md). It retains our
agent, three tools, prompt strategy, model integration, Langfuse and batch wrapper.
It proposes a writable disposable solver, standard Docker copy/exec, one-shot
file writing, bounded head/tail output and narrower target configuration changes.
Image selection is an independent build/evaluation decision.

Hypotheses to record before implementation or live comparison:

- Removing the restrictive filesystem and its staging/startup workarounds can
  preserve required boundaries with fewer runtime mechanisms.
- Restarting the same writable solver on a command timeout can eliminate command
  supervisors while allowing the agent to continue with its files/installations.
  Running processes and connections are lost; the attempt ID, limits and target
  state do not reset. Deadline/scope/guard failures remain terminal.
- Preserving supplied target behavior, with justified socket exceptions, can
  reduce compatibility problems introduced by blanket overrides.

These hypotheses are not verified behavior or measured performance improvements.
The image has not been built and restart recovery has not been prototyped. Existing
95/31 passing checks apply to the current worker-based implementation. Source and
read-only Compose configuration inspection found 17 actual socket mounts among
27 supplied definitions; previous successful runs show socket omission worked
for `cry-describeme` and `web-poem-collection`, not that every mount is unnecessary.

First verify the replacement with synthetic/offline checks and zero-solving
preparation. Keep unrelated message handling, stopping-policy, context and GDB
changes separate. Any later live pilot or comparison needs its own authorization;
preserve the old configuration, failed attempts and historical evidence.
