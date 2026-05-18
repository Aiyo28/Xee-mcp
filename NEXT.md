# NEXT — Xee-mcp

> Resume line for the next session. Under 15 lines. Updated by `/session --end`.

**Status (2026-05-18 s1):** ⏸️ PAUSED — v0.1.0 ship blocked by upstream Python X-scrape ecosystem breakage. Pre-tag live smoke uncovered:
- **twikit 2.3.3**: `KEY_BYTE indices` failure on every request — `ON_DEMAND_FILE_REGEX` in `twikit/x_client_transaction/transaction.py:15` does not match current X webpack chunk format (`'ondemand.s",60041:"i18n/...'` — old `"key":"hash"` pair gone).
- **twscrape 0.17.0**: `IndexError: list index out of range` in response parser for both `UserByScreenName` and `SearchTimeline` GraphQL endpoints. Account auto-locks 15 min on each error.
- Two libs, two different failure modes, same day — confirmed upstream issue, not local.

Repo + rename + CI green + docs + 14/14 tests + scripts + Phase B all preserved. `twscrape` dep added during spike then removed — pyproject back to `twikit>=2.0.0`. Vault [D]#8 (supersedes [D]#7).

## Resume when (any of)
- `twikit` ships parser fix in 2.3.4+ → retry Phase C with twikit.
- `twscrape` ships parser fix in 0.18+ → swap to twscrape per [D]#1 / ROADMAP v0.3, then Phase C.
- MCP spec adds first-class X auth handshake → revisit stack lock [D]#3.

## When resuming
1. `~/Documents/Developer/Xee-mcp` — repo at master `981228b` (last commit before pause).
2. Re-run live smoke from `docs/release.md`: `XEE_MCP_COOKIES=... uv run python -c "...search('mcp servers')..."`.
3. If green → Phase C: tag v0.1.0, `gh release create`, USER runs `uv publish` (token in their shell).
4. Phase C tasks #21–#25 still in tracker.

## Optional cleanup (manual)
- `unset UV_PUBLISH_TOKEN` — token unused, still in your shell env.
- x.com → Settings → Sessions → Log out of all other sessions — rotates the cookies that were in the May 17 screenshot.

## Upstream issues to file (drafts in `docs/upstream-issues.md`)
- twikit: `ON_DEMAND_FILE_REGEX` stale vs current X webpack chunk format
- twscrape: response parser IndexError on UserByScreenName + SearchTimeline
