# Implementation-aware proposal evidence — November 15, 2026

Supports the [concrete change proposal](../../docs/AGENT_CHANGE_PROPOSAL.md).
This is metadata analysis and source review, not an implemented agent change or
new experiment. No model calls, Docker operations, task-private reads or replay
of recorded commands occurred.

`context-growth.json` has one usage/size profile for each of the 355 generation
records across the existing 36 baseline attempts. Provider input totals reconcile
to every original run. Adjacent input growth measures all new request material,
not only a preceding tool result. Per-item JSON sizes are not token counts.
Encrypted reasoning content is never decoded or retained in these profiles.

Request bodies are readable for 353 generations. The final two inputs in
open-ellipti-ph trial 1 are null, alongside their two missing outputs and the four
missing tool input/output fields counted in the earlier review. Thus a full
request/action audit finds **eight missing fields across four observations**;
the earlier six-field count covered generation outputs and tool payloads.
One package-inventory event also lacks classification metadata. These gaps are
preserved; no original export was changed or silently filled.

All 36 initial package inventories explicitly succeeded. Thirty-five final
inventory events explicitly report unavailable with `RuntimeError`; one cannot
be classified from its metadata. Source review explains the expected terminal
failure: stop kills the solver before the final Docker exec. The proposed skip
records `attempt_stopping` and does not infer kill success from the flag alone.

The [checks record](checks.json) records profile/export reconciliation, source
hashes and document verification. It does not claim runtime verification of any
proposed feature. Raw run records remain Git-ignored; the derived profiles contain
no command text, candidate values, request contents or credentials.
