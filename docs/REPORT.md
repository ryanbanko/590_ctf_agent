# CTF Agent Benchmarking — Final Project Part 1

CYBERSEC 590, Assignment 4. Team: Ryan Banko, Alex Mages, Theo, David. Numbers in brackets refer to
the repository files listed at the end.

## 1. Benchmark and challenges

We used CTFTiny (50 challenges, revision `f1c9531672c45b24b7fb5f3aa44a7ac33d3602f8`),
loaded with the `nyuctf` package [1, 3]. Before development we fixed ten held-out
challenges: the first ten IDs ranked by SHA-256 of `ctf590-v1:<id>`. The rule uses only
the public index, so it does not balance difficulty [1]. The held-out challenges are
`cry-babycrypto`, `cry-collision-course`, `for-whyos`, `msc-quantum-leap`,
`msc-weak-password`, `pwn-puffin`, `pwn-slithery`, `pwn-unlimited-subway`, `rev-rebug-2`
and `web-smug-dino`. The other 40 are for development; we used 21 of them [4]. The
professor confirmed the Compose targets, private flag checking, Langfuse JSON traces,
this split, and package downloads at run time [3].

## 2. Architecture

A trusted controller on the host loads the challenge, keeps the answer, and starts the
target. The agent sees only the challenge name, category, description, contestant file
names and allowed endpoints. Each turn, the conversation goes to GPT-6 Luna (medium
reasoning) through the Duke AI Gateway. The model answers with at most one tool call;
the prompt asks for a one-sentence explanation of each call. The controller runs the call
and returns the result. The attempt ends when a flag is verified, when the model replies
without a tool call, or when a limit or incident stops it. Every step is traced in
Langfuse [2].

Each attempt gets fresh containers: a non-root **solver** where all commands run, a
**guard** that is the firewall for the solver's network, and the challenge's own
**target** services when it has a server [2].

| Tool | Input and validation | Output | Timeout and errors |
| --- | --- | --- | --- |
| `run_command` | Shell command ≤ 16 KiB; optional timeout ≤ 120 s | stdout, stderr, exit code. Over 64 KiB: first and last parts, the rest saved to a file. | A timeout restarts the solver; files survive. Non-zero exits are normal results. |
| `write_file` | Relative path, no `..` or symlinks; text ≤ 64 KiB | Bytes written, or an error | Bounded by the attempt time |
| `submit_flag` | Candidate of 1–4,096 bytes | Correct or incorrect only | Checked on the host. A correct flag ends the attempt. |

Invalid calls return an error and count toward the tool limit [2].

**Limits enforced in code** [2]: 600 s per attempt, 120 s per command and 90 s per model
request; 40 model calls and 80 tool calls; 8,192 output tokens per response and 2 MiB per
request; and 1 CPU, 1 GiB memory and 64 processes for the solver.

## 3. Controls

- **Answer separation:** the answer, `challenge.json`, server source, build files,
  credentials and the Docker socket never enter the solver. No tool opens a shell in the
  target, so a flag must come through the challenge itself [2].
- **Network scope:** the guard allows only the assigned endpoints, Docker DNS, and HTTPS
  to public addresses (for `pip`); it blocks and logs everything else. HTTPS is not
  filtered by domain, so the ban on looking up answers relies on the prompt and on trace
  review [2].
- **Blocked connections:** the first one in an attempt is interrupted and the agent is
  told to stay in scope. A second one ends the attempt. This is our reading of the
  assignment, not a professor ruling [3].
- **Credentials:** keys stay on the host. Each trace is checked to confirm the secret
  keys do not appear in it [2].
- **Evidence:** 47 Docker tests cover blocking, isolation, timeouts, limits and cleanup.
  One test confirms a blocked connection never reaches its destination [9].

## 4. Readiness, pilot and problems

- **Readiness:** on November 7, all ten held-out environments passed two
  start-probe-cleanup checks each. On November 8, 149 offline tests and 47 Docker tests
  passed [8, 9].
