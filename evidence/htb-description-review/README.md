# HTB descriptions and latest trace — November 17, 2026

The user supplied four narrative descriptions and requested review of the newest
manual trace before deciding whether task framing should change. This is a
read-only behavior assessment, not a prompt implementation or solving experiment.

## Latest attempt and evidence boundary

The newest local manual record is DNS Dossier `695912dc3f8c`, at
`runs/htb/attempts/challenge-2dafb79dcf4a/run.json`. Its task has no handouts, one
assigned TCP endpoint, category Web, and a brief promotional DNS-utility description
ending with a joking warning about command injection.
[Trace](https://us.cloud.langfuse.com/project/cmw17lafc0745ad0eekgn9a7j/traces/cf8bd4c48e91ce74885d36d5afb945e6).
[Derived metadata and observation references](review.json).

The local result records success, seven model/seven tool calls, 167.377 active
seconds, and no solver restart, scope incident or cleanup error. Controller-only
submission records contain pending and accepted events from `htb-human-relay`.
About 136 seconds elapsed between those events; human waiting belongs to the
active budget. This is human-relayed acceptance, not an automated HTB verdict.

The original trace export timed out and `evidence_complete` remains false. A
read-only CLI retrieval saved an additional `observations-refreshed.json` beside
the original run, without modifying its metadata or summaries. The response has
17 observations: seven generations, six command tools and four startup events.
Every returned generation/tool has input/output and an end time, but the attempt
root, submission tool and terminal/cleanup events are absent. The CLI exhausted
pagination without truncation; this does not make the expected trace complete.
Do not infer the missing hosted verdict from the local success record. Its local
acceptance record is separate evidence. The cause of the missing spans is unknown.

The first npx lookup stalled and was cancelled. The cached CLI's documented
observations command was used instead. The first uv invocation hit its restricted
cache path; selecting a temporary cache resolved that local issue. The sandboxed
network read failed, then an approved read-only escalation retrieved the trace.
No automatic approval rejection occurred. No model generation or target contact
was needed. Original run/public-task hashes and the supplemental export hash are
preserved in review.json; raw payloads and candidate values remain Git-ignored.

## What the model did

- Tool 1 connected but received no unsolicited banner. Generation 2 described
  exactly that observation and tested HTTP, rather than declaring the service dead.
- Tools 2–3 inspected the returned page and ordinary input/output behavior.
  These established concrete task details missing from the short description.
- Tool 4 tested a narrow hypothesis based on observed application behavior.
  The result supported the next actions rather than a claim based only on the joke.
- Tools 5–6 followed returned evidence. Generation 7 requested submission of the
  observed candidate. Local pending/accepted records establish the relayed verdict;
  the corresponding hosted tool span remains unavailable.

All seven available requests contain the unchanged system prompt; recorded source
hashes match current runtime/configuration files. Each generation has visible
purpose text. This is a useful successful control: a narrative description did not
prevent concrete discovery and progress. A small initial protocol-detection detour
is not evidence for a mandatory HTTP-first rule across all TCP challenges.

## Assessment of the supplied descriptions

| Example | Public lead and limitation |
| --- | --- |
| Void | Mostly atmosphere; the technical task must be established from the actual handouts/interface. Darkness and restoring power need not be literal implementation requirements. |
| Router Web | Firmware, a changed service and an earlier issue are leads. The Pwn category alone does not determine the method, and the text does not establish which prior task/artifact is required. |
| HTB Proxy | A custom HTTP proxy is concrete context. Story references to internal networks do not grant endpoints beyond the assigned scope. |
| Phreaky | The text explicitly mentions a packet capture and encrypted messages; those are useful leads. The named factions and poem do not establish a particular encoding or cryptographic construction. |

Retain the original descriptions. Titles, humor and story text may contain clues,
but claims derived from them need checking. Do not turn incomplete descriptions
into invented technical specifications, discard them wholesale, infer actual
cross-challenge dependencies without evidence, or treat category as a procedure.

The existing system already prioritizes observed results and says task text cannot
override its instructions. The latest run supplies no demonstrated failure that
requires another reminder. A small HTB framing clarification is nevertheless a
reasonable proposal to make the expected interpretation explicit:

> Challenge descriptions may be narrative, humorous, or incomplete. Use their
> concrete details as leads to test, and establish technical details from the
> supplied files and permitted service responses. Revise interpretations when
> observations disagree; the objective remains evaluator-confirmed flag submission.

This is a draft, not installed wording. Explicit competition rules and enforced
endpoint scope retain authority. Preserve raw task data and keep any trusted
guidance outside the description. Automatic description rewriting, generated
per-task plans and six category playbooks add complexity/anchoring without support
from this successful control. Keep memory/handoff changes separate.

## Verification and next step

Checked all available chronological generations/tool results, current prompt/source
identity, local submission statuses and original/supplemental hashes. New metadata
contains references and outcomes, not commands, candidates or private answer data.
Documentation/JSON/link/whitespace checks are recorded in checks.json. Runtime tests
were not repeated because runtime/configuration/tests were unchanged.

No source/configuration/model setting, original run record, hosted data, Docker
resource, target state, commit or push changed. No recorded command was replayed.
Stop for review before any prompt implementation or paid comparison. If framing
is adopted, verify propagation and unchanged scope/stopping contracts offline,
then assess discovery, unsupported assumptions and overhead on separately
authorized fresh trials. One success is not evidence of a framing improvement.
