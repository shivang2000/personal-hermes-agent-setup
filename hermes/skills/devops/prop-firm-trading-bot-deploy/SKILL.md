---
name: prop-firm-trading-bot-deploy
description: Deploy and manage an automated trading bot on a funded prop-firm account. Covers rule verification, config drift detection, safety-stack review, alert channel setup, post-mortem preconditions, and deploy/monitor workflow. Use when setting up a bot against any prop firm (FundingPips, FTMO, MyFundedFX, etc.) — especially funded accounts where config drift can lose the account.
version: 1.2.0
created_by: agent
platforms: [macos, linux]
metadata:
  hermes:
    tags: [trading, prop-firm, deployment, risk-management, fundingpips, mt5]
    changelog:
      - 1.3.0 (2026-07-12): Python `FileHandler` block-buffering pitfall (Docker stdout lag, impact on log readers), hourly-digest-script pattern (ssh+parse in pure Python, no LLM in loop) for catching warnings/restarts/lifecycle when no real-time visibility is available.
      - 1.2.0 (2026-07-12): Phase 7 recovery path for "user logged in late" (bounce bot only, not MT5), alert-routing note (parent channel vs thread), DEGRADED-mode-is-benign pitfall, 2 new pitfall entries.
      - 1.1.0 (2026-07-12): Phase 7 EC2 first-boot fixes (mt5_data chown 911:911, docker-compose v5 + buildx 0.12 workaround, IMDSv2), correct deploy order (start MT5 only, log in via noVNC, then start bot to avoid crash loop), and 4 new pitfall entries.
      - 1.0.0 (2026-07-11): Initial 8-phase workflow with FP rules, EC2/Apple-Silicon pitfalls, MT5 investor-password pattern.
---

# Prop-Firm Trading Bot Deployment

Use this skill when deploying or managing an automated trading bot against a funded prop-firm account. The stakes are materially different from personal/demo trading: a config drift can terminate the account and forfeit the evaluation fee.

## When to load this skill

- User mentions a prop firm (FundingPips, FTMO, MyFundedFX, The Funded Trader, etc.)
- User has a "funded account" or "challenge" or "evaluation" they want to trade with a bot
- User asks to "set up" or "start trading" with an existing bot against a prop firm
- Config files reference prop-firm rules (daily loss, overall DD, profit target, min trading days)
- A post-mortem document exists for a previous account failure

## Critical principle: bot must be TIGHTER than the prop firm

The bot's own risk guard (EmergencyStop, PropFirmGuard) must trip BEFORE the prop firm's hard breach. If the bot's daily-loss limit equals the prop firm's limit, the bot will trigger its emergency stop at the same moment the prop firm terminates the account — which means the bot's guard is useless.

**Rule of thumb:** bot trips at 1% under the prop firm's daily limit and 1.5% under the overall limit. This leaves real headroom.

Example: FundingPips 1 Step has 3% daily / 6% overall. Bot should trip at 2% / 4.5%.

## Workflow: 8 phases

### Phase 1: Research the prop firm's actual rules

Do NOT trust existing config files to be accurate. Prop firms update rules frequently. Verify from primary sources:

1. Navigate to the prop firm's Trading Objectives / Rules page via `browser_navigate`
2. If the site is behind bot-mitigation (Cloudflare, Vercel security checkpoint), use the Wayback Machine: `curl -sL "https://web.archive.org/web/2025/https://help.example.com/en/articles/..." -o /tmp/wb.html`
3. Extract the specific numbers: profit target, daily loss limit, overall loss limit, min trading days, leverage, news trading policy, weekend holding policy, inactivity limit
4. Check the help center for: forbidden strategies, EA policy, copy trading policy, IP rule, toxic trading flow, lot exposure limits
5. Record findings in the project's `docs/propfirm-approvals/` directory

**Key articles to find (most prop firms have equivalents):**
- "What are the Forbidden Strategies?" — tells you if EAs/bots are allowed and which types
- "Copy Trading Policy" — tells you if you can mirror between own accounts
- "What is the IP rule?" — tells you if VPS/VPN is allowed
- "Can I hold trades during news?" — tells you the news window restrictions
- "What is Toxic Trading Flow?" — tells you what constitutes a breach

### Phase 2: Detect config drift

Compare the verified rules against the bot's config file. Common drift items:

