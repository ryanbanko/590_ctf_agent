# Original resources and design context

These are the five technical resources the user supplied at the start of this
project. They informed the design and should be reviewed when working on the
corresponding integration. Findings below describe the November 3, 2026 review;
verify current package/API details when implementing them.

## Authority and professor clarification

[ASSIGNMENT.md](../ASSIGNMENT.md) preserves the original assignment and is the
authoritative source for course requirements. The user's initial approach was
tentative; examples, defaults, dependencies, prompts, and permissions in external
resources are not additional requirements or automatically approved choices.

The user asked the professor whether the referenced Implementation Guide meant
the CTFTiny and NYU CTF Bench documentation rather than a separate class guide.
The professor replied, as reported by the user:

> Thanks. Yeah it is basically the implementation guide there.

Use the resources below as that setup/operation guidance while checking them
against the assignment, especially its solver/evaluator and access boundaries.

## 1. CTFTiny — required benchmark target

Original link: <https://github.com/NYU-LLM-CTF/CTFTiny>

- The README explicitly says CTFTiny follows NYU CTF Bench's structure and refers
  to NYU's usage guidance. This is why the NYU documentation and loader apply.
- We inspected the index metadata and repository filenames: 50 indexed challenges,
  with category/challenge/event/path/year fields. We did not open individual
  challenge answers or solutions.
- Design consequence: later use `nyuctf` with an explicit path to `ctftiny.json`.
  The assignment's scored set must come from CTFTiny, with 10 challenges kept
  separate from development. The current manifest reserves 10 scored IDs and 40
  development IDs using metadata only; dataset pinning and validation remain pending.

## 2. NYU CTF Bench — dataset conventions and Python package

Original link: <https://github.com/NYU-LLM-CTF/NYU_CTF_Bench>

- Its `nyuctf` package provides `CTFDataset`, `CTFChallenge`, contestant-file and
  endpoint metadata, and Compose lifecycle helpers. Its NYU development/test
  splits are not CTFTiny selections.
- We reviewed generic loader/lifecycle code and the published wheel in memory.
  At review time PyPI published 1.1.1 while repository main declared 1.1.2;
  relevant APIs existed in the published wheel. Installation is still pending.
- `CTFChallenge` holds the expected flag alongside public metadata. The lifecycle
  helpers invoke the supplied Compose file directly and do not enforce all course
  controls. Package objects must remain trusted host data; construct public task
  messages explicitly rather than serializing whole objects.
- Design consequence: reuse package conventions and supplied target Compose files
  wherever compatible. Inspect actual target configuration before deciding that
  an override or additional lifecycle code is needed. Real CTFTiny target
  compatibility has not been tested or modified.

