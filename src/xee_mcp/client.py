"""twikit client wrapper. Loads cookies from XEE_MCP_COOKIES path, exposes a single async client."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

from twikit import Client


_client: Client | None = None
_logger_configured = False


def _configure_logger() -> logging.Logger:
    global _logger_configured
    logger = logging.getLogger("xee_mcp")
    if _logger_configured:
        return logger
    if os.environ.get("XEE_MCP_DEBUG"):
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter("xee-mcp %(levelname)s %(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
    else:
        logger.addHandler(logging.NullHandler())
    _logger_configured = True
    return logger


log = _configure_logger()


def cookies_path() -> Path:
    raw = os.environ.get("XEE_MCP_COOKIES")
    if not raw:
        raise RuntimeError(
            "XEE_MCP_COOKIES env var not set. "
            "Point it at a twikit-format cookies JSON file. "
            "See docs/cookies.md for setup."
        )
    p = Path(raw).expanduser()
    if not p.exists():
        raise FileNotFoundError(
            f"Cookie file not found: {p}. See docs/cookies.md for setup."
        )
    return p


async def get_client() -> Client:
    """Return a singleton twikit Client with cookies loaded."""
    global _client
    if _client is None:
        path = cookies_path()
        log.debug("loading cookies from %s", path)
        c = Client(language="en-US")
        c.load_cookies(str(path))
        _client = c
        log.debug("twikit client ready")
    return _client
