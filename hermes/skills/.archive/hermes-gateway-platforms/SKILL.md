---
name: hermes-gateway-platforms
description: "Configure Hermes messaging gateway platforms/channels safely — enabling Discord/Slack/etc., disabling unwanted platforms, handling credentials without exposing secrets, and verifying gateway service state."
version: 1.0.0
metadata:
  hermes:
    tags: [hermes, gateway, messaging, discord, telegram, config, credentials]
    related_skills: [hermes-agent, hermes-durable-services]
---

# Hermes Gateway Platform Configuration

## When to use this skill

Load this skill when the user asks to:

- set up Hermes messaging channels/platforms such as Discord, Telegram, Slack, WhatsApp, Signal, etc.
- switch from one gateway platform to another, e.g. “use Discord and not Telegram”
- disable a platform that is still connecting because old credentials remain configured
- verify the Hermes gateway service after platform config changes
- inspect platform configuration without printing tokens or secrets

This skill complements `hermes-agent`: use the official docs and `hermes gateway setup` as source of truth, but use this workflow to avoid credential leakage and platform re-enable surprises.

## Core workflow

1. **Load Hermes docs context first.** For Hermes itself, `hermes-agent` remains authoritative; check current docs if commands differ.
2. **Inspect non-secret state.** Read/summarize:
   - `~/.hermes/config.yaml` platform enable flags (`platforms.<platform>.enabled`)
   - whether related `.env` keys are present, but never their values
   - `hermes gateway status` for service/staleness state
3. **Set platform flags in config.** Prefer CLI config setters over manual YAML edits when possible:

   ```bash
   hermes config set platforms.discord.enabled true
   hermes config set platforms.telegram.enabled false
   ```

4. **Handle credentials separately and safely.** Bot tokens are secrets. Do not ask the user to paste tokens into chat, and do not type them yourself. Ask the user to run `hermes gateway setup`, or provide local shell commands they can run on their machine.
5. **Remove or comment stale credentials for platforms the user no longer wants.** Some platform adapters are also controlled by env vars. Before declaring a platform disabled, verify there are no active `.env` entries such as `TELEGRAM_BOT_TOKEN` or `TELEGRAM_ALLOWED_USERS` that could confuse future gateway runs or setup flows. Back up `.env` first, then comment obsolete platform keys.
6. **Restart/refresh the gateway.** After credentials and config change:

   ```bash
   hermes gateway start
   # or: hermes gateway restart
   hermes gateway status
   ```

   If `hermes gateway status` says the LaunchAgent/systemd service definition is stale, `hermes gateway start` is the preferred refresh command.
7. **Verify without secrets.** Report:
   - platform enable flags
   - presence/absence of required credential keys
   - gateway service status
   - any remaining user action, e.g. “Discord token missing; run setup locally.”

## Discord setup checklist

For Discord, the user must configure at least:

- `DISCORD_BOT_TOKEN` — bot token from Discord Developer Portal
- either `DISCORD_ALLOWED_USERS` or `DISCORD_ALLOWED_ROLES` — authorization gate

Recommended local setup path:

```bash
hermes gateway setup
```

Select **Discord**, then enter the bot token and numeric Discord user ID / role IDs locally.

Operational notes:

- DMs respond without `@mention`.
- Server channels require `@mention` by default unless `discord.free_response_channels` or `DISCORD_FREE_RESPONSE_CHANNELS` is configured.
- Discord bots need Message Content Intent enabled in the Discord Developer Portal for normal message handling.

### Bot-to-bot / multi-Hermes Discord coordination

When one Hermes Discord bot needs to trigger another Hermes Discord bot in the same server (for example personal-laptop Hermes coordinating with office-laptop Hermes), plain text such as the visible bot name `hermes-work-agent` may not create a real Discord mention. Use the bot's numeric user ID mention form and verify Discord resolved it in the sent message's `mentions` list if debugging through the REST API.

Known Discord bot mention tokens for Shivang's current setup:

- Office Hermes / `hermes-work-agent`: `<@1516899802913308733>`
- Personal Hermes / this bot: `<@1516782563757133964>`

Important pitfall: Hermes Discord ignores messages from other bots by default (`DISCORD_ALLOW_BOTS=none`). On the receiving Hermes gateway, set:

```bash
DISCORD_ALLOW_BOTS=mentions
hermes gateway restart
```

This allows bot-authored messages only when they explicitly mention the receiving bot. If sending via Discord REST instead of the gateway, include `allowed_mentions: {"users": ["BOT_USER_ID"], "parse": []}` so Discord actually pings/resolves the target bot while avoiding broad mention parsing. Also check whether the receiving gateway is online; if its last visible message says the gateway is shutting down, no mention format will trigger it until restarted.

