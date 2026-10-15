# NEXT — Xee-mcp

> Resume line for the next session. Under 15 lines.

**Status (2026-05-20):** 🟡 SHIP-READY — v0.1.0 scoped to thin MCP info-aggregation wrapper. Two commits shipped + pushed to master: `05f1195` (cookie UX: `xee-mcp init` via browser-cookie3, no extension/paste/password), `d1e7672` (degraded read tools + honest README Status block + error routing distinguishes upstream-lib breakage from cookie failure). GH repo description + Aiyo28/portfolio_2.0 data.json both updated + pushed to mirror the new "thin aggregator" framing. 29/29 tests, ruff clean.

## Phase C (ship) — left to do
1. File upstream issues from `docs/upstream-issues.md` drafts (twikit + twscrape repos). Cheap insurance; both repos ~13mo dead so don't expect fast response.
2. `git tag v0.1.0 && gh release create v0.1.0 --generate-notes`.
3. USER runs `uv publish` (PyPI token must be in your shell, never in repo).
4. When twikit ships 2.3.4+ parser fix: bump dep in pyproject.toml, delete README "Status (v0.1.0)" block, ship v0.1.1.

## When resuming
1. `~/Documents/Developer/Xee-mcp` — master at `a1b85ca`; run `git status` first — the working tree may have uncommitted changes.
2. No active edits in progress. Either file upstream issues, tag + publish, or move to next project.

## Optional cleanup (manual)
- `unset UV_PUBLISH_TOKEN` if still in shell env from May.
- x.com → Settings → Sessions → Log out other sessions to rotate cookies if not already done.
