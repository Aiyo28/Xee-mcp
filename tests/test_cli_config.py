"""Tests for `xee-mcp config` — prints a client config with absolute paths, writes nothing.

GUI clients (Claude Desktop, Cursor) do not load the shell PATH, so a bare `xee-mcp` or `uv`
command often fails to start there. Every path this prints must be absolute.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

from xee_mcp import cli

FAKE_SCRIPT = "/opt/venv/bin/xee-mcp"


@pytest.fixture
def on_path(monkeypatch):
    monkeypatch.setattr(cli.shutil, "which", lambda name: FAKE_SCRIPT if name == "xee-mcp" else None)


@pytest.fixture
def cookie_file(monkeypatch, tmp_path) -> Path:
    path = tmp_path / "cookies.json"
    path.write_text('{"auth_token": "secret-value"}')
    monkeypatch.setenv("XEE_MCP_COOKIES", str(path))
    return path


def _run(*args: str):
    return CliRunner().invoke(cli.main, ["config", *args])


@pytest.mark.parametrize("client", ["claude-desktop", "cursor"])
def test_json_clients_get_absolute_command_and_cookie_path(on_path, cookie_file, client):
    result = _run("--client", client)

    assert result.exit_code == 0, result.output
    entry = json.loads(result.stdout)["mcpServers"]["xee-mcp"]
    assert entry["command"] == FAKE_SCRIPT
    assert entry.get("args", []) == []
    assert entry["env"] == {"XEE_MCP_COOKIES": str(cookie_file)}


def test_claude_code_gets_mcp_add_command(on_path, cookie_file):
    result = _run("--client", "claude-code")

    assert result.exit_code == 0, result.output
    assert result.stdout.strip() == (
        f"claude mcp add --scope user xee-mcp -e XEE_MCP_COOKIES={cookie_file} -- {FAKE_SCRIPT}"
    )


def test_no_client_prints_all_three_with_headers(on_path, cookie_file):
    result = _run()

    assert result.exit_code == 0, result.output
    assert "# Claude Desktop" in result.output
    assert "# Claude Code" in result.output
    assert "# Cursor" in result.output


def test_falls_back_to_this_python_when_script_not_on_path(monkeypatch, cookie_file):
    monkeypatch.setattr(cli.shutil, "which", lambda name: None)
    result = _run("--client", "claude-desktop")

    assert result.exit_code == 0, result.output
    entry = json.loads(result.stdout)["mcpServers"]["xee-mcp"]
    assert entry["command"] == sys.executable
    assert entry["args"] == ["-m", "xee_mcp.cli"]


def test_relative_script_path_is_made_absolute(monkeypatch, cookie_file):
    monkeypatch.setattr(cli.shutil, "which", lambda name: ".venv/bin/xee-mcp")
    entry = json.loads(_run("--client", "cursor").stdout)["mcpServers"]["xee-mcp"]
    assert Path(entry["command"]).is_absolute()


def test_cookie_path_is_expanded_and_absolute(on_path, monkeypatch):
    monkeypatch.setenv("XEE_MCP_COOKIES", "~/somewhere/cookies.json")
    entry = json.loads(_run("--client", "claude-desktop").stdout)["mcpServers"]["xee-mcp"]
    cookies = entry["env"]["XEE_MCP_COOKIES"]
    assert "~" not in cookies
    assert Path(cookies).is_absolute()


def test_defaults_to_init_output_path_when_env_unset(on_path, monkeypatch, tmp_path):
    monkeypatch.delenv("XEE_MCP_COOKIES", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    entry = json.loads(_run("--client", "claude-desktop").stdout)["mcpServers"]["xee-mcp"]
    assert entry["env"]["XEE_MCP_COOKIES"] == str(tmp_path / ".config" / "xee-mcp" / "cookies.json")


def test_cookies_option_overrides_env(on_path, cookie_file, tmp_path):
    other = tmp_path / "other.json"
    entry = json.loads(_run("--client", "cursor", "--cookies", str(other)).stdout)
    assert entry["mcpServers"]["xee-mcp"]["env"]["XEE_MCP_COOKIES"] == str(other)


def test_warns_on_stderr_when_cookie_file_missing(on_path, monkeypatch, tmp_path):
    monkeypatch.setenv("XEE_MCP_COOKIES", str(tmp_path / "absent.json"))
    result = CliRunner().invoke(cli.main, ["config", "--client", "cursor"])

    assert result.exit_code == 0
    json.loads(result.stdout)  # stdout stays pasteable
    assert "xee-mcp init" in result.stderr


def test_never_prints_cookie_contents(on_path, cookie_file):
    assert "secret-value" not in _run().output


def test_writes_no_file(on_path, cookie_file, tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    before = sorted(p for p in tmp_path.rglob("*"))
    _run()
    assert sorted(p for p in tmp_path.rglob("*")) == before
