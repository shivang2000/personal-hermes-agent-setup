---
name: bot-blocked-web-fetch
version: 1.0.0
description: When an agent must load a web target (job portal, social, e-commerce) but bot-mitigation (DataDome, Cloudflare Turnstile, Akamai, IP denylist) blocks every request from the agent's network. Provides an escalation ladder, ethical lines, and a "log blocked, never fabricate" recovery pattern. Use when curl, browser tools, and Playwright all return a CAPTCHA iframe or 403 page.
triggers:
  - DataDome blocked
  - Cloudflare challenge
  - CAPTCHA wall
  - 403 forbidden on portal
  - cannot fetch job posting
  - bot mitigation
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
---

# Bot-Blocked Web Fetch — Recovery When Anti-Bot-Mitigation Blocks the Target

## What this skill is for

You're trying to load a URL — usually a job posting on a portal like Wellfound, LinkedIn, Greenhouse-behind-CDN, a SaaS marketing site, or a third-party login wall. Every request from the agent's network returns a 403 page with an `<iframe>` to a CAPTCHA delivery service, a "Just a moment..." challenge, or empty content. Standard tools (curl, browser_navigate, Playwright) all hit the same wall.

This skill gives you a **tried ladder** for diagnosing the block layer, a clear **ethical line** on what not to do, and a **fallback workflow** so the request still gets handled (logged as blocked, drafted from JD paste, or routed to a non-portal equivalent) instead of silently failing or faking a success.

## When to load this

Load this skill when **any** of the following are true:

- `curl -L` to a portal returns `HTTP 403` with HTML containing `captcha-delivery.com`, `cf-chl-bypass`, `Just a moment...`, or `Akamai Bot Manager`.
- `browser_navigate` to a portal returns title like `wellfound.com` (not the job title) and the page text is empty or contains only a CAPTCHA iframe.
- Playwright (headless, headed, or CDP-attached to a real browser session) returns a CAPTCHA iframe even with a real Chrome binary.
- A GraphQL/REST endpoint to the same domain returns Cloudflare's "Just a moment..." challenge instead of JSON.
- The portal's URL is on a bot-mitigation service: wellfound.com, linkedin.com, instagram.com, facebook.com, twitter.com (x.com), glassdoor.com, indeed.com, most e-commerce sites, most ATS sites behind Cloudflare.

**Don't load this skill** for:

- 404 / 410 / 5xx errors (those are different problems — use systematic-debugging).
- Login walls that are stable and solvable (use a different skill / hand to the user).
- Captcha-free but JS-rendered pages (use Playwright normally; this skill is specifically for the IP-level block case).

## Diagnosis: which layer is blocking?

Run these in order — each one is fast and tells you where to escalate.

### 1. Confirm it's bot-mitigation, not a real error

```bash
curl -sI -A "Mozilla/5.0 ..." "https://target.example/page" -o /dev/null -w "%{http_code}\n"
```

- `200` → not bot-mitigation, real page reachable. Stop here, use normal fetch.
- `403` with `server: datadome` or HTML containing `captcha-delivery.com` → **DataDome**.
- `403` / `503` with HTML containing `cf-mitigated` or `cf-chl-bypass` or `Just a moment...` → **Cloudflare Turnstile / Bot Fight Mode / Under Attack Mode**.
- `403` with `akamai` headers or `_abck` cookies → **Akamai Bot Manager**.
- `200` but empty / placeholder content → likely JS-rendered, not blocked. Use Playwright.

Save the response headers + first 500 bytes of HTML. These are the evidence for the "blocked" record.

### 2. Confirm it's network-level (IP denylist), not fingerprint-level

The cheapest test: **does the same URL load in the user's normal browser right now?** If you have a way to drive a real-user browser session (CDP-attached Chrome for Testing, real Chrome on user's machine, etc.), try it. If it works there, the block is on the *agent's network egress*, not on the fingerprint. If it fails there too, the block is on the *origin host* (e.g., the URL is just dead).

**Decision point:**

