# NEXT — Xee-mcp

> Resume line for the next session. Under 15 lines. Updated by `/session --end`.

**Status (2026-05-17 s2):** Phase A (rename) + Phase B (issue #1 items) complete. GH repo `Aiyo28/Xee-mcp`, Python module `xee_mcp`, PyPI distro target `xee-mcp`. CI green on 3.11/3.12/3.13 matrix (`setup-uv@v6`). Pytest 14/14 (smoke 6 + serialize 5 + cookies_path_tilde 3). Ruff clean. Shipped: scripts (login_and_save, convert_cookies), docs (cookies, release), examples (claude_desktop, claude_code), `XEE_MCP_DEBUG` logger, `COOKIE_HINT` error wrapping in `tools.py`. Commits `df65d80` (rename), `74adba8` (Phase B), `799aa79`+`22b9256` (CI fixes). Issues #1 + #2 open under new repo. Vault context at `~/Documents/Developer/knowledge-os/Projects/Xee-mcp/_context.md`.

## Continue
- **Phase C (deploy):**
  1. Verify PyPI account `aiyo28` — login + scoped token export as `UV_PUBLISH_TOKEN`.
  2. Local pre-tag smoke against fresh @Aiyo91 cookies (script in `docs/release.md`).
  3. `git tag v0.1.0 && git push --tags`.
  4. `gh release create v0.1.0 --generate-notes` (edit body).
  5. `UV_PUBLISH_TOKEN=… uv publish` after `uv build`.
  6. Fresh-venv install smoke + Claude Desktop handshake verify.
  7. Append README "Install via `pip install xee-mcp`" line; commit.
  8. Close #1 + #2 with commit refs; append [D]#7 (v0.1.0 shipped) to vault.

## Decide (next session)
- Trusted publishing (GitHub OIDC) vs scoped API token for `uv publish`? Default: scoped token at v0.1; OIDC at v0.2.
- v0.1.0 tag today or after fresh-cookie smoke?

## Blocked
- PyPI account `aiyo28` verification (login + token).
- Fresh @Aiyo91 X cookies for pre-tag smoke (`docs/release.md` script).
