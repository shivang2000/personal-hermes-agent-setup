---
name: prop-firm-trading-bot-deploy
description: Deploy and manage an automated trading bot on a funded prop-firm account. Covers rule verification, config drift detection, safety-stack review, alert channel setup, post-mortem preconditions, and deploy/monitor workflow. Use when setting up a bot against any prop firm (FundingPips, FTMO, MyFundedFX, etc.) — especially funded accounts where config drift can lose the account.
version: 1.0.0
created_by: agent
platforms: [macos, linux]
metadata:
  hermes:
    tags: [trading, prop-firm, deployment, risk-management, fundingpips, mt5]
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
QEMU emulation is significantly slower than Rosetta but should not hit the GDT selector bug. Monitor `docker logs metatrader5-mac` for "terminal64.exe is installed" vs the rosetta error.

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

## Pitfalls

- **Config drift in the safe direction is still drift.** If the bot is tighter than the prop firm, that's safe — but if it's tighter because of a WRONG base number (e.g. daily loss calculated on $50 demo balance instead of $5000 funded), the bot will either trip too early or too late. Always verify the base.
- **Daily reset timezone mismatch.** Many prop firms reset daily limits at 00:00 Platform Time (GMT+2). If the bot uses UTC midnight, there's a 2-hour window where the bot and the prop firm disagree on "today." This is usually safe (bot is stricter) but can cause unnecessary emergency stops if a loss straddles the GMT+2 midnight boundary.
- **Daily loss uses HIGHER of equity or balance.** Some prop firms calculate the daily limit from max(equity, balance), not just equity. If the bot only tracks equity, it may under-count the limit. Again, usually safe direction (bot trips earlier) but worth verifying.
- **m30_rsi2_mean_reversion or any new strategy with R:R < 1.0.** Mean-reversion strategies can have R:R 0.5 but 70% win rate — positive expectancy. A flat 1.5 R:R gate will silently reject 100% of these signals. Add a `min_rr_ratio_scalping` exemption.
- **Stale pytest plugins from other tools** (e.g. `superclaude.pytest_plugin`) can block the test suite. Temporarily move the dist-info directory to run tests, then restore it.
- **Running funded accounts on a laptop.** Sleep, WiFi, battery, Rosetta overhead. The compose file says "DO NOT" — listen to it. If user overrides, mitigate with `caffeinate -d -i -m -s` and don't close the lid.
- **Apple Silicon Docker pull fails without --platform flag.** The MT5 image (`gmag11/metatrader5_vnc:latest`) has no arm64 manifest. `docker pull` without `--platform linux/amd64` fails with "no matching manifest for linux/arm64/v8 in the manifest list entries." Must explicitly pass `--platform linux/amd64` to pull the amd64 image for Rosetta 2 emulation.
- **Docker + Rosetta 2 cannot install MT5.** Even with `--platform linux/amd64` and a clean wine prefix, the MT5 installer fails under Rosetta 2 with `rosetta error: invalid gdt selector index 5`. This is a Wine + Rosetta CPU emulation incompatibility, not a fixable config issue. Fix: disable `useVirtualizationFrameworkRosetta` in Docker Desktop settings to force QEMU emulation (slower but Wine-compatible), or use the native MT5 Mac app's bundled Wine 8.0.1 instead — see the "QEMU emulation workaround" and "Native MT5 Mac app workaround" in Phase 7 above.
- **Native MT5 Mac app's Wine may hang on Python installer.** The bundled Wine in `/Applications/MetaTrader 5.app` is minimal — configured only to run MT5, not to install arbitrary Windows software. The Python 3.9 Windows installer hung for 70+ minutes with zero progress in this Wine. If using the native Wine approach, monitor the install closely and fall back to QEMU Docker or EC2 if it stalls.
- **Docker Desktop Rosetta setting lives in TWO files.** Both `settings-store.json` (`UseVirtualizationFrameworkRosetta`) and `settings.json` (`useVirtualizationFrameworkRosetta`) must be set to `False`. Docker Desktop must be restarted (`killall Docker; open -a Docker`) for the change to take effect. Verify after restart: `cat ~/Library/Group\ Containers/group.com.docker/settings-store.json | python3 -c "import json,sys; print(json.load(sys.stdin).get('UseVirtualizationFrameworkRosetta'))"` should print `False`.
- **CONFIG_OVERLAY env var may point to wrong account size.** Always verify `CONFIG_OVERLAY` in the bot's `.env` matches the intended account (e.g. `fundingpips-5k` not `fundingpips-10k`). A mismatch means the bot trades with wrong risk parameters — wrong DD limits, wrong lot sizing, wrong profit target. Check with `grep CONFIG_OVERLAY .env` before every deploy.
- **Manual trades during news events.** The #1 documented cause of prop-firm busts. The bot can't prevent this by force — the MT5 investor password pattern is the mitigation.

## Overlap note (for curator)

`routing-hermes-models` (devops) and `hermes-model-orchestration` (devops) cover the same territory — multi-tier Hermes model routing. `hermes-model-orchestration` has a concrete worked example (`references/minimax-glm-claude-codex.md`) and a config template. `routing-hermes-models` has more detailed verification rules, reliability rules, and two reference files (`tiered-routing-notes.md`, `provider-routing-verification.md`). Consider merging `routing-hermes-models` into `hermes-model-orchestration` as the umbrella, preserving the verification and reliability sections from `routing-hermes-models` as additional reference content.