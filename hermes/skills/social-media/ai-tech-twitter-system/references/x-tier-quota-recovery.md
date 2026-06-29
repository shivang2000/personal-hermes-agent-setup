# X API Tier-Quota Failure: Detection & Recovery

Use this reference when Shivang's X/Twitter autopost fleet starts hitting `HTTP 429: The usage limit has been reached`. The pattern has appeared in production more than once and is easy to misdiagnose as a per-job rate limit.

## Symptom signature

Multiple X-facing cron jobs (`post`, `reply`, `like`, `repost`, search-heavy reads) fail with the same error inside a narrow window — usually 30–60 minutes — even though `xurl whoami` still succeeds:

```text
RuntimeError: HTTP 429: The usage limit has been reached
```

Affected jobs in Shivang's setup so far:
- `cdd18a71e079` — AI engineering lessons daily autopost (`45 12 * * *`)
- `24fd916089e3` — AI engineering source-backed opportunity autopost scan (`every 45m`)
- `6be19c7edbdb` — Tech/AI/YC/YouTube news digest for #tech-news (`55 12,16,20,0 * * *`)
- `e9f85b48274e` — X reply autopilot (`every 5m`)

After this pattern fires once, all four jobs sit in `paused` state. `last_status: error` is permanent until manually resumed.

## Diagnosis commands

```bash
# List every job (active + paused) with last_status and last run
hermes cron list --all

# Confirm X auth itself still works (cheap endpoint)
xurl whoami

# Confirm 429 vs auth issue (writes vs reads)
xurl search "from:shivangchheda22" -n 1
```

If `whoami` works but `search` 429s, this is the tier-quota pattern, not an auth failure.

## Root cause

`every 5m` reply scanner alone can burn an X API monthly cap in well under 24 hours. Once the cap is hit, **every other X-facing job in the same profile stops working within minutes** because they share the same tier quota.

This is distinct from `CreditsDepleted`, which means the account has $0 balance. A 429 here means credits still exist but the tier-level monthly cap is hit.

## Recovery procedure

Do these steps in order; skipping cadence review tends to put the fleet back into paused state within hours.

1. **Audit cadence first.** Identify the highest-cadence job in the paused set. In Shivang's setup it is almost always the `every 5m` reply scanner. Move it to `every 30m` (or longer) **before** resuming anything. Even if the cap has reset, leaving `every 5m` in place guarantees another outage within a day.

2. **Top up the tier.** Developer Console → Products → Pro/Basic → Usage, or Developer Console → Billing → add credits. Verify with `xurl post` against an approved draft, or `xurl search -n 1`.

3. **Resume one job at a time.** Start with the lowest-cadence one (the daily post). Verify `last_status: ok` before resuming the next. If a resumed job immediately re-429s, pause it and re-check credits/cadence — something is still wrong.

```bash
# Resume
hermes cron resume cdd18a71e079

# Watch for next run
hermes cron list --all | grep -A 2 cdd18a71e079
```

4. **Verify fleet health.** Wait for one full cycle of each resumed job. Do not declare the workflow healthy until at least one run of each cadence has returned `last_status: ok`.

## Cadence recommendations for Shivang's setup

| Job type | Unsafe | Default | Notes |
| --- | --- | --- | --- |
| Reply scanner | `every 5m` | `every 30m` | A reply scanner at `every 5m` is the most common quota bomb |
| Opportunity/source scan | `every 15m` | `every 45m` to `every 2h` | Most scans have nothing genuinely fresh; longer cadence + `[SILENT]` works better |
| News digest | every <2h | `every 4h` (e.g. `55 12,16,20,0`) | Europe + US coverage without burning quota |
| Daily approval queue | multiple per day | 1/day at the start of the active window | Already correct in Shivang's setup |

Anything at `every 5m` or `every 10m` for X-facing jobs should be treated as a quota bomb unless Shivang explicitly approves it for a short, time-boxed campaign.

## Cross-profile note

The `office-work-summary-for-tweets` cron (`81a56cfa2830`) is owned by Shivang's office-laptop/work-agent profile. It delivers a safe local work-signal digest into `#tweets-automation` for tweet-drafting material — **it is not an autopost job** and does not post on its own.

When the personal-Hermes bot (this profile, `default`) receives one of these digests:
- It is a passive data drop, not a request to act.
- The bot cannot `resume` or edit jobs owned by another profile.
- It can surface downstream issues the digest reveals (like a paused autopost fleet), since those jobs usually belong to this profile.
- Paginated digests (`(1/6)` etc.) should not be drafted-from until the full set lands.

## Related references

- `references/x-developer-setup-and-policy.md` — OAuth setup, `xurl auth status` interpretation, `CreditsDepleted` vs `HTTP 429` distinction.
- `references/local-work-summary-cron.md` — proven job shape for the office-work-summary digest cron.