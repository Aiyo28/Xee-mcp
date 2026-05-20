"""Tool implementations. v0.1 surface: search + user_tweets. Read-only."""

from __future__ import annotations

from typing import Any

from .client import get_client, log


COOKIE_HINT = (
    "Cookie auth failed. Your cookie file may be missing, expired, or bot-detected. "
    "Try: xee-mcp init --force. See docs/cookies.md."
)

UPSTREAM_HINT = (
    "Read tools are temporarily blocked by an upstream twikit issue against current X. "
    "twikit's ON_DEMAND_FILE_REGEX cannot parse X's current webpack chunk format, so the "
    "X-Client-Transaction-Id header cannot be built. Your cookies are fine — this is not "
    "an auth problem. See docs/upstream-issues.md or the project NEXT.md for status. "
    "When twikit ships a fix, bump the dep and these tools resume working with no code change."
)

UPSTREAM_SIGNATURES = ("KEY_BYTE", "key_byte", "x_client_transaction", "ON_DEMAND_FILE")


def _serialize(tweet: Any) -> dict[str, Any]:
    """Pull the public fields off a twikit Tweet into a JSON-safe dict."""
    return {
        "id": getattr(tweet, "id", None),
        "text": getattr(tweet, "text", None) or getattr(tweet, "full_text", None),
        "author": getattr(getattr(tweet, "user", None), "screen_name", None),
        "author_name": getattr(getattr(tweet, "user", None), "name", None),
        "created_at": str(getattr(tweet, "created_at", "")),
        "url": (
            f"https://x.com/{tweet.user.screen_name}/status/{tweet.id}"
            if getattr(tweet, "user", None) and getattr(tweet, "id", None)
            else None
        ),
        "reply_count": getattr(tweet, "reply_count", 0),
        "retweet_count": getattr(tweet, "retweet_count", 0),
        "favorite_count": getattr(tweet, "favorite_count", 0),
        "view_count": getattr(tweet, "view_count", None),
    }


def _wrap_twikit_error(exc: Exception) -> RuntimeError:
    """Re-raise twikit exceptions with an actionable preamble for MCP clients.

    Distinguishes upstream-lib breakage (don't ask the user to re-auth) from genuine
    cookie failures. Once twikit ships a parser fix, the upstream branch stops firing
    and the cookie branch handles only real auth problems.
    """
    msg = f"{type(exc).__name__}: {exc}"
    if any(sig in msg for sig in UPSTREAM_SIGNATURES):
        return RuntimeError(f"{UPSTREAM_HINT} Underlying error: {msg}")
    return RuntimeError(f"{COOKIE_HINT} Underlying error: {msg}")


async def search(query: str, limit: int = 20) -> list[dict[str, Any]]:
    """Search X posts by keyword.

    Args:
        query: Search query string. Supports X search syntax (from:, to:, since:, etc.).
        limit: Maximum number of posts to return. Default 20.

    Returns:
        List of post dicts: id, text, author, author_name, created_at, url, engagement counts.
    """
    client = await get_client()
    log.debug("search query=%r limit=%d", query, limit)
    try:
        results = await client.search_tweet(query, "Latest", count=limit)
    except Exception as exc:
        raise _wrap_twikit_error(exc) from exc
    return [_serialize(t) for t in results[:limit]]


async def user_tweets(handle: str, limit: int = 20) -> list[dict[str, Any]]:
    """Read a user's recent posts.

    Args:
        handle: X handle without @. Example: "simonw".
        limit: Maximum number of posts to return. Default 20.

    Returns:
        List of post dicts: id, text, author, author_name, created_at, url, engagement counts.
    """
    client = await get_client()
    log.debug("user_tweets handle=%r limit=%d", handle, limit)
    try:
        user = await client.get_user_by_screen_name(handle.lstrip("@"))
        tweets = await user.get_tweets("Tweets", count=limit)
    except Exception as exc:
        raise _wrap_twikit_error(exc) from exc
    return [_serialize(t) for t in tweets[:limit]]