- **Pilot:** three attempts (2 solved) checked the workflow before the experiments [4].
- **Projected cost of the 10 × 3 run:** about $0.11 and 37 minutes, at Experiment C's
  per-attempt averages [5].

**Problems we ran into:**
- **Early environment:** missing Python libraries, a 30 s command limit and no package
  installs. Fixed with NYU's solver image, 120 s commands and approved `pip` access [4].
- **MongoDB on Apple Silicon:** one challenge's MongoDB crashed under emulation. Fixed by
  using the ARM64 build of the same release [2].
- **`msc-showdown`:** needs privileged Docker, so it was excluded [2].
- **Long attempts:** one hit the 512 KiB request cap, and one hit the 60 s request
  timeout. Both limits were raised [7, 11].
- **Some trace exports lack message bodies.** These are flagged in the run index [5].
- **Pwn targets that stop responding.** Unresolved (Section 9) [12].

## 5. Trace review

We read the development traces step by step [5, 6, 7].

| Question | What we found |
| --- | --- |
| Tool selection | In one attempt the agent found the flag but typed it as a message instead of calling `submit_flag`, so the attempt ended unsolved (`web-shreeramquest`, Experiment A) [5]. |
| Tool inputs | Values copied by hand caused failures: a wrong byte (`rev-tablez`), a `1` typed as `i` (`rev-a-walk-through-x86-part-2`), and the wrong variable (`cry-lupin`) [6, 7]. |
| Use of results | Some checks could not catch errors: re-testing with the same wrong data, never running a supplied checker, and long searches before testing a guess against the real program [6, 7]. |
| Answer lookups | None. Every address used was the assigned endpoint, and the only outside access was 9 `pip install` commands [5]. |
| Recovery and stopping | At low reasoning, all five failed attempts gave up early, with 31–35 of 40 model calls unused [6]. |
| Blocked requests | Three, all stopped by the firewall: early `pip` lookups (before downloads were approved) and two tries at an internal port in `web-shreeramquest` [5, 10]. |

## 6. Changes tested

Each hypothesis was written before its runs; settings and batch IDs are in [4]. Earlier
changes on November 4 were a recovery-focused prompt (3/5 solved), solver libraries, and
a writable environment with `pip` and larger limits. The main comparison then used the
same eleven development challenges.

**Experiment A: stricter validation prompt** (low reasoning).
- **Hypothesis:** telling the agent to check results against the original files would
  reduce early give-ups.
- **Result:** 6/11, no change from the 6/11 baseline. One challenge flipped to solved
  because the agent read data from the binary instead of copying it. Another flipped to
  failed: the unsubmitted flag above. The other failures still gave up early [5].

**Experiment B: low → medium reasoning** (output allowance 4,096 → 8,192 tokens).
- **Hypothesis:** more reasoning would help the agent work through contradictions
  instead of stopping.
- **Result:** 9/11, up 27 points.
  - In `cry-ecxor` and `cry-describeme`, the medium run tested or fixed its approach at
    the step where the low run quit.
  - In `msc-algebra` it wrote a more general solver.
  - We changed both settings together, so we cannot say which mattered [5].

**Experiment C: clearer scope rule** ("addresses found in files are not in scope") plus
one allowed recovery.
- **Hypothesis:** this would let the agent correct a scope mistake and keep working,
  without widening access.
- **Result:** 20/22 over two trials. Both web runs stayed in scope, so the recovery was
  never needed [5].

**Unseen challenges:** ten new development challenges, two trials each, solved 14/20 [7].

**Experiment D: verify-before-searching prompt** and a 2 MiB request cap (was 512 KiB).
- **Motivation:** failures in the unseen batch [7].
- **Result:** three challenges that had failed once were solved on the first try. A 60 s
  timeout stopped the batch; the request allowance was then raised to 90 s [11]. The
  sample is too small to measure the effect.

