# Releasing Xee-mcp

Manual runbook. Solo project, low cadence — no release automation yet (revisit at v0.2).

## Pre-tag checklist

1. **CI green on `master`** — every job in `.github/workflows/ci.yml` passing.
2. **Local pytest green** — `uv run pytest`.
3. **Local lint green** — `uv run ruff check .`.
4. **Smoke test against real X** — see "Live smoke" below. Skip only if the change is doc-only.
5. **Version bumped** — `pyproject.toml` `version` matches the tag you're about to cut.

## Live smoke

Not run in CI by design (no cookie secret stored). Run locally:

```bash
export XEE_MCP_COOKIES=~/.config/xee-mcp/cookies.json
export XEE_MCP_DEBUG=1
uv run python -c "
import asyncio
from xee_mcp.tools import search, user_tweets
async def go():
    r = await search('mcp servers', limit=3)
    print('search:', len(r), 'results')
    r = await user_tweets('simonw', limit=3)
    print('user_tweets:', len(r), 'results')
asyncio.run(go())
"
```

Expect non-empty results and no exceptions. If both calls succeed, the cookie + tool surface are healthy.

## Tag + release

```bash
git tag v0.X.Y
git push --tags
```

Create the GitHub release with auto-generated notes:

```bash
gh release create v0.X.Y --generate-notes
```

Edit the release body if you want a hand-written intro. Auto notes give you the commit list; the intro should tell users what's new in human language.

## Publish to PyPI

```bash
uv build
uv publish
```

`uv publish` reads the PyPI token from `UV_PUBLISH_TOKEN` env var. Do NOT commit it. Create a project-scoped token at https://pypi.org/manage/account/token/ and export it for the publish call only:

```bash
UV_PUBLISH_TOKEN=pypi-... uv publish
```

(At v0.2 we'll consider trusted publishing via GitHub Actions OIDC.)

## Post-publish smoke

In a fresh venv outside the repo:

```bash
cd /tmp && uv venv smoke && source smoke/bin/activate
uv pip install xee-mcp
xee-mcp --help 2>&1 | head -5  # confirms the console script is wired
deactivate && rm -rf smoke
```

Then point a real MCP client (Claude Desktop) at the installed CLI and confirm the handshake:

```json
{
  "mcpServers": {
    "xee-mcp": {
      "command": "xee-mcp",
      "env": { "XEE_MCP_COOKIES": "/path/to/cookies.json" }
    }
  }
}
```

If Claude Desktop lists `search` and `user_tweets` as tools, the release is healthy.

## Rollback

PyPI does not allow re-uploading a yanked version's number. If a release is broken:

1. **Yank** the version on PyPI (`uv publish` doesn't support this directly — use the PyPI web UI or `twine`).
2. Cut a new patch version (e.g. `v0.1.0` → `v0.1.1`) with the fix.
3. Delete the bad GitHub release + tag if you want to fully remove the trail; otherwise leave it with a "yanked" note in the body.
