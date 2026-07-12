# Hourly log-digest cron pattern (for any log-emitting long-running service)

A reusable pattern for catching warnings/errors/restarts/lifecycle events from
a log file emitted by a long-running process (Docker container, systemd
service, remote box). Pure Python, no LLM in the loop, no model cost per
tick, deterministic output, surfaces in Discord within the hour.

When to use: any service that writes a log file and where the user wants
"is it still running and did anything bad happen since the last hour"
visibility without tailing logs manually. Examples from real deploys:
the trading bot (`logs/trading.log` on EC2), the personal-website envoy
(`envoy` access log), a long-running batch job, a systemd service.

## Why pure Python, not an LLM-driven cron job

LLM-driven crons (`no_agent: false` + `prompt`) are the right tool for
"go do research and summarize" tasks. They're the wrong tool for
"read a file, classify lines, emit markdown": every tick burns input
tokens on the whole file, output tokens on the summary, and adds
latency (5-30s) for a job that should be near-instant. Worse, the
model's classification is non-deterministic — the same log might be
categorized differently hour to hour.

The pattern below:
- Script does the parsing in pure Python (deterministic, <2s runtime, $0)
- Cron job is `no_agent: true` + `script=...` (the script IS the job)
- The script's stdout IS the Discord message (no model rewording)

## Working script (trading bot, 2026-07-12)

`/Users/shivang/.hermes/scripts/trading_bot_hourly_digest.py` — full
source. Key design decisions:

1. **Timestamp-windowed, not byte-offset.** Filter to `now - 75m` based on
   parsed timestamps. Survives log rotation, container restarts, and
   `tail -n 4000` truncation. The 75m window is 25% overlap with the
   60m cadence so we never miss an event at the window boundary.
2. **Most-recent-state wins for the health pulse.** If a "started" and
   "stopped" both appear in the window, use whichever is later — not
   "did the word 'started' appear anywhere". This is the most common
   bug in log-digest scripts.
3. **Explicit log-lag warning.** Compute `wall_clock - last_log_line`
   and surface it in the message if > 5 min. Python `FileHandler` is
   block-buffered on non-TTY processes (Docker), so the log file
   can lag the actual service state. The warning prevents the user
   from reading too much into "no events recently".
4. **Categorize by source module + message keywords.** Don't try to be
   clever — the bot's log lines have well-defined formats and the
   bucket logic is `if "X" in msg: category = "X"`. See the
   `classify()` function for the full taxonomy.
5. **Discord length safety.** Drop the trailing source/cron footer
   first (least useful), then truncate at line boundaries if still
   over 1900 chars. Never blindly slice at char 1900 (cuts messages
   mid-word).

## Cron job (the `no_agent: true` schema, verified 2026-07-12)

The CLI accepts both `prompt` and `script` — they're mutually exclusive.
For `no_agent: true` you MUST pass `script` (and `prompt` is ignored):

```bash
cronjob create \
  --name "Hourly <service> log digest" \
  --schedule "5 * * * *" \
  --no_agent true \
  --script "trading_bot_hourly_digest.py" \
  --model "minimax-m3" \
  --provider "ollama-cloud" \
  --deliver "discord:<channel_id>" \
  --enabled_toolsets terminal
```

Pitfall: the error message is `create with no_agent=True requires a
script — the script is the job` if you pass `prompt` and forget
`script`. The reverse (`script` with `no_agent: false`) is also
rejected.

Pitfall: `--schedule` accepts both cron expressions (`"5 * * * *"`)
and relative forms (`"every 60m"`). Use the cron form when you want
sub-hourly precision.

Pitfall: when delivery is to a Discord thread (not the parent channel),
the `deliver` format is `discord:<thread_id>` — Hermes resolves the
parent channel automatically. For the parent channel itself, use
`discord:#channel-name` (verified) or `discord:<channel_id>`.

## Delivery header wrap (verified 2026-07-12)

When the cron job delivers to Discord, the message arrives wrapped in
a "Cronjob Response: <job name> (job_id: <id>)" header. The script's
stdout appears below it. This is intentional — the header lets the
user identify and manage the job by name ("stop reminder Hourly
trading bot log digest (EC2)"). If you want the message shorter, the
header can't be disabled.

## What to monitor vs. what to ignore

- **Always include in the digest**: `CRITICAL`, `FATAL`, `ERROR`,
  `WARNING` (filter out known-noise like "Telegram not configured"
  for services that intentionally don't use Telegram — keep a small
  set of known-noisy message patterns to strip).
- **Surface lifecycle explicitly**: started / stopped / connected /
  disconnected / restarted. These are the most useful signals for
  "is the service actually running?".
- **Compress noisy repeated events**: if the same "MT5 connect attempt
  N/12 failed" appears 12 times in a row, count them ("12 attempts in
  3 min") and show 1-2 samples. Don't flood Discord.
- **Skip pure debug noise**: "scan loop starting", "heartbeat",
  "position 0" — these are normal operation. Only surface if there's
  a sudden change (e.g. "scans stopped" after a crash).

## Verification before declaring the cron done

1. `python3 /Users/shivang/.hermes/scripts/<script>.py` exits 0
   locally and emits the expected markdown.
2. `cronjob list` shows the job with `state: scheduled` and a future
   `next_run_at`.
3. `cronjob run <job_id>` delivers a message to the target channel
   (manual test, no need to wait for the scheduled tick).
4. The delivered message in Discord is well-formatted (no escaped
   backticks, no broken markdown, no truncation artifacts).

## Reusing this pattern for other services

To adapt the script for a new service:
1. Update `LINE_RE` to match the new log format
2. Update `classify()` keywords to the new service's modules/levels
3. Update `PEM` / `EC2_HOST` / `LOG_PATH` constants
4. Test once locally
5. `cronjob create` with a new `--script` and `--deliver`
