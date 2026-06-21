---
name: hermes-durable-services
description: "Run Hermes subprocesses (dashboard, gateway profiles, etc.) as independent OS-level daemons so they survive gateway restarts, process-registry cleanup, and system reboots."
version: 1.0.0
metadata:
  hermes:
    tags: [macos, launchd, systemd, services, daemon, persistence, dashboard, gateway]
    related_skills: [hermes-agent, hermes-s6-container-supervision]
---

# Hermes Durable Background Services

## When to use this skill

Load this skill when:
- A Hermes background process (dashboard, gateway worker, agent subprocess) keeps dying and you need it to be durable
- The process was started via `terminal(background=true)` but dies whenever the gateway restarts
- You need a Hermes subprocess to survive system reboots, gateway restarts, or process-registry cleanup
- You're setting up a **one-time permanent service** (like the dashboard) that should always be running
- You're restoring Hermes skills/cron/LaunchAgents from a backup and need the gateway/dashboard to autostart after login

## The core problem

When you start a Hermes subprocess via the terminal tool with `background=true`, it gets tracked in the **process registry**. This has a critical side effect:

> **When the gateway receives SIGTERM (restart/shutdown), it runs `Shutdown (final-cleanup): killed N tool subprocess(es)` — murdering every tracked background process including your dashboard.**

The dashboard process then becomes a zombie: the PID stays alive briefly but the port stops serving (HTTP 000 / curl error 7: "Failed to connect to host").

Additionally, terminal-tool background processes:
- Have **no auto-restart** if they crash
- Do **not survive** system reboots
- Are coupled to the gateway's lifecycle

## The solution

Run the subprocess as an **OS-level service** managed by the native init system. This decouples it from the gateway entirely.

**Reference files:**
- `references/macos-launchd-hermes-dashboard.md` contains the full real-world session detail including log evidence and timeline.
- `references/hermes-selected-backup-restore.md` contains a selective backup-restore recipe for skills, cron jobs, and gateway/dashboard LaunchAgents, including verification commands and macOS launchd pitfalls.

### macOS (launchd) — Full recipe

Create a `.plist` in `~/Library/LaunchAgents/` modeled on the existing Hermes gateway service (`ai.hermes.gateway.plist`).

#### 1. Create the plist

```xml
<!-- ai.hermes.dashboard.plist — save to ~/Library/LaunchAgents/ -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>ai.hermes.dashboard</string>

    <key>ProgramArguments</key>
    <array>
        <string>/Users/shivang/.hermes/hermes-agent/venv/bin/python</string>
        <string>-m</string>
        <string>hermes_cli.main</string>
        <string>dashboard</string>
        <string>--port</string>
        <string>9119</string>
    </array>

    <key>WorkingDirectory</key>
    <string>/Users/shivang/.hermes/hermes-agent</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/Users/shivang/.hermes/hermes-agent/venv/bin:/usr/local/bin:/usr/bin:/bin</string>
        <key>VIRTUAL_ENV</key>
        <string>/Users/shivang/.hermes/hermes-agent/venv</string>
        <key>HERMES_HOME</key>
        <string>/Users/shivang/.hermes</string>
    </dict>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>

    <key>StandardOutPath</key>
    <string>/Users/shivang/.hermes/logs/dashboard.log</string>

    <key>StandardErrorPath</key>
    <string>/Users/shivang/.hermes/logs/dashboard.error.log</string>
</dict>
</plist>
```

Key settings explained:

| Key | Purpose |
|-----|---------|
| `RunAtLoad` | Starts the service when you log in |
| `KeepAlive / SuccessfulExit: false` | Auto-restarts if the process crashes (restarts on non-zero exit) |
| `EnvironmentVariables` | Must include `HERMES_HOME`, `VIRTUAL_ENV`, and `PATH` pointing to the Hermes venv — launchd does NOT inherit your shell env |
| `WorkingDirectory` | Must match the project root so relative imports resolve |

> **IMPORTANT:** Do NOT use `launchctl setenv` or ~/.launchd.conf — those are deprecated/broken on modern macOS. Put every needed env var in the plist's `EnvironmentVariables` dict.

#### 2. Load the service

```bash
# Register and start
launchctl load ~/Library/LaunchAgents/ai.hermes.dashboard.plist

# Verify it's running
launchctl list | grep hermes-dashboard
# → "PID\t0\tai.hermes.dashboard"    ← running
# → "-1\t0\tai.hermes.dashboard"     ← exited, will restart
# → "-\t78\tai.hermes.dashboard"     ← loaded but not running (?)
```

#### 3. Management commands

```bash
# Restart (send graceful signal + relaunch)
launchctl kickstart gui/$(id -u)/ai.hermes.dashboard

# Stop / unload
launchctl bootout gui/$(id -u)/ai.hermes.dashboard
# or: launchctl unload ~/Library/LaunchAgents/ai.hermes.dashboard.plist

# Reload after editing the plist
launchctl bootout gui/$(id -u)/ai.hermes.dashboard 2>/dev/null
launchctl load ~/Library/LaunchAgents/ai.hermes.dashboard.plist

# Check logs
tail -f ~/.hermes/logs/dashboard.log
tail -f ~/.hermes/logs/dashboard.error.log
```

#### 4. Verify it's serving

```bash
curl -s -o /dev/null -w "HTTP %{http_code}\n" http://127.0.0.1:9119
# → HTTP 200
```

