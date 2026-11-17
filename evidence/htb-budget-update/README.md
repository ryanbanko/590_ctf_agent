# HTB manual budget update — November 17, 2026

After reviewing the latest Omni Watch run (`967483a16994`), the user selected a
30-minute wall limit and asked to increase the model-turn limit. The run stopped
at 900 seconds after 20 model requests and 15 tool spans; the configured 60 model
request cap was not reached. It had three solver restarts, and the latest browser
payload attempt ended at the wall deadline before its marker could be inspected.
The run gives a reason to test a longer monitored attempt, not evidence that more
time or turns will improve success.

Both HTB-only profiles now allow 1,800 seconds, 100 model requests and 120 tool
calls. The existing 90-second per-request timeout, 120-second command timeout,
reasoning, output cap, isolation/resource bounds, network scope and recovery limit
are unchanged. The tool-call allowance was raised proportionally to avoid making
it the immediate cap if the agent uses small commands. CTFTiny's 600-second/40
model-call development profile is unchanged. The operator plans to watch traces
and can stop early. No challenge run was started by this change.

The larger limits permit higher total model/tool use and can increase cost. They
are experimental operating bounds, not a performance claim or a dollar cap. In
particular, the Omni Watch trace showed repeated hypotheses without a confirmed
bot execution marker; added time should be assessed alongside that behavior.

## Verification

Loaded both profiles with the project configuration loader and confirmed the
derived `max_requests=100`, 1,800-second wall and 120-tool cap. The existing Luna
profile differs from its previous committed form only in these three limit
fields. CTFTiny development configuration matches `HEAD` byte-for-byte. The Sol
profile was already an untracked user-requested config; it now matches the Luna
HTB limits while retaining its separate model/pricing values. Details are in
[checks.json](checks.json).

No model call, target contact, Docker operation, test suite, hosted mutation,
commit or push occurred.
