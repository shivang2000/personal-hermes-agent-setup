# Hermes selected backup restore: skills, cron, gateway/dashboard LaunchAgents

Use this reference when restoring only selected Hermes state from a tar.gz setup backup instead of extracting the whole archive over `~/.hermes`.

## Scenario

A backup archive contained:
- `.hermes/skills/`
- `.hermes/cron/jobs.json`
- `Library/LaunchAgents/ai.hermes.gateway.plist`
- `Library/LaunchAgents/ai.hermes.dashboard.plist`
- config/auth/env/session state that the user did **not** want restored yet

The user chose to restore only: all skills, xurl/Twitter skills, cron jobs, gateway autostart, dashboard autostart, dashboard port `9119`.

## Safe restore pattern

1. Create a safety backup of the current selected targets before overwriting:

```bash
RESTORE_SAFETY_DIR="$HOME/dev/shivang-automation/pre-restore-safety-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$RESTORE_SAFETY_DIR"
(cd "$HOME" && tar -czf "$RESTORE_SAFETY_DIR/current-selected-before-restore.tar.gz" \
  .hermes/skills \
  .hermes/cron/jobs.json \
  Library/LaunchAgents/ai.hermes.gateway.plist \
  Library/LaunchAgents/ai.hermes.dashboard.plist)
shasum -a 256 "$RESTORE_SAFETY_DIR/current-selected-before-restore.tar.gz" \
  > "$RESTORE_SAFETY_DIR/current-selected-before-restore.tar.gz.sha256"
```

2. Extract selected paths to a temporary directory, not directly over `$HOME`:

```bash
ARCHIVE=/path/to/hermes-complete-setup.tar.gz
TMP="$(mktemp -d /tmp/hermes-restore-selected.XXXXXX)"
tar -xzf "$ARCHIVE" -C "$TMP" \
  .hermes/skills \
  .hermes/cron/jobs.json \
  Library/LaunchAgents/ai.hermes.gateway.plist \
  Library/LaunchAgents/ai.hermes.dashboard.plist
```

3. Copy only the requested components:

```bash
mkdir -p ~/.hermes ~/.hermes/cron ~/Library/LaunchAgents ~/.hermes/logs
rm -rf ~/.hermes/skills
cp -a "$TMP/.hermes/skills" ~/.hermes/skills
cp -a "$TMP/.hermes/cron/jobs.json" ~/.hermes/cron/jobs.json
chmod 600 ~/.hermes/cron/jobs.json || true
cp -a "$TMP/Library/LaunchAgents/ai.hermes.dashboard.plist" ~/Library/LaunchAgents/
cp -a "$TMP/Library/LaunchAgents/ai.hermes.gateway.plist" ~/Library/LaunchAgents/
chmod 644 ~/Library/LaunchAgents/ai.hermes.*.plist
```

4. Rewrite the dashboard `ProgramArguments` defensively instead of doing index-based plist edits:

```python
import plistlib
p = '/Users/shivang/Library/LaunchAgents/ai.hermes.dashboard.plist'
with open(p, 'rb') as f:
    d = plistlib.load(f)
d['ProgramArguments'] = [
    '/Users/shivang/.hermes/hermes-agent/venv/bin/python',
    '-m', 'hermes_cli.main', 'dashboard', '--port', '9119',
]
with open(p, 'wb') as f:
    plistlib.dump(d, f)
```

Index-based edits like `PlistBuddy Set :ProgramArguments:4 9119` can corrupt the command into `dashboard 9119 9119` if the expected argument positions differ.

## Gateway service caveat

After restoring an old gateway LaunchAgent, prefer the official command:

```bash
cd ~/.hermes/hermes-agent
~/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main gateway start
~/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main gateway status
```

Why: Hermes may report the restored plist is stale relative to the current install. `hermes gateway start` updates the service definition to match the current install and loads it. Manual `launchctl bootstrap` may show `Bootstrap failed: 5: Input/output error`; macOS logs may reveal this is actually a stale/existing-label condition. Do not create a second permanent gateway label as the final fix; use the official command and verify `Service definition matches the current Hermes install` and `Gateway service is loaded`.

## Dashboard service commands

Dashboard status is a flag, not a subcommand:

```bash
hermes dashboard --status
```

`hermes dashboard status` is invalid.

## Verification checklist

```bash
find ~/.hermes/skills -name SKILL.md | wc -l
[ -f ~/.hermes/skills/social-media/xurl/SKILL.md ] && echo xurl-present
hermes cron list --all
hermes gateway status
hermes dashboard --status
lsof -nP -iTCP:9119 -sTCP:LISTEN
python3 - <<'PY'
import urllib.request
r = urllib.request.urlopen('http://127.0.0.1:9119', timeout=5)
print(r.status, r.headers.get('content-type'))
PY
launchctl print "gui/$(id -u)/ai.hermes.dashboard"
```

If cron jobs are restored after their scheduled time, due one-shot jobs may run immediately when the gateway scheduler starts. Check `~/.hermes/cron/output/<job-id>/` before assuming nothing ran.
