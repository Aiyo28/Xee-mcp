# Xee-mcp Roadmap

> Public scope. Discipline: read-only forever. Posting belongs in a separate repo.

## v0.1 — current

- `search(query, limit)` — keyword search across X posts
- `user_tweets(handle, limit)` — recent posts from a handle
- twikit cookie auth, single account
- **`xee-mcp init` — zero-friction cookie setup via `browser-cookie3`.** Reads Chrome's local cookie store directly. No extension, no DevTools paste, no password. Promoted from v0.2 on 2026-05-20: extension/DevTools friction undermines the plug-and-play MCP promise — the moat is the setup UX, not just the $0 cost. (Vault [D]#9.)
- Claude Desktop + Claude Code config examples
- MIT, paypal.me/aiyo28 donation CTA

## v0.2 — next

- `replies(post_id, limit)` — read replies on a thread
- `bookmarks(limit)` — read your own bookmarks (auth-required)
- Cookie health-check tool — flag near-expiry / bot-detection signals before tools fail
- MCP Server Registry submission

## v0.3 — conditional

- Multi-account cookie pool — only if v0.1/v0.2 hit reliable bot-detection. Likely path: swap twikit → twscrape internally, keep tool surface identical.
- `analytics_summary(handle)` — top-engagement post pattern extraction. Only if community asks.

## Out of scope (forever, unless invalidated)

- Posting / DMs / likes / retweets. Different threat model. New repo if ever.
- Web dashboard. Xee-mcp is a primitive, not a product.
- Paid X API integration. Wrong shape for this tool's audience.

## Invalidation triggers

- twikit cookie auth bot-detected within first 50 calls in real use → swap twscrape, keep tool surface (D1 in vault).
- Xee-mcp scope grows to ≥3 global-platform connectors AND wants Yzel's vault → extract `yzel-core` shared library or fold into Yzel (D1 fallback).
- X reverses Feb 2026 pay-per-use pricing back to free tier → revisit official API path; cookie auth may become unnecessary.