## Disabling Telegram cleanly

To stop using Telegram:

```bash
hermes config set platforms.telegram.enabled false
```

Then inspect `.env` for active Telegram keys and comment/remove them after taking a backup:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_ALLOWED_USERS`
- `TELEGRAM_HOME_CHANNEL`
- `TELEGRAM_HOME_CHANNEL_NAME`
- `TELEGRAM_HOME_CHANNEL_THREAD_ID`

Do not print token values while doing this. It is enough to report `<set>`/`<empty>`/`active=REDACTED_SET_LOCALLY

## Safe inspection snippets

Use snippets that redact values and only show key presence. Example pattern:

```bash
python3 - <<'PY'
from pathlib import Path
p = Path.home() / '.hermes' / '.env'
text = p.read_text(errors='replace') if p.exists() else ''
for key in ['DISCORD_BOT_TOKEN','DISCORD_ALLOWED_USERS','TELEGRAM_BOT_TOKEN']:
    active = commented = False
    for line in text.splitlines():
        s = line.strip()
        if not s or '=' not in s:
            continue
        k = s.lstrip('#').split('=', 1)[0].strip()
        if k == key:
            if s.startswith('#'):
                commented = True
            else:
                active = True
    print(f'{key}: active={active} commented={commented}')
PY
```

## Discord session management: auto-thread and context loss

When `discord.auto_thread: true` (the default), Hermes creates a **new Discord thread** for every @mention in a text channel. Each thread gets its own session key. This means:

- If the user @mentions the bot in the parent channel repeatedly, each mention creates a **new thread = new session = fresh context**. The user experiences apparent memory loss between messages.
- Messages sent **inside** an existing thread do NOT re-trigger auto-threading — they continue the same session.

Session key structure:
- Thread: `agent:main:discord:thread:<thread_id>` (shared across participants by default)
- Group: `agent:main:discord:group:<channel_id>` (no thread, single session for channel)
- DM: `agent:main:discord:dm:<chat_id>`

### Fixing context loss in Discord

Symptom: User reports "the bot forgets everything" or "context resets between messages" in a Discord channel.

Diagnosis steps:
1. Check `discord.auto_thread` in `~/.hermes/config.yaml` — if `true`, auto-threading is creating new threads.
2. Check `discord_threads.json` in `~/.hermes/` — a growing list of thread IDs confirms auto-threading is active.
3. Ask the user: are they sending new @mentions in the parent channel, or continuing inside the existing thread?

Solutions (pick one):

**Option A — disable auto-thread** (recommended for single-channel-per-topic setups):
```bash
hermes config set discord.auto_thread false
hermes gateway restart
```
Now all messages in a channel share one session. Messages in the channel use `require_mention` to gate responses.

**Option B — keep auto-thread, continue inside threads** (recommended for multi-topic channels):
Keep `auto_thread: true` but instruct the user to type follow-up messages **inside the thread**, not re-mention in the parent channel. Set `discord.thread_require_mention: false` so the bot responds to any message inside the thread without needing @mention.

**Option C — per-user thread isolation** (multi-user channels):
```bash
hermes config set discord.thread_sessions_per_user true
hermes gateway restart
```
Each user gets their own session within a thread. Without this, all thread participants share one session.

### Session reset policy interaction

Even with auto-thread disabled, sessions can reset based on `session_reset` policy:
- `mode: idle` — resets after `idle_minutes` of inactivity (default 1440 = 24h)
- `mode: daily` — resets at `at_hour` (default 4am)
- `mode: none` — never auto-resets (your current setting)

Check current policy:
```bash
grep -A3 'session_reset' ~/.hermes/config.yaml
```

## Provider rate-limit exhaustion — the "silent context loss" mimic

When a provider hits its usage cap (HTTP 429 `usage_limit_reached`), the agent cannot call the LLM at all. Messages may appear to "lose context" or produce empty/garbage responses because the model call fails entirely. This is especially dangerous when no `fallback_model` is configured — the gateway has no backup and the user just sees the bot stop working.

### Diagnosis

Check gateway logs for 429 errors:

```bash
grep -i "429\|RateLimitError\|usage_limit\|overload" ~/.hermes/logs/gateway.log | tail -20
```

Look for patterns like:
```
⚠️  API call failed (attempt 1/3): RateLimitError [HTTP 429]
   🔌 Provider: openai-codex  Model: gpt-5.5
   📝 Error: HTTP 429: The usage limit has been reached
   📋 Details: {'type': 'usage_limit_reached', ...}
```

