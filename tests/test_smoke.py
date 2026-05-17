"""Smoke tests — module imports and tool registration. No live network."""

from __future__ import annotations

import importlib


def test_package_imports():
    pkg = importlib.import_module("xee_mcp")
    assert pkg.__version__


def test_server_module_imports():
    importlib.import_module("xee_mcp.server")


def test_tools_module_imports():
    importlib.import_module("xee_mcp.tools")


def test_client_module_imports():
    importlib.import_module("xee_mcp.client")


def test_server_name_is_xee_mcp():
    from xee_mcp.server import mcp

    assert mcp.name == "xee-mcp"


def test_cookies_path_raises_without_env(monkeypatch):
    from xee_mcp.client import cookies_path

    monkeypatch.delenv("XEE_MCP_COOKIES", raising=False)
    try:
        cookies_path()
    except RuntimeError as e:
        assert "XEE_MCP_COOKIES" in str(e)
    else:
        raise AssertionError("expected RuntimeError when env var unset")
