"""Xee-mcp CLI dispatcher.

Three subcommands:
  - `xee-mcp init` — extract X cookies from a local browser, write twikit JSON
  - `xee-mcp config` — print the client config for Claude Desktop / Claude Code / Cursor with
    absolute paths filled in (prints only, writes no file)
  - `xee-mcp serve` — run the MCP server (also the default when invoked with no subcommand,
    preserving Claude Desktop / Claude Code configs that point at bare `xee-mcp`)
"""

from __future__ import annotations

import json
import os
import shlex
import shutil
import sys
from pathlib import Path

import click

DEFAULT_COOKIE_PATH = Path("~/.config/xee-mcp/cookies.json")
X_HOSTS = {"x.com", ".x.com", "twitter.com", ".twitter.com"}
REQUIRED_COOKIES = ("auth_token", "ct0")
SUPPORTED_BROWSERS = ("chrome", "brave", "arc", "firefox", "safari", "edge")
CLIENTS = ("claude-desktop", "claude-code", "cursor")


@click.group(invoke_without_command=True)
@click.version_option(package_name="xee-mcp")
@click.pass_context
def main(ctx: click.Context) -> None:
    """Xee-mcp — MCP server for X (Twitter): search + read."""
    if ctx.invoked_subcommand is None:
        ctx.invoke(serve)


@main.command()
def serve() -> None:
    """Run the MCP server (stdio transport)."""
    from .server import main as run_server

    run_server()


@main.command()
@click.option(
    "--browser",
    type=click.Choice(SUPPORTED_BROWSERS, case_sensitive=False),
    default="chrome",
    show_default=True,
    help="Browser to extract cookies from. Must be logged in to x.com.",
)
@click.option(
    "--out",
    "out_path",
    type=click.Path(dir_okay=False, path_type=Path),
    default=str(DEFAULT_COOKIE_PATH),
    show_default=True,
    help="Output JSON path. Will be chmod 600.",
)
@click.option(
    "--force",
    is_flag=True,
    default=False,
    help="Overwrite an existing cookie file.",
)
def init(browser: str, out_path: Path, force: bool) -> None:
    """Extract X cookies from a local browser into a twikit-compatible JSON file.

    Requires a logged-in x.com session in the chosen browser. On macOS, Chrome / Brave / Edge
    will trigger a Keychain prompt to decrypt the cookie store — approve it.
    """
    out = out_path.expanduser()
    if out.exists() and not force:
        raise click.ClickException(
            f"{out} already exists. Pass --force to overwrite."
        )

    try:
        jar = _load_browser_jar(browser)
    except Exception as exc:
        raise click.ClickException(
            f"Failed to read {browser} cookie store: {exc}. "
            "Is the browser installed and have you logged in to x.com at least once?"
        ) from exc

    cookies = _filter_x_cookies(jar)
    missing = [name for name in REQUIRED_COOKIES if name not in cookies]
    if missing:
        raise click.ClickException(
            f"No logged-in x.com session found in {browser} "
            f"(missing: {', '.join(missing)}). Log in to x.com in {browser} and retry."
        )

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(cookies), encoding="utf-8")
    os.chmod(out, 0o600)

    click.echo(f"Wrote {len(cookies)} cookies to {out} (chmod 600).")
    click.echo("")
    click.echo("Next:")
    click.echo(f"  export XEE_MCP_COOKIES={out}")
    click.echo("  xee-mcp serve   # or wire into Claude Desktop / Claude Code")



@main.command()
@click.option(
    "--client",
    type=click.Choice(CLIENTS, case_sensitive=False),
    default=None,
    help="Print only this client's config, ready to paste. Default: all three, with headers.",
)
@click.option(
    "--cookies",
    "cookies_opt",
    type=click.Path(dir_okay=False, path_type=Path),
    default=None,
    help="Cookie file path. Default: $XEE_MCP_COOKIES, else the path `init` writes to.",
)
def config(client: str | None, cookies_opt: Path | None) -> None:
    """Print the config a client needs to launch Xee-mcp, with absolute paths.

    GUI clients (Claude Desktop, Cursor) do not load your shell PATH, so a bare `xee-mcp` or
    `uv` command often fails to start there. This prints full paths instead. Writes no file.
    """
    command, args = _launch_command()
    cookies = _cookie_path(cookies_opt)
    if not cookies.exists():
        click.echo(f"Note: {cookies} does not exist yet. Run: xee-mcp init", err=True)

    if client:
        click.echo(_client_config(client.lower(), command, args, cookies))
        return
    for name in CLIENTS:
        click.echo(f"# {_CLIENT_HEADERS[name]()}")
        click.echo(_client_config(name, command, args, cookies))
        click.echo("")


def _launch_command() -> tuple[str, list[str]]:
    """Absolute command + args that start the server: the `xee-mcp` script, else this Python."""
    script = shutil.which("xee-mcp")
    if script:
        return str(Path(script).absolute()), []
    return sys.executable, ["-m", "xee_mcp.cli"]


def _cookie_path(explicit: Path | None) -> Path:
    raw = explicit or os.environ.get("XEE_MCP_COOKIES") or DEFAULT_COOKIE_PATH
    return Path(raw).expanduser().absolute()


def _client_config(client: str, command: str, args: list[str], cookies: Path) -> str:
    """One client's config: a `claude mcp add` line for Claude Code, mcpServers JSON otherwise."""
    if client == "claude-code":
        argv = ["claude", "mcp", "add", "--scope", "user", "xee-mcp",
                "-e", f"XEE_MCP_COOKIES={cookies}", "--", command, *args]
        return " ".join(shlex.quote(part) for part in argv)
    entry: dict[str, object] = {"command": command}
    if args:
        entry["args"] = args
    entry["env"] = {"XEE_MCP_COOKIES": str(cookies)}
    return json.dumps({"mcpServers": {"xee-mcp": entry}}, indent=2)


def _claude_desktop_header() -> str:
    if sys.platform == "darwin":
        where = "~/Library/Application Support/Claude/claude_desktop_config.json"
    elif sys.platform == "win32":
        where = r"%APPDATA%\Claude\claude_desktop_config.json"
    else:
        where = "~/.config/Claude/claude_desktop_config.json"
    return f"Claude Desktop: merge into {where}, then quit it fully and reopen"


_CLIENT_HEADERS = {
    "claude-desktop": _claude_desktop_header,
    "claude-code": lambda: "Claude Code: run in a terminal, then /mcp to check it is connected",
    "cursor": lambda: "Cursor: merge into ~/.cursor/mcp.json, then reload the window",
}

def _load_browser_jar(browser: str):
    """Return a CookieJar from the requested browser, scoped to x.com.

    Isolated so tests can monkeypatch this without touching browser_cookie3 internals.
    """
    import browser_cookie3 as bc3

    fn = getattr(bc3, browser.lower())
    return fn(domain_name="x.com")


def _filter_x_cookies(jar) -> dict[str, str]:
    """Reduce a CookieJar to the flat {name: value} dict twikit expects."""
    cookies: dict[str, str] = {}
    for c in jar:
        domain = getattr(c, "domain", "")
        if domain in X_HOSTS or domain.lstrip(".") in {"x.com", "twitter.com"}:
            cookies[c.name] = c.value
    return cookies


if __name__ == "__main__":
    sys.exit(main())