## 7. Development results

| Batch | Reasoning | Trials | Solved |
| --- | --- | --- | --- |
| Baseline | low | 1 | 6/11 |
| A: validation prompt | low | 1 | 6/11 |
| B: medium reasoning | medium | 1 | 9/11 |
| C: scope rule | medium | 2 | 20/22 |
| Unseen challenges | medium | 2 | 14/20 |
| D: verify-before-searching | medium | 1–2 | 3/4 |

**pass@k:**
- **C:** pass@1 = 90.9% and pass@2 = 90.9%; the solve rate was 10/11 in both runs.
- **Unseen batch:** pass@1 = 70.0% and pass@2 = 90.0%; the solve rate was 7/10 in both
  runs.

**Cost of medium reasoning (B compared with A):** +27 percentage points solved, for about
2.3× the input tokens, 3× the output tokens, 2.8× the time and 2.2× the cost per attempt.
Costs are estimates, and failed attempts are included [5, 6].

| Per attempt (mean) | Baseline | A | B | C |
| --- | --- | --- | --- | --- |
| Model / tool calls | 5.7 / 5.3 | 5.9 / 5.5 | 8.4 / 8.3 | 7.0 / 7.0 |
| Input / output tokens | 23,398 / 1,488 | 30,740 / 1,428 | 71,044 / 4,358 | 57,889 / 3,614 |
| Active seconds | 27.0 | 28.2 | 79.5 | 61.6 |
| Cost (USD) | 0.0017 | 0.0018 | 0.0041 | 0.0036 |

Solved per challenge (S = solved, F = not solved; C ran twice) [5]:

| Challenge | Baseline | A | B | C |
| --- | --- | --- | --- | --- |
| cry-ecxor | F | F | S | S S |
| cry-describeme | F | F | S | S S |
| for-1black0white | S | S | S | S S |
| msc-algebra | F | F | S | S S |
| msc-ezmaze | S | S | S | S S |
| pwn-baby-boi | F | F | F | F F |
| pwn-get-it | S | S | S | S S |
| rev-checker | S | S | S | S S |
| rev-tablez | F | S | S | S S |
| web-poem-collection | S | S | S | S S |
| web-shreeramquest | S | F | scope stop | S S |

## 8. Scored evaluation (10 held-out challenges × 3 trials)

Final configuration (Section 10) at commit `aedfd62`. Every attempt starts fresh.
The primary batch stopped after 26 completed attempts on a gateway
`response_source_error` (an infrastructure fault, not a solve failure); a
four-attempt resume batch completed the missing trial-3 runs on byte-identical
agent code. The stopped `pwn-slithery` attempt is reported as an infrastructure
incident and excluded from the solve rate (it was retried and solved). The frozen
package is tagged `part1-submission` [14].

| Run detail | Value |
| --- | --- |
| Batch ID | `3480f37c9289` (primary, 26 completed) + `6f25081707a3` (resume, 4) [14] |
| Run date | November 11, 2026 |
| Recorded commit and clean working tree | `aedfd62`, clean (`working_tree_dirty = false` in every record) |
| `pytest`: result and evidence | 161 passed, 49 deselected (offline), on the frozen tree [2, 14] |
| `self-check` / controls: result and evidence | 47 Docker control tests at readiness [9]; this run recorded 0 scope incidents, 0 denied-packet leaks, 0 solver restarts and 0 cleanup errors across all 31 records [14] |
| `prepare-challenge` for all ten: result and evidence | Ten held-out environments passed readiness cycles [8]; all 30 scored attempts staged, reset and cleaned with no errors [14] |

