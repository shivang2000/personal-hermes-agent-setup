# Local Work Summary Cron Pattern

Use this reference for recurring jobs that turn Shivang's recent local work into safe Twitter/X draft angles for review.

## Proven job shape

- Purpose: summarize recent work signals into tweet angles; never auto-post.
- Schedule used: weekdays at 7:30 PM IST (`30 19 * * 1-5`) for end-of-office-day reflection.
- Delivery: current Discord review thread (`origin`) unless Shivang asks for a different channel; for Twitter automation status/review, prefer `#tweets-automation` when selecting a non-origin Discord target.
- Model pin: `openai-codex` / `gpt-5.5` for recurring Hermes cron jobs unless Shivang explicitly requests another model.
- Minimal toolsets: `terminal`, `file`, `session_search` are enough for local-work-signal drafts and reduce cron context/tool overhead.

## Prompt guardrails

The cron prompt should instruct the agent to:

1. Use only safe local work signals: session summaries, git/file metadata, command history, high-level codebase structure, and non-sensitive task names.
2. Avoid secrets, customer data, private payloads, proprietary docs, exact configs, sensitive traces, credentials, or raw internal logs.
3. Produce tweet angles/drafts for review only; do **not** post tweets.
4. Bias toward concrete engineering details and lessons: backend, infra, reliability, payments/refunds, observability, integration edge cases, debugging practice, and implementation tradeoffs.
5. Avoid generic founder/productivity/AI-agent takes unless grounded in Shivang's actual work.

## Verification notes

After creating or updating the cron:

- Manually trigger a run with the cron tool/CLI.
- A consumed trigger plus `next_run` advancing proves the scheduler accepted the run, but not necessarily that the agent completed successfully.
- If cron metadata still reports `last_status: null`, state that limitation clearly instead of claiming a completed successful run.
- Remove any temporary duplicate jobs created while reconciling schedule/model/delivery settings.

## Worked example: 2026-07-17 window

This is a real end-to-end auto-post that came out of the work-agent digest for the Jul 16 19:30 → Jul 17 19:30 IST window. Use it as a shape reference, not as boilerplate to copy.

**Source signal** (from `developer-portal-ui`, agent-assisted mission with 3 workers):
> "Adjusted Lens email name-match handling from a boolean-derived status to a string status passed through from API data. ... Fixed Email Card registered-name row signal behavior: exact match → positive/green, not matched → negative/red, unknown / no status → default/gray, no registered name → default/gray. Added regression tests around the Email Card row signal so missing/unknown name-match status no longer appears as a false-positive match."

**What the agent did after paginating the digest:**
1. Saw the `(1/6)` first page in the trigger, used `fetch_messages` to recover the remaining 5 pages, confirmed the stop-footer page before acting.
2. Picked the boolean→string collapse bug as the freshest, most mechanism-rich signal.
3. Drafted three angles, trimmed all to ≤280 chars (one required 4 trim passes — see the "draft under 260 first" pitfall in SKILL.md), applied the humanizer checklist (stripped em-dashes, removed AI-vocab like "underscoring", varied rhythm, kept concrete mechanism, used `#DevTools`).
4. Auto-posted via `xurl post` and reported the tweet URL + the two unposted alternate angles to the thread for Shivang to swap in with a quick "post 2" or "post 3".

**Posted tweet (272 chars):**
> Email name-match was a boolean. "Unknown" kept collapsing into match=true in the UI.
>
> Fix: thread the real backend string through the transformer, color by enum not truthy. Gray for unknown, green only for explicit exact match. Regression tests on every branch. #DevTools

**Why it worked:**
- Specific mechanism (transformer, enum-vs-truthy, gray/green semantic map).
- Teaching framing ("smallest rendering bugs eat the most time") without being preachy.
- No "in today's landscape" / "game-changer" / "delve".
- 272 chars gave a small edit buffer if Shivang wanted to react with a quick tweak.

**Alternate angles that were not posted (kept on hand):**
1. The "Clear API Key" 4-layer fix (controller + service + repository + tests) — `button behavior is backend semantics wearing a modal`.
2. The HubSpot UI extension overlay lifecycle lesson — `platform constraints aren't polish, they're architecture`.

If Shivang replies "post 2" or "post 3" in the same thread, post the matching alternate in the next session.
