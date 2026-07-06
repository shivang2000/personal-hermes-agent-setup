# DataDome / Cloudflare / Akamai 403 — Recognition Recipes

The exact HTML / header markers that tell you which bot-mitigation layer is blocking the request. Copy this when you hit a 403 and need to know whether to keep escalating or give up.

## DataDome (wellfound.com, sometimes Greenhouse-behind-CDN)

**Header signature:**
```
HTTP/1.1 403 Forbidden
Server: DataDome
```

**HTML signature (the page body is ~1.7 KB, no real content):**
```html
<html lang="en">
<head><title>wellfound.com</title>
<style>#cmsg{animation: A 1.5s;}@keyframes A{0%{opacity:0;}99%{opacity:0;}100%{opacity:1;}}</style>
</head>
<body style="margin:0">
<p id="cmsg">Please enable JS and disable any ad blocker</p>
<script data-cfasync="false">
var dd={'rt':'c','cid':'AHrlqAAAAAMA...',
       'hsh':'BA3EB296E8BE96A496929870E20CD4',
       't':'bv','qp':'','s':23647,
       'e':'<sha256>',
       'host':'geo.captcha-delivery.com',
       'cookie':'<token>'};
</script>
<script data-cfasync="false" src="https://ct.captcha-delivery.com/c.js"></script>
<iframe src="https://geo.captcha-delivery.com/captcha/?initialCid=...&hash=...&cid=...&t=fe&referer=...&s=23647&e=...&dm=cd"
  sandbox="allow-scripts allow-same-origin allow-forms"
  title="DataDome CAPTCHA" width="100%" height="100%"></iframe>
</body>
</html>
```

**Tells:**
- Title is `<portal-name>.com` (e.g. `wellfound.com`), not the actual job title.
- `host: 'geo.captcha-delivery.com'` is the giveaway — that's DataDome's CDN.
- `t: 'bv'` = bot-verdict, `t: 'fe'` = first encounter. Doesn't change the conclusion.
- The body is tiny (~1.7 KB), no nav, no job content. If you see this, give up.

**Confirmed-ineffective bypasses (as of 2026-07):**
- `curl` with realistic Chrome User-Agent → still 403
- `curl` with `Referer: https://wellfound.com/...` and `Origin: https://wellfound.com` → still 403
- `curl` Googlebot UA → still 403 (DataDome maintains its own bot list, not just well-known bots)
- Playwright Chromium headless with `--disable-blink-features=AutomationControlled` → CAPTCHA iframe
- Playwright `channel: 'chrome'` headless (real Chrome binary) → CAPTCHA iframe
- Playwright `channel: 'chrome'` **headed** (visible window) → CAPTCHA iframe
- Playwright `connectOverCDP` to a real running Chrome for Testing session on `localhost:<port>` → CAPTCHA iframe

**What works (and how to know it works):**
- A real human opens the URL in their own browser from a non-cloud-egress IP. Sometimes they get a clean page; sometimes they also get the CAPTCHA (DataDome fingerprints).
- A residential proxy through a different IP range. Costs money; only justifiable for high-value targets the user has approved.

## Cloudflare Turnstile / Bot Fight Mode / Under Attack Mode

**Header signature (Bot Fight Mode / Under Attack):**
```
HTTP/1.1 403 Forbidden (or 503 Service Temporarily Unavailable)
Server: cloudflare
cf-mitigated: challenge
```

**HTML signature (Under Attack Mode / Turnstile):**
```html
<!DOCTYPE html>
<html lang="en-US">
<head>
  <title>Just a moment...</title>
  <meta http-equiv="refresh" content="8">
  ...
  <script src="/cdn-cgi/challenge-platform/scripts/jsd/main.js"></script>
</head>
<body>
  ...
</body>
</html>
```

**Tells:**
- Page title is "Just a moment..." (always).
- `cf-mitigated: challenge` header is the definitive signal.
- Body has a `cf-challenge` form or Turnstile widget. No real content.

**Confirmed-ineffective bypasses:**
- `User-Agent` spoofing (Cloudflare maintains a fingerprint DB, not just UA strings).
- Adding `Accept-Language: en-US` or similar headers.
- The same Playwright patterns listed under DataDome above.
- GraphQL POST to `https://target.com/graphql` from the same origin — Cloudflare challenge fires before the body is parsed.

**What works:**
- A real browser on a real human IP. Cloudflare's challenge auto-resolves on JS execution + cookie acceptance; humans don't notice, headless clients can't pass it.
- Cloudflare's "Authenticated Origin Pulls" — if the site has it enabled, a valid client cert can bypass. Most sites don't.
- A residential proxy through a non-blocked IP.

## Akamai Bot Manager

**Header signature:**
```
HTTP/1.1 403 Forbidden
Server: AkamaiGHost
or
set-cookie: _abck=...; sensor_data=...
```

**Tells:**
- `_abck` cookie is set on every request, then validated on a follow-up. Hard to defeat without solving the sensor_data challenge.
- Sometimes returns a 200 with a page that says "Access Denied" — the request is *accepted* but the content is rejected.

**Confirmed-ineffective bypasses:**
- Same as the others. Akamai's sensor_data is a JavaScript-computed payload; headless browsers without a real JS engine + canvas/WebGL/AudioContext fingerprint get `_abck` rejection.

**What works:**
- A real human browser session, or a residential proxy with a clean IP reputation.

## Generic 403 / 5xx (NOT bot-mitigation)

If you see `403 Forbidden` with `Server: nginx` or `Server: Apache` and no DataDome/Cloudflare/Akamai markers, the 403 is a *real* authorization failure — login required, geo-block, or the URL is dead. Do not use the escalation ladder; treat as a regular blocked-resource and either ask the user to log in or accept the block.

## How to copy this into the blocked record

When you write the report, include a 1-2 KB excerpt of the actual response (or the first 500 bytes if the body is large) so future-you can confirm which layer was blocking. The blocked record should have:

```
## Block summary
- HTTP status: 403
- Server header: DataDome
- Body markers: captcha-delivery.com, captcha iframe
- Conclusion: DataDome IP-level block. Real-user browser may or may not pass.
```
