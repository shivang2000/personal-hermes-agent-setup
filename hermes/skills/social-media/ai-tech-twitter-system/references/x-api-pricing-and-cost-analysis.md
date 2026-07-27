# X API Pricing & Cost Analysis

## Pricing (pay-per-use, no subscription)

### Reads (per resource returned)

| Operation | Cost |
|---|---|
| Post read (search results, timeline) | $0.005 per post |
| User read | $0.010 per resource |
| DM event read | $0.010 per resource |
| Following/Followers read | $0.010 per resource |
| Like/Mute/Block read | $0.001 per resource |
| Owned read (own tweets, mentions, bookmarks) | $0.001 per resource |
| **Monthly post read cap** | **2 million posts** |

### Writes (per request)

| Operation | Cost |
|---|---|
| Post: Create | $0.015 per request |
| Post: Create with URL | $0.200 per request |
| Post: Create (summoned) | $0.010 per request |
| Reply / Quote | $0.015 per request |
| User Interaction (like, repost, bookmark) | $0.015 per request |
| Media upload | $0.005 per request |
| Interaction: Delete | $0.010 per request |

### Deduplication
Resources are deduplicated within a 24-hour UTC day window. Requesting the same post multiple times in a day counts as one charge. The dedup window resets at midnight UTC.

## Cost breakdown by operation type

The dominant cost is **search reads**. Each `xurl search` call returns up to 20 posts at $0.005/post = **$0.10 per search call**. With 265 searches in 3 days, that's $26.50 — **97% of total cost**.

Write operations are cheap: 34 posts × $0.015 = $0.51.

## Real usage data (July 25-27, 2026, 3 days)

| Call type | Count | Cost |
|---|---|---|
| xurl search (reads) | 265 calls | ~$13-27 |
| xurl post (writes) | 34 calls | $0.51 |
| xurl whoami (reads) | 24 calls | $0.02 |
| xurl read (reads) | 11 calls | $0.06 |
| xurl media (writes) | 11 calls | $0.06 |
| xurl user (reads) | 7 calls | $0.07 |
| xurl quote (writes) | 4 calls | $0.06 |
| xurl auth (free) | 174 calls | $0.00 |
| **TOTAL (3 days)** | **538 calls** | **~$14-27** |

## Monthly projections at various cadences

| Cadence | Monthly cost |
|---|---|
| 4 scanners at every 30m/45m (current) | $140-273/month |
| 4 scanners reduced to every 2h | $40-60/month |
| Browser-based automation (Arc) | **$0/month** |

## Browser-based alternative ($0/month)

X.com can be driven via AppleScript JavaScript execution in Arc browser, completely bypassing the X API. See:
- Script: `~/.hermes/scripts/x_browser.py`
- Skill section: "Browser-based automation" in SKILL.md

This is the default method since July 2026 when API credits depleted.