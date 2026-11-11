# Harder development trace review — November 11, 2026

This is an assistant-assisted, read-only diagnosis for team review, not human
annotation ground truth or an improvement experiment. No agent/settings changes,
challenge reruns, trace-command execution, target operations or paid model calls
were made. Existing hosted observations were queried read-only for the last
Android attempt. Candidate values and raw transcripts are omitted here.

## Coverage and evidence limits

Source: local `runs/pilots/unseen-development-three-per-category/batch-8c98b0fc7e14/`.
All 20 scheduled attempts were reached: 19 completed and the final attempt stopped.
There were 14 verified successes and six unsuccessful attempts. The batch status
is **stopped**, with 3,389.44 seconds recorded batch elapsed time. This is a
development capability sample, not held-out performance or a controlled comparison
with the earlier, different challenge sets.

Detailed review covered all six unsuccessful attempts and their four successful
counterparts: attempts 001, 004, 007, 008, 010, 011, 014, 017, 018 and 020.
The other ten successes were inventoried from records, not behaviorally reviewed.
All ten reviewed records have identical source hashes, runtime configuration and
model settings. Saved application/container source hashes match the current files.
Dirty provenance remains recorded; identical hashes do not establish identical
random challenge instances or live target state.

Local observation exports were available for nine reviewed attempts. Android
trial 2 has no original local export: a separate read-only hosted query recovered
20 observations (eight generations, eight tools, four startup events), but not
the ninth generation or error/cleanup tail. The recovered copy is local at
`runs/trace-review-new-development/android-observations-recovered.json`; it is
partial and does not replace the original record. Android trial 1 is missing
generation/tool 7 payloads; gibberish trial 2 lacks tool 6 input. Structural
`evidence_complete` does not establish that every payload is present.

| Challenge | Trial 1 | Trial 2 | Consistency |
| --- | --- | --- | --- |
| cry-lupin | Wall limit; 21 model / 21 tool calls; 600.08 active seconds | Success; 17 / 17; 156.88 s | Mixed outcome; parsing/editing problems in both |
| cry-open-ellipti-ph | Success | Success | 2/2 |
| cry-beyond-quantum | Success | Success | 2/2 |
| pwn-roppity | Text-only unsuccessful ending; 12 / 11; 130.03 s | Text-only unsuccessful ending; 20 / 19; 275.77 s | Repeated loss of endpoint access |
| pwn-pilot | Success | Success | 2/2 |
| pwn-got-milk | Success | Success | 2/2 |
| rev-gibberish-check | Input limit; 27 / 27; 437.40 s | Success; 23 / 23; 278.92 s | Incorrect reconstructed model and expensive search in both |
| rev-a-walk-through-x86-part-2 | Success; 5 / 5; 47.02 s | Text-only unsuccessful ending; 12 / 11; 94.82 s | Confirmed copying error in failed trial |
| rev-the-big-bang | Success | Success | 2/2 |
| msc-android-dropper | Success; 8 / 8; 87.07 s | Response-source error; 9 / 8; 136.69 s | Failed trial has incomplete telemetry |

Times above are attempt active time, distinct from batch/launch/export elapsed
time. Unknown Android trial-2 usage/cost remains unknown. Reviewed records show
zero scope incidents and no recorded cleanup errors; that does not prove targets
remained healthy during execution. See [review.json](review.json) for exact local
paths, trace URLs and file hashes.

## Diagnoses

### Exact data handling: reverse-engineering walk, trial 2

The decoder printed the same 50-character brace-terminated body accepted in trial
1. Trial 2's first submission changed a digit `1` to lowercase `i` at zero-based
index 35. The comparison uses recorded decoder output and recorded submitted
input, not an expected-answer file. Five subsequent submissions changed wrappers
or padding while retaining that body error. The agent ended with substantial
time/call headroom.

