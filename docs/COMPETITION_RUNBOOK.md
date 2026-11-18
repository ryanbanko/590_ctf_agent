# Competition day runbook — Duke AI CTF (event 3755)

Run these in order. The HTB MCP integration is validated offline but the live
container path is gated on HTB's backend, so validate in gates before launching.

Branch: `feat/htb-mcp`. Agent team: `[AI] ai-agent-of-6unt3r` (registered).

## Pre-flight (before noon)

1. Connect the Duke VPN (needed for the model gateway, not for HTB's MCP server).
2. Start Docker. Images are prebuilt (`ctf590-solver/guard/fixture:m1`).
3. Be on the branch: `git checkout feat/htb-mcp`.
4. `.env` has all five keys: `HTB_MCP_TOKEN`, `LITELLM_TOKEN`, `LANGFUSE_PUBLIC_KEY`,
   `LANGFUSE_SECRET_KEY`, `LANGFUSE_BASE_URL`.
5. Confirm the MCP token has not expired: HTB → Profile Settings → MCP Access.
6. Preview the live challenge list (read-only):
   ```sh
   uv run --frozen --env-file .env python -m ctf_agent htb-challenges --ctf-id 3755
   ```

## Gate 1 — does spawning work, and what is the endpoint shape?

The `connection_endpoints` parser has not seen a real running container. Capture it:

```sh
cd runs/htb/mcp-probe
py htb_mcp_probe.py call start_container '{"challenge_id": <ID>}' --allow-write
py htb_mcp_probe.py call container_status '{"challenge_id": <ID>}'
```

Check the returned host/port fields against `ctf_agent/htb.py:connection_endpoints`
(ip / host / hostname + port / ports / docker_ports, or a "host:port" string). Adjust
that one function if HTB's shape differs. If `start_container` still 500s, spawning is
down — use the manual fallback below.

## Gate 2 — one-challenge smoke test (spends a little)

```sh
uv run --frozen --env-file .env python -m ctf_agent run-htb --ctf-id 3755 --challenge <EASY_ID>
```

Confirms: solver reaches the HTB target, agent solves, flag submits, `verified_success`.
Watch the Duke gateway dashboard for the real cost (the local estimate undercounts).

## Gate 3 — launch the event

```sh
# Sequential, conservative (default budget $20, safe under the $25 key):
uv run --frozen --env-file .env python -m ctf_agent run-htb-event --ctf-id 3755

# For placement speed, once it is clearly working:
uv run --frozen --env-file .env python -m ctf_agent run-htb-event --ctf-id 3755 --workers 3
```

`--budget USD` overrides the budget. `--limit N` caps challenges attempted (testing).

## Monitor

- Real spend on the Duke gateway dashboard, not just the printed `spent_usd`
  (local cost omits the cache-write premium and undercounts).
- The HTB scoreboard.
- Keep notes: challenges attempted/solved, tokens, where it got stuck (for the summary).

## Fallbacks

- MCP `submit_flag` misbehaves but spawn works — keep MCP for everything except the
  verdict, relay flags by hand (works with `--workers`, prompts are serialized):
  ```sh
  uv run --frozen --env-file .env python -m ctf_agent run-htb-event --ctf-id 3755 --manual-verify
  ```
- MCP fully broken — spawn each challenge on the HTB website and run one at a time;
  it prompts for the challenge + target IP:port, then the agent solves and you relay:
  ```sh
  uv run --frozen --env-file .env python -m ctf_agent run-manual
  ```

## Budget / policy knobs

`ctf_agent/compete.py:DEFAULT_POLICY` — global budget ($20 default), per-difficulty
turn/wall/effort caps, and `reserve_hard_below_fraction` (defer hard/insane when low).
Strategy: breadth first (easy/medium), defer expensive hard attempts. Recalibrate the
caps from real per-challenge costs after Gate 2.

## Deliverables (due Nov 24)

- One-page team summary (what you learned, performance, placement, budget used).
- Individual contribution statement (each member).
- Do not include the API key or MCP token in either.
