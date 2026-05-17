# Getting a cookie file for Xee-mcp

Xee-mcp talks to X via [twikit](https://github.com/d60/twikit), which reads a JSON cookie file produced by a logged-in X session. You have two ways to produce one. Pick the path that matches your trust model.

`XEE_MCP_COOKIES` points at the resulting file. Example:

```bash
export XEE_MCP_COOKIES=~/.config/xee-mcp/cookies.json
```

---

## Path A — twikit login (pythonic, requires password)

Use this if you trust the script with your X credentials. Password is held in memory only for the duration of the login call; nothing is written to disk except the resulting session cookie inside the output JSON.

```bash
python scripts/login_and_save.py --out ~/.config/xee-mcp/cookies.json
```

The script prompts for:

1. **Handle** (without `@`)
2. **Email** (optional but recommended — X often demands it during interactive login)
3. **Password** (hidden via `getpass`)

Output is `chmod 600` so other local users can't read it.

**When to prefer A:** scripted setup, headless box, you control the machine. **When to avoid A:** shared machine, you'd rather not type the password into a Python process.

---

## Path B — browser export (no password handling)

Use this if you'd rather not feed your password to a script. The trade-off is one extra manual step.

1. Install the [Get cookies.txt LOCALLY](https://chrome.google.com/webstore/detail/get-cookiestxt-locally) Chrome extension.
2. Log in to `x.com` in your browser (regular session — no incognito).
3. Click the extension icon while on any `x.com` page and download `cookies.txt`.
4. Convert to twikit JSON:

```bash
python scripts/convert_cookies.py ~/Downloads/cookies.txt --out ~/.config/xee-mcp/cookies.json
```

The converter:

- Reads Netscape `cookies.txt` format (the format the extension exports).
- Keeps only cookies on `x.com` / `twitter.com` hosts.
- Writes a flat `{name: value}` JSON dict — the exact shape twikit's `load_cookies()` expects.
- `chmod 600` on the output.

**When to prefer B:** you don't want to type your X password into anything other than X itself. **When to avoid B:** you're scripting from a server with no browser session to lift cookies from.

---

## Security tradeoffs

| Concern | Path A (login) | Path B (browser) |
|---|---|---|
| Password typed into local Python | Yes | No |
| Browser extension trust required | No | Yes (Get cookies.txt LOCALLY is open-source — verify the build you install) |
| Output file format | Same (`{name: value}` JSON) | Same |
| Output file permissions | `chmod 600` | `chmod 600` |
| Rotation cost | Re-run script | Re-export + re-convert |

Either way, **the cookie file IS the session.** Anyone with read access to it can act as your X account for the duration of that session. Keep it out of git, dotfile sync, Dropbox, and any directory that gets indexed by Spotlight/desktop search agents.

---

## Refresh / rotation

Cookies don't have an explicit TTL surfaced by X — they expire opaquely. Signs you need to rotate:

- Tools start returning empty results without errors.
- `XEE_MCP_DEBUG=1` shows auth-related stack traces.
- The MCP tool error message contains "cookie auth failed" (the hint from `tools.py`).

Re-run whichever path you used originally. The MCP server picks up the new file on next process start; restart Claude Desktop / Claude Code to recycle.

---

## Troubleshooting

- **`XEE_MCP_COOKIES env var not set`** — export the variable in the same shell that launches your MCP client, or put it in the `env` block of your `claude_desktop_config.json` entry (see `examples/claude_desktop_config.json`).
- **`Cookie file not found: …`** — path expansion of `~` is supported, but the file must exist. Re-check the path you exported.
- **`Cookie auth failed. Your cookie file may be missing, expired, or bot-detected.`** — twikit got a non-auth response from X. First try regenerating the cookie file. If still failing, the account may be bot-detection-flagged — switch accounts or wait it out.
