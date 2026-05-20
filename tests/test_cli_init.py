"""Tests for `xee-mcp init` — cookie extraction via browser-cookie3."""

from __future__ import annotations

import json
import os
import stat

import pytest
from click.testing import CliRunner

from xee_mcp import cli


class FakeCookie:
    def __init__(self, name: str, value: str, domain: str = ".x.com") -> None:
        self.name = name
        self.value = value
        self.domain = domain


def _jar(*cookies: FakeCookie) -> list[FakeCookie]:
    """browser_cookie3 jars are iterable of cookie objects with .name/.value/.domain."""
    return list(cookies)


@pytest.fixture
def valid_jar() -> list[FakeCookie]:
    return _jar(
        FakeCookie("auth_token", "abc123"),
        FakeCookie("ct0", "def456"),
        FakeCookie("guest_id", "v1%3A123"),
        FakeCookie("unrelated", "skip", domain=".example.com"),
    )


@pytest.fixture
def patch_loader(monkeypatch, valid_jar):
    monkeypatch.setattr(cli, "_load_browser_jar", lambda browser: valid_jar)
    return valid_jar


def test_init_writes_default_path(monkeypatch, tmp_path, patch_loader):
    monkeypatch.setenv("HOME", str(tmp_path))
    runner = CliRunner()
    result = runner.invoke(cli.main, ["init"])

    assert result.exit_code == 0, result.output
    out = tmp_path / ".config" / "xee-mcp" / "cookies.json"
    assert out.exists()
    data = json.loads(out.read_text())
    assert data == {"auth_token": "abc123", "ct0": "def456", "guest_id": "v1%3A123"}


def test_init_writes_to_out_path(tmp_path, patch_loader):
    out = tmp_path / "custom" / "cookies.json"
    runner = CliRunner()
    result = runner.invoke(cli.main, ["init", "--out", str(out)])

    assert result.exit_code == 0, result.output
    assert out.exists()
    assert "auth_token" in json.loads(out.read_text())


def test_init_chmod_600(tmp_path, patch_loader):
    out = tmp_path / "cookies.json"
    runner = CliRunner()
    result = runner.invoke(cli.main, ["init", "--out", str(out)])

    assert result.exit_code == 0, result.output
    mode = stat.S_IMODE(os.stat(out).st_mode)
    assert mode == 0o600, f"expected 0o600, got {oct(mode)}"


def test_init_refuses_overwrite_without_force(tmp_path, patch_loader):
    out = tmp_path / "cookies.json"
    out.write_text("{}")
    runner = CliRunner()
    result = runner.invoke(cli.main, ["init", "--out", str(out)])

    assert result.exit_code != 0
    assert "already exists" in result.output
    assert out.read_text() == "{}"


def test_init_force_overwrites(tmp_path, patch_loader):
    out = tmp_path / "cookies.json"
    out.write_text("{}")
    runner = CliRunner()
    result = runner.invoke(cli.main, ["init", "--out", str(out), "--force"])

    assert result.exit_code == 0, result.output
    assert "auth_token" in json.loads(out.read_text())


def test_init_errors_when_no_logged_in_session(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "_load_browser_jar", lambda browser: _jar(
        FakeCookie("guest_id", "v1%3A123"),  # no auth_token, no ct0
    ))
    out = tmp_path / "cookies.json"
    runner = CliRunner()
    result = runner.invoke(cli.main, ["init", "--out", str(out)])

    assert result.exit_code != 0
    assert "auth_token" in result.output
    assert "Log in to x.com" in result.output
    assert not out.exists()


def test_init_errors_when_browser_unavailable(monkeypatch, tmp_path):
    def boom(browser: str) -> None:
        raise RuntimeError("could not find cookie database")

    monkeypatch.setattr(cli, "_load_browser_jar", boom)
    out = tmp_path / "cookies.json"
    runner = CliRunner()
    result = runner.invoke(cli.main, ["init", "--browser", "brave", "--out", str(out)])

    assert result.exit_code != 0
    assert "brave" in result.output
    assert "logged in to x.com" in result.output


def test_init_filters_to_x_domains_only(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "_load_browser_jar", lambda browser: _jar(
        FakeCookie("auth_token", "abc", domain=".x.com"),
        FakeCookie("ct0", "def", domain="twitter.com"),
        FakeCookie("session", "leak", domain=".google.com"),
        FakeCookie("tracker", "leak2", domain=".facebook.com"),
    ))
    out = tmp_path / "cookies.json"
    runner = CliRunner()
    result = runner.invoke(cli.main, ["init", "--out", str(out)])

    assert result.exit_code == 0, result.output
    data = json.loads(out.read_text())
    assert set(data.keys()) == {"auth_token", "ct0"}


def test_init_supports_all_browsers(monkeypatch, tmp_path, valid_jar):
    calls: list[str] = []

    def record(browser: str) -> list[FakeCookie]:
        calls.append(browser)
        return valid_jar

    monkeypatch.setattr(cli, "_load_browser_jar", record)
    for b in cli.SUPPORTED_BROWSERS:
        out = tmp_path / f"{b}.json"
        runner = CliRunner()
        result = runner.invoke(cli.main, ["init", "--browser", b, "--out", str(out)])
        assert result.exit_code == 0, f"{b}: {result.output}"

    assert calls == list(cli.SUPPORTED_BROWSERS)


def test_bare_invocation_runs_serve(monkeypatch):
    """Existing Claude Desktop configs use bare `xee-mcp` — must still launch serve."""
    called = {"n": 0}

    def fake_run_server() -> None:
        called["n"] += 1

    monkeypatch.setattr("xee_mcp.server.main", fake_run_server)
    runner = CliRunner()
    result = runner.invoke(cli.main, [])

    assert result.exit_code == 0, result.output
    assert called["n"] == 1
