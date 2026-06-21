# Discord without Telegram — migration recipe

Use this when the user wants Hermes gateway on Discord and explicitly does not want Telegram.

## Goal

- Enable Discord in `~/.hermes/config.yaml`.
- Disable Telegram in `~/.hermes/config.yaml`.
- Remove active Telegram `.env` influence without printing secrets.
- Leave Discord credential entry to the user, because bot tokens are secrets.
- Refresh and verify the gateway service.

## Steps

1. Inspect current state without secrets:

   ```bash
   hermes config path
   hermes config env-path
   hermes gateway status || true
   ```

   Also inspect `config.yaml` for `platforms.discord.enabled` and `platforms.telegram.enabled`, and inspect `.env` key presence only.

2. Enable Discord and disable Telegram:

   ```bash
   hermes config set platforms.discord.enabled true
   hermes config set platforms.telegram.enabled false
   ```

3. Back up `.env` before changing credential lines:

   ```bash
   cp ~/.hermes/.env ~/.hermes/.env.backup-discord-setup-$(date +%Y%m%d%H%M%S)
   ```

4. Comment active Telegram keys rather than printing or deleting them:

   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_ALLOWED_USERS`
   - `TELEGRAM_HOME_CHANNEL`
   - `TELEGRAM_HOME_CHANNEL_NAME`
   - `TELEGRAM_HOME_CHANNEL_THREAD_ID`

   Report only which keys were commented, not their values.

5. Ask the user to enter Discord credentials locally. Required:

   - `DISCORD_BOT_TOKEN`
   - `DISCORD_ALLOWED_USERS` or `DISCORD_ALLOWED_ROLES`

   Preferred command:

   ```bash
   hermes gateway setup
   ```

   Select Discord and paste secrets into the local prompt, not into chat.

6. Restart or refresh the service:

   ```bash
   hermes gateway start
   hermes gateway status
   ```

   If status says the service definition is stale, `hermes gateway start` refreshes it.

## Verification output shape

Keep the final concise and grounded:

- `platforms.discord.enabled = true`
- `platforms.telegram.enabled = false`
- Telegram env keys: active false / commented true
- Discord env keys: present or missing, without values
- Gateway service: loaded/running/stale/error
- Remaining user action, if credentials are missing

## Pitfall from the source session

A clean config change is not enough to claim the migration is complete: Discord was enabled and Telegram disabled in config, but Discord still could not connect because `DISCORD_BOT_TOKEN` and authorization keys were not present. The correct final answer was “prepared; credentials still required locally,” not “Discord is working.”