| Config field | What to check | Direction of safe drift |
|---|---|---|
| `daily_loss_limit_pct` | Matches prop firm? | Bot must be LOWER (tighter) |
| `max_overall_dd_pct` | Matches prop firm? | Bot must be LOWER (tighter) |
| `safety_buffer_daily_usd` | Recalculated on correct base? | Should be 1% of account × buffer_pct |
| `safety_buffer_dd_usd` | Recalculated on correct base? | Should be 1.5% of account × buffer_pct |
| `leverage_metals` | Matches prop firm per instrument? | Varies by instrument class |
| `profit_target_pct` | Matches the current phase? | Step 1 ≠ Step 2 ≠ Master |
| `min_trading_days` | Matches prop firm? | Usually 3 |
| `inactivity_limit_days` | Matches prop firm? | Usually 30 |
| `news_filter_enabled` | Required on Master? | Safe to keep enabled on all phases |
| `pre_news_flat_minutes` | Matches prop firm's news window? | Usually 5 min before/after |

### Phase 3: Review the safety stack

Before going live, verify these components exist and their tests pass:

- **EmergencyStop** — daily loss + trailing max-DD (peak-relative, not initial-relative)
- **PropFirmGuard** — daily DD, overall DD, profit-target halt, payout reset
- **NewsEventFilter** — high-impact calendar, pre-news flat, central gate (not just one scan loop)
- **ForeignPositionMonitor** — detects positions with wrong magic number (manual trades)
- **OrderExecutor** — naked-entry guard (rejects orders without SL), close orders carry position_ticket
- **TrailingStopManager** — SL modify respects broker stops_level (clamps, doesn't skip)

Run the unit tests: `python3 -m pytest tests/unit/ -q`

**Stale pytest plugin fix:** If pytest fails with `ModuleNotFoundError: No module named 'superclaude.pytest_plugin'`, temporarily move the dist-info directory:
```bash
mv "/Library/.../site-packages/superclaude-4.1.9.dist-info" /tmp/superclaude-backup
python3 -m pytest tests/unit/ -q
mv /tmp/superclaude-backup "/Library/.../site-packages/superclaude-4.1.9.dist-info"
```

### Phase 4: Review uncommitted changes

If the repo has uncommitted changes in safety-critical paths (`src/risk/`, `src/safety/`, `src/execution/`, `src/monitoring/`, `src/config/schema.py`), read the diff before going live. Look for:

- Directional cap (max_positions_per_direction) — prevents stacking
- In-flight order tracking — closes the race where 15s-spaced signals stack before fills register
- Regime filter — blocks whipsaw in ranging markets
- R:R gate with scalping exemption — some strategies (mean reversion) have R:R < 1.0 but positive expectancy from win rate

### Phase 5: Set up alert channels

The #1 lesson from every post-mortem: silent failure on a funded account is how accounts die. Set up at least one alert channel before going live.

**User preference (2026-07-11): use existing Discord connection, don't create new infrastructure.**
When Hermes gateway is already connected to Discord, the user prefers reusing the existing channel + bot identity over creating webhooks or new channels. Check `hermes send --list discord` for an existing `#trading-bot` channel and use the `DISCORD_BOT_TOKEN` from `~/.hermes/.env` + the channel ID. Do NOT ask the user to create a webhook or a new channel unless no suitable existing channel exists.

**Discord via Hermes bot token (recommended if Hermes gateway is already connected):**
1. Find the channel: `hermes send --list discord`
2. Set env vars on the bot's host: `DISCORD_BOT_TOKEN=REDACTED_SET_LOCALLY
3. The bot posts as the same Discord identity as Hermes (e.g. hermesagent#5141)
4. Test with a live send before deploying

**Discord via webhook (alternative):**
1. Create a webhook in Discord: channel settings → Integrations → Webhooks → New Webhook
2. Set `DISCORD_WEBHOOK_URL` env var
3. Simpler but separate identity from Hermes

**Critical alerts that MUST fire:**
- Emergency stop (daily DD / overall DD breached)
- Foreign position detected (manual trade — this was the proximate cause of at least one $5k bust)
- Bot started / bot stopped
- Trade opened / trade closed
- Heartbeat stale (Docker healthcheck)

**Alert routing — parent channel vs thread (verified 2026-07-12):** The bot's `DiscordNotifier` posts to the `DISCORD_ALERT_CHANNEL_ID` (parent channel, e.g. `#trading-bot`). Threads on that channel do NOT inherit the alert stream — they are for operator discussion, not the operational log. This is the correct design: the channel is the audit log ("Trading Bot V2 started", "WARNING: ... Telegram not authenticated", "CRITICAL: ..."), threads are for context-setting messages. If the user reports they can't see the alerts, check they're looking at the parent channel, not a thread.

**DEGRADED-mode startup is a non-error (verified 2026-07-12).** When Telegram isn't configured, the bot logs `WARNING: Trading Bot V2 started DEGRADED: Telegram not authenticated` and then `Trading Bot V2 started`. The DEGRADED status is a feature: it signals the bot is running but a non-critical subsystem is offline. For deploys that use the bot's own strategies (no signal channels), Telegram-skip is expected and safe — do NOT misread the DEGRADED line as a fatal error. The bot continues to run PositionMonitor, SignalGenerator, and trade execution; only the optional Telegram notifier is disabled.

### Phase 6: Verify post-mortem preconditions

If a post-mortem document exists (e.g. `docs/post-mortem-5k.md`), read it and check every item in the "Decisions" or "Preconditions" section. Typical items:

- [ ] Safety-gate code merged in working tree (check `git log`)
- [ ] Foreign-position monitor active
- [ ] News filter covers ALL signal paths (not just one scan loop)
- [ ] Pre-news flat implemented
- [ ] Calendar expanded (high-impact events)
- [ ] MT5 investor password verified to reject manual trades
- [ ] EBS DeleteOnTermination=false (if EC2)
- [ ] Nightly S3 backup active (if EC2)
- [ ] Data-durability: no single-instance data loss path

### Phase 7: Deploy

**EC2 (recommended for funded accounts):**
```bash
./scripts/deploy-propfirm.sh    # interactive: pick account size + phase
docker compose -f docker-compose.ec2.yml up -d
# Open http://<ec2-ip>:8080 in browser (noVNC)
# Log into MT5 with funded account credentials
# Enable AutoTrading
docker compose -f docker-compose.ec2.yml restart trading-bot
```

**EC2 first-boot: 3 mandatory one-time fixes BEFORE `up -d` (discovered 2026-07-12)**

These are NOT optional. Skipping any of them causes silent failures that look like "the deploy is broken" but are actually one-line config fixes. Apply in this exact order on a fresh EC2.

**Fix 1 — `mt5_data` ownership.** The `gmag11/metatrader5_vnc` image runs Wine as `abc` (uid 911, set by `PUID/PGID=911` in the compose file). If the host bind-mount dir is owned by any other user, every step in `start-mt5.sh` fails with `wine: '/config/.wine' is not owned by you` AND every curl download silently fails with `curl: (23) Failure writing output to destination` because curl can't create the temp file. Result: MT5 never installs, RPyC never starts, and you get "RPyC server failed to start" with no other explanation. Fix BEFORE first `up -d`:

```bash
# push project to EC2 first
rsync -az --exclude=.git --exclude=mt5_data --exclude=data --exclude=logs \
  ./ ec2-user@<ec2-host>:trading-bot-v2/
ssh ec2-user@<ec2-host> "cd trading-bot-v2 && mkdir -p mt5_data data logs && \
  sudo chown -R 911:911 mt5_data && \
  docker-compose -f docker-compose.ec2.yml up -d metatrader5"
# wait ~3-5 min for first-boot install, verify RPyC up:
ssh ec2-user@<ec2-host> "docker exec metatrader5 ss -tln | grep :8001"   # → LISTEN on 0.0.0.0:8001
```

If you ALREADY did the first start without chown, stop the container, chown, and start it again — Wine does not auto-recover, the partial prefix is poisoned.

**Fix 2 — `docker-compose` v5 + buildx 0.12 incompatibility (Amazon Linux 2023 stock).** The default `docker-compose` on a fresh Amazon Linux 2023 EC2 is the v5.0.1 standalone binary, which requires `buildx >= 0.17`. The bundled buildx is `0.12.1`, so `docker compose -f docker-compose.ec2.yml up -d` fails with `compose build requires buildx 0.17 or later`. Workaround: build the bot image directly with `docker build`, then bring up the stack:

```bash
ssh ec2-user@<ec2-host> "cd trading-bot-v2 && \
  docker build -t trading-bot-v2-trading-bot:latest . && \
  docker-compose -f docker-compose.ec2.yml up -d"
```

The image name MUST be `trading-bot-v2-trading-bot` (the compose project + service name, the default Compose v2 prefix) so `docker-compose up` picks it up without rebuilding. Verify with `docker images | grep trading-bot-v2`.

**Fix 3 — IMDSv1 may be disabled (security-hardened EC2).** On EC2s with IMDSv1 disabled, `curl 169.254.169.254/...` returns HTTP 401 with no body. Use IMDSv2 to get the public IP, instance ID, and security group:

```bash
TOKEN=REDACTED_SET_LOCALLY
  -H "X-aws-ec2-metadata-token-ttl-seconds: 60")
curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/public-ipv4
curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/instance-id
```

If the box also has no public IP at all, it's a private subnet — you'll need an SSH bastion or a noVNC tunnel. Quick cross-check: `curl https://checkip.amazonaws.com` should match the instance's known EIP — if it differs, the instance is behind a NAT.

**After fixes: deploy order (CRITICAL — log into MT5 BEFORE starting the bot)**

`docker-compose up -d` brings up BOTH the metatrader5 container AND the trading-bot container. **Do NOT start the bot in the first `up -d`** — the bot will crash-loop every ~20s on `MT5 result expired` because no MT5 account is logged in, and `restart: unless-stopped` will respawn it forever, flooding logs. The correct sequence is:

```bash
# 1. Start MT5 only (skip the bot for now)
docker-compose -f docker-compose.ec2.yml up -d metatrader5
# 2. Wait for first-boot install to finish (3-5 min, watch logs)
docker logs -f metatrader5   # wait for: "RPyC server is running on port 8001."
# 3. Open the EC2 SG ports 8080 (noVNC) + 8001 (RPyC) from your IP
# 4. Open http://<ec2-public-ip>:8080 in browser, noVNC password = botpass
# 5. Log into MT5 with the funded account + enable AutoTrading
# 6. NOW start the bot
docker-compose -f docker-compose.ec2.yml up -d trading-bot
```

The "MT5 result expired" error is **distinct from "connection refused"**: RPyC accepts the TCP connection fine, but `mt5.initialize()` inside Wine returns a stale result because no account is logged in. Quick test from the bot container: `docker exec trading-bot-v2 python -c "import rpyc; c = rpyc.connect('metatrader5', 8001); print(type(c.root))"` — if it prints `<netref ...>`, RPyC is healthy and the only thing missing is a logged-in MT5 account. If the bot has already been left crash-looping while you do the noVNC login, just `docker-compose stop trading-bot` first, then start it again after MT5 is logged in.

**Recovery from "user logged in late" scenario (verified 2026-07-12):** If the user logged in via noVNC AFTER the RPyC server's `start-mt5.sh` already called `mt5.initialize()` (i.e. RPyC is in a stale "Authorization failed" state with the actual terminal now showing a logged-in account), the bot's `mt5.initialize()` will return the same stale result even though the terminal has a real session. The fix is a one-line bounce of the bot container ONLY — do not touch the MT5 container:

```bash
ssh ec2-user@<ec2-host> "cd trading-bot-v2 && \
  docker-compose -f docker-compose.ec2.yml restart trading-bot"
# watch logs — should see: "Connected to MT5 — Login: <n>, Server: <s>, Balance: ..."
```

The restart forces the bot's `MT5Client.connect()` (in `src/mt5/client.py:69`) to re-call `mt5.initialize()` from a fresh RPyC session, which re-attaches to the now-logged-in terminal. Verified working: the visible MT5 (`start.exe /exec`, PID ~524) and the RPyC's Wine Python (PID ~1043) are **the same single MT5 instance** under one Wine user — when RPyC re-inits, it inherits the terminal's existing account. This is the simplest recovery and is preferable to bouncing the whole stack, which would force the user to re-do the noVNC login.

**Local (user may insist despite warnings — mitigate aggressively):**
```bash
# 1. Prevent macOS sleep — critical for local funded trading
caffeinate -d -i -m -s &   # display + system + disk sleep prevention

# 2. Pull MT5 image with --platform (no arm64 manifest exists)
docker pull --platform linux/amd64 gmag11/metatrader5_vnc:latest

# 3. Start the stack
docker compose -f docker-compose.yml \
  -f docker-compose.macbook.override.yml up -d
# noVNC at http://localhost:8080
```

**Why NOT local for funded:** macOS sleep kills MT5 connection, WiFi drops = missed stop-losses, Rosetta 2 adds latency, battery death = total failure. The MacBook override file itself says "DO NOT run live funded accounts on a laptop."

**If user insists on local despite warnings (happened 2026-07):**
1. `caffeinate -d -i -m -s` must be running the entire time — prevents system/display/disk sleep
2. Docker image pull requires `--platform linux/amd64` flag — the MT5 image has no arm64 manifest, and `docker pull` without the flag fails with "no matching manifest for linux/arm64/v8"
3. Don't close the laptop lid — caffeinate prevents software sleep but physical lid close can still cut network
4. Keep Docker Desktop running (don't quit it)
5. The noVNC window at localhost:8080 is the MT5 terminal — use it for login and verification
6. Record the override in memory so the next session knows the user chose local against advice

**Docker + Rosetta 2 FAILS for MT5 on Apple Silicon (discovered 2026-07-11):**
The `gmag11/metatrader5_vnc` Docker image cannot install MT5 under Rosetta 2. The installer fails with `rosetta error: invalid gdt selector index 5` — a Wine + Rosetta CPU emulation incompatibility that prevents `terminal64.exe` from installing. This happens even with a clean wine prefix and `--platform linux/amd64`. Retrying produces the same error.

**QEMU emulation workaround (testing 2026-07-11):**
Docker Desktop on Apple Silicon uses Rosetta 2 for x86 emulation by default (`useVirtualizationFrameworkRosetta: True` in settings). Disabling it forces QEMU full CPU emulation, which is slower but Wine-compatible. To disable:
```bash
python3 -c "
import json
path = '$HOME/Library/Group Containers/group.com.docker/settings-store.json'
with open(path) as f: d = json.load(f)
d['UseVirtualizationFrameworkRosetta'] = False
with open(path, 'w') as f: json.dump(d, f, indent=2)
"
# Also update settings.json
python3 -c "
import json
path = '$HOME/Library/Group Containers/group.com.docker/settings.json'
with open(path) as f: d = json.load(f)
d['useVirtualizationFrameworkRosetta'] = False
with open(path, 'w') as f: json.dump(d, f, indent=2)
"
# Restart Docker Desktop
killall Docker; sleep 3; open -a Docker
# Wait for daemon, then retry MT5 container
docker pull --platform linux/amd64 gmag11/metatrader5_vnc:latest
rm -rf mt5_data  # clean wine prefix
docker compose -f docker-compose.yml -f docker-compose.macbook.override.yml up -d metatrader5
# QEMU is slower — MT5 install may take 5-10 min vs 1-2 min on native x86
```
QEMU emulation is slower than Rosetta and does NOT hit the GDT selector bug — MT5's `terminal64.exe` installs successfully. However, QEMU hits a DIFFERENT failure: `wine: Unhandled illegal instruction at address 7FB55986` when trying to run Python or MT5 itself. MT5 installs but Wine cannot launch it ("Application could not be started"). The Python installer also hits the illegal instruction error. As of 2026-07-11, **both Rosetta 2 AND QEMU fail to run the full Wine+MT5+Python stack on Apple Silicon**. The only reliable path for MT5 on Apple Silicon Macs is EC2 (native x86 Linux) or a remote Windows machine. Do not spend more than 30 minutes trying Docker-based MT5 on Apple Silicon — go to EC2.

**Native MT5 Mac app workaround (partial — Python installer hangs):**
The official MetaTrader 5 Mac app (`/Applications/MetaTrader 5.app`) ships with its own bundled Wine 8.0.1 that does NOT use Rosetta — it's a macOS-native Wine build. MT5 is already installed in its Wine prefix (`terminal64.exe` present). The intended workaround: install Python + MetaTrader5 + RPyC into the native MT5's Wine prefix, start an RPyC server, and run the bot as bare Python.

**IMPORTANT CAVEAT (discovered 2026-07-11):** The Python 3.9 Windows installer (`python-3.9.13.exe`) hangs indefinitely when run inside the native MT5 Mac app's bundled Wine. The installer was still stuck after 70 minutes with zero progress. The native MT5 Wine is a minimal Wine configured only to run MT5 — it may lack the system DLLs needed for Python's installer. If the QEMU Docker approach works, prefer it. If both Docker+QEMU and native Wine fail, EC2 is the only reliable path for Apple Silicon Macs.

```bash
WINE_PREFIX="/Users/$USER/Library/Application Support/net.metaquotes.wine.metatrader5"
WINE_BIN="/Applications/MetaTrader 5.app/Contents/SharedSupport/wine/bin/wine64"
export WINEPREFIX="$WINE_PREFIX"

# 1. Install Python in the native MT5's Wine prefix
curl -L "https://www.python.org/ftp/python/3.9.13/python-3.9.13.exe" -o /tmp/python-installer.exe
"$WINE_BIN" /tmp/python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
rm /tmp/python-installer.exe

# 2. Install MetaTrader5 + numpy + RPyC in Wine
"$WINE_BIN" python -m pip install --upgrade pip
"$WINE_BIN" python -m pip install --no-cache-dir 'MetaTrader5==5.0.36' 'numpy<2' rpyc python-dateutil

# 3. Start the RPyC server (exposes MetaTrader5 API on port 8001)
"$WINE_BIN" python -c "
from rpyc.utils.server import ThreadedServer
from rpyc.core import SlaveService
t = ThreadedServer(SlaveService, hostname='0.0.0.0', port=8001, reuse_addr=True)
t.start()
" &

# 4. Run the bot as bare Python (no Docker)
cd /path/to/trading-bot-v2
MT5_HOST=localhost MT5_PORT=8001 python src/main.py
```

Key differences from Docker approach:
- No Docker container for MT5 — uses the native app's Wine
- No Rosetta 2 emulation — native macOS Wine 8.0.1
- Bot runs as bare Python, not in a container
- MT5 terminal is the native Mac app (already installed, user may have accounts logged in)
- `MetaTrader5` Python package is Windows-only (no macOS ARM64 build) — must run inside Wine
- RPyC bridges the Wine Python (with MetaTrader5) to the host Python (the bot)

### Phase 8: Monitor 24h before scaling

After deploying to the funded account:
1. Verify the bot's "started" message appears in Discord
2. Verify at least one trade goes through cleanly (or the bot correctly reports no signals)
3. Verify the heartbeat is fresh (Docker healthcheck returns healthy)
4. Watch the daily-DD buffer — it should never exceed the bot's 2% / 4.5% trip point
5. If a news event occurs, verify the pre-news flat fires
6. After 24h with no emergency stops, consider the deploy stable

## MT5 investor-password pattern (critical operational mitigation)

This single pattern prevents the most common funded-account failure mode:

- **Master password** → goes into AWS SSM (or secure secret store) ONLY. The bot reads it from there. No human should ever type it into a terminal.
- **Investor password** → used for any human session (noVNC, mobile app, desktop terminal). Investor terminal is read-only — clicking "Buy" returns "Invalid account."
- This prevents a human from opening a manual trade alongside the bot during a news event (the proximate cause of multiple documented prop-firm busts).

Verify before going live: log into MT5 via noVNC with the investor password, attempt to place a trade, confirm it's rejected with "Invalid account."

## Known prop-firm rules (verified 2026-07)

### FundingPips — 1 Step model

| Rule | Step 1 (Student) | Master (Funded) |
|---|---|---|
| Profit target | 10% | None |
| Max daily loss | 3% | 3% |
| Max overall loss | 6% | 6% |
| Min trading days | 3 | — |
| Max risk per trade | No restriction | 3% (<$50K) / 2% ($50K+) |
| News trading | Allowed | RESTRICTED (5 min before/after high-impact) |
| Weekend holding | Allowed | Allowed |
| Inactivity | 30 days | 30 days |
| Leverage | 1:30 (FX 1:50, Indices 1:20, Metals 1:20, Energies 1:10, Crypto 1:2) |
| EA policy | Allowed as trade/risk manager only. Third-party signal EAs = prohibited. |
| Copy trading | Between own accounts = allowed. Between different users = prohibited. |
| MT5 server | "FundingPips Corp (2)" — must manually add to server list |
| Daily reset | 00:00 Platform Time (GMT+2), NOT UTC |
| Daily loss basis | Higher of equity or balance at session start |

### FundingPips — 2 Step model

| Rule | Step 1 (Student) | Step 2 (Practitioner) | Master |
|---|---|---|---|
| Profit target | 8% or 10% (trader choice) | 5% | None |
| Max daily loss | 5% | 5% | 4% |
| Max overall loss | 10% | 10% | 12% |
| Max risk per trade | No restriction | No restriction | 3% (<$50K) |

See `references/fundingpips-full-rules.md` for the complete verified ruleset including scaling plan, fail discounts, and all help-center article content.
See `references/discord-notifier-pattern.md` for the two-mode Discord notifier implementation (webhook + bot-token), MultiNotifier fan-out, channel discovery, and testing approach.
See `references/ec2-provisioning-quickstart.md` for the EC2 provisioning quickstart, cost estimate, post-provision steps, and data-durability checklist.
See `references/hourly-digest-pattern.md` for the reusable log-digest cron pattern (pure-Python script, `no_agent: true` schema, log-lag handling, Discord delivery) used to read `logs/trading.log` from a remote box.

## Pitfalls

- **Config drift in the safe direction is still drift.** If the bot is tighter than the prop firm, that's safe — but if it's tighter because of a WRONG base number (e.g. daily loss calculated on $50 demo balance instead of $5000 funded), the bot will either trip too early or too late. Always verify the base.
- **Daily reset timezone mismatch.** Many prop firms reset daily limits at 00:00 Platform Time (GMT+2). If the bot uses UTC midnight, there's a 2-hour window where the bot and the prop firm disagree on "today." This is usually safe (bot is stricter) but can cause unnecessary emergency stops if a loss straddles the GMT+2 midnight boundary.
- **Daily loss uses HIGHER of equity or balance.** Some prop firms calculate the daily limit from max(equity, balance), not just equity. If the bot only tracks equity, it may under-count the limit. Again, usually safe direction (bot trips earlier) but worth verifying.
- **m30_rsi2_mean_reversion or any new strategy with R:R < 1.0.** Mean-reversion strategies can have R:R 0.5 but 70% win rate — positive expectancy. A flat 1.5 R:R gate will silently reject 100% of these signals. Add a `min_rr_ratio_scalping` exemption.
- **Stale pytest plugins from other tools** (e.g. `superclaude.pytest_plugin`) can block the test suite. Temporarily move the dist-info directory to run tests, then restore it.
- **Running funded accounts on a laptop.** Sleep, WiFi, battery, Rosetta overhead. The compose file says "DO NOT" — listen to it. If user overrides, mitigate with `caffeinate -d -i -m -s` and don't close the lid.
- **Apple Silicon Docker pull fails without --platform flag.** The MT5 image (`gmag11/metatrader5_vnc:latest`) has no arm64 manifest. `docker pull` without `--platform linux/amd64` fails with "no matching manifest for linux/arm64/v8 in the manifest list entries." Must explicitly pass `--platform linux/amd64` to pull the amd64 image for Rosetta 2 emulation.
- **Docker + QEMU ALSO fails for MT5 on Apple Silicon (verified 2026-07-11).** Disabling Rosetta (`UseVirtualizationFrameworkRosetta: False`) and forcing QEMU emulation gets past the GDT selector error — `terminal64.exe` installs successfully. BUT QEMU then hits `wine: Unhandled illegal instruction at address 7FB55986` when trying to run Python or MT5 itself. MT5 installs but Wine cannot launch it ("Application could not be started, or no application associated with the specified file"). The Python installer also hits the illegal instruction error. **Bottom line: neither Rosetta nor QEMU can run the full Wine+MT5+Python stack on Apple Silicon. Do not spend more than 30 minutes trying. Go to EC2.**
- **Native MT5 Mac app's Wine may hang on Python installer.** The bundled Wine in `/Applications/MetaTrader 5.app` is minimal — configured only to run MT5, not to install arbitrary Windows software. The Python 3.9 Windows installer hung for 70+ minutes with zero progress in this Wine. If using the native Wine approach, monitor the install closely and fall back to QEMU Docker or EC2 if it stalls.
- **Docker Desktop Rosetta setting lives in TWO files.** Both `settings-store.json` (`UseVirtualizationFrameworkRosetta`) and `settings.json` (`useVirtualizationFrameworkRosetta`) must be set to `False`. Docker Desktop must be restarted (`killall Docker; open -a Docker`) for the change to take effect. Verify after restart: `cat ~/Library/Group\ Containers/group.com.docker/settings-store.json | python3 -c "import json,sys; print(json.load(sys.stdin).get('UseVirtualizationFrameworkRosetta'))"` should print `False`.
- **CONFIG_OVERLAY env var may point to wrong account size.** Always verify `CONFIG_OVERLAY` in the bot's `.env` matches the intended account (e.g. `fundingpips-5k` not `fundingpips-10k`). A mismatch means the bot trades with wrong risk parameters — wrong DD limits, wrong lot sizing, wrong profit target. Check with `grep CONFIG_OVERLAY .env` before every deploy.
- **Manual trades during news events.** The #1 documented cause of prop-firm busts. The bot can't prevent this by force — the MT5 investor password pattern is the mitigation.
- **`mt5_data` ownership on EC2 (verified 2026-07-12).** The bind-mount dir for `/config/.wine` inside the MT5 container must be owned by `911:911` (the image's `abc` user, PUID/PGID=911 from compose). If it's owned by `ec2-user` (the default after `mkdir -p` from a root/sudo session), Wine refuses with `/config/.wine is not owned by you` and curl downloads fail with no useful error. Symptom: "RPyC server failed to start" with the MT5 install showing curl 23 errors. Fix BEFORE first `up -d`: `sudo chown -R 911:911 mt5_data`. Wine does not auto-recover from a partially-installed prefix — if you already started, stop+chown+restart.
- **`docker-compose` v5.0.1 + `buildx` 0.12 mismatch (Amazon Linux 2023, verified 2026-07-12).** `docker compose -f ... up -d` fails with `compose build requires buildx 0.17 or later`. Workaround: `docker build -t trading-bot-v2-trading-bot:latest .` first, then `docker-compose -f ... up -d`. The image name is `<project>-<service>` (compose v2 default prefix); get it right or compose will rebuild.
- **IMDSv1 disabled on hardened EC2s.** Plain `curl 169.254.169.254/...` returns HTTP 401. Use IMDSv2 with a session token to read public IP, instance ID, and security groups. If public IP is also missing, the instance is in a private subnet — need a bastion or noVNC tunnel.
- **Bot crash-loops on "MT5 result expired" with no logged-in account (verified 2026-07-12).** The MT5 container's RPyC accepts the TCP connection fine — `mt5.initialize()` is the call that returns a stale/expired result when no account is logged in. Distinct from `[Errno 111] Connection refused` (RPyC not up yet). Quick health probe: `docker exec trading-bot-v2 python -c "import rpyc; print(type(rpyc.connect('metatrader5', 8001).root))"` — `<netref ...>` = RPyC up, just needs MT5 login. If you let `restart: unless-stopped` respawn it for 10+ minutes, you have a 1000+ line error log to grep through. Stop the bot with `docker-compose stop trading-bot` until the noVNC login is done.
- **Stale RPyC state after the user logs in late (verified 2026-07-12).** If `start-mt5.sh` already called `mt5.initialize()` before the user did the noVNC login, RPyC sits in a stale "Authorization failed" state. After the user logs in via noVNC, bouncing the **bot container only** (`docker-compose restart trading-bot`) re-attaches to the now-logged-in terminal. Do NOT bounce the metatrader5 container — that would force the user to re-do the noVNC login. The visible `start.exe /exec` MT5 and the RPyC's Wine Python share one MT5 instance per Wine user, so re-init from the bot side picks up the terminal's existing account.
- **Misreading the "DEGRADED" startup line as a fatal error (verified 2026-07-12).** When `TELEGRAM_PHONE` is unset (i.e. the bot uses its own strategies, not signal channels), the bot logs `WARNING: Trading Bot V2 started DEGRADED: Telegram not authenticated` followed by `Trading Bot V2 started`. The DEGRADED status is a feature, not a failure — Telegram is a non-critical notifier. The bot's main loop, PositionMonitor, SignalGenerator, and trade execution all run normally. Do not crash the bot, do not roll back, do not treat this as a deploy failure. Only a `FATAL: Both MT5 and Telegram are down` line is a real failure mode.

- **Python `logging.FileHandler` is block-buffered when stdout is not a TTY (verified 2026-07-12).** The bot's `logs/trading.log` lags the actual bot state by 5-30 minutes under normal operation. Crashes/restarts/sigterms still flush immediately (process death closes the file), so any log-based monitor will still catch real problems — but quiet, "everything is fine" activity won't show up in real time. Two fixes when we get there: (1) change Dockerfile's `CMD` from `python -m src.main` to `python -u -m src.main` to force unbuffered stdout (does NOT fix the FileHandler's own internal buffer, only Python's); (2) add `logging.basicConfig(force=True, stream=sys.stdout)` in `src/main.py` and remove the explicit `FileHandler` so all logs flow through stdout (the `docker logs -f` stream), or add a periodic `handler.flush()` in the bot's main loop. Until this is fixed, the right way to read the bot's log is **not** by tailing the file — use `docker logs --tail 200 trading-bot-v2` (always-live stdout) or set up a cron that SSHes in and parses the log with explicit lag detection (see `references/hourly-digest-pattern.md`).

- **The trading bot's "laptop vs EC2" question is a recurring confusion (verified 2026-07-12).** The bot always runs on EC2 (or wherever the user deployed it). The laptop/desktop is just an SSH terminal + source-code editor — Docker doesn't run locally, Wine doesn't run on Apple Silicon, MT5 only runs in `gmag11/metatrader5_vnc`. If the user asks "is the bot on EC2 or on my laptop?", the answer is "EC2 — your laptop is just the SSH terminal to it." Keep this in mind when designing log readers, alerts, and on-call workflows: they must work against the remote box, not the local Mac.

## Overlap note (for curator)

`routing-hermes-models` (devops) and `hermes-model-orchestration` (devops) cover the same territory — multi-tier Hermes model routing. `hermes-model-orchestration` has a concrete worked example (`references/minimax-glm-claude-codex.md`) and a config template. `routing-hermes-models` has more detailed verification rules, reliability rules, and two reference files (`tiered-routing-notes.md`, `provider-routing-verification.md`). Consider merging `routing-hermes-models` into `hermes-model-orchestration` as the umbrella, preserving the verification and reliability sections from `routing-hermes-models` as additional reference content.