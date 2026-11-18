# Optional human guidance — November 18, 2026

Approved milestone: branch from current `htb-manual`, implement optional guidance
from a second terminal, and perform offline checks. Created `feat/htb-guidance`
from clean commit `7cb1837`. Initial sandboxed branch creation could not write Git
metadata; the authorized escalated retry succeeded. No automatic review rejection,
commit or push occurred.

## Implemented behavior

- Manual HTB `run-manual --allow-guidance` creates a host-only inbox and prints a
  ready-to-copy `guide --run DIRECTORY --message TEXT` command after solver startup.
  The command uses local files and no hosted credentials or model calls.
- Bounded message files are atomically published. Senders serialize publication
  using a short local file lock; the running agent never acquires that lock.
  Limits: 4096 UTF-8 text bytes/message, 64 messages total/attempt, bounded directory
  scans and record reads. Queue message symlinks and non-regular files are rejected.
- A callback before model requests inserts messages after completed tool results:
  `Human guidance: Consider this alongside the evidence gathered so far.` followed
  by a blank line and the supplied message. Guidance stays in history. No separate
  acknowledgment turn or tool is requested. Original system/tool definitions stay.
- Immutable message files preserve IDs, run binding, queue timestamps and text.
  Local receipt events and root-linked Langfuse events identify the receiving request
  attempt. Receipts are written after the responder returns/raises, using its
  invocation timestamp. They prove inclusion in the responder's input, not provider
  acceptance or model compliance. `--status` distinguishes queued,
  included_in_request, and undelivered after closure. Failed requests can have
  included guidance with unknown provider receipt.
- Summaries distinguish `guidance_enabled`, `guidance_messages`, `human_assisted`
  and `guidance_errors`. Enabled empty inboxes remain unassisted. Disabled runs
  create no inbox and perform no guidance filesystem operations.
- Known closed/dead runs reject messages. A send racing shutdown can remain
  undelivered. Success, text-only final output, deadlines, incident stops and
  cancellation remain terminal; limits and verification are unchanged. Guidance
  I/O/telemetry errors visibly disable the channel and allow solving to continue.

## Verification

Commands and checks are recorded in [checks.json](checks.json).

1. Initial focused queue/manual-SDK check: 20 passed.
2. An attempted wider command referenced nonexistent `tests/test_config.py`:
   no tests ran; corrected the file selection.
3. Wider check: 108 passed, one failed, two Docker cases deselected. The failure
   was the existing manual-config test expecting 900 seconds/60 requests instead
   of committed 3600 seconds/200 requests/240 tools. Updated the expectation,
   without changing configuration. Added startup/cap checks: 111 passed.
4. Tightened request inclusion bookkeeping, with checks that a stop between
   preparing a message and requesting a response leaves it undelivered, while a
   failed responder invocation retains the request attempt. Final focused suite:
   **113 passed, two Docker cases deselected**. [JUnit](offline-tests.xml).
5. Shared-launcher regression checks: **25 passed**. [JUnit](launcher-tests.xml).

Disabled versus empty-inbox checks cover identical histories/tool schemas,
model/scripted/tool counters and outcomes for success, text-only ending, turn cap,
deadline and scope stop. Other checks cover arrival during response/tool work,
ordering/persistence, duplicate prevention, CLI use without credentials/Docker,
malformed/oversized/symlink/non-regular/overfull records, queue cap and inbox startup
failure. The native SDK integration uses the pinned real OpenAI/Langfuse clients
with an offline HTTP transport and local span exporter; no hosted ingestion occurs.

The [empty-inbox microbenchmark](empty-inbox-timing.json) ran seven samples of 200
checks on this Mac. Median: **3.212 ms/200 checks**, **0.0161 ms/check**. This measures
the empty local directory path rather than model/solver latency. No performance
threshold is enforced across machines.

## Limits and next step

No live model request, real challenge, Docker operation, hosted mutation or
original-run modification occurred. Offline checks demonstrate mechanics, not
behavioral usefulness or a universal regression guarantee. The queue targets the
project's Linux/macOS hosts (`fcntl`, like the existing Unix terminal handling).

There is no recovery/replay after a crashed process. Message files remain, but an
abrupt crash can leave request inclusion unconfirmed; a reused PID can make an
old inbox's liveness check inconclusive. The explicit run path prevents automatic
rerouting to a different attempt. Local recording failures can leave incomplete
receipts even if a request received the text. Consult native generation payloads
when available. Guidance text is ordinary human input; the wrapper does not prove
its accuracy. Larger context and changed actions can increase later model use.

The existing pinned SDK remains 5.1.0; a dependency migration is outside this
milestone. Current [Langfuse instrumentation documentation](https://langfuse.com/docs/observability/sdk/instrumentation)
was consulted for root-linked event instrumentation; the existing native model
integration remains. No additional trace backend or service is introduced.

Review this milestone before an independently authorized monitored practice trial.
