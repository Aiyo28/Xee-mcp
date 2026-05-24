"""Hermes Tweet backend tests. No live network."""

from __future__ import annotations

import pytest

from xee_mcp import hermes_tweet
from xee_mcp.tools import search, user_tweets


def test_backend_selection_accepts_env(monkeypatch):
    monkeypatch.setenv("XEE_MCP_BACKEND", "hermes_tweet")
    assert hermes_tweet.should_use_hermes_tweet()


def test_backend_selection_accepts_tool_override(monkeypatch):
    monkeypatch.delenv("XEE_MCP_BACKEND", raising=False)
    monkeypatch.delenv("XEE_MCP_SEARCH_BACKEND", raising=False)
    assert hermes_tweet.should_use_hermes_tweet("xquik")


def test_build_search_url_clamps_limit():
    url = hermes_tweet.build_search_url(
        query="MCP servers",
        limit=250,
        base_url="https://example.test/",
    )
    assert (
        url
        == "https://example.test/api/v1/x/tweets/search?"
        "q=MCP+servers&queryType=Latest&limit=100"
    )


def test_normalize_tweets_supports_nested_payload():
    tweets = hermes_tweet.normalize_tweets(
        {
            "data": {
                "tweets": [
                    {
                        "tweet_id": "123",
                        "source_full_text": "hello",
                        "author": {"userName": "alice", "name": "Alice"},
                        "public_metrics": {
                            "like_count": "7",
                            "retweet_count": 2,
                            "reply_count": 1,
                            "view_count": 99,
                        },
                        "created_at": "2026-05-24T09:00:00Z",
                    }
                ]
            }
        }
    )
    assert tweets == [
        {
            "id": "123",
            "text": "hello",
            "author": "alice",
            "author_name": "Alice",
            "created_at": "2026-05-24T09:00:00Z",
            "url": "https://x.com/alice/status/123",
            "reply_count": 1,
            "retweet_count": 2,
            "favorite_count": 7,
            "view_count": 99,
        }
    ]


@pytest.mark.asyncio
async def test_search_uses_hermes_backend_without_cookie_env(monkeypatch):
    async def fake_fetch(query: str, limit: int):
        return [{"id": "1", "text": query, "limit": limit}]

    monkeypatch.delenv("XEE_MCP_COOKIES", raising=False)
    monkeypatch.setattr("xee_mcp.tools.fetch_hermes_tweets", fake_fetch)

    assert await search("MCP", 3, backend="hermes-tweet") == [
        {"id": "1", "text": "MCP", "limit": 3}
    ]


@pytest.mark.asyncio
async def test_user_tweets_uses_from_query_for_hermes_backend(monkeypatch):
    seen = {}

    async def fake_fetch(query: str, limit: int):
        seen["query"] = query
        seen["limit"] = limit
        return []

    monkeypatch.delenv("XEE_MCP_COOKIES", raising=False)
    monkeypatch.setattr("xee_mcp.tools.fetch_hermes_tweets", fake_fetch)

    assert await user_tweets("@simonw", 5, backend="hermes-tweet") == []
    assert seen == {"query": "from:simonw", "limit": 5}
