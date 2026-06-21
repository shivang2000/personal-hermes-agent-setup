#!/usr/bin/env python3
"""Post a short Hermes Agent Discord-integration Twitter/X series.

Runs once per cron tick, posting the next unposted item and persisting progress.
Set HERMES_DRY_RUN=1 to validate without posting.
"""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
from datetime import datetime, timezone

STATE_PATH = pathlib.Path.home() / ".hermes" / "cron" / "twitter_discord_series_state.json"

POSTS = [
    "Been playing around with Hermes Agent for a couple of days now. Today I’ll share a few quick findings from setting it up across chat platforms and using it for real workflows. Stay tuned — this journey is getting fun. #HermesAgent #BuildInPublic",
    "First stop was Telegram. Setup was surprisingly easy: fast to connect, intuitive to use, and familiar enough that I could start chatting with Hermes Agent from a mobile-first interface almost immediately.",
    "Then I moved the same Hermes Agent workflow into Discord. I’m literally building and scheduling this series from a Discord thread right now, and it already feels closer to a shared workspace than a simple chatbot.",
    "My quick take: Telegram is great for lightweight agent chats. Discord gives Hermes Agent more room to breathe — threads, channels, reactions, and cleaner context separation for work that lasts longer than one message.",
    "The biggest difference is richness. Discord has better styling, clearer organization, more interaction options, and a UI that feels built for collaboration. For agent workflows, that structure matters more than I expected.",
    "Next experiment: install Hermes Agent on another laptop too — one personal, one work — and see how well I can manage both contexts together across the machines I actually live in every day.",
    "After that, I want to try the fun stuff: spin up cloud terminals, route daily tasks through Hermes, and see how far this multi-device + Discord setup can go. Still early, but it’s already becoming a real workflow.",
]


def load_state() -> dict:
    if not STATE_PATH.exists():
        return {"next_index": 0, "posted": []}
    try:
        return json.loads(STATE_PATH.read_text())
    except Exception:
        # Preserve the broken file for debugging rather than overwriting it silently.
        raise RuntimeError(f"Could not parse state file: {STATE_PATH}")


def save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2, sort_keys=True))
    tmp.replace(STATE_PATH)


def main() -> int:
    for i, post in enumerate(POSTS, start=1):
        if len(post) > 280:
            print(f"Post {i} is {len(post)} chars, exceeds 280", file=sys.stderr)
            return 2

    state = load_state()
    idx = int(state.get("next_index", 0))
    if idx >= len(POSTS):
        return 0  # all done; stay silent

    text = POSTS[idx]
    if os.environ.get("HERMES_DRY_RUN") == "1":
        print(json.dumps({"dry_run": True, "next_index": idx, "chars": len(text), "text": text}, ensure_ascii=False))
        return 0

    # Do not use shell=True; avoids quoting issues and keeps secrets out of command strings.
    result = subprocess.run(["xurl", "post", text], text=True, capture_output=True, timeout=120)
    if result.returncode != 0:
        print("xurl post failed", file=sys.stderr)
        if result.stdout:
            print(result.stdout, file=sys.stderr)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result.returncode

    try:
        payload = json.loads(result.stdout or "{}")
    except json.JSONDecodeError:
        payload = {"raw_stdout": result.stdout}

    posted_entry = {
        "index": idx,
        "posted_at_utc": datetime.now(timezone.utc).isoformat(),
        "tweet_id": payload.get("data", {}).get("id"),
        "text": text,
    }
    state.setdefault("posted", []).append(posted_entry)
    state["next_index"] = idx + 1
    save_state(state)
    remaining = len(POSTS) - state["next_index"]
    print(
        f"Hermes Twitter/X cron ran: posted item {idx + 1}/{len(POSTS)} "
        f"(tweet_id={posted_entry.get('tweet_id')}). Remaining: {remaining}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
