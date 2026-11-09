"""MCP server entrypoint. Registers two read tools: search, user_tweets.

Each tool returns a `CallToolResult` itself so a failure can carry `isError: true` together with
a JSON failure result (`{ok, class, reason, next}`). FastMCP only passes a `CallToolResult`
through untouched when the return annotation says so; with `-> list[dict]` it would validate an
error against the success schema.
"""

from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import CallToolResult, TextContent

from .tools import ToolFailure
from .tools import search as search_impl
from .tools import user_tweets as user_tweets_impl

mcp = FastMCP("xee-mcp")


def _text(value: Any) -> TextContent:
    return TextContent(type="text", text=json.dumps(value, ensure_ascii=False, indent=1))


def _posts(posts: list[dict[str, Any]]) -> CallToolResult:
    """Success: one text block per post (as before) plus the list as structured content."""
    return CallToolResult(content=[_text(p) for p in posts], structuredContent={"result": posts})


def _failure(failure: ToolFailure) -> CallToolResult:
    body = dict(failure.result())
    return CallToolResult(content=[_text(body)], structuredContent=body, isError=True)


@mcp.tool()
async def search(query: str, limit: int = 20) -> CallToolResult:
    """Search X (Twitter) posts by keyword. Read-only.

    Supports X search syntax: from:handle, to:handle, since:YYYY-MM-DD, until:YYYY-MM-DD,
    "exact phrase", -exclude, OR. Returns latest matches.

    On failure returns {ok: false, class, reason, next}. class is auth (run `xee-mcp init`),
    upstream (X scraping library broken; cookies are fine, do not re-auth), input, blocked
    (rate-limited; wait, do not retry in a loop) or error. Follow `next`.
    """
    try:
        return _posts(await search_impl(query, limit))
    except ToolFailure as failure:
        return _failure(failure)


@mcp.tool()
async def user_tweets(handle: str, limit: int = 20) -> CallToolResult:
    """Read recent posts from an X (Twitter) user. Read-only.

    Pass the handle with or without @. Example: handle="simonw" → fetches simonw's recent posts.
    On failure returns {ok: false, class, reason, next}; see `search` for the classes.
    """
    try:
        return _posts(await user_tweets_impl(handle, limit))
    except ToolFailure as failure:
        return _failure(failure)


def main() -> None:
    """Entrypoint for the `xee-mcp` console script."""
    mcp.run()


if __name__ == "__main__":
    main()
