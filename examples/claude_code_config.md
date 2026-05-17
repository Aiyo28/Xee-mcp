# Wiring Xee-mcp into Claude Code

Claude Code reads MCP servers from `~/.claude/mcp.json` (or the per-project equivalent in `.mcp.json` at the repo root). Add Xee-mcp to the `mcpServers` block.

## From source (current install path)

```json
{
  "mcpServers": {
    "xee-mcp": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/ABSOLUTE/PATH/TO/Xee-mcp",
        "xee-mcp"
      ],
      "env": {
        "XEE_MCP_COOKIES": "/ABSOLUTE/PATH/TO/cookies.json"
      }
    }
  }
}
```

Replace both `/ABSOLUTE/PATH/TO/...` placeholders with real paths. `~` and shell expansion are not parsed inside this JSON.

## After PyPI publish

Once `xee-mcp` is on PyPI you can drop the `--directory` and call the installed console script directly:

```json
{
  "mcpServers": {
    "xee-mcp": {
      "command": "xee-mcp",
      "env": {
        "XEE_MCP_COOKIES": "/ABSOLUTE/PATH/TO/cookies.json"
      }
    }
  }
}
```

## Debug logs

Add `XEE_MCP_DEBUG=1` to the `env` block to see twikit lifecycle events on stderr (cookie load, request boundaries). Default is silent so MCP stdio stays clean.

```json
"env": {
  "XEE_MCP_COOKIES": "/ABSOLUTE/PATH/TO/cookies.json",
  "XEE_MCP_DEBUG": "1"
}
```

## Verify

After saving, restart Claude Code. Ask:

> "What MCP tools do you have for X?"

You should see `search` and `user_tweets` listed. If they're missing, check the Claude Code logs for the spawn error — the most common cause is a wrong path in `--directory` or a missing cookie file.

## Cookies

See [`docs/cookies.md`](../docs/cookies.md) for how to produce the JSON file that `XEE_MCP_COOKIES` points at.