#### 5. Removing the service

```bash
launchctl bootout gui/$(id -u)/ai.hermes.dashboard
rm ~/Library/LaunchAgents/ai.hermes.dashboard.plist
```

#### 6. Gateway service after restoring a backup plist

For the Hermes gateway specifically, prefer the official service command after copying/restoring a plist:

```bash
cd ~/.hermes/hermes-agent
~/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main gateway start
~/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main gateway status
```

Reason: restored gateway plists can be stale relative to the currently installed Hermes checkout. The CLI knows how to rewrite the service definition and verify it. A raw `launchctl bootstrap` may return `Bootstrap failed: 5: Input/output error`; check `gateway status` and macOS logs before creating alternate labels. The desired final state is:

```text
Service definition matches the current Hermes install
Gateway service is loaded
```

For dashboard status, use the flag form:

```bash
hermes dashboard --status
```

`hermes dashboard status` is not a valid command.

### Model for other Hermes services

The same pattern works for any Hermes subcommand. Change the `ProgramArguments` array:

```xml
<!-- Example: profile-specific gateway -->
<key>ProgramArguments</key>
<array>
    <string>/Users/shivang/.hermes/hermes-agent/venv/bin/python</string>
    <string>-m</string>
    <string>hermes_cli.main</string>
    <string>-p</string>
    <string>coder</string>
    <string>gateway</string>
    <string>run</string>
</array>
```

## Pitfalls

### ⚠️ Process registry death on gateway restart

This is the exact problem this skill solves. Before using this skill, the dashboard (or other service) was started with `terminal(background=true)`, which registered it in the process registry. When the gateway restarts, `Shutdown (final-cleanup): killed 1 tool subprocess(es)` kills it. The launchd approach entirely sidesteps this.

### ⚠️ Zombie process (PID alive, port not serving)

If `curl` returns `HTTP 000` / `exit code 7` (Failed to connect to host) but a PID still shows, the process is a zombie — killed from within (e.g. TUI gateway crash) or by a gateway restart that left a half-dead orphan. Kill it with `hermes dashboard --stop` or `kill <PID>` before restarting.

### ⚠️ `--tui` flag is crash-prone on macOS

The `--tui` flag activates a TUI gateway subsystem (WebSocket-based embedded terminal in the browser) that has threading and connection stability issues. For production/durable dashboard runs, **omit `--tui`**:

```bash
# Stable (launchd)
hermes dashboard --port 9119

# Crash-prone (do NOT use for durable services)
hermes dashboard --port 9119 --tui
```

### ⚠️ Environment variables don't inherit

launchd runs services in a minimal environment. You MUST explicitly set:
- `PATH` — including the Hermes venv's bin dir
- `VIRTUAL_ENV` — so Python finds the right packages
- `HERMES_HOME` — so Hermes finds its config and state
- Any `PYTHONPATH` or other vars your subcommand needs

### ⚠️ PATH must include the Hermes venv

The `hermes` binary is at `$HERMES_HOME/hermes-agent/venv/bin/hermes`. The `PATH` must include `$HERMES_HOME/hermes-agent/venv/bin` for subprocesses that expect `hermes` on PATH. However, the plist's `ProgramArguments` calls Python directly, so `PATH` is mainly needed for child processes the subcommand spawns.

### ⚠️ Avoid index-based plist edits for dashboard ports

When changing a restored dashboard plist to a target port, rewrite the full `ProgramArguments` array with `plistlib` or inspect it first. Blind edits such as `PlistBuddy -c 'Set :ProgramArguments:4 9119'` can turn a valid command into `dashboard 9119 9119` if the array shape differs. The known-good array is:

```text
python -m hermes_cli.main dashboard --port 9119
```

### ⚠️ Restored one-shot cron jobs may fire immediately

If `jobs.json` is restored after a one-shot job's scheduled time but before it is marked completed, the gateway cron scheduler can run it as soon as the gateway starts. After restoring cron jobs, inspect `hermes cron list --all` and `~/.hermes/cron/output/<job-id>/` for any due one-shot jobs that fired.

### ⚠️ Port conflicts

If a previous dashboard process is still occupying port 9119, launchd's new process will fail. Always verify with `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:9119` before declaring success. Kill any leftover zombie with `hermes dashboard --stop` or `lsof -ti :9119 | xargs kill`.

## Diagnosis flow

When a launchd service is not working:

1. `launchctl list | grep <label>` — check if service is registered and its last exit code
2. `tail -f ~/.hermes/logs/<service>.error.log` — check stderr for Python tracebacks
3. `curl` the port — confirm it's actually serving
4. Check the gateway logs (`~/.hermes/logs/gateway.log`) for `Shutdown (final-cleanup): killed` — confirms the old pattern was destroying the process
5. If the plist was just edited, unload and reload

## Reference files

- `references/macos-launchd-hermes-dashboard.md` — Full session detail: log evidence, root cause chain, timeline of the original diagnosis and fix
- `references/hermes-selected-backup-restore.md` — Selective restore recipe for skills, cron jobs, and gateway/dashboard LaunchAgents from a full Hermes setup backup

## Related skills

- `hermes-agent` — general Hermes configuration and CLI reference
- `hermes-s6-container-supervision` — Docker container supervision (s6-overlay), the Linux/Docker equivalent of this skill
- `macos-computer-use` — general macOS computer-use automation