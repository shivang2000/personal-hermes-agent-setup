# Discord Notifier for Trading Bots — Pattern Reference

## Problem

Trading bots need alert channels. The post-mortem lesson #1 from every prop-firm bust: silent failure on a funded account. The bot must alert on:
- Emergency stop (DD breach)
- Foreign position detected (manual trade)
- Trade opened / closed
- Bot started / stopped
- Heartbeat stale

## Solution: Two-mode Discord notifier

### Mode 1: Webhook (simplest)

Set `DISCORD_WEBHOOK_URL` env var. Bot posts via HTTP POST to the webhook URL.
- Pro: no bot token needed, no Discord library dependency
- Con: separate identity from Hermes gateway, one-way only

### Mode 2: Bot token (recommended if Hermes gateway is already connected)

Set `DISCORD_BOT_TOKEN` + `DISCORD_ALERT_CHANNEL_ID`. Bot posts via Discord API v10:
```
POST https://discord.com/api/v10/channels/{channel_id}/messages
Authorization: REDACTED_SET_LOCALLY
Content-Type: application/json
{"content": "message text"}
```
- Pro: same identity as Hermes gateway (hermesagent#5141), posts appear as the bot
- Con: requires the bot token (from ~/.hermes/.env)

### Finding the channel ID

```bash
hermes send --list discord
```

Look for the channel you want (e.g. `discord:trading-bot [1525476646176690297]`). The number in brackets is the channel ID.

### Implementation pattern

See `src/monitoring/discord.py` in trading-bot-v2 for the full implementation. Key points:

1. `DiscordConfig` pulls from env vars, auto-disables if neither mode is configured
2. `DiscordNotifier.send(message, critical=False)` — if critical=True, prepends `DISCORD_CRITICAL_PING` (e.g. "@here" or a role ID)
3. 2000-char limit: truncate with marker at 1900 chars
4. Failures swallowed (5xx → return False, don't crash the bot)
5. All typed methods (send_trade_opened, send_emergency_stop, etc.) mirror SlackNotifier's surface

### MultiNotifier fan-out

Wrap all notifiers (Slack + Telegram + Discord) in a `MultiNotifier` that fans out via `asyncio.gather(return_exceptions=True)`. One channel failing doesn't block the others.

Critical methods (emergency_stop, foreign_position, error_alert) should pass `critical=True` to Discord so the configured ping gets prepended.

### Testing

```python
# Disabled when env unset
def test_disabled_when_url_unset(monkeypatch):
    monkeypatch.delenv("DISCORD_WEBHOOK_URL", raising=REDACTED_SET_LOCALLY
    cfg = DiscordConfig()
    assert cfg.enabled is False

# Bot-token mode
def test_enabled_with_bot_token(monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "MTUxNjc4...")
    monkeypatch.setenv("DISCORD_ALERT_CHANNEL_ID", "1525476646176690297")
    cfg = DiscordConfig()
    assert cfg.mode == "bot_token"

# Send posts correct URL + headers
async def test_send_bot_token_mode(monkeypatch):
    # ... mock httpx.AsyncClient.post, verify URL + Authorization header
```

### EC2 deployment

Add to the bot's `.env` on EC2:
```
DISCORD_BOT_TOKEN=REDACTED_SET_LOCALLY
DISCORD_ALERT_CHANNEL_ID=1525476646176690297
```

Or store in AWS SSM Parameter Store for production:
```bash
aws ssm put-parameter --name /trading-bot/discord-bot-token --value "$DISCORD_BOT_TOKEN" --type SecureString
aws ssm put-parameter --name /trading-bot/discord-channel-id --value "1525476646176690297" --type String
```

### Live test

```bash
hermes send --to discord:trading-bot "Test alert from trading bot"
```

Or from the bot's Python code directly:
```python
import asyncio, os
os.environ['DISCORD_BOT_TOKEN']=REDACTED_SET_LOCALLY
os.environ['DISCORD_ALERT_CHANNEL_ID'] = '1525476646176690297'
from src.monitoring.discord import DiscordNotifier, DiscordConfig
asyncio.run(DiscordNotifier(DiscordConfig()).send("🟢 Test alert"))
```