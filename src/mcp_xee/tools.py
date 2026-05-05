"""Tool implementations. v0.1 surface: search + user_tweets. Read-only."""

from __future__ import annotations

from typing import Any

from .client import get_client


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


async def search(query: str, limit: int = 20) -> list[dict[str, Any]]:
    """Search X posts by keyword.

    Args:
        query: Search query string. Supports X search syntax (from:, to:, since:, etc.).
        limit: Maximum number of posts to return. Default 20.

    Returns:
        List of post dicts: id, text, author, author_name, created_at, url, engagement counts.
    """
    client = await get_client()
    results = await client.search_tweet(query, "Latest", count=limit)
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
    user = await client.get_user_by_screen_name(handle.lstrip("@"))
    tweets = await user.get_tweets("Tweets", count=limit)
    return [_serialize(t) for t in tweets[:limit]]
