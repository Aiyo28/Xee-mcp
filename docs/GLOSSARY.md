# Glossary

One name per thing. Use these terms in code, docs, issues and specs.

| Term | Definition | Aliases to avoid | Owning entity |
|---|---|---|---|
| read tool | An MCP tool Xee-mcp registers. Today: `search`, `user_tweets`. Never mutates X | endpoint, command, function | `server.py` |
| backend | The library that sends requests to X on a read tool's behalf. Today twikit | scraper, driver, engine | `client.py` |
| op | One named X request the api-anything backend knows (`searchPosts`, `userTweets`, `getUser`) | endpoint, query, operation | op file |
| op file | The JSON file listing the ops Xee-mcp ships, vendored from crossbar's `spec/x.json`, read ops only | spec, site spec, catalog | `client.py` |
| tier | api-anything's transport level for one call: 1 plain HTTPS, 2 fetch inside a browser page, 3 run the x.com page | mode, level | backend |
| cookie file | The JSON file `xee-mcp init` writes; its path comes from `XEE_MCP_COOKIES` | session file, auth file | `cli.py` |
| failure result | What a read tool returns when it cannot answer: `{ok: false, class, reason, next}` | error dict, error response | `tools.py` |
| failure class | The `class` field of a failure result: `auth`, `upstream`, `input`, `blocked`, `error` | error type, error code | `tools.py` |
| client | An MCP host that launches Xee-mcp (Claude Desktop, Claude Code, Cursor) | app, agent, IDE | — |
| client config | The JSON or command a client needs to launch Xee-mcp | MCP config, setup | `cli.py` |
| plugin | The Claude Code plugin defined in `.claude-plugin/` | extension, add-on | repo root |
