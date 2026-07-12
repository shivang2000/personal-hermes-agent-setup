# 5-minute health-watchdog cron pattern (for any dockerized service)

A reusable pattern for proactive health monitoring of any dockerized
service: silent on success, alerts to Discord only when something's
wrong, auto-remediates safe failures (container restart), and
auto-alerts on unsafe ones (anything that would lose user state).

When to use: any production service where silent failure is worse
than noisy alerts. Examples from real deploys: the trading bot
(`trading-bot-v2` on EC2), a long-running model server, a database
container that should be up 24/7, an internal API. Pair it with the
hourly log-digest pattern in `references/hourly-digest-pattern.md`
for full coverage: digest tells you what happened in the last hour,
watchdog tells you about the next failure within 5 minutes.

## Why this complements (not replaces) the hourly log digest

| Cron | Cadence | Goal | Output |
|---|---|---|---|
| `trading_bot_hourly_digest` | 60m | "What happened in the last hour?" | Always emits a summary; quiet when green |
| `trading_bot_watchdog` | 5m | "Is something broken RIGHT NOW?" | Silent when green; alerts only on failure |

The digest is for trend analysis (restart counts, error rates over time,
strategy health trends). The watchdog is for paging the operator on
events that need attention within minutes, not hours (container death,
OOM pressure, new CRITICAL log lines).

## The four checks (running script: `trading_bot_watchdog.py`)

```python
def check_containers() -> list[str]:
    """Both containers running? Auto-restart the safe one (the bot).
    Never auto-restart the MT5 container — would lose the noVNC login."""

def check_memory() -> list[str]:
    """free < 150Mi AND swap > 85%? Alert (OOM imminent).
    Low free is normal if swap is absorbing it — only fire when both signals trigger."""

def check_log_fatals() -> list[str]:
    """Track byte offset of last-seen log. Alert on any new [CRITICAL] / [FATAL] line."""

def main() -> int:
    problems = check_containers() + check_memory() + check_log_fatals()
    if not problems:
        return 0   # silent success — cron sees no output
    emit_discord(format_alert(problems))
    return 0
```

## Critical design decisions (each one is a real pitfall)

### 1. Silent on success, NOT periodic

`main()` returns 0 with no stdout when everything is green. The cron
sees no output and considers the run successful. **This is the
opposite of the hourly digest, which always emits a summary.** Why:
the digest is for the user to read on a schedule; the watchdog is for
paging the operator. If the watchdog posts every 5 minutes saying
"all green", Discord gets spammed 288 times a day with nothing. The
`deliver: local` cron setting (vs `deliver: discord:...`) is the
cleanest way to express this: the script's stdout goes to a local log
file (silent), and the script itself calls `hermes send` only when
it has something to say.

### 2. Auto-remediate ONLY when safe

The bot container is safe to auto-restart — it's stateless (the DB
is on a bind-mount, the MT5 session is owned by the other container,
config comes from .env). The MT5 container is NOT safe to auto-restart
because restarting kills the noVNC session, forcing a manual re-login
through the web UI. The watchdog's auto-remediate path is split:

```python
if any(BOT_CONTAINER in p for p in problems):
    ssh(f"cd /home/ec2-user/trading-bot-v2 && "
        f"docker-compose -f docker-compose.ec2.yml up -d {BOT_CONTAINER}")
    # MT5 problems: alert only, never auto-restart
```

**Rule of thumb:** if auto-remediation would lose user state, alert
only. If it just re-runs the process and the process is stateless,
auto-remediate.

### 3. Offset-based state file (so we don't re-alert)

`/tmp/bot_watchdog.state` on the EC2 box holds the byte offset of the
last log line we examined. Next run: read only `[offset+1, end]`. If
any of those bytes contain a new CRITICAL line, alert and advance
the offset. This is critical because:

- The bot writes ~1000+ lines/day even in normal operation
- Without offset tracking, every 5-min run would re-process the
  whole log and re-alert on the same historical CRITICALs
- Offset survives container restarts (it's on the EC2 host's `/tmp`,
  not inside the container)

```python
state = load_state()                              # /tmp/bot_watchdog.state on EC2
last_offset = int(state.get("bot_log_offset", "0"))
cur_size = ssh_wc_c(log_path)
if cur_size > last_offset:
    new_content = ssh_tail(log_path, last_offset + 1)
    for line in new_content.splitlines():
        if "[CRITICAL" in line or "[FATAL" in line:
            problems.append(line)
    state["bot_log_offset"] = str(cur_size)
    save_state(state)
```

