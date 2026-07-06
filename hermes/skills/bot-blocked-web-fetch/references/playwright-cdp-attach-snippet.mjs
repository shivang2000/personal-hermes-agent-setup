// CDP-attach Playwright snippet — use as step 6 of the bot-blocked-web-fetch ladder.
//
// What this does:
//   1. Connects to a real Chrome for Testing / Chrome DevTools session that's
//      already running on the user's machine. This reuses the user's actual
//      browser session (cookies, localStorage, IP reputation from the user's
//      network), NOT a fresh launched instance.
//   2. If no CDP endpoint is reachable, falls back to launching a fresh
//      Playwright Chromium.
//   3. Navigates to the target URL and dumps the page text + HTML + screenshot
//      to /tmp/ for inspection.
//
// Why this is the right tool for the diagnosis question:
//   If the user's real running browser session ALSO gets blocked, then the
//   block is IP-level (or origin-level), NOT fingerprint-level. That's the
//   diagnostic that should make you stop escalating and go to the recovery
//   pattern.
//
// Usage:
//   CDP_URL=http://localhost:58469 node playwright-cdp-attach-snippet.mjs
//
// Finding the CDP port of an already-running Chrome for Testing:
//   pgrep -fl "Chrome for Testing"   # find the PID
//   lsof -p <PID> | grep TCP | grep LISTEN   # find the listening port
//   # the URL is http://localhost:<port>
//
// (The snippet defaults to /tmp/wellfound-profile, but you should override
// PROFILE to something like /tmp/<your-target>-profile.)

import { chromium } from 'playwright';
import { writeFileSync, mkdirSync } from 'node:fs';

const URL = process.env.URL || 'https://wellfound.com/jobs/4417557-software-engineer-clone';
const CDP_URL = process.env.CDP_URL || 'http://localhost:58469';
const PROFILE_DIR = process.env.PROFILE || '/tmp/wellfound-profile';
mkdirSync(PROFILE_DIR, { recursive: true });

let browser;
let page;
let mode;

try {
  console.log('Connecting to existing Chrome via CDP:', CDP_URL);
  browser = await chromium.connectOverCDP(CDP_URL);
  mode = 'cdp';
  const pages = browser.contexts()[0]?.pages() || [];
  page = pages[0] || await browser.contexts()[0].newPage();
  console.log('Reusing existing page, current URL:', page.url());
} catch (e) {
  console.log('CDP connect failed:', e.message);
  console.log('Falling back to fresh headed Chrome launch');
  browser = await chromium.launchPersistentContext(PROFILE_DIR, {
    headless: true,
    channel: 'chrome',
    args: [
      '--disable-blink-features=AutomationControlled',
      '--no-sandbox',
    ],
    viewport: { width: 1440, height: 900 },
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    locale: 'en-US',
  });
  mode = 'fresh';
  page = await browser.newPage();
}

console.log('Mode:', mode);
console.log('Navigating to', URL);

try {
  await page.goto(URL, { waitUntil: 'domcontentloaded', timeout: 60000 });
} catch (e) {
  console.log('NAV ERROR:', e.message);
}
await page.waitForTimeout(8000);

const title = await page.title();
const url = page.url();
const text = await page.evaluate(() => document.body?.innerText || '').catch(() => '');
const html = await page.content().catch(() => '');
const iframeCount = await page.locator('iframe').count();
const captchaPresent = html.includes('captcha-delivery.com') || html.includes('DataDome');

writeFileSync('/tmp/wellfound-4417557.txt', `# TITLE: ${title}\n# URL: ${url}\n# CAPTCHA: ${captchaPresent}\n# IFRAMES: ${iframeCount}\n# MODE: ${mode}\n\n${text}`);
writeFileSync('/tmp/wellfound-4417557.html', html);
await page.screenshot({ path: '/tmp/wellfound-4417557.png', fullPage: true }).catch(() => {});

console.log('---TITLE---', title);
console.log('---CAPTCHA BLOCKED---', captchaPresent);
console.log('---IFRAMES---', iframeCount);
console.log('---TEXT (first 3000 chars)---');
console.log(text.slice(0, 3000));
console.log('---TEXT LEN---', text.length);

if (mode === 'cdp') {
  await browser.close(); // detaches, doesn't kill
} else {
  await browser.close();
}
