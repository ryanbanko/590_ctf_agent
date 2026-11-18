# Command cheat-sheet — Duke AI CTF (event 3755)

**Rule:** every `ctf_agent` command that reaches HTB or the model needs
`--env-file .env` (loads `HTB_MCP_TOKEN`, `LITELLM_TOKEN`, `LANGFUSE_*`). Only
offline commands (`build-images`, `self-check`) omit it. The probe script reads
`.env` itself, so it never needs the flag. Full context: `docs/COMPETITION_RUNBOOK.md`.

Prereqs for anything that solves: **Duke VPN up**, Docker running, on `feat/htb-mcp`.

## The one you'll live on
```sh
uv run --frozen --env-file .env python -m ctf_agent run-htb-event --ctf-id 3755 --workers 3
```
Flags: `--workers N` (concurrent, 1=sequential, cap 6) · `--budget 24` (USD ceiling,
default 20) · `--limit N` (only N challenges) · `--manual-verify` (MCP spawns, you relay flags).

## Pre-flight
```sh
cd ~/Projects/590_ctf_agent && git checkout feat/htb-mcp
uv run --frozen --env-file .env python -m ctf_agent htb-challenges --ctf-id 3755   # live board (read-only)
```

## Validate concurrency first (once >1 challenge is unsolved)
```sh
uv run --frozen --env-file .env python -m ctf_agent run-htb-event --ctf-id 3755 --limit 2 --workers 2
```

## Single challenge (smoke test / one-off)
```sh
uv run --frozen --env-file .env python -m ctf_agent run-htb --ctf-id 3755 --challenge <ID>
```

## Fallbacks
```sh
# MCP spawns, you relay flags (hedge if submit_flag misbehaves; works with --workers):
uv run --frozen --env-file .env python -m ctf_agent run-htb-event --ctf-id 3755 --manual-verify

# No MCP at all — spawn each challenge on the HTB site, enter it, relay the flag:
uv run --frozen --env-file .env python -m ctf_agent run-manual
```

## Probe (debug MCP / inspect a container) — reads .env itself, no --env-file
```sh
cd ~/Projects/590_ctf_agent/runs/htb/mcp-probe
py htb_mcp_probe.py                                               # list tools
py htb_mcp_probe.py call container_status '{"challenge_id": <ID>}'
py htb_mcp_probe.py call start_container '{"challenge_id": <ID>}' --allow-write
```

## Monitor (while a run is going)
```sh
docker ps --filter name=ctf590                                   # agents running?
docker stats --no-stream $(docker ps --filter name=ctf590 -q)    # CPU moving = working
```
Also: **Langfuse dashboard** for live per-call detail, **Duke gateway dashboard** for real spend.
