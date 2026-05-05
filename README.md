# mcp-xee — MCP server for X (Twitter): search + read, no paid API

> **What is mcp-xee?** It's a [Model Context Protocol](https://modelcontextprotocol.io) server that gives Claude, ChatGPT, and other AI assistants two read-only tools for X (Twitter): **search posts** and **read a user's timeline**. It uses cookie-based auth via [twikit](https://github.com/d60/twikit) — no X API keys, no pay-per-use fees.

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![MCP Compatible](https://img.shields.io/badge/MCP-compatible-green.svg)](https://modelcontextprotocol.io)

**Naming:** X + See = **Xee** (pronounced "ex-ee"). The name encodes the scope — `mcp-xee` is for *seeing* X, not posting to it. Posting is intentionally out-of-scope for v0.x.

---

## Why mcp-xee

Six MCP servers for X already exist. Most require the [paid X API](https://docs.x.com/x-api/getting-started/about-x-api) — pay-per-use since Feb 2026, ~$0.005 per read. For solo developers and OSS authors who just want to let Claude search what's being said about their work, that's wrong shape.

`mcp-xee` solves one job: read X with zero API cost. Cookie auth via twikit, two tools, one MCP server. That's it.

| | mcp-xee | [mcp-twikit](https://github.com/adhikasp/mcp-twikit) | [official xmcp](https://github.com/xdevplatform/xmcp) | [Infatoshi/x-mcp](https://github.com/Infatoshi/x-mcp) |
|---|---|---|---|---|
| Auth | Cookie (twikit) | Cookie (twikit) | OAuth 2.0 | OAuth 1.0a |
| API cost | $0 | $0 | Pay-per-use | Pay-per-use |
| Scope | Read + search only | Read + search + post + DMs | Full | Full |
| Tools count | 2 (focused) | ~10+ | ~10+ | ~10+ |
| Goal | Minimal, solo-OSS friendly | Power user | Production | Production |

If you want posting, DMs, or production-grade reliability — use one of the others. If you want **the smallest thing that lets Claude see X for you**, use `mcp-xee`.

---

## Tools

### `search(query, limit=20)`
Search X posts by keyword. Returns text, author, timestamp, URL, and engagement stats.

### `user_tweets(handle, limit=20)`
Read a user's recent posts. Returns the same fields.

That's the v0.1 surface. Two tools. Read-only. No surprises.

---

## Install

```bash
git clone https://github.com/Aiyo28/mcp-xee.git
cd mcp-xee
uv sync
```

PyPI publish follows the first wave of feedback (`pip install mcp-xee`).

---

## Quickstart

1. **Get an X account cookie file.** twikit reads cookies from a JSON file. Easiest path: log in to X in your browser, export cookies via [Get cookies.txt LOCALLY](https://chrome.google.com/webstore/detail/get-cookiestxt-locally) → convert to twikit format (one-line script in `docs/cookies.md`), or use twikit's `client.login(...)` once and `client.save_cookies(path)`.

2. **Point mcp-xee at the cookie file.**
   ```bash
   export MCP_XEE_COOKIES=~/.config/mcp-xee/cookies.json
   ```

3. **Wire into Claude Desktop / Claude Code.** Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "mcp-xee": {
         "command": "uv",
         "args": ["run", "--directory", "/path/to/mcp-xee", "mcp-xee"],
         "env": { "MCP_XEE_COOKIES": "/path/to/cookies.json" }
       }
     }
   }
   ```

4. **Ask Claude:**
   > "Search X for posts about MCP servers from the last week."
   > "Show me the last 10 posts from @simonw."

---

## Limitations

- **Single account.** v0.1 uses one cookie file. If X bot-detects, you wait it out or rotate. Multi-account pool is roadmapped (see [twscrape](https://github.com/vladkens/twscrape) swap path in [ROADMAP.md](ROADMAP.md)).
- **Read-only.** No post, no DMs, no like/retweet. Intentional — see naming.
- **No analytics dashboard.** This is a primitive, not a product. Compose with other MCP tools.
- **Cookie auth is brittle by design.** X may rotate session formats. Pin issues here.

---

## Roadmap

See [ROADMAP.md](ROADMAP.md). v0.2 likely adds replies + bookmarks (still read). Posting stays separate (different threat model, different repo).

---

## Support the project

`mcp-xee` is MIT, ad-free, and will never have paid tiers. If it saves you time or money, you can throw a coffee:

**[paypal.me/aiyo28](https://paypal.me/aiyo28)** — keeps everything ad-free, no paid tiers, ever.

Or just star the repo and tell someone. That works too.

---

## Related projects

- [Yzel](https://github.com/Aiyo28/yzel) — MCP connectors for CIS business tools (1C, Wildberries, Ozon, Bitrix24, AmoCRM, МойСклад, Telegram, iiko). Sibling OSS project, different scope (CIS-first business APIs).

---

## License

MIT. See [LICENSE](LICENSE).
