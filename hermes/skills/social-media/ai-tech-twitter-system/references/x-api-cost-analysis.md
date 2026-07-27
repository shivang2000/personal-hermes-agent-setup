# X API Pay-Per-Use Cost Analysis

Use this reference when Shivang asks about X API costs, how much credits to deposit, or why credits ran out. The X API moved from subscription tiers to pay-per-use pricing — credits are bought upfront and deplete per API call.

## Pricing table (as of July 2026)

### Read operations (per resource returned)

| Resource | Unit cost |
|---|---|
| Posts: Read (search results, timeline) | $0.005 per post |
| User: Read (user lookup) | $0.010 per user |
| DM Event: Read | $0.010 per event |
| Following/Followers: Read | $0.010 per resource |
| List: Read | $0.005 per resource |
| Space: Read | $0.005 per resource |
| Like: Read | $0.001 per resource |
| Mute: Read | $0.001 per resource |
| Profile Update: Read | $0.005 per resource |

**Owned Reads** (your own data: posts, mentions, bookmarks, followers, likes) = **$0.001 per resource** (10x cheaper than regular reads).

Monthly cap: 2 million Post reads per billing cycle on pay-per-use.

### Write operations (per request)

| Action | Unit cost |
|---|---|
| Post: Create | $0.015 per request |
| Post: Create (with URL) | **$0.200 per request** |
| Post: Create (summoned) | $0.010 per request |
| Reply / Quote | $0.015 per request (same as Post: Create) |
| User Interaction (like, repost, follow) | $0.015 per request |
| Media upload | $0.005 per request |
| Bookmark | $0.005 per request |
| Delete | $0.010 per request |

### Deduplication

All resources are deduplicated within a 24-hour UTC day window. Requesting the same post multiple times in a day counts as one charge. The dedup window resets at midnight UTC.

## CreditsDepleted (HTTP 402) vs HTTP 429

| Symptom | Cause | Fix |
|---|---|---|
| `{"detail":"credits depleted","status":402}` | Account balance is $0 | Deposit credits at Developer Console → Billing |
| `HTTP 429: usage limit` | Monthly tier cap hit | Upgrade tier or wait for monthly reset (see `references/x-tier-quota-recovery.md`) |
| `CreditsDepleted` but `whoami` works | whoami is an owned read ($0.001), still works when balance is $0 | Same — deposit credits |

Key diagnostic: `xurl whoami` uses an owned read endpoint that costs $0.001. It can still succeed when the balance is technically $0 because X allows a tiny grace margin. But `xurl search` (which returns posts at $0.005 each) and `xurl post` ($0.015) will fail with `credits depleted`.

## Session DB cost analysis technique

When Shivang asks "how much did we spend" or "how many reads/writes did we do", use the Hermes session database to calculate actual usage from terminal command history.

### Database location

```python
from pathlib import Path
db = Path.home() / ".hermes" / "state.db"
```

### Query pattern

```sql
-- Get all xurl terminal commands from assistant messages
SELECT m.tool_calls, m.timestamp
FROM messages m
WHERE m.tool_calls LIKE '%xurl%'
AND m.role = 'assistant'
```

Then parse the JSON `tool_calls` array to extract commands:

```python
import json, re

for msg in results:
    tool_calls = json.loads(msg[0])  # tool_calls column
    for tc in tool_calls:
        func = tc.get('function', {})
        if func.get('name') == 'terminal':
            args = json.loads(func['arguments'])
            cmd = args.get('command', '')
            if 'xurl' in cmd:
                # Extract subcommand: search, post, quote, reply, whoami, etc.
                match = re.search(r'xurl\s+(\w+)', cmd)
                subcmd = match.group(1) if match else 'unknown'
                # Categorize and count
```

### Cost calculation

Multiply each subcommand count by its unit cost:

| xurl subcommand | API operation | Cost per call | Notes |
|---|---|---|---|
| `xurl search` | Post reads | $0.005 × N results (default N=20) = **$0.10/call** | Most expensive operation |
| `xurl post` | Post create | $0.015/call | |
| `xurl quote` | Post create | $0.015/call | |
| `xurl reply` | Post create | $0.015/call | |
| `xurl whoami` | Owned user read | $0.001/call | Cheapest — works even at $0 balance |
| `xurl user` | User read | $0.010/call | |
| `xurl media upload` | Media upload | $0.005/call | |
| `xurl read` | Post read | $0.005/call | |
| `xurl mentions` | Owned mentions read | $0.001 × N results | Cheap |
| `xurl timeline` | Post reads | $0.005 × N results | |
| `xurl auth` | Auth check | $0.00/call | Free — no API cost |

### Pitfall: skill text in cron outputs inflates counts

Cron output files (under `~/.hermes/cron/output/<job_id>/`) contain the full prompt including skill text, which mentions `xurl post`, `xurl search`, etc. in examples. Grepping these files for `xurl post` will massively overcount because every file contains the skill text.

**Always query the session DB (`messages` table with `tool_calls` column) for actual terminal executions**, not the cron output files. The `tool_calls` column contains JSON with the actual commands the agent ran.

### Pitfall: `*/45` cron schedule is not "every 45 minutes"

