# Getting a cookie file for Xee-mcp

Xee-mcp talks to X via [twikit](https://github.com/d60/twikit), which reads a JSON cookie file produced by a logged-in X session. Most people want **Path A**. The others exist for when Path A doesn't fit your environment.

`XEE_MCP_COOKIES` points at the resulting file. Example:

```bash
export XEE_MCP_COOKIES=~/.config/xee-mcp/cookies.json
```

---

## Path A — `xee-mcp init` (recommended)

Reads your existing logged-in browser session directly. No extension, no DevTools paste, no password.

```bash
uv run xee-mcp init
```

Default browser is Chrome. To use a different one:

```bash
uv run xee-mcp init --browser brave    # or arc | firefox | safari | edge
```

Output goes to `~/.config/xee-mcp/cookies.json`, `chmod 600`. To choose a different path:

```bash
uv run xee-mcp init --out ~/somewhere/else.json
```

To overwrite an existing file, pass `--force`.

**macOS Keychain prompt.** Chrome / Brave / Edge encrypt their cookie store; the first run triggers a single Keychain prompt to decrypt it. Approve it. (Firefox and Arc don't prompt — their cookie stores are unencrypted on disk.)

**Prerequisite:** you must already be logged in to x.com in that browser. If you aren't, `init` fails with a clear "no logged-in x.com session" message — log in via the browser, retry.

**When to prefer A:** anyone with a desktop browser they're already logged in with. This is the default path. **When to avoid A:** headless server (no browser to read from) → Path D. Locked-down corporate machine that won't allow Keychain access → Path B or C.

---

## Path B — Chrome extension export

Use this if `xee-mcp init` is blocked by your environment and you'd rather not install browser-cookie3-style local store access (or you're not on a supported browser).

1. Install the [Get cookies.txt LOCALLY](https://chrome.google.com/webstore/detail/get-cookiestxt-locally) Chrome extension.
2. Log in to `x.com` in your browser (regular session — no incognito).
3. Click the extension icon while on any `x.com` page and download `cookies.txt`.
4. Convert to twikit JSON:

```bash
uv run python scripts/convert_cookies.py ~/Downloads/cookies.txt --out ~/.config/xee-mcp/cookies.json
```

The converter keeps only cookies on `x.com` / `twitter.com` hosts, writes a flat `{name: value}` JSON dict, `chmod 600` on output.

**When to prefer B:** you don't want any process reading your browser's local cookie store (zero-trust toolchain audit). **When to avoid B:** Path A works for you (one command vs four).

---

## Path C — Manual DevTools paste

Zero-tooling fallback. ~30 seconds.

1. Open https://x.com in Chrome and confirm you're logged in.
2. Press **Cmd+Opt+I** (macOS) or **Ctrl+Shift+I** (Linux/Windows) to open DevTools.
3. Go to **Application** tab → **Storage → Cookies → https://x.com**.
4. Find these two rows and copy each **Value** column entry:
   - `auth_token`
   - `ct0`
5. Create the cookie file with those two values:

```bash
mkdir -p ~/.config/xee-mcp
cat > ~/.config/xee-mcp/cookies.json <<'JSON'
{
  "auth_token": "PASTE_auth_token_VALUE_HERE",
  "ct0": "PASTE_ct0_VALUE_HERE"
}
JSON
chmod 600 ~/.config/xee-mcp/cookies.json
```

twikit only needs `auth_token` + `ct0` to authenticate read endpoints.

**When to prefer C:** you don't want any extra dependency, browser extension, or script. **When to avoid C:** you'd rather one command than five.

---

## Path D — Password login (advanced / headless)

Use this on a box with no browser session to lift cookies from — typically a headless server. Trades manual steps for handing your X password to a Python process for the duration of the login call.

```bash
uv run python scripts/login_and_save.py --out ~/.config/xee-mcp/cookies.json
```

The script prompts for handle, email (recommended — X often demands it during interactive login), and password (hidden via `getpass`). Output is `chmod 600`. If you hit `KEY_BYTE` errors on some Python installs, retry with `--no-ui-metrics`.

**When to prefer D:** headless box, no logged-in browser available. **When to avoid D:** you have a desktop browser (use Path A instead).

---

## Security tradeoffs

| Concern | A (init) | B (extension) | C (DevTools) | D (login) |
|---|---|---|---|---|
| Password typed into local Python | No | No | No | **Yes** |
| Browser extension trust required | No | **Yes** | No | No |
| Reads browser cookie store | **Yes** (browser-cookie3) | No | No | No |
| Output file format | flat JSON | flat JSON | flat JSON | flat JSON |
| Output file permissions | `chmod 600` | `chmod 600` | `chmod 600` (manual) | `chmod 600` |
| Rotation cost | re-run `init` | re-export + re-convert | re-copy from DevTools | re-run script |

**The cookie file IS the session.** Anyone with read access can act as your X account for the duration of that session. Keep it out of git, dotfile sync, Dropbox, and any directory indexed by Spotlight or desktop search agents.

---

## Refresh / rotation

Cookies don't have an explicit TTL surfaced by X — they expire opaquely. Signs you need to rotate:

- Tools start returning empty results without errors.
- `XEE_MCP_DEBUG=1` shows auth-related stack traces.
- The MCP tool error message contains "cookie auth failed" (hint from `tools.py`).

Re-run whichever path you used originally — `xee-mcp init --force` for Path A. Restart Claude Desktop / Claude Code to recycle the MCP process.

---

## Troubleshooting

- **`xee-mcp init` fails with "no logged-in x.com session found"** — you're not actually logged into x.com in the chosen browser. Open https://x.com in that browser, log in (full credentials, not just SSO), reload once, then re-run `xee-mcp init`. If the browser is Firefox / Arc and you're sure you're logged in, check that cookies aren't being cleared by privacy extensions on each session.
- **`xee-mcp init` fails with "Failed to read <browser> cookie store"** — either the browser isn't installed at the expected location, or macOS Keychain access was denied. Approve the prompt and retry. If you denied permanently, open Keychain Access → search "Chrome Safe Storage" → delete the entry → retry (you'll be re-prompted).
- **`XEE_MCP_COOKIES env var not set`** — export the variable in the same shell that launches your MCP client, or put it in the `env` block of your `claude_desktop_config.json` entry.
- **`Cookie file not found: …`** — `~` expands fine, but the file must exist. Re-run `xee-mcp init` or check the path you exported.
- **`Cookie auth failed. Your cookie file may be missing, expired, or bot-detected.`** — twikit got a non-auth response from X. First try `xee-mcp init --force` to refresh. If still failing, the account may be bot-detection-flagged — switch accounts or wait it out.
- **`login failed: Couldn't get KEY_BYTE indices`** (Path D only) — retry with `--no-ui-metrics`:
  ```bash
  uv run python scripts/login_and_save.py --no-ui-metrics --out ~/.config/xee-mcp/cookies.json
  ```
  If still failing, fall back to **Path A** — it bypasses the login + ui_metrics path entirely.
