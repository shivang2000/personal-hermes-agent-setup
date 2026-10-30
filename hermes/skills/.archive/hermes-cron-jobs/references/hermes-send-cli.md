# `hermes send` CLI reference

The `hermes send` command lets any script, agent, or cron job deliver a
message to any messaging platform Hermes is already configured for. It
reuses the gateway's platform credentials (`~/.hermes/.env` +
`~/.hermes/config.yaml`) — no separate auth, no running gateway
required for bot-token platforms like Discord/Telegram/Slack/Signal.

Verified 2026-07-12 against a Discord-targeted run.

## Synopsis

```
hermes send [-h] [-t TARGET] [-f PATH] [-s LINE] [-l] [-q] [--json] [message]
```

Positional `message` is the message body. If omitted, read from `--file`
or stdin.

## Flags

| Flag | Effect |
|---|---|
| `-t TARGET` / `--to TARGET` | Delivery target. Format: `platform` (home channel), `platform:chat_id`, `platform:chat_id:thread_id`, or `platform:#channel-name`. |
| `-f PATH` / `--file PATH` | Read message body from PATH (text only). Use `-` to force stdin. For images/documents, use `MEDIA:<path>` in the message text instead. |
| `-s LINE` / `--subject LINE` | Prepend a subject/header line before the message body. |
| `-l` / `--list` | List available targets. Optional filter: `hermes send --list telegram`. |
| `-q` / `--quiet` | Suppress stdout on success (exit code only). |
| `--json` | Emit raw JSON result instead of human-readable. |

## Examples (verified 2026-07-12)

```bash
# Inline message to a Discord thread (positional message arg)
hermes send -t discord:1525706622238724109 "Bot restarted"

# Multi-line markdown from a file (preferred for log digests)
hermes send -t discord:1525706622238724109 -f /tmp/digest.md

# By channel name (no thread, posts to parent channel)
hermes send -t discord:#trading-bot "Hourly digest ready"

# Pipe from stdin
echo "Heartbeat OK" | hermes send -t telegram:-1001234567890

# With subject header (useful for ALERT: prefixes)
hermes send -t discord:#ops -s "ALERT" "Disk usage at 92%"

# Quiet (exit code only, no stdout leak in logs)
hermes send -t discord:1525706622238724109 -q "Heartbeat OK" && echo "sent"

# Send a media file (image/attachment)
hermes send -t discord:1525706622238724109 "MEDIA:/Users/me/screenshot.png"
```

## Common pitfalls

- **`--to` is not a flag.** The flag is `-t` / `--to`. `--to "..."` is
  accepted as `--to` shorthand, but **`--message` is rejected** — the
  message is positional, not a flag. `hermes send -t X --message "Y"`
  returns `unrecognized arguments: --message`.
- **Thread ID, not message ID.** When the user replies, the
  conversation context block shows a "Triggering message id" — that's
  the message's snowflake, not a channel. Extract the thread ID from
  `discord_threads.json` or the channel's `last_thread_id` metadata.
  Sending to a message ID returns `Unknown Channel (404)`.
- **Discord parent channel ID alone is wrong if you want a thread.**
  Use `discord:<thread_id>` and Hermes auto-resolves the parent. Using
  the parent channel ID with a separate thread ID field is rejected.
- **`-f PATH` is the right choice for multi-line / markdown.** Inline
  positional messages work but quoting in bash is fragile. Always prefer
  writing the body to a tempfile and using `-f`.

## Per-platform quick refs

### Discord

- `discord:#channel-name` — resolve by name (Hermes looks up the ID)
- `discord:<channel_id>` — resolve by ID
- `discord:<thread_id>` — posts into a thread, auto-resolves parent
- `discord:<chat_id>:<thread_id>` — explicit chat+thread (rare)
- Discord threads opened by auto-thread (`discord.auto_thread: true`,
  the default) each get their own session — see `hermes-gateway-platforms`
  for context-loss debugging.

### Telegram

- `telegram` — home channel (whatever `TELEGRAM_HOME_CHANNEL` is)
- `telegram:<chat_id>` — by chat ID (negative for groups, positive for
  DMs). `telegram:-1001234567890:17585` includes a topic/thread ID for
  supergroups with topics enabled.

### Slack

- `slack:<channel_id>` — by channel ID (e.g. `slack:C0123ABCD`). Slack
  threads are a different target format; check the gateway docs.

### Signal

- `signal:<phone>` — by phone number, e.g. `signal:+15551234567`. Note
  the E.164 format with `+`.

## Exit codes

- `0` — message delivered (with `-q`, stdout suppressed; without, prints
  `sent`)
- Non-zero — delivery failed. With `--json`, the response is a JSON
  object with `error` details. Without, the error message is on stderr.

## See also

- `hermes send --list` to see what's currently configured
- `hermes send --list <platform>` to filter by platform
- `references/discord-without-telegram.md` in `hermes-gateway-platforms`
  for Discord credential setup
- `references/discord-session-keys.md` in `hermes-gateway-platforms`
  for why auto-thread creates new sessions (relevant when the user
  says "the bot forgot context in this thread")
