"""Log in to X via twikit and save the cookies file Xee-mcp consumes.

Prompts for handle/email + password interactively. Password is held in memory
for the duration of the login call only — never echoed, never logged, never
written to disk except as a session cookie inside the output JSON.

Usage:
    python scripts/login_and_save.py --out ~/.config/xee-mcp/cookies.json

Pass --no-ui-metrics if you hit twikit's "Couldn't get KEY_BYTE indices" error
(js2py struggles to compute X's obfuscated ui_metrics blob on some Python
versions / installs). See docs/cookies.md.

If login still fails, fall back to scripts/convert_cookies.py (browser export).
"""

from __future__ import annotations

import argparse
import asyncio
import getpass
import os
import sys
from pathlib import Path

from twikit import Client


async def _login_and_save(
    handle: str,
    email: str | None,
    password: str,
    out: Path,
    enable_ui_metrics: bool,
) -> None:
    client = Client(language="en-US")
    await client.login(
        auth_info_1=handle,
        auth_info_2=email,
        password=password,
        enable_ui_metrics=enable_ui_metrics,
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    client.save_cookies(str(out))
    os.chmod(out, 0o600)


def main() -> int:
    p = argparse.ArgumentParser(description="Log in to X and save cookies for Xee-mcp.")
    p.add_argument(
        "--out",
        type=Path,
        default=Path("~/.config/xee-mcp/cookies.json").expanduser(),
        help="Output path for the cookie JSON (default: ~/.config/xee-mcp/cookies.json)",
    )
    p.add_argument(
        "--no-ui-metrics",
        action="store_true",
        help="Disable twikit's js2py ui_metrics computation. Use if you hit "
        "'Couldn't get KEY_BYTE indices'. May very slightly raise bot-detection risk.",
    )
    args = p.parse_args()

    handle = input("X handle (without @): ").strip()
    if not handle:
        print("error: handle is required", file=sys.stderr)
        return 2
    email = input("Email (optional, recommended): ").strip() or None
    password = getpass.getpass("Password: ")
    if not password:
        print("error: password is required", file=sys.stderr)
        return 2

    out = args.out.expanduser()
    try:
        asyncio.run(
            _login_and_save(handle, email, password, out, not args.no_ui_metrics)
        )
    except Exception as e:
        msg = str(e)
        hint = ""
        if "KEY_BYTE" in msg:
            hint = (
                "\nhint: js2py failed to compute X's ui_metrics blob. "
                "Retry with --no-ui-metrics, or use scripts/convert_cookies.py."
            )
        print(f"login failed: {e}{hint}", file=sys.stderr)
        return 1

    print(f"Saved cookies to {out} (chmod 600)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