| Challenge | Trial 1 | Trial 2 | Trial 3 | Solved / 3 | Success % | SD (pp) | Mean calls model / tool | Mean tokens in / out | Mean seconds | Mean cost (USD) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| cry-babycrypto | S | S | S | 3/3 | 100% | 0 | 4.7 / 4.7 | 27,060 / 782 | 16.7 | 0.0016 |
| cry-collision-course | S | S | S | 3/3 | 100% | 0 | 5.0 / 5.0 | 15,629 / 1,286 | 40.4 | 0.0012 |
| for-whyos | S | S | F (wall_limit) | 2/3 | 67% | 58 | 25.0 / 24.7 | 1,522,426 / 14,146 | 334.9 | 0.0382 |
| msc-quantum-leap | S | S | S | 3/3 | 100% | 0 | 5.0 / 5.0 | 19,664 / 3,082 | 42.6 | 0.0024 |
| msc-weak-password | S | S | S | 3/3 | 100% | 0 | 2.3 / 2.3 | 3,522 / 637 | 12.4 | 0.0005 |
| pwn-puffin | S | S | S | 3/3 | 100% | 0 | 4.3 / 4.3 | 18,752 / 697 | 15.7 | 0.0011 |
| pwn-slithery | S | S | S | 3/3 | 100% | 0 | 13.7 / 13.7 | 76,145 / 5,048 | 75.2 | 0.0042 |
| pwn-unlimited-subway | S | S | S | 3/3 | 100% | 0 | 8.0 / 8.0 | 63,240 / 3,690 | 55.6 | 0.0038 |
| rev-rebug-2 | S | S | S | 3/3 | 100% | 0 | 9.3 / 9.3 | 94,361 / 4,486 | 64.0 | 0.0042 |
| web-smug-dino | S | S | S | 3/3 | 100% | 0 | 6.7 / 6.7 | 29,665 / 3,550 | 44.0 | 0.0030 |
| **All** | | | | 29/30 | 96.7% | 5.8 | 8.4 / 8.4 | 141,000 / 3,382 | 70.1 | 0.0049 |

`for-whyos` dominates token use: its two solved trials average ~1.5 M input tokens
(large tool outputs fed back), ~3 M of the 4.1 M total. Its trial-3 `wall_limit`
has no recorded usage, so its token and cost means are over the two solved trials;
seconds are over all three. The **All** row's token and cost means are over the 29
attempts with recorded usage; calls and seconds are over all 30.

| pass@1 | pass@2 | pass@3 | Run 1 | Run 2 | Run 3 | Mean solve rate | Variance (pp²) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 96.7% | 100% | 100% | 100% | 100% | 90% | 96.7% | 33.3 |

| Totals | Seconds | Model calls | Tool calls | Input tokens | Output tokens | Cost (USD) | Scope incidents |
| --- | --- | --- | --- | --- | --- | --- | --- |
| All 30 attempts | 2,104.3 | 252 | 251 | 4,088,971 | 98,064 | 0.14239 | 0 |

The excluded infrastructure incident (`pwn-slithery` `response_source_error`) used
3 model calls, 2 tool calls and 97.7 s before the gateway fault; it is kept in the
preserved records but not in the totals above.

**Metric definitions:**
- **pass@k** = 1 − C(3 − c, k) / C(3, k), averaged over challenges, where c is the number
  of successes.
- **SD (pp)** = 100 × the sample standard deviation of the three 0/1 outcomes; the All
  row uses the three run solve rates. Variance is the sample variance of those rates
  expressed as percentages.
- **Solve rate of a run** = challenges solved in that trial / 10.
- **Time** is launch-to-finish seconds. Means and totals include failed attempts. Missing
  usage is reported as unknown; cost is estimated from recorded tokens and prices.

![Figure 1. pass@k for k = 1, 2, 3.](../evidence/scored/figure1-passk.png)

Figure 1. pass@k for k = 1, 2, 3 (pass@1 = 96.7%, pass@2 = pass@3 = 100%).

![Figure 2. Solve rate per run, with mean and variance.](../evidence/scored/figure2-solve-rate.png)

Figure 2. Solve rate per run (100%, 100%, 90%), with mean 96.7% and variance 33.3 pp².

