"""Convert a Netscape cookies.txt (e.g. from 'Get cookies.txt LOCALLY' Chrome extension)
into the JSON dict format twikit consumes.

No password handling. Operates on already-exported browser cookies; useful if you
don't want to feed your X password to a script. Only cookies on x.com / twitter.com
hosts are kept.

Usage:
    python scripts/convert_cookies.py cookies.txt --out ~/.config/xee-mcp/cookies.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

X_HOSTS = ("x.com", ".x.com", "twitter.com", ".twitter.com")


def parse_netscape(text: str) -> dict[str, str]:
    cookies: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) < 7:
            continue
        domain, _, _, _, _, name, value = parts[:7]
        if domain in X_HOSTS:
            cookies[name] = value
    return cookies


def main() -> int:
    p = argparse.ArgumentParser(description="Convert Netscape cookies.txt to twikit JSON.")
    p.add_argument("input", type=Path, help="Path to cookies.txt (Netscape format)")
    p.add_argument(
        "--out",
        type=Path,
        default=Path("~/.config/xee-mcp/cookies.json").expanduser(),
        help="Output JSON path (default: ~/.config/xee-mcp/cookies.json)",
    )
    args = p.parse_args()

    src = args.input.expanduser()
    if not src.exists():
        print(f"error: file not found: {src}", file=sys.stderr)
        return 2

    cookies = parse_netscape(src.read_text(encoding="utf-8"))
    if not cookies:
        print("error: no x.com/twitter.com cookies found in input", file=sys.stderr)
        return 1

    out = args.out.expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(cookies), encoding="utf-8")
    os.chmod(out, 0o600)
    print(f"Wrote {len(cookies)} cookies to {out} (chmod 600)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
