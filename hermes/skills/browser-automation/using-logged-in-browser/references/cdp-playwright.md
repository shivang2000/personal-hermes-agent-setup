# CDP-Attached Playwright Escalation

## When to use

Use CDP when computer-use can see the browser but repeated AX/visual interaction is unreliable, and DOM-level control will materially improve correctness for complex forms, iframes, shadow DOM, virtualized lists, or file inputs.

Do not make CDP the first assumption. A normal running Chrome/Arc process may not expose a debugging endpoint.

## Safety rules

- Attach only to a browser endpoint the user already authorized or Hermes opened through its supported `/browser` flow.
- Never expose a CDP port beyond loopback.
- Never read/export cookies, localStorage tokens, passwords, session secrets, or unrelated tabs.
- Scope operations to the target domain/tab.
- Do not quit or relaunch the user's browser to add remote-debugging flags without explicit permission; this can lose tabs/state and changes the security posture.
- CDP access does not weaken final-action safety gates.

## Preferred discovery

1. Check Hermes-supported browser/CDP connection status (`/browser` or the configured browser automation stack) rather than scanning arbitrary ports.
2. If a known loopback endpoint was explicitly provided, verify it returns a browser version document before attaching.
3. Enumerate contexts/pages and select by exact domain/title. Do not operate on the first page by position.
4. Keep a reference to the selected page only; avoid inspecting unrelated contexts.

## Minimal Playwright pattern

```javascript
import { chromium } from 'playwright';

const browser = await chromium.connectOverCDP(process.env.CDP_URL);
const pages = browser.contexts().flatMap(c => c.pages());
const page = pages.find(p => new URL(p.url()).hostname === 'app.example.com');
if (!page) throw new Error('Authorized target tab not found');

await page.getByRole('button', { name: 'Continue', exact: true }).click();
await page.getByText('Step 2 of 3', { exact: true }).waitFor();

// Detach only. Do not close the user's browser.
await browser.close();
```

`browser.close()` on a CDP connection should detach, but verify library behavior/version when uncertain. Never call context/page close unless the task explicitly asks to close them.

## Selector hierarchy

1. `getByRole` + exact accessible name
2. `getByLabel`
3. stable application test ID
4. exact visible text scoped to a container
5. CSS selector only when semantic selectors are unavailable
6. coordinates only outside CDP as a last resort

After navigation or rerender, query locators again. Avoid storing raw element handles across state transitions.

## Uploads

Use `setInputFiles` only on the intended file input after verifying path and destination:

```javascript
const input = page.locator('input[type=file]').filter({ has: page.locator(':visible') });
await input.setInputFiles('/absolute/path/report.pdf');
await page.getByText('report.pdf', { exact: true }).waitFor();
```

If there are multiple inputs, scope by associated label/container; never use the first match blindly.

## Verification

Combine DOM and destination-state checks:

- wait for explicit confirmation;
- verify created/updated record in a list or detail page;
- confirm URL/domain/account context;
- for uncertain submissions, inspect the resulting record before retrying.

A fulfilled click promise or successful network status alone is insufficient.

## Fallback

If attachment is unavailable, do not relaunch automatically. Return to computer-use. If the site presents bot mitigation, use `bot-blocked-web-fetch`. If the user's action is blocked by authentication/challenge, hand control to the user and resume after they say it is complete.
