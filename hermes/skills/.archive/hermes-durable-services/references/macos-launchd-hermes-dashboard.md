# macOS launchd: Hermes Dashboard Service

Created: 2026-05-26
Session: Diagnosing and fixing recurring Hermes Dashboard downtime

## Problem

The Hermes Dashboard (http://127.0.0.1:9119) kept going offline even though the process was still alive. Port 9119 returned `HTTP 000` / curl error 7 ("Failed to connect to host") while the PID still showed in `ps`.

## Root cause chain

1. The dashboard was started via `terminal(command="hermes dashboard --port 9119 --tui", background=true)` — registered in the **process registry**
2. The gateway (`ai.hermes.gateway` launchd service) was restarting due to Telegram token issues and/or SIGTERM signals
3. Each gateway restart triggered: `Shutdown (final-cleanup): killed 1 tool subprocess(es)` — killing the dashboard
4. The `--tui` flag activated the TUI gateway subsystem which has threading/connection stability issues (see `tui_gateway_crash.log`)
5. Result: zombie process — PID alive but port not serving

## Log evidence

From `~/.hermes/logs/agent.log`:
```
08:29:48,288 WARNING gateway.run: Shutdown context: signal=SIGTERM under_systemd=yes parent_pid=1
08:29:48,390 INFO  gateway.run: Exiting with code 1 ... so systemd Restart=on-failure can revive
08:29:49,651 INFO  tools.process_registry: Recovered detached process: hermes dashboard --port 9119 --tui (pid=39133)
```

Repeated 3x in the log window:
- PID 34916 → exit clean → replace
- PID 35260 → SIGTERM → exit non-zero → replace  
- PID 43684 → SIGTERM → exit non-zero → replace
- PID 46806 → SIGTERM → exit non-zero → replace (current running gateway)

From `~/.hermes/logs/errors.log`:
```
WARNING [20260526_082534_59f72b] agent.tool_executor: Tool terminal returned error (0.09s): 
{"output": "000", "exit_code": 7, "error": null, "exit_code_meaning": "Failed to connect to host"}
```

From `tui_gateway_crash.log`:
```
=== SIGTERM received · 2026-05-26 07:33:08 ===
main-thread stack at signal delivery:
  ... File "tui_gateway/entry.py", line 227, in main
    for raw in sys.stdin:
...thread Thread-6 (_drain_stdout) ... File "tui_gateway/server.py", line 216, in _drain_stdout
    for line in self.proc.stdout or []:
```

## The fix

1. **Stop relying on terminal tool background processes** for durable services
2. **Create a dedicated launchd service** (`ai.hermes.dashboard`) independent of the gateway
3. **Omit the `--tui` flag** — stable web-only dashboard mode

## Timeline

| Time | Event |
|------|-------|
| T-2h | Dashboard started with `--tui` and `background=true` |
| T-1h | Gateway gets SIGTERM → kills dashboard (process registry cleanup) |
| T-30m | Gateway restarted via launchd → dashboard gone |
| T-0 | User reports "dashboard is down" |
| T+5m | Diagnosis: zombie PID, port not serving |
| T+10m | Created `ai.hermes.dashboard.plist`, loaded via launchctl |

## Final state

```bash
$ launchctl list | grep hermes
92220  0  ai.hermes.dashboard    # Running since fix
46806 -15  ai.hermes.gateway     # -15 last exit status from old instance; PID 46806 is current running

$ curl -s -o /dev/null -w "HTTP %{http_code}\n" http://127.0.0.1:9119
HTTP 200
```

## Verification that launchd dashboard survived

To confirm the fix works, simulate a gateway restart:

```bash
launchctl kickstart gui/$(id -u)/ai.hermes.gateway
sleep 5
curl -s -o /dev/null -w "HTTP %{http_code}\n" http://127.0.0.1:9119
# Should still be HTTP 200 — dashboard was not affected
```
