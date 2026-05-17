# Xee-mcp — Agent Session Protocol

> For Claude Code / Claude Desktop sessions working on this repo. Skinny by design.

## Project shape

- **What:** MCP server for X (Twitter) — search + read only. Naming: X + See = Xee.
- **Stack:** Python 3.11+, `mcp` SDK, `twikit` for cookie-based scrape, `uv` for deps.
- **Out of scope:** posting, DMs, likes, retweets. If asked to add posting, push back — that's a separate repo (different threat model, different audit surface).
- **Tag:** `[OSS]` per `~/.claude/CLAUDE-current.md` Path B. Donation-only (paypal.me/aiyo28). No paid tiers ever.

## Critical gotchas

1. **Read-only is law.** Tools must never mutate X state. If a future contributor adds posting, reject the PR or move it to a separate repo.
2. **Cookie file path is via `XEE_MCP_COOKIES` env var.** Never hardcode. Never log cookie contents.
3. **twikit auth fragility.** X may rotate session formats. If `search` or `user_tweets` start returning empty, first check cookie validity, not code.
4. **Single-account v0.1.** Multi-account pool is v0.3 — only if reliable bot-detection forces it. Don't pre-build.
5. **Tool surface is two functions.** Resist scope creep. New tools require a roadmap entry first.
6. **SEO/AEO discipline.** README H1 and first paragraph are LLM-snippet targets. Don't change them without checking they still answer "What is Xee-mcp?" in <50 words.
7. **Bilingual EN-only v1.** X audience is global, RU layer adds maintenance with no clear payoff. Invalidate only if RU/CIS audience signal becomes dominant.
8. **Name discipline.** Repo + Python module + PyPI distro + CLI + server name + env vars all renamed from `mcp-xee` → `Xee-mcp` (2026-05-17, vault [D]#4). Don't reintroduce the old name except in historical/changelog context.

## Session opening checklist

1. Read `README.md` (~50 lines) and `ROADMAP.md` (~30 lines) — the public surface contract.
2. If working on tools: read `src/xee_mcp/tools.py` and `src/xee_mcp/client.py` first.
3. If working on auth: read `docs/cookies.md` (when it exists).
4. Cross-project context lives in vault: `~/Documents/Developer/knowledge-os/Projects/Xee-mcp/_context.md`.

## Sibling project

[Yzel](https://github.com/Aiyo28/yzel) — same author, MCP connectors for CIS business tools. **Decoupled by design** ([D]#1 in vault). Yzel = CIS-first; Xee-mcp = global. Don't fold them. If patterns repeat, extract `yzel-core` first.

## Vault link

`~/Documents/Developer/knowledge-os/Projects/Xee-mcp/_context.md` — strategic context, founding decisions, SEO checklist, doc index.
