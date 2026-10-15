# Single account in v0.1

v0.1 uses one cookie file for one account. A multi-account cookie pool adds state and rotation logic that is not justified until reliable bot-detection makes a single account unusable; if that happens the likely path is swapping the scraper library internally while keeping the tool surface identical. Do not pre-build the pool.