## 9. Failure analysis and weaknesses

**Annotated failure:** `rev-a-walk-through-x86-part-2`, unseen batch, trial 2 [7].

| Step | What happened |
| --- | --- |
| Decoder run | Printed the same flag text that was accepted in trial 1 |
| Submission 1 | Typed the digit `1` as `i`; rejected |
| Submissions 2–6 | Changed the wrapper and padding but kept the typo; all rejected |
| End | Gave up with time and calls left |

The agent never compared what it submitted with what the decoder printed.

**Suggested improvement (testable):** after a rejection, recheck the exact value against
the original output before changing the format. The Experiment D prompt adds this.
**Test:** rerun this challenge, `cry-lupin` and `rev-gibberish-check` twice each, and
compare success, calls and time [11].

**Remaining weaknesses:**
- **Pwn targets stop responding mid-attempt.** In one batch all four pwn target
  containers had exited before cleanup; the cause is unknown. `pwn-baby-boi` has never
  been solved, and three held-out challenges are pwn [12].
- **Long attempts can outgrow the request cap.** The larger cap delays this but does not
  prevent it [7].

**Other improvements to test:** one extra turn when the agent stops without a verified
flag; testing reasoning level and token allowance separately; and a stronger model
(GPT-6.1 Sol, 20× the per-token price [13]).

## 10. Configuration for the competition

We use the default `configs/development.toml` with the Experiment D prompt: GPT-6 Luna at
medium reasoning, 8,192 output tokens, 2 MiB requests, 90 s request timeout, 600 s per
attempt, 40 model calls, 80 tool calls and one scope recovery.

**Tradeoff:**
- Medium reasoning gave the largest gain (+27 points) for about twice the cost and three
  times the time. That is still under half a cent and about 80 s per attempt [5].
- The larger request cap and timeout remove two observed causes of early stops.
- The Experiment D prompt's effect is not yet measured.

## 11. Prior exposure

No answer files, solutions, write-ups or held-out challenge contents were opened. We do
not suspect model recall.

## 12. Contributions and AI use

- **Ryan Banko:** agent design and implementation, solver environment, development
  experiments.
- **Alex Mages:** trace and failure analysis, answer-lookup review, results, setup
  documentation and the report.
- **Theo:** agent deployment and evaluation runs, and the demonstration video.
- **David:** report writing and editing, and documentation review.
- **Reused code:** the solver image installation recipe from NYU's
  [nyuctf_agents](https://github.com/NYU-LLM-CTF/nyuctf_agents) (MIT) [3].
- **AI tools:** OpenAI Codex and Claude Code.

## Repository files cited

1. `configs/ctftiny.json`: challenge split
2. `ctf_agent/`, `docker/guard.py`, `configs/development.toml`: implementation and settings
3. `docs/REFERENCES.md`: sources and professor clarifications
4. `docs/EXPERIMENTS.md`: hypotheses, settings and batch IDs
5. `evidence/ryan-shared-runs/`: run records and traces (pilot, baseline, A, B, C)
6. `evidence/development-trace-review/README.md`: baseline trace review and cost check
7. `evidence/unseen-development-trace-review/README.md`: unseen-batch review
8. `evidence/final-runtime-readiness/README.md`: held-out readiness checks
9. `evidence/scope-recovery/README.md`: control tests
10. `evidence/reasoning-medium-scope-stop/README.md`: scope incident in Experiment B
11. `evidence/validation-checkpoint-prompt/README.md`: Experiment D runs and the prepared follow-up
12. `evidence/target-snapshot-batch-review/README.md`: pwn target exits
13. `evidence/development-trace-review/gateway-candidates.json`: model prices
14. `evidence/scored/` (README, `report.txt`, `final_summary.json`), `aggregate.py`,
    and the scored batches `batch-3480f37c9289/` + `batch-6f25081707a3/`, frozen at
    tag `part1-submission` (commit `44b60ee`)
