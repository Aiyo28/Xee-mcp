"""Xee-mcp CLI dispatcher.

Two subcommands:
  - `xee-mcp init` — extract X cookies from a local browser, write twikit JSON
  - `xee-mcp serve` — run the MCP server (also the default when invoked with no subcommand,
    preserving Claude Desktop / Claude Code configs that point at bare `xee-mcp`)
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import click

DEFAULT_COOKIE_PATH = Path("~/.config/xee-mcp/cookies.json")
X_HOSTS = {"x.com", ".x.com", "twitter.com", ".twitter.com"}
REQUIRED_COOKIES = ("auth_token", "ct0")
SUPPORTED_BROWSERS = ("chrome", "brave", "arc", "firefox", "safari", "edge")


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
