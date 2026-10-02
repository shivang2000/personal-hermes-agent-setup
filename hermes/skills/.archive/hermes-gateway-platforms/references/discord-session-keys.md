# Discord Session Key Construction

How Hermes builds session keys for Discord messages, and why context appears to "reset".

## Key construction rules

Source: `gateway/session.py` → `build_session_key()`

```
{namespace}:{platform}:{chat_type}:{chat_id}:{thread_id}:{user_id?}
```

- `namespace` — defaults to `agent:main` (or profile-specific for multiplexing)
- `platform` — `discord`
- `chat_type` — `dm`, `thread`, or `group`
- `chat_id` — Discord channel/thread ID (snowflake)
- `thread_id` — Discord thread ID when inside a thread
- `user_id` — Discord user ID (only when `group_sessions_per_user=true` or `thread_sessions_per_user=true`)

## Thread session behavior

| Config | Session key | Effect |
|--------|-------------|--------|
| `auto_thread: false` | `agent:main:discord:group:<channel_id>` | All messages in channel share one session |
| `auto_thread: true` (default) | `agent:main:discord:thread:<thread_id>` | Each thread = separate session |
| `thread_sessions_per_user: false` (default) | No user_id in key | All thread participants share the session |
| `thread_sessions_per_user: true` | `agent:main:discord:thread:<thread_id>:<user_id>` | Each user gets own session in thread |

## Why context "resets"

1. User sends `@Hermes do X` in #general → auto-thread creates thread #1 → session key = `thread:111`
2. User sends `@Hermes now do Y` in #general → auto-thread creates thread #2 → session key = `thread:222`
3. Different key → different session → no prior context

The old thread still exists in `discord_threads.json` but is orphaned.

## How to preserve context

- **Disable auto-thread**: `hermes config set discord.auto_thread false`
- **Continue inside thread**: once a thread exists, messages inside it reuse the same session
- **Set `thread_require_mention: false`**: bot responds to any message in thread without needing @mention

## Thread lifecycle

- Threads are created with `auto_archive_duration: 1440` (24 hours)
- Archived threads still hold session data in SQLite but new messages can't be sent to them
- When the user @mentions in the parent after a thread is archived, a new thread is created

## When context loss is NOT a session issue — provider rate-limit exhaustion

If sessions are correctly keyed but the bot still "forgets" or stops responding, check whether the model provider is rate-limited (HTTP 429). This is the #1 non-obvious cause of sudden amnesia on always-on gateways.

```bash
# Check for 429 rate-limit errors in gateway logs
grep -i "429\|RateLimitError\|usage_limit\|overload" ~/.hermes/logs/gateway.log | tail -20

# Check which model Discord sessions are actually using (may differ from config)
sqlite3 ~/.hermes/state.db "SELECT DISTINCT model FROM sessions WHERE source LIKE 'discord%';"

# Check if fallback_model is configured
grep -A3 "fallback_model" ~/.hermes/config.yaml
```

If you see `usage_limit_reached` with `plan_type: plus` and a `resets_in_seconds` value, the provider has exhausted its quota. The agent cannot call the LLM at all — this is not a session management bug.

**Fix**: Configure `fallback_model` so Hermes auto-fails over to a secondary provider when the primary rate-limits:
```bash
hermes config set fallback_model.provider openrouter
hermes config set fallback_model.model <model-name>
hermes gateway restart
```

## Debugging session state

```bash
# List all thread IDs the bot has tracked
cat ~/.hermes/discord_threads.json

# Check current session store
sqlite3 ~/.hermes/state.db "SELECT session_key, updated_at FROM sessions WHERE session_key LIKE '%discord%thread%' ORDER BY updated_at DESC LIMIT 10;"
```
