#!/usr/bin/env python3
"""
Trading Bot V2 — hourly log digest.

SSHes into the EC2 instance running the bot, reads the last hour of
/home/ec2-user/trading-bot-v2/logs/trading.log, classifies the events, and
emits a tight Discord-friendly markdown summary on stdout.

Exit code 0 = success (a message is printed and the cron job delivers it).
Exit code 1 = error (the cron job will surface the error to the user).

The script is intentionally LLM-free: log parsing is deterministic, so
writing it in Python is more reliable + cheaper than asking the model to
grovel over the file every hour.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────────
# Same key the user uses to ssh into the bot's EC2.
PEM = os.path.expanduser(
    "/Users/shivang/dev/advanced-trading-bot/trading-bot-v2/south-mumbai-key-pair.pem"
)
EC2_HOST = "ec2-user@ec2-3-7-59-175.ap-south-1.compute.amazonaws.com"
LOG_PATH = "/home/ec2-user/trading-bot-v2/logs/trading.log"

# Look back window. The cron runs every 60m, so default to 75m to give a
# little overlap (and so we don't miss anything if a tick drifts a few
# minutes late).
WINDOW_MIN = 75

# IST is the user's home timezone; the bot logs are in UTC (the server's
# local time). We'll convert to IST for the human-facing timestamp.
IST = timezone(timedelta(hours=5, minutes=30))

# Maximum number of "noisy" lines we'll allow in the summary before we
# truncate. Keeps the message under Discord's 2000-char limit.
MAX_LINES_IN_SUMMARY = 25

# ── Helpers ────────────────────────────────────────────────────────────
LINE_RE = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) "
    r"\[(?P<level>[A-Z]+)\s*\] "
    r"(?P<src>\S+)\s+"
    r"(?P<msg>.*)$"
)


def ssh_cat_log() -> str:
    """Tail the log file from EC2. Streams to stdout via SSH."""
    cmd = [
        "ssh",
        "-i", PEM,
        "-o", "StrictHostKeyChecking=no",
        "-o", "BatchMode=yes",
        EC2_HOST,
        f"tail -n 4000 {LOG_PATH} 2>/dev/null || echo __LOG_READ_FAIL__",
    ]
    try:
        out = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30
        )
    except subprocess.TimeoutExpired:
        return "__SSH_TIMEOUT__"
    if out.returncode != 0 and not out.stdout:
        return "__SSH_FAIL__"
    return out.stdout


def ssh_check_container(container: str) -> dict | None:
    """Quick docker inspect fallback for live state.

    Returns {"status": str, "health": str | None} if the container exists,
    or None if it can't be reached. Used when the log file is too stale
    to make reliable state calls.
    """
    cmd = [
        "ssh",
        "-i", PEM,
        "-o", "StrictHostKeyChecking=no",
        "-o", "BatchMode=yes",
        EC2_HOST,
        f"docker inspect --format "
        f"'{{{{.State.Status}}}}|{{{{.State.Health.Status}}}}' {container} 2>/dev/null",
    ]
    try:
        out = subprocess.run(
            cmd, capture_output=True, text=True, timeout=15
        )
    except subprocess.TimeoutExpired:
        return None
    if out.returncode != 0 or not out.stdout.strip():
        return None
    parts = out.stdout.strip().split("|")
    return {
        "status": parts[0] if parts else "unknown",
        "health": parts[1] if len(parts) > 1 else None,
    }


def parse_log(text: str) -> list[dict]:
    """Parse lines of trading.log into structured events."""
    events: list[dict] = []
    for line in text.splitlines():
        if not line or line.startswith("__"):
            continue
        m = LINE_RE.match(line)
        if not m:
            continue
        try:
            ts = datetime.strptime(m["ts"], "%Y-%m-%d %H:%M:%S").replace(
                tzinfo=timezone.utc
            )
        except ValueError:
            continue
        events.append({
            "ts": ts,
            "level": m["level"].strip(),
            "src": m["src"].strip(),
            "msg": m["msg"].rstrip(),
        })
    return events


def in_window(ev: dict, cutoff: datetime) -> bool:
    return ev["ts"] >= cutoff


def classify(ev: dict) -> str:
    """Return a category tag for the event. Used for the bucketed summary."""
    msg = ev["msg"]
    src = ev["src"]
    if "FATAL" in ev["level"] or "CRITICAL" in ev["level"]:
        return "critical"
    if ev["level"] == "ERROR":
        return "error"
    if "Connect" in msg and "MT5" in msg:
        return "lifecycle_mt5"
    if "Trading Bot V2 started" in msg or "Trading Bot V2 stopped" in msg:
        return "lifecycle_bot"
    if "DEGRADED" in msg or "Telegram not" in msg:
        return "lifecycle_degraded"
    if "RiskManager" in src and ("peak equity" in msg or "drawdown" in msg.lower() or "halt" in msg.lower() or "trip" in msg.lower() or "block" in msg.lower()):
        return "risk"
    if "PropFirmGuard" in src:
        return "risk"
    if "PositionMonitor" in src and ("closed" in msg.lower() or "opened" in msg.lower() or "modify" in msg.lower() or "stop" in msg.lower()):
        return "position"
    if "executor" in src.lower() and ("order" in msg.lower() or "fill" in msg.lower()):
        return "position"
    if "news" in src.lower() and ("block" in msg.lower() or "release" in msg.lower() or "filter" in msg.lower()):
        return "news"
    if "signal" in src.lower() and ("signal" in msg.lower() or "entry" in msg.lower() or "skip" in msg.lower()):
        return "signal"
    if "strategy_health" in src.lower() or "StrategyHealth" in src:
        return "strategy_health"
    if ev["level"] == "WARNING":
        return "warning"
    return ""  # boring INFO line, drop


def fmt_time_ist(ts: datetime) -> str:
    return ts.astimezone(IST).strftime("%H:%M")


def main() -> int:
    raw = ssh_cat_log()
    if raw.startswith("__SSH_TIMEOUT__"):
        print(
            "**Trading bot hourly digest — ERROR**\n\n"
            "SSH to the bot's EC2 instance timed out. "
            "Is the instance up? Is the PEM key still at the expected path?"
        )
        return 1
    if raw.startswith("__SSH_FAIL__") or raw.startswith("__LOG_READ_FAIL__"):
        print(
            "**Trading bot hourly digest — ERROR**\n\n"
            f"Could not read `{LOG_PATH}` on the bot's EC2. "
            "The SSH session worked but `tail` failed (or returned no output)."
        )
        return 1

    events = parse_log(raw)
    if not events:
        print(
            "**Trading bot hourly digest — no parseable log lines**\n\n"
            f"SSH worked but no lines matched the expected format in {LOG_PATH}. "
            "Likely the log file was rotated/empty, or the format changed."
        )
        return 1

    # "Now" should be wall clock, not the last log line timestamp. The last
    # log line is often minutes/hours behind the bot's actual state because
    # Python's FileHandler is block-buffered on a non-TTY process. The window
    # cutoff uses wall-now so the digest always covers a real 75-min slice.
    wall_now_utc = datetime.now(timezone.utc)
    cutoff = wall_now_utc - timedelta(minutes=WINDOW_MIN)
    window = [e for e in events if in_window(e, cutoff)]
    last_event_utc = events[-1]["ts"]
    if not window:
        # No activity in the window — emit a quiet heartbeat
        print(
            f"**Trading bot hourly digest — {fmt_time_ist(wall_now_utc)} IST**\n\n"
            f"No log activity in the last {WINDOW_MIN}m "
            f"(last log line: {last_event_utc.astimezone(IST).strftime('%H:%M:%S IST')}). "
            "If the bot has been running, this is normal. If you expected activity, "
            "check `#trading-bot` and Slack for the last alert."
        )
        return 0

    # Bucket the events
    buckets: dict[str, list[dict]] = {}
    for e in window:
        cat = classify(e)
        if not cat:
            continue
        buckets.setdefault(cat, []).append(e)

    level_counts = Counter(e["level"] for e in window)

    # Health pulse: derive from the MOST RECENT state, not whether an event
    # happened anywhere in the window. The bot can be both started and stopped
    # in the window — the latest event wins.
    def latest_match(pred) -> dict | None:
        for e in reversed(window):
            if pred(e):
                return e
        return None

    last_bot_started = latest_match(
        lambda e: "Trading Bot V2 started" in e["msg"]
    )
    last_bot_stopped = latest_match(
        lambda e: "Trading Bot V2 stopped" in e["msg"]
    )
    last_mt5_connect = latest_match(
        lambda e: "Connected to MT5" in e["msg"] and "Authorization failed" not in e["msg"]
    )
    last_mt5_fail = latest_match(
        lambda e: "MT5 connect attempt" in e["msg"] and "failed" in e["msg"]
    )
    degraded_lines = [e for e in window if "DEGRADED" in e["msg"]]

    # Decide current state. If the most recent lifecycle event is a stop,
    # the bot is down. Otherwise it's up.
    if last_bot_stopped and (
        not last_bot_started or last_bot_stopped["ts"] > last_bot_started["ts"]
    ):
        bot_state = "🔴 Bot down"
    elif last_bot_started:
        bot_state = "🟢 Bot up"
    else:
        bot_state = "🟡 No bot lifecycle in window"

    if last_mt5_connect and (
        not last_mt5_fail or last_mt5_connect["ts"] > last_mt5_fail["ts"]
    ):
        mt5_state = "🟢 MT5 connected"
    elif last_mt5_fail:
        # Count recent failures (last 15 min) — historical "failed" lines
        # shouldn't taint the current-state indicator
        recent_cutoff = wall_now_utc - timedelta(minutes=15)
        recent_fails = [
            e for e in window
            if "MT5 connect attempt" in e["msg"] and "failed" in e["msg"]
            and e["ts"] >= recent_cutoff
        ]
        if recent_fails:
            mt5_state = f"🔴 MT5 failing ({len(recent_fails)} in last 15m)"
        else:
            mt5_state = "🟡 MT5 unknown"
    else:
        mt5_state = "🟡 MT5 unknown"

    # Header
    ist_now = wall_now_utc.astimezone(IST)
    out: list[str] = [
        f"**Trading bot hourly digest — {ist_now.strftime('%H:%M IST, %d %b')}**",
        f"Window: last {WINDOW_MIN}m · "
        f"{level_counts.get('INFO', 0)} INFO / "
        f"{level_counts.get('WARNING', 0)} WARN / "
        f"{level_counts.get('ERROR', 0)} ERR / "
        f"{level_counts.get('CRITICAL', 0)} CRIT",
    ]

    # Log lag: how stale is the last log line relative to wall clock?
    # Python's FileHandler on a TTY-detached process is block-buffered, so the log
    # can lag the actual bot state by many minutes. If the lag is large, we
    # call it out so the user doesn't read too much into "no events recently".
    lag_min = int((wall_now_utc - last_event_utc).total_seconds() // 60)
    if lag_min > 5:
        out.append(
            f"_⚠️ Log is {lag_min}m stale (last flush at "
            f"{last_event_utc.astimezone(IST).strftime('%H:%M:%S IST')}; "
            f"Python FileHandler is block-buffered on a non-TTY process). "
            f"Crashes/restarts still flush immediately._"
        )

    # Live state override: when the log is too stale, the "bot_state" /
    # "mt5_state" derived from log events is unreliable. Cross-check with
    # `docker inspect` for the actual container state, and prefer that.
    # Threshold of 5m matches the stale-warning threshold above, so a stale
    # log always means we cross-check live state too.
    used_live_check = False
    if lag_min > 5:
        live_bot = ssh_check_container("trading-bot-v2")
        live_mt5 = ssh_check_container("metatrader5")
        if live_bot is not None:
            used_live_check = True
            cs = live_bot["status"]
            ch = live_bot.get("health") or "no-healthcheck"
            if cs == "running" and ch in ("healthy", "starting", "no-healthcheck"):
                bot_state = f"🟢 Bot up (live check: {cs}/{ch})"
            elif cs == "running":
                bot_state = f"🟡 Bot running but unhealthy (live check: {ch})"
            elif cs in ("exited", "dead", "paused"):
                bot_state = f"🔴 Bot {cs} (live check)"
            else:
                bot_state = f"🟡 Bot state unknown (live check: {cs})"
        if live_mt5 is not None:
            used_live_check = True
            if live_mt5["status"] == "running":
                mt5_state = "🟢 MT5 container up (live check)"
            else:
                mt5_state = f"🔴 MT5 container {live_mt5['status']} (live check)"
        if used_live_check:
            out.append(
                f"_ℹ️ State above from `docker inspect` (log is {lag_min}m stale)._"
            )

    # Health pulse
    pulse = [bot_state, mt5_state]
    if degraded_lines:
        pulse.append(f"🟡 DEGRADED state ({len(degraded_lines)} mentions)")
    out.append(" · ".join(pulse))

    # Restarts in the window: count "started" events
    starts_in_window = [
        e for e in window
        if "Trading Bot V2 started" in e["msg"]
    ]
    stops_in_window = [e for e in window if "Trading Bot V2 stopped" in e["msg"]]
    if len(starts_in_window) > 1 or (stops_in_window and starts_in_window):
        out.append(
            f"_⚠️ {len(starts_in_window)} bot restart(s) and {len(stops_in_window)} "
            f"stop(s) in window — see warnings below for root cause._"
        )

    # Critical / Errors first
    crit = buckets.get("critical", [])
    errs = buckets.get("error", [])
    if crit or errs:
        out.append("")
        out.append("**Critical / Errors**")
        lines = []
        for e in (crit + errs)[-MAX_LINES_IN_SUMMARY:]:
            lines.append(
                f"• `{fmt_time_ist(e['ts'])}` [{e['level']:8}] {e['msg']}"
            )
        out.extend(lines)
        if len(crit) + len(errs) > MAX_LINES_IN_SUMMARY:
            out.append(f"…({len(crit) + len(errs) - MAX_LINES_IN_SUMMARY} more suppressed)")

    # Warnings (short list)
    warns = buckets.get("warning", [])
    if warns:
        out.append("")
        out.append(f"**Warnings** ({len(warns)})")
        for e in warns[-MAX_LINES_IN_SUMMARY:]:
            out.append(
                f"• `{fmt_time_ist(e['ts'])}` {e['msg'][:180]}"
                + ("…" if len(e["msg"]) > 180 else "")
            )
        if len(warns) > MAX_LINES_IN_SUMMARY:
            out.append(
                f"…({len(warns) - MAX_LINES_IN_SUMMARY} more suppressed)"
            )

    # Risk events (DD, halts, trips)
    risk = buckets.get("risk", [])
    if risk:
        out.append("")
        out.append("**Risk events**")
        for e in risk[-10:]:
            out.append(
                f"• `{fmt_time_ist(e['ts'])}` {e['msg'][:200]}"
                + ("…" if len(e["msg"]) > 200 else "")
            )

    # Positions
    pos = buckets.get("position", [])
    if pos:
        out.append("")
        out.append(f"**Position events** ({len(pos)})")
        for e in pos[-10:]:
            out.append(
                f"• `{fmt_time_ist(e['ts'])}` {e['msg'][:200]}"
                + ("…" if len(e["msg"]) > 200 else "")
            )

    # News blocks
    news = buckets.get("news", [])
    if news:
        out.append("")
        out.append(f"**News filter events** ({len(news)})")
        for e in news[-5:]:
            out.append(
                f"• `{fmt_time_ist(e['ts'])}` {e['msg'][:200]}"
                + ("…" if len(e["msg"]) > 200 else "")
            )

    # Strategy signals (compressed)
    sig = buckets.get("signal", [])
    if sig:
        out.append("")
        out.append(f"**Signals** ({len(sig)})")
        for e in sig[-5:]:
            out.append(
                f"• `{fmt_time_ist(e['ts'])}` {e['msg'][:200]}"
                + ("…" if len(e["msg"]) > 200 else "")
            )

    # Strategy health (any halting signals)
    sh = buckets.get("strategy_health", [])
    if sh:
        out.append("")
        out.append(f"**Strategy health** ({len(sh)})")
        for e in sh[-5:]:
            out.append(
                f"• `{fmt_time_ist(e['ts'])}` {e['msg'][:200]}"
                + ("…" if len(e["msg"]) > 200 else "")
            )

    # Tail
    out.append("")
    out.append(
        f"_Source: `{LOG_PATH}` on `i-095ac6e00402283e5` · "
        f"last log line: {events[-1]['ts'].astimezone(IST).strftime('%H:%M:%S IST')}_"
    )

    text = "\n".join(out)
    # Discord limit safety — drop the source footer first (least useful), then
    # truncate at a line boundary if we're still over.
    if len(text) > 1900:
        # Drop the trailing source/cron line — it's nice-to-have
        lines = text.split("\n")
        while lines and len("\n".join(lines)) > 1900 and lines[-1].startswith("_Source:"):
            lines.pop()
        text = "\n".join(lines)
    if len(text) > 1900:
        text = text[:1900] + "\n…(truncated for Discord limit)"
    print(text)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(
            "**Trading bot hourly digest — UNEXPECTED ERROR**\n\n"
            f"```\n{type(e).__name__}: {e}\n```"
        )
        sys.exit(1)
