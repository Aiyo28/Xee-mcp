"""Failure results: every read tool failure carries a failure class and a `next` step.

The auth/upstream split is the one that matters most ([D]#10): an `upstream` failure must never
tell the user to re-run `xee-mcp init`, because their cookies are fine.
"""

from __future__ import annotations

import json

import pytest
from twikit import errors as tw

from xee_mcp import client, server, tools
from xee_mcp.tools import (
    COOKIE_HINT,
    UPSTREAM_HINT,
    UPSTREAM_SIGNATURES,
    ToolFailure,
    _classify_twikit_error,
)


@pytest.mark.parametrize(
    "exc",
    [
        Exception("Couldn't get KEY_BYTE indices"),
        Exception("error in twikit.x_client_transaction.transaction"),
        Exception("ON_DEMAND_FILE_REGEX missed"),
    ],
)
def test_upstream_signatures_classify_as_upstream(exc):
    failure = _classify_twikit_error(exc)
    assert failure.failure_class == "upstream"
    assert failure.next_step == UPSTREAM_HINT


@pytest.mark.parametrize(
    "exc",
    [
        Exception("401 Unauthorized"),
        tw.Unauthorized("expired"),
        tw.Forbidden("nope"),
        tw.AccountLocked("locked"),
        tw.AccountSuspended("suspended"),
    ],
)
def test_auth_failures_classify_as_auth(exc):
    failure = _classify_twikit_error(exc)
    assert failure.failure_class == "auth"
    assert failure.next_step == COOKIE_HINT


def test_rate_limit_classifies_as_blocked():
    failure = _classify_twikit_error(tw.TooManyRequests("slow down"))
    assert failure.failure_class == "blocked"
    assert "init" not in failure.next_step


@pytest.mark.parametrize(
    "exc",
    [tw.UserNotFound("x"), tw.UserUnavailable("x"), tw.NotFound("x"), tw.BadRequest("x")],
)
def test_bad_target_classifies_as_input(exc):
    assert _classify_twikit_error(exc).failure_class == "input"


def test_unknown_error_classifies_as_error_not_auth():
    """An unknown cause must not send the user to re-auth for nothing."""
    failure = _classify_twikit_error(Exception("boom"))
    assert failure.failure_class == "error"
    assert failure.next_step != COOKIE_HINT


def test_reason_names_the_underlying_error():
    failure = _classify_twikit_error(tw.TooManyRequests("slow down"))
    assert "TooManyRequests" in failure.reason
    assert "slow down" in failure.reason


def test_failure_result_shape():
    result = ToolFailure("auth", "why", "do this").result()
    assert result == {"ok": False, "class": "auth", "reason": "why", "next": "do this"}


def test_upstream_signatures_set_is_nonempty():
    """Guards against accidental empty-tuple regression that would route everything elsewhere."""
    assert len(UPSTREAM_SIGNATURES) > 0


# ---- input checks run before any network or cookie access ------------------------------------


@pytest.mark.parametrize("query,limit", [("", 20), ("   ", 20), ("mcp", 0), ("mcp", -3)])
async def test_search_rejects_bad_input(query, limit):
    with pytest.raises(ToolFailure) as info:
        await tools.search(query, limit)
    assert info.value.failure_class == "input"


@pytest.mark.parametrize("handle", ["", "not a handle", "way_too_long_handle_1", "a/b"])
async def test_user_tweets_rejects_bad_handle(handle):
    with pytest.raises(ToolFailure) as info:
        await tools.user_tweets(handle)
    assert info.value.failure_class == "input"


async def test_missing_cookie_env_is_auth(monkeypatch):
    monkeypatch.delenv("XEE_MCP_COOKIES", raising=False)
    monkeypatch.setattr(client, "_client", None)
    with pytest.raises(ToolFailure) as info:
        await tools.search("mcp")
    assert info.value.failure_class == "auth"
    assert "xee-mcp init" in info.value.next_step


async def test_missing_cookie_file_is_auth(monkeypatch, tmp_path):
    monkeypatch.setenv("XEE_MCP_COOKIES", str(tmp_path / "absent.json"))
    monkeypatch.setattr(client, "_client", None)
    with pytest.raises(ToolFailure) as info:
        await tools.user_tweets("simonw")
    assert info.value.failure_class == "auth"


# ---- what the client sees on the wire ---------------------------------------------------------


async def test_server_returns_failure_result_with_is_error(monkeypatch):
    async def fail(query, limit):
        raise ToolFailure("upstream", "KEY_BYTE", UPSTREAM_HINT)

    monkeypatch.setattr(server, "search_impl", fail)
    result = await server.mcp.call_tool("search", {"query": "mcp"})

    assert result.isError is True
    body = json.loads(result.content[0].text)
    assert body == {"ok": False, "class": "upstream", "reason": "KEY_BYTE", "next": UPSTREAM_HINT}
    assert result.structuredContent == body


async def test_server_returns_posts_on_success(monkeypatch):
    post = {"id": "1", "text": "hello", "author": "simonw"}

    async def ok(handle, limit):
        return [post]

    monkeypatch.setattr(server, "user_tweets_impl", ok)
    result = await server.mcp.call_tool("user_tweets", {"handle": "simonw"})

    assert result.isError is False
    assert json.loads(result.content[0].text) == post
    assert result.structuredContent == {"result": [post]}
