"""Smoke tests — module imports and tool registration. No live network."""

from __future__ import annotations

import importlib


def test_package_imports():
    pkg = importlib.import_module("mcp_xee")
    assert pkg.__version__


def test_server_module_imports():
    importlib.import_module("mcp_xee.server")


def test_tools_module_imports():
    importlib.import_module("mcp_xee.tools")


def test_client_module_imports():
    importlib.import_module("mcp_xee.client")


def test_cookies_path_raises_without_env(monkeypatch):
    from mcp_xee.client import cookies_path

    monkeypatch.delenv("MCP_XEE_COOKIES", raising=False)
    try:
        cookies_path()
    except RuntimeError as e:
        assert "MCP_XEE_COOKIES" in str(e)
    else:
        raise AssertionError("expected RuntimeError when env var unset")
