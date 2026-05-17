"""twikit client wrapper. Loads cookies from XEE_MCP_COOKIES path, exposes a single async client."""

from __future__ import annotations

import os
from pathlib import Path

from twikit import Client


_client: Client | None = None


def cookies_path() -> Path:
    raw = os.environ.get("XEE_MCP_COOKIES")
    if not raw:
        raise RuntimeError(
            "XEE_MCP_COOKIES env var not set. "
            "Point it at a twikit-format cookies JSON file. "
            "See README quickstart."
        )
    p = Path(raw).expanduser()
    if not p.exists():
        raise FileNotFoundError(f"Cookie file not found: {p}")
    return p


async def get_client() -> Client:
    """Return a singleton twikit Client with cookies loaded."""
    global _client
    if _client is None:
        c = Client(language="en-US")
        c.load_cookies(str(cookies_path()))
        _client = c
    return _client
