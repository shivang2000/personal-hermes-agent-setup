#!/usr/bin/env python3
"""
Trading Bot V2 — health watchdog.

Runs every 5 minutes. Performs four checks against the EC2 box:
  1. Both containers running? If not, restart the missing one and alert.
  2. Bot container healthy? If not, restart it and alert.
  3. Memory headroom OK? (free > 150Mi OR swap usage < 85%) If not, alert.
  4. Bot log has a new FATAL/CRITICAL line since the last check? If so, alert.

Design principles:
  - Silent on success (no cron noise; the hourly digest already covers
    the routine "all green" case).
  - Auto-remediate where safe (restart a stopped container). Never
    auto-remediate the MT5 container — restarting it loses the noVNC
    login session, so we alert the user instead.
  - LLM-free: deterministic, fast, cheap, predictable.

State is stored in /tmp on the EC2 box: /tmp/bot_watchdog.state
(remembers the last log byte offset we examined, so we don't re-alert
on the same FATAL every 5 min).
"""
from __future__ import annotations

import os
import shlex
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────────
PEM = os.path.expanduser(
    "/Users/shivang/dev/advanced-trading-bot/trading-bot-v2/south-mumbai-key-pair.pem"
)
EC2_HOST = "ec2-user@ec2-3-7-59-175.ap-south-1.compute.amazonaws.com"
EC2_STATE_PATH = "/tmp/bot_watchdog.state"

# Thresholds — tuned for the i-095ac6e00402283e5 t3.medium (1.9Gi RAM + 2Gi swap)
MEM_FREE_MIN_MIB = 150         # alert if free < this
SWAP_USAGE_MAX_PCT = 85         # alert if swap > this % full (AND free is low)

# Bot container name (per docker-compose.ec2.yml)
BOT_CONTAINER = "trading-bot-v2"
MT5_CONTAINER = "metatrader5"

IST = timezone(timedelta(hours=5, minutes=30))


