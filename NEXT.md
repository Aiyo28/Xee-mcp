# NEXT — Xee-mcp

> Resume line for the next session. Under 15 lines. Updated by `/session --end`.

**Status (2026-05-20):** 🟢 UNPAUSED — reframed. The cookie acquisition UX (extension OR DevTools paste) is the OSS moat-killer, not the ship blocker. An MCP server that requires "install a Chrome extension first" loses plug-and-play before the user reaches the README's second paragraph. Scope shift: `xee-mcp init` via `browser-cookie3` promoted from v0.2 → **v0.1 blocker**. Vault [D]#9 (supersedes [D]#8).

**Two independent tracks — work in parallel:**

## Track 1 — Cookie UX (moat work, unblocks regardless of upstream)
1. Add `browser-cookie3>=0.20.0` dep (`pyproject.toml`).
2. New `src/xee_mcp/cli.py` subcommand `xee-mcp init` — reads Chrome cookie store (macOS Keychain prompt is acceptable), writes `~/.config/xee-mcp/cookies.json` with `auth_token` + `ct0` only, `chmod 600`. Browser flag: `--browser chrome|brave|arc|firefox|safari` (default chrome).
3. `docs/cookies.md` — promote `init` to Path A (top of doc); demote login script to Path D (advanced/headless).
4. README quickstart — replace 4-step DevTools dance with `uv run xee-mcp init && uv run xee-mcp serve`.
5. Tests — mock `browser_cookie3.chrome()` fixture; verify writer path + permissions.

## Track 2 — Upstream lib breakage (ship blocker)
- twikit 2.3.3 still broken (`ON_DEMAND_FILE_REGEX` stale vs X webpack); twscrape 0.17.0 still broken (parser `IndexError`).
- File upstream issues from `docs/upstream-issues.md` drafts (currently un-filed — do this in T2.1 to start the clock).
- Optional fallback to investigate: vendor `x-client-transaction-id` PyPI package directly, bypass twikit's stale module. Spike before deciding.

## When resuming
1. `~/Documents/Developer/Xee-mcp` — repo at master `f2abcd4`.
2. Start T1 (UX) — it's value-additive even before upstream resolves; ship `xee-mcp init` as v0.1.0 even if read tools degrade gracefully with "cookies OK, but upstream parser broken — track issue #N" message.
3. Track 2 in parallel: file upstream issues today.

## Upstream issues to file (drafts in `docs/upstream-issues.md`)
- twikit: `ON_DEMAND_FILE_REGEX` stale vs current X webpack chunk format
- twscrape: response parser IndexError on UserByScreenName + SearchTimeline
