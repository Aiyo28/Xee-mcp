# NEXT — Xee-mcp

> Resume line for the next session. Under 15 lines.

**Status (2026-05-20):** 🟡 SHIP-READY — v0.1.0 scoped down to thin MCP aggregation wrapper per founder call. T1 (cookie UX via `xee-mcp init`) done + committed `05f1195`. Read tools (search, user_tweets) ship in **degraded mode**: error path now distinguishes upstream-lib breakage from cookie failure (`tools.py:_wrap_twikit_error` routes on `UPSTREAM_SIGNATURES`), so users get accurate signal. README "Status (v0.1.0)" section sets the expectation up front. We don't fork twikit, vendor patches, or build our own scraper — when upstream ships, we bump the dep. Vault [D]#9 (no [D]#10 needed — this is the application of "less maintenance" principle, not a new decision).

**Why ship degraded now:** init UX is the value users feel first; shipping it gets people configured so the day upstream lands a parser fix, tools just start working. Both repos (twikit + twscrape) are ~13 months dead on code; filing upstream issues is cheap insurance, not a plan.

## Phase C (ship) — left to do
1. File the two upstream issues from `docs/upstream-issues.md` drafts (twikit + twscrape). Low cost, just-in-case.
2. `git tag v0.1.0 && gh release create v0.1.0 --generate-notes`.
3. USER runs `uv publish` (PyPI token in their shell, never in repo or env).
4. README "Status" section will need updating once upstream resolves — bump twikit dep, delete the degraded-mode paragraph, ship v0.1.1.

## When resuming
1. `~/Documents/Developer/Xee-mcp` — master at `05f1195` (T1) plus uncommitted error-routing + README status (this turn).
2. Commit current diff (`tools.py`, `tests/test_error_routing.py`, `README.md`, `NEXT.md`), then file upstream issues, then tag.

## Optional cleanup (manual)
- `unset UV_PUBLISH_TOKEN` if still in shell env from May.
- x.com → Settings → Sessions → Log out of all other sessions — rotates the cookies in the May 17 screenshot if not already done.
