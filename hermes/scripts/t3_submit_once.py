#!/usr/bin/env python3
"""Submit the already-entered T3 Code prompt by pressing Return once."""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

APP_BUNDLE_ID = "com.t3tools.t3code"
APP_NAME = "T3 Code (Nightly)"


def cua(tool: str, payload: dict) -> dict:
    proc = subprocess.run(
        ["cua-driver", "call", tool, json.dumps(payload)],
        text=True,
        capture_output=True,
        timeout=60,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"cua-driver {tool} failed ({proc.returncode}): "
            f"{proc.stderr.strip() or proc.stdout.strip()}"
        )
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON from cua-driver {tool}: {proc.stdout[:500]}") from exc


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    apps = cua("list_apps", {}).get("apps", [])
    app = next(
        (
            item
            for item in apps
            if item.get("bundle_id") == APP_BUNDLE_ID and item.get("running")
        ),
        None,
    )
    if not app:
        raise RuntimeError(f"{APP_NAME} is not running; Return was not pressed")

    pid = int(app["pid"])
    windows = [
        window
        for window in cua("list_windows", {}).get("windows", [])
        if int(window.get("pid", -1)) == pid
        and window.get("layer") == 0
        and window.get("title")
    ]
    if not windows:
        raise RuntimeError(f"No usable {APP_NAME} window found; Return was not pressed")

    # Prefer the visible, largest titled app window.
    window = max(
        windows,
        key=lambda item: (
            bool(item.get("is_on_screen")),
            float(item.get("bounds", {}).get("width", 0))
            * float(item.get("bounds", {}).get("height", 0)),
        ),
    )
    window_id = int(window["window_id"])

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    screenshot_dir = Path.home() / ".hermes" / "cache" / "screenshots"
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    before_path = screenshot_dir / f"t3-submit-before-{stamp}.png"
    after_path = screenshot_dir / f"t3-submit-after-{stamp}.png"

    # Capture immediately before acting to confirm the target exists.
    cua(
        "get_window_state",
        {
            "pid": pid,
            "window_id": window_id,
            "max_elements": 600,
            "screenshot_out_file": str(before_path),
        },
    )

    if args.dry_run:
        print(
            json.dumps(
                {
                    "status": "dry-run-ok",
                    "app": APP_NAME,
                    "pid": pid,
                    "window_id": window_id,
                    "before_screenshot": str(before_path),
                    "pressed_return": False,
                }
            )
        )
        return 0

    # Safety invariant: invoke press_key exactly once; never retry automatically.
    result = cua(
        "press_key",
        {
            "pid": pid,
            "window_id": window_id,
            "key": "return",
            "delivery_mode": "background",
            "session": f"t3-submit-{stamp}",
        },
    )

    time.sleep(2)
    cua(
        "get_window_state",
        {
            "pid": pid,
            "window_id": window_id,
            "max_elements": 600,
            "screenshot_out_file": str(after_path),
        },
    )

    print(
        json.dumps(
            {
                "status": "return-pressed-once",
                "app": APP_NAME,
                "pid": pid,
                "window_id": window_id,
                "driver_result": result,
                "before_screenshot": str(before_path),
                "after_screenshot": str(after_path),
            }
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}), file=sys.stderr)
        raise SystemExit(1)
