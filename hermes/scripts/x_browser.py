#!/usr/bin/env python3
"""
X.com browser automation via AppleScript + Arc.
Replaces xurl API calls with free browser-based operations.
Requires: Arc browser with X.com logged in, "Allow JavaScript from Apple Events" enabled.

Usage:
  python3 x_browser.py search "Claude OR GPT OR LLM" 5
  python3 x_browser.py post "Tweet text here"
  python3 x_browser.py quote "POST_URL" "Quote tweet text"
  python3 x_browser.py reply "POST_URL" "Reply text"
  python3 x_browser.py timeline 10
  python3 x_browser.py profile "@shivangchheda22" 10
"""

import subprocess
import json
import sys
import time
import urllib.parse
import re


def arc_js(js_code: str, timeout: int = 15) -> str:
    """Execute JavaScript in Arc's active tab and return the result."""
    # Escape the JS code for AppleScript
    escaped = js_code.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
    applescript = f'''
tell application "Arc"
    execute active tab of front window javascript "{escaped}"
end tell'''
    result = subprocess.run(['osascript', '-e', applescript], capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        raise RuntimeError(f"AppleScript error: {result.stderr}")
    # osascript returns the JS result as a quoted string
    return result.stdout.strip()


def arc_navigate(url: str, wait: int = 4) -> str:
    """Navigate Arc's active tab to a URL and wait for it to load."""
    applescript = f'tell application "Arc" to set URL of active tab of front window to "{url}"'
    result = subprocess.run(['osascript', '-e', applescript], capture_output=True, text=True, timeout=10)
    if result.returncode != 0:
        raise RuntimeError(f"Navigation error: {result.stderr}")
    time.sleep(wait)
    return "ok"


def arc_get_url() -> str:
    """Get the current URL of Arc's active tab."""
    result = subprocess.run(['osascript', '-e', 'tell application "Arc" to get URL of active tab of front window'],
                          capture_output=True, text=True, timeout=10)
    return result.stdout.strip()


def arc_get_title() -> str:
    """Get the current page title of Arc's active tab."""
    result = subprocess.run(['osascript', '-e', 'tell application "Arc" to get title of active tab of front window'],
                          capture_output=True, text=True, timeout=10)
    return result.stdout.strip()


def parse_js_result(raw: str) -> str:
    """Parse the string result from osascript JS execution."""
    # osascript wraps string results in double quotes
    if raw.startswith('"') and raw.endswith('"'):
        # Unescape the string
        inner = raw[1:-1]
        # AppleScript escapes: \\ -> \, \" -> "
        inner = inner.replace('\\"', '"').replace('\\\\', '\\')
        return inner
    return raw


def search_tweets(query: str, limit: int = 20) -> list:
    """Search X.com for tweets matching the query. Returns list of tweet dicts."""
    encoded_q = urllib.parse.quote(query)
    url = f"https://x.com/search?q={encoded_q}&f=live"
    
    arc_navigate(url, wait=5)
    
    # Scroll down a bit to load more tweets
    arc_js("window.scrollBy(0, 1000)")
    time.sleep(2)
    
    js = f"""
    var tweets = document.querySelectorAll('article');
    var results = [];
    for (var i = 0; i < Math.min(tweets.length, {limit}); i++) {{
        var tweet = tweets[i];
        var textEl = tweet.querySelector('[data-testid=tweetText]');
        var text = textEl ? textEl.innerText : '';
        var timeEl = tweet.querySelector('time');
        var time = timeEl ? timeEl.getAttribute('datetime') : '';
        var linkEl = tweet.querySelector('a[href*="/status/"]');
        var link = linkEl ? linkEl.getAttribute('href') : '';
        var nameEl = tweet.querySelector('[data-testid="User-Name"]');
        var name = nameEl ? nameEl.innerText : '';
        
        // Get engagement metrics
        var groups = tweet.querySelectorAll('[role="group"] button');
        var metrics = [];
        for (var j = 0; j < groups.length; j++) {{
            var label = groups[j].getAttribute('aria-label');
            if (label) metrics.push(label);
        }}
        
        results.push({{text: text, time: time, link: link, author: name, metrics: metrics}});
    }}
    JSON.stringify(results);
    """
    
    raw = arc_js(js, timeout=15)
    parsed = parse_js_result(raw)
    try:
        return json.loads(parsed)
    except json.JSONDecodeError:
        return [{"error": "Failed to parse results", "raw": parsed[:500]}]


def post_tweet(text: str) -> dict:
    """Post a tweet via the X.com compose page."""
    arc_navigate("https://x.com/compose/post", wait=3)
    
    # Click the compose box and type
    js_click = f"""
    var compose = document.querySelector('[data-testid=tweetTextarea_0]');
    if (compose) {{
        compose.focus();
        compose.click();
        'COMPOSE_READY';
    }} else {{
        'NO_COMPOSE';
    }}
    """
    result = parse_js_result(arc_js(js_click))
    if result != "COMPOSE_READY":
        return {"error": "Compose box not found", "result": result}
    
    time.sleep(0.5)
    
    # Type the tweet text by setting innerHTML and dispatching input event
    escaped_text = text.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
    js_type = f"""
    var compose = document.querySelector('[data-testid=tweetTextarea_0]');
    compose.focus();
    
    // Use document.execCommand to insert text (X.com uses contenteditable)
    document.execCommand('insertText', false, "{escaped_text}");
    
    // Wait and check
    var typedText = compose.innerText;
    typedText.substring(0, 50);
    """
    typed = parse_js_result(arc_js(js_type, timeout=10))
    
    time.sleep(1)
    
    # Check if the tweet button is enabled (X.com uses tweetButtonInline on compose page)
    js_btn = """
    var btn = document.querySelector('[data-testid="tweetButtonInline"]') || document.querySelector('[data-testid="tweetButton"]');
    if (btn) {
        btn.disabled ? 'BUTTON_DISABLED' : 'BUTTON_ENABLED';
    } else {
        'NO_BUTTON';
    }
    """
    btn_state = parse_js_result(arc_js(js_btn))
    
    if btn_state != "BUTTON_ENABLED":
        return {"error": "Tweet button not enabled", "state": btn_state, "typed": typed}
    
    # Click the tweet button (try tweetButtonInline first, then tweetButton)
    js_post = """
    var btn = document.querySelector('[data-testid="tweetButtonInline"]') || document.querySelector('[data-testid="tweetButton"]');
    if (btn) {
        if (!btn.disabled) {
            btn.click();
            'POSTED';
        } else {
            'BUTTON_DISABLED';
        }
    } else {
        'NO_BUTTON';
    }
    """
    post_result = parse_js_result(arc_js(js_post, timeout=10))
    time.sleep(3)
    
    # Get the current URL to extract the tweet ID
    current_url = arc_get_url()
    
    return {
        "status": post_result,
        "url": current_url,
        "typed_preview": typed
    }


def quote_tweet(post_url: str, text: str) -> dict:
    """Quote-tweet a post by URL."""
    # Extract the tweet ID from the URL
    match = re.search(r'/status/(\d+)', post_url)
    if not match:
        return {"error": "Invalid post URL", "url": post_url}
    
    tweet_id = match.group(1)
    
    # Navigate to the tweet
    arc_navigate(f"https://x.com/i/status/{tweet_id}", wait=4)
    
    # Click the retweet button and select "Quote"
    js_quote = """
    // Find the retweet button
    var repostBtn = document.querySelector('[data-testid="retweetButton"]');
    if (!repostBtn) return 'NO_REPOST_BTN';
    
    repostBtn.click();
    
    // Wait for the menu to appear, then click "Quote"
    setTimeout(function() {
        var quoteBtn = document.querySelector('[data-testid="retweetButtonConfirm"] ~ [role="menuitem"], [data-testid="unretweet"]');
        // Actually, let's look for the Quote option in the popup menu
        var menuItems = document.querySelectorAll('[role="menuitem"]');
        for (var i = 0; i < menuItems.length; i++) {
            if (menuItems[i].innerText.toLowerCase().includes('quote')) {
                menuItems[i].click();
                break;
            }
        }
    }, 500);
    
    'QUOTE_MENU_OPENED';
    """
    result = parse_js_result(arc_js(js_quote, timeout=10))
    time.sleep(2)
    
    # Type in the quote tweet compose box
    escaped_text = text.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
    js_type = f"""
    var compose = document.querySelector('[data-testid="tweetTextarea_0"]');
    if (compose) {{
        compose.focus();
        compose.click();
        document.execCommand('insertText', false, "{escaped_text}");
        'TYPED';
    }} else {{
        'NO_COMPOSE';
    }}
    """
    typed = parse_js_result(arc_js(js_type, timeout=10))
    time.sleep(1)
    
    # Click the post button
    js_post = """
    var btns = document.querySelectorAll('[data-testid="tweetButtonInline"], [data-testid="tweetButton"]');
    for (var i = 0; i < btns.length; i++) {
        if (!btns[i].disabled) {
            btns[i].click();
            return 'POSTED';
        }
    }
    'NO_BUTTON';
    """
    post_result = parse_js_result(arc_js(js_post, timeout=10))
    time.sleep(3)

    return {
        "status": post_result,
        "quote_of": post_url,
        "typed_preview": typed
    }


def reply_to_tweet(post_url: str, text: str) -> dict:
    """Reply to a tweet by URL."""
    # Navigate to the tweet
    arc_navigate(post_url, wait=4)
    
    # Click the reply box and type
    escaped_text = text.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
    js_type = f"""
    var compose = document.querySelector('[data-testid="tweetTextarea_0"]');
    if (compose) {{
        compose.focus();
        compose.click();
        document.execCommand('insertText', false, "{escaped_text}");
        'TYPED';
    }} else {{
        'NO_COMPOSE';
    }}
    """
    typed = parse_js_result(arc_js(js_type, timeout=10))
    time.sleep(1)
    
    # Click the reply button
    js_post = """
    var btns = document.querySelectorAll('[data-testid="tweetButtonInline"], [data-testid="tweetButton"]');
    for (var i = 0; i < btns.length; i++) {
        if (!btns[i].disabled) {
            btns[i].click();
            return 'POSTED';
        }
    }
    'NO_BUTTON';
    """
    post_result = parse_js_result(arc_js(js_post, timeout=10))
    time.sleep(3)
    
    return {
        "status": post_result,
        "reply_to": post_url,
        "typed_preview": typed
    }


def get_timeline(limit: int = 20) -> list:
    """Get tweets from the home timeline."""
    arc_navigate("https://x.com/home", wait=5)
    
    js = f"""
    var tweets = document.querySelectorAll('article');
    var results = [];
    for (var i = 0; i < Math.min(tweets.length, {limit}); i++) {{
        var tweet = tweets[i];
        var textEl = tweet.querySelector('[data-testid=tweetText]');
        var text = textEl ? textEl.innerText.substring(0, 200) : '';
        var timeEl = tweet.querySelector('time');
        var time = timeEl ? timeEl.getAttribute('datetime') : '';
        var linkEl = tweet.querySelector('a[href*="/status/"]');
        var link = linkEl ? linkEl.getAttribute('href') : '';
        results.push({{text: text, time: time, link: link}});
    }}
    JSON.stringify(results);
    """
    
    raw = arc_js(js, timeout=15)
    parsed = parse_js_result(raw)
    try:
        return json.loads(parsed)
    except json.JSONDecodeError:
        return [{"error": "Failed to parse", "raw": parsed[:500]}]


def get_profile_tweets(handle: str, limit: int = 20) -> list:
    """Get recent tweets from a user's profile."""
    handle = handle.lstrip('@')
    arc_navigate(f"https://x.com/{handle}", wait=5)
    
    js = f"""
    var tweets = document.querySelectorAll('article');
    var results = [];
    for (var i = 0; i < Math.min(tweets.length, {limit}); i++) {{
        var tweet = tweets[i];
        var textEl = tweet.querySelector('[data-testid=tweetText]');
        var text = textEl ? textEl.innerText.substring(0, 200) : '';
        var timeEl = tweet.querySelector('time');
        var time = timeEl ? timeEl.getAttribute('datetime') : '';
        var linkEl = tweet.querySelector('a[href*="/status/"]');
        var link = linkEl ? linkEl.getAttribute('href') : '';
        
        // Get view count
        var viewLink = tweet.querySelector('a[href*="/analytics"]');
        var views = viewLink ? viewLink.innerText : '';
        
        results.push({{text: text, time: time, link: link, views: views}});
    }}
    JSON.stringify(results);
    """
    
    raw = arc_js(js, timeout=15)
    parsed = parse_js_result(raw)
    try:
        return json.loads(parsed)
    except json.JSONDecodeError:
        return [{"error": "Failed to parse", "raw": parsed[:500]}]


def check_login() -> dict:
    """Check if X.com is logged in."""
    arc_navigate("https://x.com/home", wait=5)
    
    url = arc_get_url()
    title = arc_get_title()
    
    js = """
    var compose = document.querySelector('[data-testid=tweetTextarea_0]');
    var tweets = document.querySelectorAll('article');
    JSON.stringify({
        logged_in: !!compose,
        tweets_on_timeline: tweets.length,
        url: window.location.href,
        title: document.title
    });
    """
    
    raw = arc_js(js, timeout=10)
    parsed = parse_js_result(raw)
    try:
        return json.loads(parsed)
    except:
        return {"url": url, "title": title, "logged_in": "unknown"}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "search":
        query = sys.argv[2]
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 20
        results = search_tweets(query, limit)
        print(json.dumps(results, indent=2))
    
    elif cmd == "post":
        text = sys.argv[2]
        result = post_tweet(text)
        print(json.dumps(result, indent=2))
    
    elif cmd == "quote":
        post_url = sys.argv[2]
        text = sys.argv[3]
        result = quote_tweet(post_url, text)
        print(json.dumps(result, indent=2))
    
    elif cmd == "reply":
        post_url = sys.argv[2]
        text = sys.argv[3]
        result = reply_to_tweet(post_url, text)
        print(json.dumps(result, indent=2))
    
    elif cmd == "timeline":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        results = get_timeline(limit)
        print(json.dumps(results, indent=2))
    
    elif cmd == "profile":
        handle = sys.argv[2]
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 20
        results = get_profile_tweets(handle, limit)
        print(json.dumps(results, indent=2))
    
    elif cmd == "check":
        result = check_login()
        print(json.dumps(result, indent=2))
    
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)