Evidence: trial-2 decoder tool `c486c246a3325017`, first submission
`6e13351d823afdbe`, and subsequent tools through `296592243023f690`;
trial-1 decoder `f138417d69266f1f`, accepted submission `9445136fec4f13c7`.
**High confidence:** an exact transcription mistake explains the initial rejection;
failure to compare against the original output explains the unproductive recovery.
It is one observed typo, not a measured general error rate. Together with the
other reconstruction/data-flow failures below, it supports a broader hypothesis
about evidence handling. The successful paired trial is a useful counterexample.

### Validation order and context: gibberish checker, both trials

Both trials reconstructed a checker, then ran costly searches before validating
that reconstruction against the original contestant binary. Agreement between
two implementations did not establish correctness because they shared the same
underlying interpretation. In trial 1, a token predicted to score 505 actually
scored 515 in a local threshold probe. Trial 2 likewise observed discrepancies;
even an assumed constant correction failed on another token.

Trial 1 had two command timeouts/resets. Its final stop was the controller's
serialized-input cap, not exhausted output tokens or model-call count. A
reconstruction of the next request is approximately 536,570 bytes, exceeding
524,288 bytes. The last captured generation input was about 512,046 bytes,
including 253,684 characters of opaque encrypted content and 192,285 characters
of tool output. This is cumulative history growth. Several large individual tool
results remained below the 64 KiB preview threshold, so overflow-file handling
did not activate. No opaque reasoning was decrypted or interpreted.

Trial 2 also had three timeouts/resets. It eventually tested a bounded sample
against the original unmodified local checker, found an accepted input after ten
iterations, used the permitted service and obtained verified success.

Evidence: trial-1 search tools `06de7e1f0ae344ff`, `28daba852b9a9c27`, local
validation `2336b26360f481f1`, threshold probe `db76a91449e1b3e8`, final
tool `a01f409585378032`; trial-2 original-checker search `4147bf40928ededd`,
service `691c129058c893e2`, accepted submission `a24af5d391dd01ed`.
**High confidence:** late independent validation recurs in both trials; the input
cap triggered once but exposes a general architectural limit. The success does
not prove the same random search would solve every instance. One trace's UTC
duration is inconsistent with monotonic active-time records; it does not by itself
prove broken deadline enforcement.

### Excessive recovery work and a variable error: lupin, trial 1

The agent chose to recover an entire large secret matrix. It repeatedly rebuilt
expensive intermediate calculations, debugged scripts and escalated searches.
Its decryption script also used ciphertext `C` where the distinct public vector
`U` was required. It recognized that variable error only at generation 21, then
reran expensive work with roughly 31 seconds remaining and hit the wall limit.
The correction did not finish; this review cannot claim it would have succeeded.

Trial 2 used a smaller objective based on the ciphertext's sparse combination,
validated matrix relations, and eventually obtained a favorable fresh sample
from the permitted service. It succeeded despite repeated parsing/quoting edits.
Random instance differences prevent attributing the outcome solely to strategy.

Evidence: trial-1 tools `28a3c2da9a79dc7e` and `7b67357db972e59a` start the
expensive recovery; tools `fca6f7e08f0f65b0`, `ae036504c61e10f0` and
`99010fe35928c061` repeat roughly 50-second runs; generation `7046c870b5edbd20`
identifies the variable mix-up, final tool `192762fc1402da7d` attempts correction.
Trial-2 useful sample/validation: `c70a6eab4ea658ed`, accepted submission
`87072dd3f096f97f`.
**High confidence** in the variable error and repeated computation; **moderate
confidence** that narrower objectives/earlier checks would improve reliability.
This is not evidence that more time alone is the best fix.

Output retention worked here: the oversized response had a marked preview and
complete solver-readable capture, which the agent read. Do not classify this
failure as lost truncated output.

### Repeated availability problem: roppity, both trials

Both trials initially reached the allowed service and obtained a leak followed
by another greeting. Later connections timed out or reported no route to host,
and access never recovered. No guard denial was recorded. Startup health checks
and eventual clean teardown cannot establish service health after the payloads.
The saved evidence cannot distinguish target exit, network failure, child-process
failure or emulation behavior. Calling this a confirmed libc mismatch or a
confirmed container crash would overstate the evidence.