- **IP-level block, fingerprint works in user's browser** → escalate to the user: ask them to open the URL in their own browser, paste the JD, or use a different network.
- **Origin-level block (URL is dead / behind paywall / region-locked)** → different problem, treat as a regular blocked-resource. Don't try harder.
- **Fingerprint block (user's own browser also gets CAPTCHA)** → real bot-mitigation that doesn't yield to anything you can do. Log blocked, ask user for JD paste.

## Escalation ladder — what to try, in order

Try each one once. If it fails, the next step is the *next* rung, not retrying the same rung. Don't spend more than ~30s per rung.

| # | Method | When to use | Expected signal of success | What it actually tests |
|---|--------|-------------|---------------------------|------------------------|
| 1 | `curl -L` with realistic Chrome UA + `Accept-Language: en-US` | Always start here | Real JD text in response body, HTTP 200 | Whether the network egress is even allowed |
| 2 | Hermes `browser_navigate` (built-in) | URL is well-formed | Title matches job, `body.innerText` has JD content | Whether the bundled headless browser can render the page |
| 3 | Playwright Chromium headless, persistent context | Step 2 failed | Same as above | Whether a "real" Playwright launch gets through |
| 4 | Playwright `channel: 'chrome'` headless | Step 3 failed (DataDome usually gets past generic Chromium) | Same as above | Whether real Chrome binary + version passes fingerprint check |
| 5 | Playwright `channel: 'chrome'` **headed** | Step 4 failed | Same as above; user will see a Chrome window | Whether the user's IP is on a denylist (a headed window still uses the same egress) |
| 6 | Playwright `connectOverCDP` to user's running Chrome for Testing session | Step 5 failed (or skip to this if you know one is running) | Same as above | Whether the IP-reputation differs when reusing a real-user session (it usually doesn't) |
| 7 | Try alternate URL paths (`/jobs/{id}` vs `/jobs/{id}-slug`, `angel.co/...` legacy) | Step 6 failed | Real content via SEO/static path | Whether the bot-mitigation is path-specific |
| 8 | Try the portal's documented public API (often undocumented) | Step 7 failed | JSON response with JD data | Whether the API endpoint is whitelisted (rare) |
| 9 | Accept block. Log and move on. | All steps failed | n/a | The right answer when the IP is hard-denied |

**Wayback Machine fallback (between rungs 8 and 9):** If the target is a public website (not a personal portal or authenticated page), try the Internet Archive's Wayback Machine. This often works when the live site has Cloudflare/Vercel security checkpoints but the archived snapshot was captured before the bot-mitigation was enabled.

```bash
# Try the latest snapshot
curl -sL "https://web.archive.org/web/2025/https://target.example/page" -o /tmp/wb_page.html -w "HTTP %{http_code}\n"
```

For help-center / documentation sites (e.g. `help.example.com/en/articles/12345-slug`), the Wayback Machine frequently returns the full article body in static HTML. Extract the `<article>` tag content:

```python
import re, html
with open('/tmp/wb_page.html') as f: t = f.read()
m = re.search(r'<article[^>]*>(.*?)</article>', t, re.S)
if m:
    body = re.sub(r'<[^>]+>', ' ', m.group(1))
    body = re.sub(r'\s+', ' ', html.unescape(body)).strip()
    print(body[:3000])
```

For collection/index pages, extract article links: `grep -oE '/articles/[0-9]+-[a-z0-9-]+' /tmp/wb_page.html | sort -u`

**Limitations:** Wayback snapshots can be months old. Always check the capture date in the Wayback toolbar. If the content has changed since the snapshot (rules updated, pricing changed, policies revised), note the snapshot date and verify against the live site via `browser_navigate` if possible. Wayback is a **last-resort fallback for public content**, not a primary fetch method.

**Do NOT use Wayback for:** authenticated pages, user dashboards, account-specific data, or any page that requires login. It only archives public content.

**If step 6 fails when step 5 also failed with the user's real browser at `localhost:<CDP-port>`** — that is conclusive evidence the block is network-level, not fingerprint-level. **Stop escalating.** More attempts waste tokens and time. Move to the recovery pattern below.

## Ethical line — what NOT to do

- **Do not bypass CAPTCHAs.** DataDome / Cloudflare Turnstile / hCaptcha / reCAPTCHA challenges require a human to solve. There is no legitimate way for an AI agent to click through them. If you do, you are also violating the target's Terms of Service and may be committing computer-misuse-style offenses depending on jurisdiction.
- **Do not use residential proxy services** the user has not explicitly authorized. The user pays for these, they have cost, and the moral question of "whose IP is this, did they consent" is real. Mentioning them in a recovery message is fine; spinning one up silently is not.
- **Do not synthesize a "successful" application** when the form was never submitted. This is the worst possible outcome: the user thinks they applied, the recruiter never sees it, and a future search may even find fake content where the real record should be.
- **Do not generate a fake JD** to "have something to evaluate." If you cannot read the JD, the score is `N/A`, the report says `UNVERIFIED`, and the user pastes the JD.
- **Do not retry indefinitely.** Three failures of the same rung is enough; move on.

## Recovery pattern — what to do when blocked

