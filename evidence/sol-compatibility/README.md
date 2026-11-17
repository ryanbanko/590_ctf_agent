# Sol gateway diagnostics — November 17, 2026

## Follow-up after the second user-run failure

The user's retry `c49236369760` again ended on its first request with HTTP 400,
zero tool actions and clean cleanup/export. Two additional API-only checks ran:

- Original system prompt, all three production tools and 8192 output tokens,
  with harmless user input: completed, returning OK (976 input/43 output tokens).
- Latest failed first request rebuilt from recorded input/tools and unchanged
  settings: HTTP 400. Its error body reports a nested provider `cyber_policy`
  rejection, stating that the content was flagged for possible cybersecurity risk.

The latter body is in local
`runs/sol-compatibility/probe-068ec8d6f502/probe.json`, under `http_error.message`.
The original runner's privacy hook retained only HTTP status; it did not retain
the raw rejection text. This confirms the replay's cause and supports an
explanation of the earlier matching failures, but does not recover their bodies
or identify a specific triggering phrase. The error directs authorized security
users to the provider's access process; no access change was made.

No solver was started, target contacted or returned tool executed by these checks.
Five diagnostic model requests ran in total; the $0.000614 below belongs only to
the first three. Rejected usage/cost remain unknown; the follow-up has no hosted
readback or independently reconciled billing. Diagnostics are stopped. Application
code/default Luna configuration are unchanged; optional Sol config is retained.
No prompt rephrasing, model alias or automatic fallback was introduced.
[Hashes, sanitized results and request reconstruction checks](followup.json).
[Follow-up diagnostic script](followup-probe-script.txt).

The original three-probe checkpoint follows; its unresolved-cause and retry
recommendation were superseded by this follow-up.

## Original three-probe checkpoint

The user-run Void attempt `b5a999ddfb5c` loaded `htb-sol.toml` and ended on its
first model request with `gateway_http_400` / `response_source_error`, before any
tool action. Cleanup passed and the local trace exported. The error hook preserves
HTTP status but intentionally excludes the raw provider error body; the rejected
field or rule is not identifiable from this trace. Unknown usage is not zero cost.

The user then authorized very simple single model calls. The announced limit was
three synthetic requests, without challenge execution or returned-tool execution.
Read-only live Duke metadata advertised the exact configured name `gpt-6.1-sol`.
Both it and working Luna are listed as chat mode; this alone does not establish
the gateway's internal Responses routing or explain the original error.

| Synthetic request | Result | Input/output tokens | Native cost USD |
| --- | --- | --- | ---: |
| Exact model name, reply OK | Completed; OK | 11 / 5 | 0.000072 |
| Add medium reasoning, auto summary, encrypted-content include and parallel_tool_calls=false | Completed; OK | 11 / 5 | 0.000072 |
| Add one diagnostic function definition and request a function call | Completed; function_call returned; not executed | 140 / 19 | 0.000470 |

Total: **three requests, zero executed tools, $0.000614 summed native generation
cost**. No name variation was needed because the exact advertised name worked.
All three traces have one root and one complete, correctly parented generation.
Readback used the existing cached Langfuse CLI. No additional model requests ran
during readback; native costs are not an independently reconciled bill.

[Requests, outcomes, trace links, hashes and limits](review.json).
[Exact diagnostic script snapshot](probe-script.txt). Original records/exports
remain Git-ignored under `runs/sol-compatibility/`; source run hashes are retained.
No credentials, challenge payloads or candidate flags enter this evidence.

These probes use a harmless short prompt, 128 output tokens, and at most one
synthetic function. They do not reproduce the original 8192-token request with
the challenge/system input and all three production tools. A transient rejection
or a difference in those inputs remains possible; neither is diagnosed. The
original naming, medium effort and basic API features are supported by the probes,
but full application compatibility and follow-up tool-result replay remain untested.

No runtime/configuration correction is justified by these results, and none was
made. One fresh user-run retry with unchanged settings is reasonable. If HTTP 400
recurs, stop repeated retries and capture a bounded, sanitized rejection in a
separately authorized diagnostic. Do not blindly rename the model, switch APIs,
remove reasoning, relax scope or replace the failed record. No Docker operation,
challenge request, target command, commit or push was performed during diagnosis.

Before these model calls, the first sandboxed metadata GET failed with ConnectError;
the approved read-only escalation returned HTTP 200. This local network restriction
does not explain the user's earlier gateway HTTP 400. Online documentation supports
the model identifier, medium effort and Responses tool calling, but does not
establish Duke's deployment behavior. Runtime tests were not rerun because no
runtime/configuration/test files changed. Evidence checks are in checks.json.
