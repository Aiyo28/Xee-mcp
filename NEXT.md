# NEXT — Xee-mcp

> Resume line for the next session. Under 15 lines. Updated by `/session --end`.

**Status (2026-05-17 s1):** Rename `mcp-xee` → `Xee-mcp` complete (vault [D]#4 executed). GH repo `Aiyo28/Xee-mcp`, local `~/Documents/Developer/Xee-mcp/`, Python module `xee_mcp`, PyPI distro target `xee-mcp`, CLI `xee-mcp`, env vars `XEE_MCP_COOKIES`/`XEE_MCP_DEBUG`, FastMCP server name `"xee-mcp"`. Spec for rename+deploy filed as github.com/Aiyo28/Xee-mcp/issues/2; #1 (v0.1 ship-readiness) still open and unchanged. Smoke tests 6/6 (added `test_server_name_is_xee_mcp`). Vault context at `~/Documents/Developer/knowledge-os/Projects/Xee-mcp/_context.md`.

## Continue
- Phase B (issue #1 items, 11 modules): `scripts/login_and_save.py`, `scripts/convert_cookies.py`, `docs/cookies.md`, `docs/release.md`, `examples/claude_desktop_config.json`, `examples/claude_code_config.md`, `.github/workflows/ci.yml`, `XEE_MCP_DEBUG` logger, tool-error wrapping with cookie hint, `tests/test_serialize.py` + `tests/test_cookies_path_tilde.py`, README `pip install xee-mcp` line (gated on Phase C).
- Phase C (deploy): verify PyPI account `aiyo28`, local pre-tag smoke against fresh @Aiyo91 cookies, tag v0.1.0, `gh release create`, `uv build && uv publish`, fresh-venv install smoke.

## Decide (next session)
- Phase B in one commit or sliced? Default: sliced (scripts → CI → debug → tests → docs).
- v0.1.0 tag date — today or after Phase B fully green?

## Blocked
- PyPI account `aiyo28` verification (login + token / trusted publisher setup).
- Fresh @Aiyo91 X cookies for local pre-tag verify.