In cron syntax, `*/45` in the minute field means "at minute 0 and 45 of every hour" — i.e. two fires per hour with a 15-min then 45-min gap, NOT every-45-minutes uniformly. For true every-N-minutes cadence, use the Hermes shorthand `every 45m` instead of raw cron `*/45`.

## Real cost data from Shivang's fleet (July 2026)

### New fleet (July 25-27, 3 days)

| Call type | Count | Cost |
|---|---|---|
| `xurl search` | 265 calls | $26.50 (worst case, no dedup) / $13.25 (with 50% dedup) |
| `xurl post` | 34 calls | $0.51 |
| `xurl whoami` | 24 calls | $0.02 |
| `xurl read` | 11 calls | $0.06 |
| `xurl media` | 11 calls | $0.06 |
| `xurl user` | 7 calls | $0.07 |
| `xurl quote` | 4 calls | $0.06 |
| `xurl auth` | 174 calls | $0.00 |
| **Total** | **538 calls** | **~$14-27** |

Search calls = **97% of total cost**.

### Old fleet (June 17-22, 5 days)

| Call type | Count | Cost |
|---|---|---|
| `xurl mentions` | 251 calls | $2.51 |
| `xurl search` | 42 calls | $4.20 |
| `xurl post` | 26 calls | $0.39 |
| `xurl read` | 26 calls | $0.13 |
| `xurl whoami` | 16 calls | $0.02 |
| **Total** | **739 calls** | **~$7** |

The old fleet was cheaper because it used `xurl mentions` (owned read at $0.001/resource) more than `xurl search` ($0.005/resource).

### Monthly projection

| Cadence | Monthly cost |
|---|---|
| 3 scanners at `every 30m` (current) | ~$140-273/month |
| 3 scanners at `every 2h` (recommended) | ~$40-60/month |
| 1 daily autopost only | ~$3-5/month |

## Cost optimization recommendations

1. **Reduce scanner cadence from 30m/45m to 2h** — saves ~75% of search costs
2. **Cache search results across scanners** — multiple scanners search the same keywords; share results within a cycle
3. **Use owned reads ($0.001) instead of search ($0.005/post)** for checking Shivang's own tweets
4. **Avoid `xurl post` with URLs** — Post: Create with URL costs $0.200 (13x more than without URL)
5. **Deposit $50-100** at a time to avoid running out mid-cycle

## Browser-based alternative: $0/month (July 2026)

X API credits depleted after ~$25-30 deposit. Instead of paying $140-273/month, switched to browser-based automation via Arc browser. The script `scripts/x_browser.py` drives Arc (where X.com is logged in) using AppleScript JavaScript execution. All operations are free.

### How it works
- Arc is Chromium-based and supports `osascript` JavaScript execution in its active tab.
- "Allow JavaScript from Apple Events" must be enabled in Arc's Developer menu.
- The script navigates to X.com pages, extracts tweet data from the DOM, and types/posts via `document.execCommand('insertText')`.

### Commands
```bash
python3 scripts/x_browser.py search "query" 20     # Search tweets (free)
python3 scripts/x_browser.py post "tweet text"      # Post a tweet (free)
python3 scripts/x_browser.py quote "URL" "text"     # Quote-tweet (free)
python3 scripts/x_browser.py reply "URL" "text"     # Reply (free)
python3 scripts/x_browser.py profile "@handle" 20   # Get user's tweets (free)
python3 scripts/x_browser.py timeline 20            # Home timeline (free)
python3 scripts/x_browser.py check                  # Verify login status
```

### When to use which
| Scenario | Use |
|---|---|
| Arc running, X.com logged in | `x_browser.py` (free) |
| Arc closed / X.com logged out | `xurl` API (paid, needs credits) |
| Need image attachment | `xurl media upload` (paid) — browser script doesn't support images yet |
| Need high-speed batch operations | `xurl` API (faster, <1s vs ~5-10s per browser op) |

### Limitations of browser approach
- Slower than API (~5-10s per operation vs <1s)
- No image attachment support yet
- Active tab is shared — don't navigate Arc while a cron job is running
- Arc must be running with X.com logged in (check with `x_browser.py check`)

### Finding which browser has X.com logged in

Chrome cookie decryption won't work if auth cookies are in a different browser. Check all browser profiles for `auth_token`, `ct0`, `twid`, `kdt` cookies:

```python
import sqlite3, os
# Check Chrome profiles
for profile in ['Default', 'Profile 1', ..., 'Profile 6']:
    db = os.path.join(chrome_base, profile, 'Cookies')
    # Query for auth_token, ct0, twid, kdt on x.com/twitter.com
# Also check Arc: ~/Library/Application Support/Arc/User Data/Default/Cookies
```

In Shivang's case, X.com was logged in on **Arc** (not Chrome). Arc had `auth_token`, `ct0`, `twid`, `kdt` cookies. Chrome only had `guest_id` cookies.

## Related references

- `references/x-tier-quota-recovery.md` — HTTP 429 tier-cap recovery (old subscription model)
- `references/x-developer-setup-and-policy.md` — OAuth setup, auth pitfalls, CreditsDepleted vs auth failure
- `references/twitter-growth-tactics.md` — competitive analysis of @cheatyyyy (quote-tweet amplification, screenshots, breaking-news speed)
- `scripts/x_browser.py` — browser-based X.com automation script (free alternative to xurl API)