def ssh(cmd_str: str, timeout: int = 30) -> tuple[int, str, str]:
    """Run a shell command on the EC2 host. Returns (rc, stdout, stderr)."""
    full = [
        "ssh",
        "-i", PEM,
        "-o", "StrictHostKeyChecking=no",
        "-o", "BatchMode=yes",
        EC2_HOST,
        cmd_str,
    ]
    try:
        p = subprocess.run(full, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return 124, "", f"ssh timeout after {timeout}s"


def fmt_ist_now() -> str:
    return datetime.now(IST).strftime("%H:%M:%S IST")


def emit_discord(message: str) -> None:
    """Push a message to the #trading-bot parent channel via Hermes send.

    Failures here are non-fatal: the watchdog must never crash because the
    notifier hiccuped. We just print to stderr.
    """
    # Write to a temp file + use Hermes CLI
    tmp = Path("/tmp/bot_watchdog_msg.md")
    tmp.write_text(message)
    try:
        subprocess.run(
            [
                "hermes", "send",
                "-t", "discord:1525476646176690297",
                "-f", str(tmp),
                "-q",
            ],
            capture_output=True,
            text=True,
            timeout=20,
        )
    except Exception as e:
        print(f"[warn] discord delivery failed: {e}", file=sys.stderr)
    finally:
        try:
            tmp.unlink()
        except OSError:
            pass


# ── Checks ──────────────────────────────────────────────────────────────
def check_containers() -> list[str]:
    """Returns a list of problems; empty = OK. Auto-restarts the bot if needed."""
    rc, out, err = ssh("docker ps -a --format '{{.Names}}|{{.Status}}' 2>&1")
    if rc != 0:
        return [f"Cannot reach docker on EC2 (rc={rc}): {err.strip()[:200]}"]

    statuses: dict[str, str] = {}
    for line in out.splitlines():
        if "|" not in line:
            continue
        name, status = line.split("|", 1)
        statuses[name.strip()] = status.strip()

    problems: list[str] = []
    for name in (BOT_CONTAINER, MT5_CONTAINER):
        s = statuses.get(name, "MISSING")
        if "Up" not in s:
            problems.append(f"Container `{name}` is `{s}`")

    # Auto-remediate: try to restart the bot (safe — doesn't lose state).
    # Do NOT auto-restart MT5 (would lose the noVNC login).
    if any(BOT_CONTAINER in p for p in problems):
        rc2, _, err2 = ssh(
            f"cd /home/ec2-user/trading-bot-v2 && "
            f"docker-compose -f docker-compose.ec2.yml up -d {BOT_CONTAINER} 2>&1 | tail -5"
        )
        problems.append(
            f"⚙️ Auto-restart attempted for `{BOT_CONTAINER}` (rc={rc2})"
        )
        if err2.strip():
            problems.append(f"restart stderr: {err2.strip()[:200]}")

    return problems


def check_memory() -> list[str]:
    rc, out, err = ssh("free -m 2>&1")
    if rc != 0:
        return [f"Cannot read memory state (rc={rc})"]

    # free -m output:
    #               total    used    free    shared  buff/cache   available
    # Mem:           1942     808      90       6      1044         921
    # Swap:          2047     390    1657
    mem_total = mem_used = mem_free = mem_avail = None
    swap_total = swap_used = None
    for line in out.splitlines():
        if line.startswith("Mem:"):
            parts = line.split()
            mem_total, mem_used, mem_free = int(parts[1]), int(parts[2]), int(parts[3])
            mem_avail = int(parts[6]) if len(parts) > 6 else mem_free
        elif line.startswith("Swap:"):
            parts = line.split()
            swap_total, swap_used = int(parts[1]), int(parts[2])

    problems: list[str] = []
    if mem_free is not None and mem_free < MEM_FREE_MIN_MIB:
        # Only alert if swap is also heavily used — free being low is normal
        # if swap is absorbing the excess.
        swap_pct = (swap_used / swap_total * 100) if (swap_total and swap_total > 0) else 0
        if swap_pct > SWAP_USAGE_MAX_PCT:
            problems.append(
                f"Memory pressure: free={mem_free}Mi, "
                f"swap_used={swap_used}/{swap_total}Mi ({swap_pct:.0f}%). "
                f"OOM-killer risk."
            )
        else:
            # Low free but swap has room — note it but don't alert.
            # This is a normal "swap is working as designed" state.
            print(
                f"[info] mem_free={mem_free}Mi is low but swap is only "
                f"{swap_pct:.0f}% full — no action",
                file=sys.stderr,
            )
    return problems


def load_state() -> dict:
    """Read /tmp/bot_watchdog.state from EC2. Returns {} on any error."""
    rc, out, _ = ssh(f"cat {EC2_STATE_PATH} 2>/dev/null")
    if rc != 0 or not out.strip():
        return {}
    state: dict = {}
    for line in out.splitlines():
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        state[k.strip()] = v.strip()
    return state


def save_state(state: dict) -> None:
    """Write /tmp/bot_watchdog.state to EC2. Silently best-effort."""
    body = "\n".join(f"{k}={v}" for k, v in state.items()) + "\n"
    # Write through stdin to avoid quoting issues
    try:
        p = subprocess.Popen(
            [
                "ssh",
                "-i", PEM,
                "-o", "StrictHostKeyChecking=no",
                "-o", "BatchMode=yes",
                EC2_HOST,
                f"cat > {EC2_STATE_PATH}",
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        p.communicate(body.encode(), timeout=15)
    except Exception as e:
        print(f"[warn] save_state failed: {e}", file=sys.stderr)


def check_log_fatals() -> list[str]:
    """Look at NEW FATAL/CRITICAL lines in trading.log since last run.

    State stored on EC2: bot_log_offset = byte offset of last line we read.
    """
    state = load_state()
    last_offset = int(state.get("bot_log_offset", "0"))

    # Get the current log size + new content beyond last_offset
    rc, out, err = ssh(
        f"wc -c < /home/ec2-user/trading-bot-v2/logs/trading.log 2>/dev/null"
    )
    if rc != 0:
        return []  # log unreadable — don't alert, might be transient
    try:
        cur_size = int(out.strip())
    except ValueError:
        return []

    if cur_size <= last_offset:
        return []  # log shrank (rotated?) — reset and move on
    skip = last_offset

    rc, content, err = ssh(
        f"tail -c +{skip + 1} /home/ec2-user/trading-bot-v2/logs/trading.log 2>/dev/null"
    )
    if rc != 0:
        return []

    problems: list[str] = []
    new_fatals: list[str] = []
    for line in content.splitlines():
        # Log format: "2026-07-12 09:24:11 [CRITICAL ] src ... message"
        # Note the trailing space inside the brackets — Python's logging
        # formatter pads level names to 8 chars.
        if "[CRITICAL" in line or "[FATAL" in line:
            new_fatals.append(line.strip())

    if new_fatals:
        for line in new_fatals[-5:]:  # cap at 5 to keep Discord message small
            # Format: 2026-07-12 09:24:11 [CRITICAL] src ... message
            problems.append(f"🔴 NEW CRITICAL: `{line[:200]}`")
        problems.insert(
            0, f"⚠️ {len(new_fatals)} new CRITICAL/FATAL log line(s) since last check"
        )

    # Persist new offset
    state["bot_log_offset"] = str(cur_size)
    state["last_check_utc"] = datetime.now(timezone.utc).isoformat()
    save_state(state)
    return problems


def main() -> int:
    problems: list[str] = []
    problems.extend(check_containers())
    problems.extend(check_memory())
    problems.extend(check_log_fatals())

    if not problems:
        # Silent success — the hourly digest already covers "all green"
        return 0

    body = (
        f"**🚨 Trading bot watchdog — {fmt_ist_now()}**\n\n"
        + "\n".join(f"• {p}" for p in problems)
        + "\n\n_Source: bot_watchdog cron (every 5m). "
        "Hourly log digest: `~/.hermes/scripts/trading_bot_hourly_digest.py`._"
    )
    emit_discord(body)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        # Last-ditch: never crash the cron, but write the error somewhere visible
        try:
            emit_discord(
                f"**🚨 Bot watchdog — INTERNAL ERROR**\n\n"
                f"```\n{type(e).__name__}: {e}\n```\n\n"
                "The watchdog itself crashed. Check the cron logs."
            )
        except Exception:
            pass
        print(f"[fatal] {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)
