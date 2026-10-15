# Tools are read-only

No Xee-mcp tool may mutate X state (post, DM, like, retweet). Write access carries a different threat model and audit surface than reading with a cookie session, so a write-capable server belongs in a separate repo, not in this one.