When the ladder is exhausted, do the following. **Do not skip steps.**

### 1. Write a blocked-job / blocked-target record

A real, honest record with:
- The URL, date, and a 1-line reason it's blocked
- The exact techniques tried (which steps of the ladder above) and their result
- A weak-signal analysis (e.g., a URL slug like `-clone` is a red flag)
- The path forward: which step of the recovery ladder the user can take next

Save it where the project's tracking convention expects:
- For career-ops: `reports/{NNN}-{slug}-{YYYY-MM-DD}.md` + a row in `data/applications.md` with Status: `BLOCKED`
- For other projects: the project's equivalent. Don't invent a new format if the project has one.

The record must have **`**Legitimacy:** UNVERIFIED`** (or equivalent) and a score of `N/A`. Never `0/5` (which implies you evaluated it and rejected it).

### 2. Update the project's tracker / inbox

- Add a row with Status: `BLOCKED` (or the project's equivalent).
- The notes column should mention the technique that failed and what the user can do next (paste JD, retry from different network, use the company's own careers page).
- Do NOT mark it `Applied`, `Evaluated`, or `Skip`. `BLOCKED` is its own status, distinct from "I evaluated it and chose not to apply."

### 3. Present the user with concrete next steps, in priority order

The recovery message should give the user 2-4 real options, not "let me try harder." Common options:

1. **You open the URL in your own browser** (often the same network egress, so likely the same block — but if they're on a different network it works). Send back a screenshot or pasted JD.
2. **Paste the JD text here** so the agent can run the project's normal evaluation pipeline on the text directly.
3. **Find the company's own careers page** (not the portal listing). Most companies have a Lever / Greenhouse / Ashby page that doesn't route through the portal's bot-mitigation, and those URLs are usually scrapable.
4. **Skip this one** — log it as blocked and move on. (This is the right answer for low-priority leads.)

Pick the one with the highest expected information-per-action, not the one that makes the agent look most capable.

## Reference files

- `references/datadome-recipes.md` — observed request/response shapes for DataDome, Cloudflare Turnstile, and Akamai-403 challenges; the HTML markers that confirm which layer is blocking.
- `references/escalation-evidence-template.md` — copy-paste template for the "Methods tried" table in the blocked record.
- `references/playwright-cdp-attach-snippet.mjs` — the working CDP-attach Playwright snippet to use as the step-6 rung of the ladder. (Reusable across sessions.)

## Pitfalls

- **"Let me just try one more thing"** — the worst reflex. If step 6 failed, step 7 (alternate path) and step 8 (API) usually fail for the same reason. Move to recovery.
- **Confusing fingerprint block with IP block.** A fingerprint block *might* be defeated by a different browser binary; an IP block will defeat every browser. The CDP-attach test is the cleanest separator.
- **"It works in the user's screenshot, so the agent should have worked too"** — false. The user's screenshot is from a different network or a cached page. Don't argue with the user about it; just log and move on.
- **Marking the row `Applied` because "we sent a request"** — sending a request to a CAPTCHA page is not an application. It is a request that was rejected.
- **Using a residential proxy without asking** — costs the user money and may be unethical depending on the proxy source.
- **Generating a generic cover letter without seeing the JD** — this is fabrication, not preparation. The cover letter will be visibly wrong (wrong company name, wrong stack, wrong role title) and damages the user's brand.
- **Hiding the block from the user** — the user is the one with the relationship to the recruiter. If the application did not actually submit, the user must know. Silent failure is worse than loud failure.

## Verification

Before claiming "I applied / I fetched the JD / I evaluated the role," verify:

- The response body actually contains role/company/requirements text (not a CAPTCHA page, not an empty body).
- For form submissions: the confirmation page or 200 response with a real confirmation token is visible, not just a 200 OK with no body.
- The tracker row is `Applied` (or equivalent) only when the response is a real success, not just a request that didn't fail loudly.
- If you cannot verify any of these, the status is `BLOCKED`, not `Applied`.

## Related skills

- `gstack/scrape` — read-only page scrape; this skill is what to do *after* scrape fails with a bot-mitigation response.
- `gstack/browse` — headless browser with `--proxy` and `handoff` mechanisms; useful when you want to try a residential proxy or hand the page to the user. The `handoff` command is the right tool when step 5 of the ladder would be the right move but you'd rather not spawn your own headed Chrome.
- `career-ops` (Shivang's local project, not a Hermes skill) — the project that surfaced this problem. Its `modes/apply.md` says "Use Playwright first"; this skill refines what to do *when Playwright also fails.*
