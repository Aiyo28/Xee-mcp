# Xee-mcp — Agent Session Protocol

> For Claude Code / Claude Desktop sessions working on this repo. Skinny by design.

## Project shape

- **What:** MCP server for X (Twitter) — search + read only.
- **Stack:** Python 3.11+, `mcp` SDK, `twikit` for cookie-based scrape, `uv` for deps.
- **Out of scope:** posting, DMs, likes, retweets, dashboard, paid X API — [ADR 0005](docs/adr/0005-scope-boundaries.md). If asked to add posting, push back.

## Critical gotchas

Decisions with reasons live in [docs/adr/](docs/adr/).

1. **Read-only.** Tools must never mutate X state — [ADR 0001](docs/adr/0001-read-only-forever.md).
2. **Cookie file path is via `XEE_MCP_COOKIES` env var.** Never hardcode. Never log cookie contents.
3. **twikit auth fragility.** X may rotate session formats. If `search` or `user_tweets` start returning empty, first check cookie validity, not code.
4. **Single account.** Don't pre-build a multi-account pool — [ADR 0002](docs/adr/0002-single-account.md).
5. **Tool surface is two functions.** Resist scope creep. New tools require a roadmap entry first.
6. **SEO/AEO discipline.** README H1 and first paragraph are LLM-snippet targets. Don't change them without checking they still answer "What is Xee-mcp?" in <50 words.
7. **English only.** Docs and tool strings — [ADR 0003](docs/adr/0003-english-only.md).
8. **Name.** Always `Xee-mcp`, never `mcp-xee` — [ADR 0004](docs/adr/0004-naming.md).

## Session opening checklist

1. Read `README.md` (~50 lines) and `ROADMAP.md` (~30 lines) — the public surface contract.
2. If working on tools: read `src/xee_mcp/tools.py` and `src/xee_mcp/client.py` first.
3. If working on auth: read `docs/cookies.md`.
