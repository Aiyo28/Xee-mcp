"""Tool implementations. v0.1 surface: search + user_tweets. Read-only.

Each read tool returns a list of post dicts, or raises `ToolFailure`. `server.py` turns a
`ToolFailure` into the failure result the client sees; this module stays MCP-free so it tests
without a server.
"""

from __future__ import annotations

import re
from typing import Any, Literal, TypedDict

from twikit import errors as tw

from .client import get_client, log

FailureClass = Literal["auth", "upstream", "input", "blocked", "error"]

# Failure results use `class` as a key, which TypedDict's class syntax cannot spell.
FailureResult = TypedDict(
    "FailureResult",
    {"ok": Literal[False], "class": FailureClass, "reason": str, "next": str},
)

COOKIE_HINT = (
    "Cookie auth failed. Your cookie file may be missing, expired, or bot-detected. "
    "Try: xee-mcp init --force. See docs/cookies.md."
)

SETUP_HINT = (
    "No usable cookie file. Run: xee-mcp init, then set XEE_MCP_COOKIES to the path it prints. "
    "See docs/cookies.md."
)

UPSTREAM_HINT = (
    "Read tools are temporarily blocked by an upstream twikit issue against current X. "
    "twikit's ON_DEMAND_FILE_REGEX cannot parse X's current webpack chunk format, so the "
    "X-Client-Transaction-Id header cannot be built. Your cookies are fine — this is not "
    "an auth problem. See docs/upstream-issues.md or the project NEXT.md for status. "
    "When twikit ships a fix, bump the dep and these tools resume working with no code change."
)

BLOCKED_HINT = (
    "X is rate-limiting or challenging this session. Wait about 15 minutes before retrying; "
    "do not retry in a loop."
)

ERROR_HINT = (
    "Unexpected failure. Retry once. If it repeats, rerun with XEE_MCP_DEBUG=1 and open an "
    "issue at https://github.com/Aiyo28/Xee-mcp/issues."
)

UPSTREAM_SIGNATURES = ("KEY_BYTE", "key_byte", "x_client_transaction", "ON_DEMAND_FILE")

HANDLE_RE = re.compile(r"^[A-Za-z0-9_]{1,15}$")

_AUTH_ERRORS = (tw.Unauthorized, tw.Forbidden, tw.AccountLocked, tw.AccountSuspended)
_INPUT_ERRORS = (tw.UserNotFound, tw.UserUnavailable, tw.NotFound, tw.BadRequest)


class ToolFailure(Exception):
    """A read tool could not answer. Carries the failure class and the next step for the user."""

    def __init__(self, failure_class: FailureClass, reason: str, next_step: str) -> None:
        super().__init__(reason)
        self.failure_class: FailureClass = failure_class
        self.reason = reason
        self.next_step = next_step

    def result(self) -> FailureResult:
        return {"ok": False, "class": self.failure_class, "reason": self.reason, "next": self.next_step}


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


def _classify_twikit_error(exc: Exception) -> ToolFailure:
    """Map a twikit exception to a failure class.

    Upstream-lib breakage is checked first so it never sends the user to re-auth when their
    cookies are fine ([D]#10). Once twikit ships a parser fix, that branch stops firing.
    """
    msg = f"{type(exc).__name__}: {exc}"
    if any(sig in msg for sig in UPSTREAM_SIGNATURES):
        return ToolFailure("upstream", msg, UPSTREAM_HINT)
    if isinstance(exc, _AUTH_ERRORS) or "401" in msg or "Unauthorized" in msg:
        return ToolFailure("auth", msg, COOKIE_HINT)
    if isinstance(exc, tw.TooManyRequests):
        return ToolFailure("blocked", msg, BLOCKED_HINT)
    if isinstance(exc, _INPUT_ERRORS):
        return ToolFailure("input", msg, "Check the handle or query and try again.")
    return ToolFailure("error", msg, ERROR_HINT)


def _check_limit(limit: int) -> None:
    if limit < 1:
        raise ToolFailure("input", f"limit must be 1 or more, got {limit}", "Pass limit >= 1.")


async def _client():
    """The twikit client, with a missing or unreadable cookie file reported as `auth`."""
    try:
        return await get_client()
    except (RuntimeError, OSError, ValueError) as exc:
        raise ToolFailure("auth", f"{type(exc).__name__}: {exc}", SETUP_HINT) from exc


async def search(query: str, limit: int = 20) -> list[dict[str, Any]]:
    """Search X posts by keyword.

    Args:
        query: Search query string. Supports X search syntax (from:, to:, since:, etc.).
        limit: Maximum number of posts to return. Default 20.

    Returns:
        List of post dicts: id, text, author, author_name, created_at, url, engagement counts.

    Raises:
        ToolFailure: bad input, missing cookies, or any X / twikit failure.
    """
    if not query.strip():
        raise ToolFailure("input", "query is empty", "Pass a non-empty search query.")
    _check_limit(limit)
    client = await _client()
    log.debug("search query=%r limit=%d", query, limit)
    try:
        results = await client.search_tweet(query, "Latest", count=limit)
    except Exception as exc:
        raise _classify_twikit_error(exc) from exc
    return [_serialize(t) for t in results[:limit]]


async def user_tweets(handle: str, limit: int = 20) -> list[dict[str, Any]]:
    """Read a user's recent posts.

    Args:
        handle: X handle, with or without @. Example: "simonw".
        limit: Maximum number of posts to return. Default 20.

    Returns:
        List of post dicts: id, text, author, author_name, created_at, url, engagement counts.

    Raises:
        ToolFailure: bad input, missing cookies, or any X / twikit failure.
    """
    name = handle.strip().lstrip("@")
    if not HANDLE_RE.match(name):
        raise ToolFailure(
            "input",
            f"{handle!r} is not an X handle",
            "Pass a handle of 1-15 letters, digits or underscores, e.g. simonw.",
        )
    _check_limit(limit)
    client = await _client()
    log.debug("user_tweets handle=%r limit=%d", name, limit)
    try:
        user = await client.get_user_by_screen_name(name)
        tweets = await user.get_tweets("Tweets", count=limit)
    except Exception as exc:
        raise _classify_twikit_error(exc) from exc
    return [_serialize(t) for t in tweets[:limit]]
