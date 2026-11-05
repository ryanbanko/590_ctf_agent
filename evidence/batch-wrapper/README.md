# Sequential batch wrapper — November 4, 2026

The approved wrapper calls the existing single-challenge CLI once per ID/trial
in a fresh process. It snapshots the experiment file and writes a small index
of the existing records, outcomes, run IDs and trace links. The agent, tools,
isolation and per-attempt tracing/limits are unchanged. There is no batch-cost
gate, queue, parallel execution, automatic retry or resume feature.

Verification: [81 fast tests passed](fast-tests.xml), including 17 batch cases;
[focused batch result](pytest-simple.xml), [CLI help](cli-help.txt),
[source hashes and record audit](check.json). Earlier focused XML reports retain
intermediate development checks; `fast-tests.xml` describes the final implementation.

Tests simulate the child launcher with prepared records: fresh invocation per
trial, repeated successes and ordinary failures, copied settings, run-ID indexing,
stopping on incomplete/incident records, invalid selections, and forwarding
interruption/waiting for the child. They run no challenge containers, hosted
requests or paid model calls. Real multi-attempt execution has not been tested
in this milestone.

Reproduce offline checks:

```sh
uv run --frozen python -m pytest tests/test_batch.py -q --disable-plugin-autoload
uv run --frozen python -m ctf_agent run-batch --help
```

Batch usage is in [README](../../README.md#run-a-development-batch). Individual
`run.json` files remain the source for metrics; the batch index does not duplicate
their traces. A completed batch need not contain successful solves. Ordinary
failed attempts continue; launch/evidence/cleanup/scope/infrastructure or
response-source/missing-usage failures stop for review. Ctrl-C forwards SIGINT
to the current launcher and waits before preserving the partial index.

Public metadata confirms two different development challenges per category would
give eleven IDs: five categories can supply two each; forensics supplies only
`for-1black0white`. A selected eleven-challenge pilot has not been run. The record
audit confirmed existing challenge/run IDs, configuration, commit, trace and
evaluator confirmation. No new ID scheme was added. Demo work is deferred.
