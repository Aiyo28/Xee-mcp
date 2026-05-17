"""Verify XEE_MCP_COOKIES expands ~ and rejects non-existent paths cleanly."""

from __future__ import annotations

import pytest

from xee_mcp.client import cookies_path


def test_cookies_path_expands_tilde(monkeypatch, tmp_path):
    fake_home = tmp_path
    monkeypatch.setenv("HOME", str(fake_home))
    cookie_file = fake_home / ".config" / "xee-mcp" / "cookies.json"
    cookie_file.parent.mkdir(parents=True)
    cookie_file.write_text("{}")

    monkeypatch.setenv("XEE_MCP_COOKIES", "~/.config/xee-mcp/cookies.json")
    resolved = cookies_path()
    assert resolved == cookie_file
    assert resolved.is_absolute()


def test_cookies_path_missing_file_raises(monkeypatch, tmp_path):
    monkeypatch.setenv("XEE_MCP_COOKIES", str(tmp_path / "does-not-exist.json"))
    with pytest.raises(FileNotFoundError):
        cookies_path()


def test_cookies_path_error_points_at_docs(monkeypatch):
    monkeypatch.delenv("XEE_MCP_COOKIES", raising=False)
    with pytest.raises(RuntimeError, match="docs/cookies.md"):
        cookies_path()
