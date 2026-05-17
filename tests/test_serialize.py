"""Unit tests for _serialize. No live X — uses a minimal mock Tweet."""

from __future__ import annotations

from types import SimpleNamespace

from xee_mcp.tools import _serialize


def _mock_user(screen_name: str = "simonw", name: str = "Simon Willison") -> SimpleNamespace:
    return SimpleNamespace(screen_name=screen_name, name=name)


def _mock_tweet(**overrides) -> SimpleNamespace:
    base = dict(
        id="1234567890",
        text="hello world",
        full_text=None,
        user=_mock_user(),
        created_at="2026-05-17 10:00:00",
        reply_count=3,
        retweet_count=7,
        favorite_count=42,
        view_count=1000,
    )
    base.update(overrides)
    return SimpleNamespace(**base)


def test_serialize_minimal_tweet():
    out = _serialize(_mock_tweet())
    assert out == {
        "id": "1234567890",
        "text": "hello world",
        "author": "simonw",
        "author_name": "Simon Willison",
        "created_at": "2026-05-17 10:00:00",
        "url": "https://x.com/simonw/status/1234567890",
        "reply_count": 3,
        "retweet_count": 7,
        "favorite_count": 42,
        "view_count": 1000,
    }


def test_serialize_falls_back_to_full_text():
    out = _serialize(_mock_tweet(text=None, full_text="long form text"))
    assert out["text"] == "long form text"


def test_serialize_no_user_yields_null_url_and_author():
    out = _serialize(_mock_tweet(user=None))
    assert out["author"] is None
    assert out["author_name"] is None
    assert out["url"] is None


def test_serialize_no_id_yields_null_url():
    out = _serialize(_mock_tweet(id=None))
    assert out["url"] is None


def test_serialize_defaults_engagement_counts_to_zero():
    minimal = SimpleNamespace(id="1", text="t", user=_mock_user(), created_at="")
    out = _serialize(minimal)
    assert out["reply_count"] == 0
    assert out["retweet_count"] == 0
    assert out["favorite_count"] == 0
    assert out["view_count"] is None
