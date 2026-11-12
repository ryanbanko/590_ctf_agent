## CTF Agent Benchmarking

**Final Project Part 1  |  50 points (an additional 150 points will be allocated after the competition)  | &#xA0;**

**Assignment can be done individually or in teams (up to 4 people) Due Wednesday, November 11, 2026, at 11:59 p.m. Eastern**\
Final CTF competition: Wednesday, November 18, 2026 

### Purpose

Build and evaluate the agent you will use in the final CTF competition. You have the option to start with your assignment 3 agent or build a new one. Use evidence from testing to identify failures, improve the agent, and check whether your changes helped. Benchmark solve rate is not graded, but testing should show evidence of improvement.  A successful autonomous run must be demonstrated through a video or live demo.

This assignment is Part 1 of the final project. Reuse your agent, tools, evaluation integration, and resource controls in Part 2. Your report must explain your architecture configuration, performance metrics, the biggest remaining weaknesses, and the changes you made to improve performance.

Your grade depends on how you use evidence to diagnose problems, test a change, and explain the result. A change that does not improve performance can still earn full credit if you test it fairly and explain what happened.

### Before you start

Work with your final-project team. Use the Implementation Guide for setup, examples, and result checks.

- **Scored evaluation:** use 10 of the CTFTiny challenges. Keep these separate from development (you are welcome to use more, but be aware that those will run into API limits)
- **Suggestion**: run on one or two challenges to test setup first before committing to a larger run. 

Do not consult evaluation flags, solutions, or write-ups while developing or scoring. (This results in scoring leakage) 

### 1. Build the agent and check the environment

Your agent must observe results, choose tool actions, and adjust its next action. A single model response does not meet this requirement. Explain the architecture, identify each team member's contribution, and cite any AI usage.

- Define each tool's inputs, outputs, validation, timeout, and error behavior. 
- Enforce a hard wall-clock limit, step, or token limit in code. This will ensure you do not have run-away loops.
- Submit candidate flags through the evaluator. Log each submission and its verification result without revealing the expected answer.

#### **Important:&#xA0;**&#x4B;eep the solver separate from the evaluator

The solver runs commands in an isolated environment. It receives only the challenge description, contestant files, and permitted target connection. The trusted controller starts and resets targets, holds the answer key, and verifies submitted flags.

Keep `challenge.json`, expected flags, server-only source, target build files, evaluator storage, and the Docker control socket out of the solver environment. Do not give the solver an administrative shell in the target. A valid flag must come through the intended challenge interface. (***note: we have seen that agents will attempt to "cheat" to get the right answer***)

#### Limit access and resource use

Restrict solver network access to the assigned challenge endpoints. Be careful about internet access, you do not want the models looking up the answer. Retain evidence that the controls work, including blocked requests. If an action reaches outside the permitted environment, stop the run, preserve its trace. Analyze blocked attempts as part of the run and report any unexpected behavior.

### 2. Use testing to improve the agent

#### Review traces for failures

Start by running your agent on development challenges and reading the traces. Follow the sequence of tool calls, arguments, returned results, and subsequent actions. 

Questions to consider:

- **Tool selection:** does it call a tool suited to the task? Does it skip a needed tool, call one unnecessarily, or repeat the same call without learning anything?
- **Tool inputs:** are arguments, paths, targets, and commands valid? Does the agent understand the tool's output or error?
- **Use of results:** does the next action follow from the returned evidence? Does the agent ignore useful information, lose it from context, or claim success without verification?
- **Attempts to find test answers:** does it try to search the web for the challenge name, a flag, or a published solution instead of solving the challenge? Check search queries, URLs, network requests, and blocked calls. 
- **Recovery and stopping:** does it change approach after a failure, get stuck in a loop, stop too early, or continue after the evaluator has verified success?

#### Test changes

Use the results above to test changes.  These could be changes to a system prompt, tool description, planner, or tool. Write a hypothesis that connects the observed problem to your proposed change before running the comparison.

#### Run a small pilot first

Run a small batch of development attempts before starting a larger batch. Fix problems and repeat a small pilot as needed. Use the pilot traces to check whether your change addresses the problem you identified. Proceed when the readiness checks pass and projected resource use fits the approved cap. The pilot does not require a high solve rate. Keep pilot records separate from scored results.

#### Freeze the setup and run against the larger batch

Once you are happy with the changes, freeze the setup and run against all challenges. Because these are variable repeat the challenges 2-3 times as token budget allows (you are limited in the number of tokens/day using the Duke AI gateway. 

### 3. Report the results

Calculate these metrics for each configuration. 

| Required metrics   |                                                                                                                                               |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------- |
| Metric             | Calculation                                                                                                                                   |
| Pass@k             | Plot the pass rate across a 1, 2, and 3 trial runs.                                                                                           |
| Average solve rate | Plot the average solve rate/run and the variance.                                                                                             |
| Time and resources | Per-attempt and total wall-clock time, tool and model calls, available token counts, and measured or estimated cost. Include failed attempts. |

#### Support the comparison with traces

- Show successes out of three (or how many times you ran it) for every challenge.
- Report solve-rate changes in percentage points, with changes in time, tokens, and cost. Explain the changed behavior and cite specific trace steps.
- Disclose prior exposure or suspected recall. 



### 4. Prepare for the final

Choose the configuration you will carry into the competition and explain the tradeoff. 

- **By November 4:** aim to get an initial version of the system running. This is a planning checkpoint, with no separate submission.
- **By November 11:** finish the scored comparison and submit this assignment.
- **November 12–17:** test any additional changes on practice challenges, check for regressions.

### What to submit

Submit one package ***per team*** in Canvas by **November 11 at 11:59 p.m. Eastern**.

1. **Repository:** agent code, evaluation integration, aggregation script, pinned dependencies, configurations, frozen commit, and README instructions for clean setup. Identify the selected configuration and its launch command.
2. **Report:** approximately three pages. Explain your architecture, any problems you ran into, changes you tested, and a full results table. State each member's contribution and cite reused code and AI assistance under course policy.
3. **Successful-run video or live demo:** show one fresh run. Include tool activity, flag submission, evaluator confirmation, configuration, commit, challenge ID, and run ID.  Videos are limited to three minutes; disclose cuts or time compression (some runs may take a while). 

### Grading

| 50 points total                   |        |                                                                                                                                      |
| --------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------ |
| Criterion                         | Points | Full-credit work                                                                                                                     |
| Agent and readiness               | 8      | An adaptive agent with clean startup, error handling, and budget termination.                                                        |
| Evaluation and reproducibility    | 10     | Pilot first; fixed settings; fresh trials; complete records; correct metrics; and instructions to rerun the experiment.              |
| Comparison and improvement        | 20     | A hypothesis based on an observed problem; controlled comparison; measured effect explained with traces; and configuration decision. |
| Failure analysis and limitations  | 6      | At least one annotated case using tool calls and results and your suggested testable improvement.                                    |
| Controls and resource limits      | 3      | Answer separation, enforced scope, protected credentials, and complete resource and incident records.                                |
| Successful-run video or live demo | 3      | An identified autonomous run with verified success, shown by video or live demo, and its complete trace.                             |