**Pitfall — log rotation breaks this.** If the log gets rotated
(typical: `trading.log` → `trading.log.1` + fresh `trading.log`),
`cur_size < last_offset` and we should reset the offset. The watchdog
handles this with `if cur_size <= last_offset: return []` (no new
content detected — could be rotation or just no activity; the next
run after rotation will see the new file and start reading from 0,
but the offset is still pointing at the old file. Better: also store
the inode or file mtime, and reset the offset if either changes.

**Pitfall — first run after a state-file reset.** The state file
starts at `bot_log_offset=0`, so the first run reads the ENTIRE log
file from the beginning. If the log has 400+ lines of historical
CRITICAL events, the first cron run will fire a giant alert with
all of them. To prevent this, pre-populate the state file with
`bot_log_offset=$(wc -c < log_path)` at deploy time.

### 4. Substring detection must handle level padding

Python's `logging.Formatter` pads level names to 8 characters. So
`[CRITICAL]` becomes `[CRITICAL ]` (with trailing space) in the log.
`[FATAL]` (5 chars) becomes `[FATAL  ]` (7 trailing spaces). The
substring `"[CRITICAL]"` (with closing bracket) does NOT match either
of these. Use `"[CRITICAL"` (no closing bracket) and `"[FATAL"` (no
closing bracket) to catch both. Pitfall I hit: `"[CRITICAL] in line`
returned `False` for an actually-critical line, and the watchdog
silently swallowed the alert.

```python
# WRONG (matches neither [CRITICAL] nor [CRITICAL ])
if "[CRITICAL]" in line:
    ...

# RIGHT (matches both [CRITICAL] and [CRITICAL ])
if "[CRITICAL" in line:
    ...
```

### 5. The "no output" silent success vs the "always-emit" digest

The hourly digest is for the user to *read* on a schedule. The
watchdog is for *paging* the operator on failure. Different goals →
different output contracts:

- **Digest:** always emits. Even on success: "🟢 Bot up · 🟢 MT5
  connected · no new warnings" is useful (confirms the cron ran).
- **Watchdog:** emits only on failure. Even one "all green" line per
  5 minutes = 288 messages/day of noise. The right way to express this
  in a Hermes cron is `deliver: local` + the script calls
  `hermes send` itself only when it has problems.

If you accidentally use `deliver: discord:...` with a silent-on-success
script, the cron job's wrapper still shows up in Discord ("Cronjob
Response: ..." header) but with no body. Worse than no alert — looks
like a broken cron. Use `deliver: local`.

## Cron job schema (verified 2026-07-12)

```bash
cronjob create \
  --name "Trading bot health watchdog (5m)" \
  --schedule "*/5 * * * *" \
  --no_agent true \
  --script "trading_bot_watchdog.py" \
  --model "minimax-m3" \
  --provider "ollama-cloud" \
  --deliver "local" \
  --enabled_toolsets terminal
```

`deliver: local` is the key — it tells the cron to NOT auto-post to
Discord, leaving that decision to the script. The script's stdout
goes to `~/.hermes/cron/output/<job_id>/...` for debugging. The
script's internal `emit_discord()` call is what actually posts to
Discord when there's a problem.

## Testing the watchdog end-to-end (without breaking prod)

Inject a fake CRITICAL into the log, reset the state file's offset to
just-before-the-injection, run the script, verify it fires a Discord
alert, then clean up. The whole cycle takes ~30 seconds:

```bash
# 1. Reset state to "I've read up to N bytes"
ssh ec2-user@<ec2> 'printf "bot_log_offset=0\n" > /tmp/bot_watchdog.state'

# 2. Inject a fake CRITICAL
ssh ec2-user@<ec2> 'echo "2026-07-12 12:00:00 [CRITICAL ] __main__   FAKE TEST: this should trigger the alert" \
  >> /home/ec2-user/trading-bot-v2/logs/trading.log'

# 3. Run the watchdog — should fire to Discord
python3 /Users/shivang/.hermes/scripts/trading_bot_watchdog.py

# 4. Verify Discord got the alert
# (check #trading-bot or whichever channel)

# 5. Clean up
ssh ec2-user@<ec2> 'sed -i "/FAKE TEST/d" /home/ec2-user/trading-bot-v2/logs/trading.log'

# 6. Reset state to current end-of-log so the next real cron run
#    doesn't re-fire on historical CRITICALs
ssh ec2-user@<ec2> 'CUR=$(wc -c < /home/ec2-user/trading-bot-v2/logs/trading.log); \
  printf "bot_log_offset=%d\n" "$CUR" > /tmp/bot_watchdog.state'
```

**Pitfall — the state advances even on no-alert runs.** `check_log_fatals`
calls `save_state` before returning. If you run the watchdog
multiple times during testing, each run advances the offset, so
your injected line at offset N will only be detected on the FIRST
run. If the watchdog says "no fatals" but you expected it to fire,
the state may have already advanced past the injection. Always
reset the state file before re-injecting.

## Reusing this pattern for other services

To adapt for a new service:
1. Update `BOT_CONTAINER` / `MT5_CONTAINER` to your container names
2. Update `check_containers` auto-restart logic to match which
   containers are safe to bounce
3. Update `check_log_fatals` keywords to your log format
   (and check your log's level padding — different frameworks
   may pad differently)
4. Update the cron schedule (`*/5` is right for trading; `*/1`
   may be too noisy for less critical services; `*/15` for
   background services)
5. Pre-populate the state file at deploy time with the current
   log size to avoid first-run historical-fire

## Production-readiness checklist

- [ ] State file location is on the host filesystem (not in any
      container) so container restarts don't lose the offset
- [ ] The "safe to auto-restart" set is conservative — better to
      alert and let a human decide than to auto-remediate wrongly
- [ ] First deploy pre-populates the state file offset to current
      log size
- [ ] Log rotation handling: store file inode or mtime alongside
      offset; reset offset on either change
- [ ] Tested with synthetic CRITICAL injection (the cycle above)
- [ ] Discord delivery tested manually with `cronjob run <job_id>`
- [ ] Cron schedule doesn't collide with the hourly digest (offset
      to a different minute to avoid the :05 overlap if you have
      `5 * * * *` for the digest)