There were secondary agent issues: trial 2 corrected an initial stack-layout
mistake, later selected unsuitable functions for additional leaks, and sometimes
interpreted connection errors too strongly. Its local crash debugging produced a
Rosetta AArch64 core rather than the expected AMD64 guest registers. That is a
concrete debugging limitation, not proof of the remote outage's cause.

Evidence: trial-1 successful leak `89426d59e5f95575`, first subsequent failure
`bdde6eb9c95152ca`; trial-2 successful leak `b006a865e71c11e2`, subsequent
failure `047991d188ce86a6`, core identification `1c8536f4d9f08d89`.
**High confidence** in repeated loss of availability (2/2); **low confidence**
in its underlying runtime cause. Both ordinary endings occurred before limits,
but the endpoint blocker makes them poor evidence for a generic continuation fix.
Other pwn tasks succeeded twice, so this does not establish a universal pwn failure.

### Request failure with missing tail: Android, trial 2

The available eight turns show progress: APK inspection, recovery from unsupported
shell syntax, decompilation, extraction of the secondary DEX and an allowed HTTP
request returning status 200 with 560 bytes. A raw TCP read had timed out before
the agent switched to HTTP. The local record then reports a ninth model call and
`response_source_error`; it does not save the original exception type. A separate
trace export raised `ReadTimeout`, which must not be assumed to be the original
model-request error. Hosted recovery also lacks that generation and stopping tail.

Evidence: shell error tool `fe188f88bcc073e0`, decompilation
`5be07cf33d024c8f`, TCP read `777e87edcaf44fd5`, HTTP result `7ae9044e34b30061`.
**High confidence** that termination was controller-classified as a response-source
failure; **unknown** exact provider/transport cause and eventual solving outcome.
This is one observed source-error ending in this batch. Missing payloads in other
reviewed exports make telemetry completeness a broader concern.

## Improvements to consider, not decisions

| Priority | Option and testable hypothesis | Smallest next check | Tradeoff / limit |
| --- | --- | --- | --- |
| High | Carry extracted values programmatically and compare exact bytes before format guesses; original-system checks early reduce self-consistent errors | Review existing prompt/tool affordances; mechanical transcription/differential-check examples, then a fresh development comparison if authorized | Generic validation advice already exists; more prompt text alone may not help. Extra checks consume time |
| High investigation | Save safe target status/exit/OOM/restart metadata at failure/end to distinguish availability from solving failures | Inspect existing lifecycle instrumentation; propose a small controller change before implementation | Does not explain this historical outage. Automatic target resets would change task state and need separate consideration |
| High investigation | Account for cumulative request size before the hard stop; selective output/checkpointing or later compaction may preserve useful progress | Reproduce sizing offline from records; compare available request headroom with retained data | Bigger caps defer the problem; compaction may lose evidence/native reasoning continuity. Do not blindly strip encrypted replay |
| Medium | Validate a small case, estimate work, and preserve expensive intermediates before full recovery/search | Examine cheapest invariants and checkpoint opportunities in the reviewed actions | Some hard problems genuinely need costly search; avoid rigid mandatory planning |
| Medium | Save a sanitized error category locally and audit payload presence, separate from structural export checks | Offline source-error/export-failure tests if implementation is approved | Avoid logging response bodies/credentials. Retrying a model request can add cost or duplicate uncertain requests |
| Separate experiments | Stronger model, reasoning, time/token allowance, planning/notes or text-only continuation | Define one variable and fresh development comparison after deciding which failure it targets | This batch does not isolate any of these interventions or show an output-token cap caused the failures |

Preserve isolation, exact scope, trusted verification, historical failures, useful
head/tail captures and reset feedback. No evidence here justifies weakening them.
The strongest next investigation is **roppity's target availability/lifecycle
evidence**, alongside choosing a small validation/data-handling improvement for a
separate approved change. Raw new-batch traces remain local; this report and
filtered manifest are shareable review artifacts, not a sanitized transcript bundle.
