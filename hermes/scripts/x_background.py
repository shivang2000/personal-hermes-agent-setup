#!/usr/bin/env python3
"""Headless X.com automation using an isolated Playwright profile.

One-time setup (visible window; user logs in manually):
    python3 x_background.py login

Background commands:
    python3 x_background.py check
    python3 x_background.py search "query" 10
    python3 x_background.py profile @handle 10
    python3 x_background.py capture URL /tmp/source.png [--selector CSS]
    python3 x_background.py post "text" [--image /tmp/source.png]
    python3 x_background.py reply POST_URL "text" [--image /tmp/source.png]
    python3 x_background.py quote POST_URL "text" [--image /tmp/source.png]

The profile is separate from Arc, all normal commands are headless, and a
process-wide file lock prevents overlapping cron jobs from racing each other.
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import sys
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from urllib.parse import quote

from playwright.sync_api import BrowserContext, Page, TimeoutError as PlaywrightTimeoutError, sync_playwright

PROFILE_DIR = Path.home() / ".hermes" / "browser-profiles" / "x-automation"
LOCK_PATH = Path.home() / ".hermes" / "locks" / "x-background.lock"
DEFAULT_HANDLE = "shivangchheda22"
VIEWPORT = {"width": 1440, "height": 1000}


def emit(value: Any, exit_code: int = 0) -> None:
    print(json.dumps(value, indent=2, ensure_ascii=False))
    raise SystemExit(exit_code)


@contextmanager
def exclusive_lock(timeout: float = 90.0):
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOCK_PATH.open("w") as fh:
        deadline = time.monotonic() + timeout
        while True:
            try:
                fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise TimeoutError("another X automation job still holds the lock")
                time.sleep(0.5)
        try:
            fh.write(str(os.getpid()))
            fh.flush()
            yield
        finally:
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)


@contextmanager
def browser_session(headless: bool = True):
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            str(PROFILE_DIR),
            executable_path=p.chromium.executable_path,
            headless=headless,
            viewport=VIEWPORT,
            locale="en-US",
            args=["--disable-background-networking"],
        )
        try:
            page = context.pages[0] if context.pages else context.new_page()
            page.set_default_timeout(45_000)
            yield context, page
        finally:
            context.close()


def goto(page: Page, url: str, wait_ms: int = 1500) -> None:
    page.goto(url, wait_until="domcontentloaded", timeout=45_000)
    page.wait_for_timeout(wait_ms)


def logged_in(page: Page) -> bool:
    goto(page, "https://x.com/home", 2500)
    if "/login" in page.url or "/i/flow/login" in page.url:
        return False
    return page.locator('[data-testid="SideNav_NewTweet_Button"], [data-testid="tweetTextarea_0"]').count() > 0


def require_login(page: Page) -> None:
    if not logged_in(page):
        raise RuntimeError(
            "isolated X profile is not logged in; run: "
            "python3 ~/.hermes/scripts/x_background.py login"
        )


def cmd_login() -> None:
    with exclusive_lock(), browser_session(headless=False) as (_, page):
        goto(page, "https://x.com/login", 1000)
        print("A separate X automation window is open.")
        print("Log in manually, then return here and press Enter. Do not paste credentials into Hermes.")
        input()
        ok = logged_in(page)
        emit({"logged_in": ok, "profile": str(PROFILE_DIR)}, 0 if ok else 2)


def cmd_check() -> None:
    with exclusive_lock(), browser_session(headless=True) as (_, page):
        ok = logged_in(page)
        emit({
            "logged_in": ok,
            "headless": True,
            "profile": str(PROFILE_DIR),
            "url": page.url,
            "title": page.title(),
        }, 0 if ok else 2)


def extract_articles(page: Page, limit: int) -> list[dict[str, Any]]:
    articles = page.locator("article")
    count = min(articles.count(), limit)
    out: list[dict[str, Any]] = []
    for i in range(count):
        article = articles.nth(i)
        text_loc = article.locator('[data-testid="tweetText"]')
        time_loc = article.locator("time")
        links = article.locator('a[href*="/status/"]')
        user = article.locator('[data-testid="User-Name"]')
        metrics = article.locator('[role="group"] button')
        href = links.first.get_attribute("href") if links.count() else ""
        out.append({
            "text": text_loc.first.inner_text() if text_loc.count() else "",
            "time": time_loc.first.get_attribute("datetime") if time_loc.count() else "",
            "link": f"https://x.com{href}" if href and href.startswith("/") else (href or ""),
            "author": user.first.inner_text() if user.count() else "",
            "metrics": [metrics.nth(j).get_attribute("aria-label") for j in range(metrics.count()) if metrics.nth(j).get_attribute("aria-label")],
        })
    return out


def cmd_search(query_text: str, limit: int) -> None:
    with exclusive_lock(), browser_session(headless=True) as (_, page):
        require_login(page)
        goto(page, f"https://x.com/search?q={quote(query_text)}&f=live", 3000)
        page.mouse.wheel(0, 900)
        page.wait_for_timeout(1200)
        emit(extract_articles(page, limit))


def cmd_profile(handle: str, limit: int) -> None:
    handle = handle.lstrip("@")
    with exclusive_lock(), browser_session(headless=True) as (_, page):
        require_login(page)
        goto(page, f"https://x.com/{handle}", 3000)
        emit(extract_articles(page, limit))


def cmd_capture(url: str, output: str, selector: str | None) -> None:
    out = Path(output).expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    with exclusive_lock(), browser_session(headless=True) as (_, page):
        goto(page, url, 2500)
        if selector:
            target = page.locator(selector).first
            target.wait_for(state="visible", timeout=15_000)
            target.screenshot(path=str(out))
        else:
            page.screenshot(path=str(out), full_page=False)
        if not out.exists() or out.stat().st_size == 0:
            raise RuntimeError("screenshot file was not created")
        emit({"status": "CAPTURED", "path": str(out), "bytes": out.stat().st_size, "url": page.url})


def compose(page: Page, text: str, image: str | None = None) -> None:
    # The /compose/post page has a React state issue in headless mode where the
    # Post button never enables even after typing. The inline composer on the
    # home timeline works correctly. Use that instead.
    goto(page, "https://x.com/home", 2500)
    box = page.locator('[data-testid="tweetTextarea_0"]').first
    box.wait_for(state="visible")
    box.click()
    page.wait_for_timeout(300)
    page.keyboard.type(text, delay=5)
    page.wait_for_timeout(500)
    if image:
        image_path = Path(image).expanduser().resolve()
        if not image_path.is_file():
            raise FileNotFoundError(str(image_path))
        file_input = page.locator('[data-testid="fileInput"], input[type="file"]').first
        file_input.set_input_files(str(image_path))
        # X clears the native file input after ingesting media. Verify the rendered
        # attachment instead; current UI exposes an attachments container, blob
        # preview, and a "Remove media" control (older builds used removeImage).
        page.wait_for_function(
            """() => !!(
                document.querySelector('[data-testid="attachments"] img') ||
                document.querySelector('[data-testid="attachments"] video') ||
                document.querySelector('img[src^="blob:https://x.com/"]') ||
                document.querySelector('button[aria-label="Remove media"]') ||
                document.querySelector('[data-testid="removeImage"]')
            )""",
            timeout=30_000,
        )


def submit(page: Page) -> None:
    # Wait for the Post button to be enabled (text registered in React state).
    page.wait_for_function(
        """() => {
            const b = document.querySelector('[data-testid="tweetButtonInline"]')
                   || document.querySelector('[data-testid="tweetButton"]');
            return b && !b.disabled;
        }""",
        timeout=15_000,
    )
    # Try JS click first, then fall back to keyboard shortcut (Cmd+Enter).
    page.evaluate(
        """() => {
            const b = document.querySelector('[data-testid="tweetButtonInline"]')
                   || document.querySelector('[data-testid="tweetButton"]');
            if (b) b.click();
        }"""
    )
    page.wait_for_timeout(2500)
    # Check if composer was cleared; if not, try Cmd+Enter as fallback.
    remaining = page.locator('[data-testid="tweetTextarea_0"]').count()
    if remaining and page.locator('[data-testid="tweetTextarea_0"]').first.inner_text().strip():
        # Focus the composer and try keyboard shortcut.
        box = page.locator('[data-testid="tweetTextarea_0"]').first
        if box.count():
            box.click()
            page.wait_for_timeout(200)
        page.keyboard.press("Meta+Enter")
        page.wait_for_timeout(3000)
        remaining = page.locator('[data-testid="tweetTextarea_0"]').count()
        if remaining and page.locator('[data-testid="tweetTextarea_0"]').first.inner_text().strip():
            # One more try: Control+Enter (some platforms use Ctrl instead of Meta).
            page.keyboard.press("Control+Enter")
            page.wait_for_timeout(3000)
            remaining = page.locator('[data-testid="tweetTextarea_0"]').count()
            if remaining and page.locator('[data-testid="tweetTextarea_0"]').first.inner_text().strip():
                raise RuntimeError("composer still contains text after submit")


def verify_recent_post(page: Page, text: str, handle: str = DEFAULT_HANDLE) -> str | None:
    goto(page, f"https://x.com/{handle}", 3000)
    for item in extract_articles(page, 5):
        if item["text"].strip() == text.strip():
            return item["link"]
    return None


def cmd_post(text: str, image: str | None) -> None:
    if len(text) > 280:
        raise ValueError(f"tweet is {len(text)} characters; maximum is 280")
    with exclusive_lock(), browser_session(headless=True) as (_, page):
        require_login(page)
        compose(page, text, image)
        submit(page)
        url = verify_recent_post(page, text)
        if not url:
            raise RuntimeError("submit completed but the post was not found on the profile")
        emit({"status": "POSTED", "url": url, "image": str(Path(image).resolve()) if image else None})


def cmd_reply(post_url: str, text: str, image: str | None) -> None:
    if len(text) > 280:
        raise ValueError(f"reply is {len(text)} characters; maximum is 280")
    with exclusive_lock(), browser_session(headless=True) as (_, page):
        require_login(page)
        goto(page, post_url, 2500)
        box = page.locator('[data-testid="tweetTextarea_0"]').first
        box.click()
        page.wait_for_timeout(200)
        page.keyboard.type(text, delay=5)
        page.wait_for_timeout(500)
        if image:
            file_input = page.locator('[data-testid="fileInput"], input[type="file"]').first
            file_input.set_input_files(str(Path(image).expanduser().resolve()))
            page.wait_for_function(
                """() => !!(
                    document.querySelector('[data-testid="attachments"] img') ||
                    document.querySelector('[data-testid="attachments"] video') ||
                    document.querySelector('img[src^="blob:https://x.com/"]') ||
                    document.querySelector('button[aria-label="Remove media"]') ||
                    document.querySelector('[data-testid="removeImage"]')
                )""",
                timeout=30_000,
            )
        submit(page)
        emit({"status": "REPLIED", "reply_to": post_url, "image": image})


def cmd_quote(post_url: str, text: str, image: str | None) -> None:
    # A status URL entered in X's composer is rendered as a native quoted-post card.
    combined = f"{text}\n{post_url}"
    if len(text) > 280:
        raise ValueError(f"quote text is {len(text)} characters; maximum is 280")
    with exclusive_lock(), browser_session(headless=True) as (_, page):
        require_login(page)
        compose(page, combined, image)
        submit(page)
        url = verify_recent_post(page, text)
        emit({"status": "POSTED", "url": url, "quote_of": post_url, "image": image})


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("login")
    sub.add_parser("check")
    s = sub.add_parser("search"); s.add_argument("query"); s.add_argument("limit", type=int, nargs="?", default=20)
    pr = sub.add_parser("profile"); pr.add_argument("handle"); pr.add_argument("limit", type=int, nargs="?", default=20)
    c = sub.add_parser("capture"); c.add_argument("url"); c.add_argument("output"); c.add_argument("--selector")
    po = sub.add_parser("post"); po.add_argument("text"); po.add_argument("--image")
    r = sub.add_parser("reply"); r.add_argument("post_url"); r.add_argument("text"); r.add_argument("--image")
    q = sub.add_parser("quote"); q.add_argument("post_url"); q.add_argument("text"); q.add_argument("--image")
    return p


def main() -> None:
    args = parser().parse_args()
    try:
        if args.command == "login": cmd_login()
        elif args.command == "check": cmd_check()
        elif args.command == "search": cmd_search(args.query, args.limit)
        elif args.command == "profile": cmd_profile(args.handle, args.limit)
        elif args.command == "capture": cmd_capture(args.url, args.output, args.selector)
        elif args.command == "post": cmd_post(args.text, args.image)
        elif args.command == "reply": cmd_reply(args.post_url, args.text, args.image)
        elif args.command == "quote": cmd_quote(args.post_url, args.text, args.image)
    except (PlaywrightTimeoutError, TimeoutError, RuntimeError, FileNotFoundError, ValueError) as exc:
        emit({"status": "ERROR", "error": str(exc), "command": args.command}, 2)


if __name__ == "__main__":
    main()
