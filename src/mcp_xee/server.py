"""MCP server entrypoint. Registers two tools: search, user_tweets."""

from __future__ import annotations

import asyncio

from mcp.server.fastmcp import FastMCP

from .tools import search as search_impl
from .tools import user_tweets as user_tweets_impl


mcp = FastMCP("mcp-xee")


@mcp.tool()
async def search(query: str, limit: int = 20) -> list[dict]:
    """Search X (Twitter) posts by keyword. Read-only.

    Supports X search syntax: from:handle, to:handle, since:YYYY-MM-DD, until:YYYY-MM-DD,
    "exact phrase", -exclude, OR. Returns latest matches.
    """
    return await search_impl(query, limit)


@mcp.tool()
async def user_tweets(handle: str, limit: int = 20) -> list[dict]:
    """Read recent posts from an X (Twitter) user. Read-only.

    Pass the handle without @. Example: handle="simonw" → fetches simonw's recent posts.
    """
    return await user_tweets_impl(handle, limit)


def main() -> None:
    """Entrypoint for the `mcp-xee` console script."""
    mcp.run()


if __name__ == "__main__":
    main()
