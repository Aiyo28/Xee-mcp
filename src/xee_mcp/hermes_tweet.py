"""Optional Hermes Tweet backend for read-only X search tools."""

from __future__ import annotations

import asyncio
import json
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "https://xquik.com"
BACKEND_ENV = ("XEE_MCP_BACKEND", "XEE_MCP_SEARCH_BACKEND")
API_KEY_ENV = (
    "XEE_MCP_HERMES_TWEET_API_KEY",
    "HERMES_TWEET_API_KEY",
    "XQUIK_API_KEY",
)


def should_use_hermes_tweet(backend: str | None = None) -> bool:
    """Return true when the caller explicitly selected the Hermes Tweet backend."""
    requested = backend or next((os.environ[name] for name in BACKEND_ENV if os.environ.get(name)), "")
    normalized = requested.strip().lower().replace("_", "-")
    return normalized in {"hermes-tweet", "xquik"}


async def fetch_hermes_tweets(query: str, limit: int = 20) -> list[dict[str, Any]]:
    """Fetch posts through Hermes Tweet and normalize them to Xee-mcp's public shape."""
    api_key = _api_key()
    url = build_search_url(query=query, limit=limit)
    payload = await asyncio.to_thread(_get_json, url, api_key)
    return normalize_tweets(payload)[: _clamped_limit(limit)]


def build_search_url(query: str, limit: int = 20, base_url: str | None = None) -> str:
    """Build a Hermes Tweet search URL for a latest-post query."""
    root = (base_url or os.environ.get("XEE_MCP_HERMES_TWEET_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
    params = urlencode(
        {
            "q": query,
            "queryType": "Latest",
            "limit": str(_clamped_limit(limit)),
        }
    )
    return f"{root}/api/v1/x/tweets/search?{params}"


def normalize_tweets(payload: Any) -> list[dict[str, Any]]:
    """Normalize common Hermes Tweet and Xquik search response shapes."""
    return [_normalize_tweet(tweet) for tweet in _tweet_candidates(payload)]


def _api_key() -> str:
    for name in API_KEY_ENV:
        value = os.environ.get(name, "").strip()
        if value:
            return value
    raise RuntimeError(
        "Hermes Tweet backend selected, but no key is configured. "
        "Set XEE_MCP_HERMES_TWEET_API_KEY, HERMES_TWEET_API_KEY, or XQUIK_API_KEY."
    )


def _get_json(url: str, api_key: str) -> Any:
    request = Request(url, headers=_headers(api_key), method="GET")
    try:
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:300]
        raise RuntimeError(f"Hermes Tweet request failed with HTTP {exc.code}: {detail}") from exc
    except URLError as exc:
        raise RuntimeError(f"Hermes Tweet request failed: {exc.reason}") from exc


def _headers(api_key: str) -> dict[str, str]:
    if api_key.lower().startswith("bearer "):
        return {"Authorization": api_key, "Accept": "application/json"}
    if api_key.startswith("xq_"):
        return {"x-api-key": api_key, "Accept": "application/json"}
    return {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}


def _tweet_candidates(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if not isinstance(value, dict):
        return []
    if _is_tweet_like(value):
        return [value]
    for key in ("tweets", "data", "results", "items", "statuses"):
        nested = _tweet_candidates(value.get(key))
        if nested:
            return nested
    for nested_value in value.values():
        nested = _tweet_candidates(nested_value)
        if nested:
            return nested
    return []


def _normalize_tweet(tweet: Any) -> dict[str, Any]:
    if not isinstance(tweet, dict):
        return _empty_tweet()
    author = _first_dict(tweet, "author", "user")
    tweet_id = _first_string(tweet, "tweet_id", "id", "id_str", "rest_id")
    username = (
        _first_string(author, "userName", "username", "screen_name")
        or _first_string(tweet, "userScreenName", "username", "screen_name")
        or ""
    )
    return {
        "id": tweet_id,
        "text": _first_string(tweet, "source_full_text", "full_text", "text", "content"),
        "author": username,
        "author_name": _first_string(author, "name") or _first_string(tweet, "name"),
        "created_at": _first_string(tweet, "createdAt", "created_at", "timestamp", "time"),
        "url": f"https://x.com/{username}/status/{tweet_id}" if username and tweet_id else None,
        "reply_count": _metric(tweet, "replyCount", "reply_count", "replies"),
        "retweet_count": _metric(tweet, "retweetCount", "retweet_count", "retweets", "reposts"),
        "favorite_count": _metric(tweet, "likeCount", "like_count", "favorite_count", "likes"),
        "view_count": _metric(tweet, "viewCount", "view_count", "views"),
    }


def _empty_tweet() -> dict[str, Any]:
    return {
        "id": None,
        "text": None,
        "author": "",
        "author_name": None,
        "created_at": None,
        "url": None,
        "reply_count": 0,
        "retweet_count": 0,
        "favorite_count": 0,
        "view_count": 0,
    }


def _is_tweet_like(value: dict[str, Any]) -> bool:
    return bool(
        _first_string(value, "tweet_id", "id", "id_str", "rest_id")
        and _first_string(value, "source_full_text", "full_text", "text", "content")
    )


def _first_dict(source: dict[str, Any], *keys: str) -> dict[str, Any]:
    for key in keys:
        value = source.get(key)
        if isinstance(value, dict):
            return value
    return {}


def _first_string(source: dict[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = source.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
        if isinstance(value, int | float):
            return str(value)
    return None


def _metric(source: dict[str, Any], *keys: str) -> int:
    metric_sources = (source, _first_dict(source, "public_metrics", "metrics"))
    for item in metric_sources:
        for key in keys:
            value = item.get(key)
            if isinstance(value, bool):
                continue
            if isinstance(value, int):
                return value
            if isinstance(value, float):
                return int(value)
            if isinstance(value, str) and value.strip():
                try:
                    return int(float(value))
                except ValueError:
                    continue
    return 0


def _clamped_limit(limit: int) -> int:
    return max(1, min(100, int(limit)))
