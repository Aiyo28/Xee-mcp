# Upstream issue drafts

Found 2026-05-18 during Xee-mcp v0.1.0 pre-tag live smoke. Both libs broken against current X (`x.com` HTML and GraphQL response shapes). File these on the respective upstream repos when ready; Xee-mcp v0.1.0 ship is paused until at least one ships a fix.

---

## twikit — `ON_DEMAND_FILE_REGEX` does not match current X webpack chunk format

**Repo:** https://github.com/d60/twikit
**Version reproduced:** `twikit==2.3.3` (latest as of 2026-05-18) on `Python 3.11.13` (Darwin 25.5.0, M-series Mac).

### Symptom

Every request through `twikit.Client` raises `Exception: Couldn't get KEY_BYTE indices` from `twikit/x_client_transaction/transaction.py:54` — including simple read calls like `client.search_tweet(...)` and `client.get_user_by_screen_name(...)`. Cookies are valid (same session works in browser).

### Root cause

`twikit/x_client_transaction/transaction.py:15`:

```python
ON_DEMAND_FILE_REGEX = re.compile(
    r"""['|\"]{1}ondemand\.s['|\"]{1}:\s*['|\"]{1}([\w]*)['|\"]{1}""",
    flags=(re.VERBOSE | re.MULTILINE))
```

This expects `"ondemand.s":"<hash>"` (a webpack JSON entry mapping the chunk name to its hash). The current `https://x.com/` HTML serves a different webpack format:

```
'ondemand.s",60041:"i18n/emoji-gu",60227:"ondemand.countries-ur",60288:"bundle.Explore",60305:"ondemand.countri'
```

i.e. `"ondemand.s",<chunk-id>:"<next-entry>"`. The regex misses → `key_byte_indices` is empty → exception.

### Repro

```python
import asyncio, httpx, re

async def repro():
    async with httpx.AsyncClient(follow_redirects=True,
        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}) as c:
        r = await c.get("https://x.com/")
        # twikit's pattern
        m = re.search(
            r"""['|\"]{1}ondemand\.s['|\"]{1}:\s*['|\"]{1}([\w]*)['|\"]{1}""",
            r.text)
        print("twikit pattern match:", m)
        # Actual format
        m2 = re.search(r"ondemand\.s.{0,30}", r.text)
        print("first context:", repr(m2.group(0)) if m2 else None)

asyncio.run(repro())
```

Output:

```
twikit pattern match: None
first context: 'ondemand.s",60041:"i18n/emoji-gu'
```

### Fix shape

Not a one-line regex update — the new format pairs `"ondemand.s"` with a numeric chunk ID, not a hash. Building the URL would now require resolving `chunk-ID → file-hash` from elsewhere in the webpack manifest.

---

## twscrape — response parser `IndexError` on `UserByScreenName` + `SearchTimeline`

**Repo:** https://github.com/vladkens/twscrape
**Version reproduced:** `twscrape==0.17.0` (latest as of 2026-05-18) on `Python 3.11.13` (Darwin 25.5.0).

### Symptom

`api.user_by_login(...)` and `api.search(...)` both throw:

```
WARNING | twscrape.queue_client:req:291 - Unknown error. Account timeouted for 15 minutes.
Err: <class 'IndexError'>: list index out of range
```

twscrape then auto-locks the account for 15 minutes per error. Account was set up via `add_account(cookies=...)` using a working browser session's cookie string (`auth_token`, `ct0`, `guest_id`, `twid`, `kdt`, `personalization_id`, etc. — 14 cookies total, all valid in browser).

### Hypothesis

`IndexError` in `req` after a 200-class response suggests twscrape's GraphQL response parser is unpacking a tuple/list from X's payload that no longer has the expected shape. Different X endpoint families (`UserByScreenName` and `SearchTimeline`) both fail identically → likely a shared response-shape assumption broken across endpoints.

### Repro

```python
import asyncio
from twscrape import API

async def repro():
    api = API("/tmp/probe.db")
    # Cookie string lifted from a logged-in browser session (auth_token + ct0 + …)
    await api.pool.add_account(
        username="<your_handle>",
        password="<unused>",  # twscrape requires the kwarg but cookie auth skips login
        email="<unused>",
        email_password="<unused>",
        cookies="auth_token=...; ct0=...; guest_id=...; twid=...; kdt=...",
    )
    await api.pool.set_active("<your_handle>", True)
    try:
        user = await api.user_by_login("simonw")
        print("ok:", user.username)
    except Exception as e:
        print(f"failed: {type(e).__name__}: {e}")
    async for tw in api.search("mcp", limit=1):
        print("search ok")
        break

asyncio.run(repro())
```

### Note

Stack: `twscrape 0.17.0` + `aiosqlite 0.22.1` + `loguru 0.7.3` + `fake-useragent 2.2.0` (all latest as resolved 2026-05-18). Cookie-string format accepted, account marked active, queue request initiated — failure is in response parsing after the GET, not in queue setup.