Also check which model the sessions are actually using vs. your config:

```bash
sqlite3 ~/.hermes/state.db "SELECT DISTINCT model FROM sessions WHERE source LIKE 'discord%';"
```

If this shows a different model than `model.default`, there may be a per-route or per-session override in play.

### Fix

**Option A — configure a fallback model** (recommended for always-on gateways):

```bash
hermes config set fallback_model.provider openrouter
hermes config set fallback_model.model <your-openrouter-model>
hermes gateway restart
```

The fallback triggers on 429, 529, 503, and connection failures. Check current state:

```bash
grep -A5 "# ── Fallback Model" ~/.hermes/config.yaml
```

If the section is commented out, no fallback is active.

**Option B — wait for the rate limit to reset.**

The 429 response includes `resets_in_seconds`. For OpenAI Codex, this can be hours or days depending on plan.

**Option C — switch the primary model** to a provider with available quota:

```bash
hermes config set model.default openrouter/<model>
hermes config set model.provider openrouter
hermes gateway restart
```

### Why this looks like context loss

From the user's perspective, the bot was working, then suddenly "forgets" everything or stops responding. The actual cause is that the LLM API is unreachable — the agent cannot process any input at all, so it either returns stale/cached text or fails silently. The session transcript in `state.db` is intact; the issue is purely upstream.

## Pitfalls

- **Do not handle bot tokens in chat.** Have the user enter secrets locally via `hermes gateway setup` or their editor.
- **Config flags are not the whole story.** Env vars in `.env` can still affect platform setup and connection behavior; always inspect credential-key presence.
- **Do not claim Discord is working until credentials exist and gateway status/logs confirm it.** Enabling `platforms.discord.enabled` only prepares the platform.
- **Service state matters.** A gateway LaunchAgent/systemd service can be loaded but stale relative to the current install. Refresh with `hermes gateway start` before final verification.
- **Back up `.env` before modifying credential lines.** Commenting stale platform keys is safer than deleting them when the user might want to restore them.
- **auto_thread context loss is the #1 Discord confusion.** Before debugging anything else, check `discord.auto_thread` and whether the user is re-mentioning in the parent channel vs. continuing inside the thread.
- **Rate-limit 429s are the #1 "sudden amnesia" mimic on always-on gateways.** When a provider exhausts its quota, the agent cannot call the LLM at all. Always check `gateway.log` for 429 errors before assuming a session management bug. Configure `fallback_model` to prevent recurrence.

## Delivering messages from agents/scripts (the `hermes send` CLI)

The gateway platform setup above is for the *gateway* (the long-running
service that listens for incoming messages and replies). The
**outbound** side — sending a message from an agent, script, or cron —
is the `hermes send` CLI. It reuses the same platform credentials and
works without a running gateway for bot-token platforms like Discord.

Full flag reference and worked examples in
`~/.hermes/skills/devops/hermes-cron-jobs/references/hermes-send-cli.md`.
Key shapes:

```bash
hermes send -t discord:<thread_id> "message"        # thread (auto-resolves parent)
hermes send -t discord:#channel-name "message"       # parent channel by name
hermes send -t discord:<chat_id>:<thread_id> "msg"   # explicit chat+thread (rare)
hermes send -t discord:<thread_id> -f /tmp/msg.md   # multi-line markdown from file
hermes send --list discord                          # see available channels/threads
```

Common mistakes to avoid (full list in the reference):
- `--message` is rejected — message is positional, not a flag.
- Sending to a *message* ID (snowflake) returns 404 — extract the
  thread ID from the `discord_threads.json` or the channel metadata.
- For multi-line markdown, use `-f PATH` not inline; bash quoting
  is fragile.
- Media (images, audio) goes inline as `MEDIA:/absolute/path`.

## References

- `references/discord-without-telegram.md` — concrete migration recipe for enabling Discord while disabling Telegram without exposing secrets.
- `references/discord-session-keys.md` — how Discord session keys are constructed, why auto-thread causes apparent context loss, and how to debug session state.
- `~/.hermes/skills/devops/hermes-cron-jobs/references/hermes-send-cli.md` — full `hermes send` CLI reference (flags, target formats, common pitfalls, per-platform notes).

- `references/discord-without-telegram.md` — concrete migration recipe for enabling Discord while disabling Telegram without exposing secrets.
- `references/discord-session-keys.md` — how Discord session keys are constructed, why auto-thread causes apparent context loss, and how to debug session state.