Supporting sources:
[dataset loader](https://github.com/NYU-LLM-CTF/NYU_CTF_Bench/blob/main/python/nyuctf/dataset.py),
[challenge/lifecycle implementation](https://github.com/NYU-LLM-CTF/NYU_CTF_Bench/blob/main/python/nyuctf/challenge.py),
[published package](https://pypi.org/project/nyuctf/).

## 3. NYU documentation — setup and operation guide

Original link: <https://nyu-llm-ctf.github.io/docs/>

- Reviewed dataset setup, framework installation/operation, and configuration.
  Some pages describe NYU's complete reference agent framework, not just the
  challenge loader package.
- Design consequence: follow benchmark data/target conventions without assuming
  we must adopt that agent architecture, its hint features, tools, default model,
  default network, or example budget. Course controls take precedence.

## 4. Reference agents — architectural examples, not challenge solutions

Original link: <https://github.com/NYU-LLM-CTF/nyuctf_agents>

- Reviewed generic baseline startup, conversation, environment, tools, setup
  script, and solver Dockerfile. The separate solver container and copying of
  listed contestant files support our basic host/solver/target arrangement.
- The command, file-creation, and flag-checking tools motivated our small tool set.
  The baseline flag checker prints the expected answer; that behavior must not be
  copied. Its ordinary shared network and solver image privileges are not proof
  that the assignment's stronger controls are satisfied.
- Design consequence: use the reference implementation to understand interfaces
  and responsibilities. Our implementation uses a small function-based loop
  (now verified with scripted responses) and explicit controls, rather than
  vendoring the full agent framework. The trusted runner supplies bounded model/tool
  functions; Langfuse now owns detailed tracing. Live model integration was pending
  at that review and is now verified synthetically below.

Supporting sources:
[baseline entry point](https://github.com/NYU-LLM-CTF/nyuctf_agents/blob/main/run_baseline.py),
[environment](https://github.com/NYU-LLM-CTF/nyuctf_agents/blob/main/nyuctf_baseline/environment.py),
[tools](https://github.com/NYU-LLM-CTF/nyuctf_agents/blob/main/nyuctf_baseline/tools/tools.py).

## 5. Duke AI Gateway guide — model access

Original link:
<https://ai.colab.duke.edu/colab-ai-blog/all-blogs/getting-started-with-dukes-ai-gateway-a-developers-guide/>

- The guide describes OpenAI-compatible access, model discovery, authentication,
  and gateway usage management. It informed the proposed use of the OpenAI Python
  client through Duke's LiteLLM gateway.
- At the initial review that approach was not implemented. Confirm available models, tool calling,
  API flavor, compatible settings, actual pricing, and account allowance before
  selecting a model or performing an approved live check.
- At that stage the approximately $1/day allowance was the user's unverified planning assumption,
  not a confirmed account limit or a requirement inferred from this guide.
- Credentials remain in trusted host configuration, outside solver environments
  and application trace inputs. No gateway model calls had occurred at that stage.

Subsequent approved model milestone: the user chose Responses and automatic
Langfuse integration and confirmed a $1/day allowance. Read-only gateway model
metadata authenticated and listed 41 models. One approved synthetic attempt with
`gpt-6-luna` used two requests and succeeded, with native hosted usage/cost readback.
Gateway pricing matched the [official model page](https://developers.openai.com/api/docs/models/gpt-6-luna).
The [Responses function-calling guide](https://developers.openai.com/api/docs/guides/function-calling)
and [reasoning guide](https://developers.openai.com/api/docs/guides/reasoning)
informed native output replay and linked function results. This is setup evidence;
model selection for real challenge performance remains future work.

## Subsequent approved reference: Langfuse

The user later selected Langfuse as the sole detailed tracing system and asked for
narrow runner/loop interfaces using normal SDK patterns. SDK **5.1.0** was resolved
from PyPI, pinned, installed, and inspected locally. Integration follows the
[SDK overview](https://langfuse.com/docs/observability/sdk/overview),
[native instrumentation](https://langfuse.com/docs/observability/sdk/instrumentation),
and [client/exporter reference](https://python.reference.langfuse.com/langfuse).
It removes custom JSONL tracing while retaining normal result/provenance files.
The real SDK's supported in-memory exporter enables local synthetic verification.
Hosted setup and verification followed as a separate milestone. No individual challenge
material or model API calls were needed for this migration.

The user then requested installation of the
[official Langfuse skill](https://github.com/langfuse/skills). Its instrumentation
and CLI references, current [best practices](https://langfuse.com/docs/observability/best-practices),
and [query documentation](https://langfuse.com/docs/api-and-data-platform/features/query-via-sdk)
guided the hosted verification. The pinned SDK's own OpenAI integration confirmed
our messages/tools generation input shape. One synthetic hosted trace was read
through the current observations API and independently through `langfuse-cli`;
[evidence](../evidence/langfuse-cloud/README.md) records the result. This verifies
hosted delivery/readback for that project, not real model usage or general service
reliability. The CLI was used for review, not added as an application dependency.

The later [automatic OpenAI integration](https://langfuse.com/integrations/model-providers/openai-py)
now owns live generations. OpenAI 3.44.0 is pinned; Langfuse 5.1.0 remained current
when checked against PyPI. The installed SDK's documented behavior and offline
transports verified native model/token observations. The normal SDK includes its
public project identifier in instrumentation scope; secret credentials remain
excluded. A response hook keeps raw provider HTTP error bodies outside tracing.
The CLI retrieved the live synthetic trace and usage/cost totals agreed with
the local estimate. See [model evidence](../evidence/model-integration/README.md).

## What is preserved versus still pending

All original links are retained here; external repositories/sites have not been
vendored or fully archived. Local code, assignment, decisions, status, and
verification evidence are saved in this workspace. External contents can change.

Generic reference-agent/infrastructure review is permitted. The assignment's
restriction on consulting held-out evaluation flags, solutions, and write-ups
during development/scoring remains in force. Trusted evaluation can load expected
answers programmatically without exposing them to the model or separately in logs.

Use [DESIGN.md](DESIGN.md) for decisions and alternatives and
[PROJECT_STATUS.md](../PROJECT_STATUS.md) for current scope, findings, and open work.
