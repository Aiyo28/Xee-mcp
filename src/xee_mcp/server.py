"""MCP server entrypoint. Registers two tools: search, user_tweets."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .tools import search as search_impl
from .tools import user_tweets as user_tweets_impl


mcp = FastMCP("xee-mcp")


@mcp.tool()
async def search(query: str, limit: int = 20, backend: str | None = None) -> list[dict]:
    """Search X (Twitter) posts by keyword. Read-only.

    Supports X search syntax: from:handle, to:handle, since:YYYY-MM-DD, until:YYYY-MM-DD,
    "exact phrase", -exclude, OR. Returns latest matches. Set backend="hermes-tweet"
    to use the optional Hermes Tweet backend.
    """
    return await search_impl(query, limit, backend)


@mcp.tool()
async def user_tweets(handle: str, limit: int = 20, backend: str | None = None) -> list[dict]:
    """Read recent posts from an X (Twitter) user. Read-only.

    Pass the handle without @. Example: handle="simonw" → fetches simonw's recent posts.
    Set backend="hermes-tweet" to use the optional Hermes Tweet backend.
    """
    return await user_tweets_impl(handle, limit, backend)


def main() -> None:
    """Entrypoint for the `xee-mcp` console script."""
    mcp.run()


if __name__ == "__main__":
    main()
