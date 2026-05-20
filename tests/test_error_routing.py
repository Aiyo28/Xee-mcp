"""Verify _wrap_twikit_error routes upstream-lib breakage vs cookie failures correctly."""

from __future__ import annotations

import pytest

from xee_mcp.tools import (
    COOKIE_HINT,
    UPSTREAM_HINT,
    UPSTREAM_SIGNATURES,
    _wrap_twikit_error,
)


@pytest.mark.parametrize(
    "exc",
    [
        Exception("Couldn't get KEY_BYTE indices"),
        Exception("error in twikit.x_client_transaction.transaction"),
        Exception("ON_DEMAND_FILE_REGEX missed"),
    ],
)
def test_upstream_signatures_route_to_upstream_hint(exc):
    wrapped = _wrap_twikit_error(exc)
    assert UPSTREAM_HINT.split(".")[0] in str(wrapped)
    assert "Cookie auth failed" not in str(wrapped)


def test_generic_error_routes_to_cookie_hint():
    wrapped = _wrap_twikit_error(Exception("401 Unauthorized"))
    assert COOKIE_HINT.split(".")[0] in str(wrapped)
    assert "twikit issue" not in str(wrapped)


def test_upstream_signatures_set_is_nonempty():
    """Guards against accidental empty-tuple regression that would route everything to cookies."""
    assert len(UPSTREAM_SIGNATURES) > 0
