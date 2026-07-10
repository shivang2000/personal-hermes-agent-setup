# Interaction Playbook

## Browser and window discovery

1. Call `computer_use(action="list_apps")`.
2. Match the browser by the exact returned app/process name. Chrome/Arc may be running with no capturable on-screen window because every window is minimized, hidden, or closed. Do not treat a running process as proof of a usable window.
3. Capture with `app=<exact name>`, `mode="som"`. If capture is empty, try `mode="ax"`, inspect app/window state, and ask the user to expose/open a browser window if doing so yourself would disturb their session.
4. Never use `focus_app(..., raise_window=true)` unless requested.

## Navigation and tabs

- Reuse the requested tab when the task clearly targets it; otherwise open a new tab with `cmd+t` to avoid destroying page state.
- Use `cmd+l`, type the exact URL, press Return, then capture and verify the domain before interacting.
- Do not navigate away from unsaved work without checking for a dirty-state warning.
- Browser back is a state-changing action: recapture afterward.

## Forms

1. Capture and identify the complete visible form, active account/workspace, and submit label.
2. Fill one logical section at a time.
3. Prefer labeled text fields and controls. For custom selects, click, recapture the opened list, then choose by fresh index.
4. Re-read critical values before submission: recipient, workspace, amount, visibility/audience, dates, file, and final action label.
5. If the task says fill/prepare/draft, stop before final submission.
6. If the task explicitly says submit/send/publish/apply, click once and immediately verify.

## File upload

- Confirm the requested local path exists and identify the intended file before browser interaction.
- Prefer a page-exposed file input or browser automation upload API. Native file pickers may require computer-use; use Finder's `cmd+shift+g` path entry rather than searching manually.
- Never type secrets into an upload field or upload a directory when a file was requested.
- After selection, verify filename, size/type when shown, upload progress completion, and destination.
- A filename chip only proves selection, not server-side persistence.

## Downloads

- Initiate once, then verify the downloaded file exists, is non-empty, and has the expected type/name. Use file tools for verification, not Finder UI alone.
- Do not open executable downloads unless explicitly requested and safe.

## Modals, popovers, cookie banners

- Recapture whenever a modal opens; background elements may remain in AX but be blocked.
- Resolve expected benign modals using labeled controls.
- Use Escape only when it cannot discard user data; otherwise use explicit Cancel/Close.
- Cookie consent is not blanket authorization. Prefer necessary-only/reject-optional when available unless the user says otherwise.
- Permission prompts, legal attestations, payments, password/2FA, and destructive confirmations are hard stops.

## Rich editors and contenteditable fields

- Click the editor, insert text, then verify visible content and formatting.
- Avoid global `cmd+a` unless focus is unquestionably inside the editor; otherwise it can select the whole page.
- For large content, paste in one bounded operation, then read back beginning/end and any length counter.

## Stale elements and dynamic pages

Symptoms: click has no effect, index missing, list reordered, rerender after validation, infinite-scroll replacement.

Recovery:
1. Capture fresh state.
2. Re-identify the control semantically, not by old index/coordinate.
3. Confirm the workflow step did not advance.
4. Retry once using a fresh index.
5. Try keyboard or visual routing once.
6. Escalate to CDP if safe; otherwise report blocked.

## Submission ambiguity and duplicate prevention

If a click timed out or the page navigated unexpectedly:

1. Do not click submit again.
2. Look for confirmation, created record, activity log, updated list, email/notification only if the task authorizes accessing it, or network state through CDP.
3. Refresh/navigate independently only when it will not lose needed evidence.
4. Retry only after proving the first attempt did not commit.

## Common recovery patterns

| Symptom | Recovery |
|---|---|
| Empty capture | Re-run list_apps, exact app name, inspect window state; ask user to expose a window if necessary |
| Element index stale | Fresh capture; never reuse index |
| Click ignored | Check modal/overlay; fresh index; keyboard; visual |
| Wrong tab | Stop; identify title/domain; do not close unknown tabs |
| Session expired | Stop at login; user completes authentication |
| CAPTCHA/2FA/passkey | Stop and hand off to user |
| Anti-bot page | Load `bot-blocked-web-fetch`; never fabricate success |
| Upload seems stuck | Verify progress/network; do not select repeatedly |
| Submit uncertain | Verify destination record before retry |
