# Agent usability milestone — November 4, 2026

Approved scope: writable Python/home/temp storage, runtime pip connectivity,
interactive sessions, recoverable command timeouts, bounded output files, expanded
live limits and removal of local spending caps. GDB changes were deferred.

The existing three tools and function-based modules remain. No dependency or
framework was added to the runner or image. Session/process handling stays in
`docker/worker.py`, using standard-library Unix sockets, PTYs and Linux subreapers.
Each command supervisor owns its descendants, including detached children. This
is necessary for recovery without killing other live terminal sessions.

## Verification

[Verification index](verification.json) records final source hashes, image IDs,
resolved live settings, 82 fast tests, 27 distinct passing Docker cases and a
successful cleanup check. This is environment evidence, not a solve-rate result.

| Evidence | Result |
| --- | --- |
| [Fast tests](fast-tests-final.xml) | 82 passed. Covers response replay, usage, limits, session arguments, unconfirmed-cleanup stopping, split labeling and batch orchestration with substitutes. |
| [Main Docker run](self-check-21e839424780/pytest.xml), [log](controls-final.log) | 22 cases passed before an absent-network cleanup error was found. |
| [Completion checks](completion-checks.xml), [log](completion-checks.log) | The corrected cleanup case and all four remaining cases passed: 27 distinct Docker cases passed across the main run and focused completion. |
| [Independent cleanup/output proof](cleanup-output-proof.xml) | Two focused checks passed: the detached PID is absent from `/proc` after timeout, and the saved output is readable through the existing command tool. |
| [Preparation check](ctftiny-readiness-a1cb587a676b/check.json), [log](preparation.log) | `pwn-baby-boi`: two fresh staging/connection/isolation/reset/cleanup cycles passed; no solving or model requests. |
| [Solver build](solver-build.log), [guard build](guard-build.log) | Images rebuilt locally. Both image IDs are in the verification index and run provenance. |

The package probe installed `humanfriendly==10.0` through pip inside the fresh
venv and imported it successfully; its install/import command took about 1.66
seconds in the main run. It also wrote an 80 MiB file (above the old workspace
limit) and checked writable home/temp settings. A separate fresh attempt confirmed
that package additions and home markers were absent, while baseline libraries
remained available. Actual installed versions are in each attempt's `packages.json`.

Session checks exercised a real terminal prompt, line input, independent ordinary
commands, exit, invalid/finished session IDs, explicit close and stopping an
unpolled session at the attempt deadline. Timeout checks include detached children
and commands with closed output; a subsequent command succeeds after cleanup.
Existing private-filesystem, capability, guard-loss, scope-denial, IPv6,
interruption and submission controls also passed.

Output checks preserve an ending diagnostic in the excerpt, save complete output
below the file bound, and explicitly mark overflow above 1 MiB. Files in
`completion-checks/*/outputs/` are copies available after solver cleanup.

Historical failures remain intact: [first run](self-check-9d4061f36ac6/suite.json)
used a three-second deadline that expired during venv startup; deadline probes now
allow eight seconds so they reach the runtime behavior under test. The next run
found Docker's absent-network error wording when setup failed before creating
an egress network. That cleanup branch was corrected and passed in the focused
completion. No existing historical evidence was removed.

## Current behavior and limits

- The live profile is 600 seconds, 120-second ordinary commands, 60-second model
  requests, forty model responses, eighty tool calls, 512 KiB serialized model
  input, 4,096 output tokens, 1 GiB RAM and 512 MiB workspace.
- Interactive calls wait at most five seconds; sessions use the attempt deadline.
  Ordinary command timeouts permit recovery only after confirmed cleanup.
- Live output is 64 KiB. Larger output returns beginning/end excerpts and a file
  path; files retain the first 1 MiB with overflow marked. Package/output snapshots
  survive reads; a hard stop can lose output generated since the last copy.
- Docker DNS/public IPv4 HTTPS provide practical pip access. The prompt restricts
  external internet purpose to dependency installation and forbids answer lookup.
  This is not enforced pip-only networking. Other private/reserved destinations
  and unapproved challenge ports still trigger recorded scope stops.
- Usage/cost estimates remain; local cost caps/reservations are removed. Missing
  usage stays unknown and terminal. No API model calls or challenge-solving
  attempts occurred; model API spending was $0.
- Pip cannot supply every native system dependency. GDB's existing live-debugging
  limitation on the tested Mac remains; no debugging permissions were changed.

Teammates rebuild with `uv run --frozen python -m ctf_agent build-images` after
pulling. Current operation and tool fields are in [README](../../README.md).
To reproduce checks, run the fast suite and `python -m ctf_agent self-check` through
uv as documented there. Review before authorizing another live development pilot.
