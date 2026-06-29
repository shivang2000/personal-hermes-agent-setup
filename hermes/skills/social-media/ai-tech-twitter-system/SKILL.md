---
name: ai-tech-twitter-system
description: Use when drafting, approving, scheduling, or posting AI/tech/product insight tweets for Shivang. Keeps a regular approval queue and handles user-discovered insights safely.
version: 1.0.0
author: REDACTED_SET_LOCALLY
license: MIT
metadata:
  hermes:
    tags: [twitter, x, ai, tech, content, approval-queue, social-media]
    related_skills: [xurl]
---

# AI/Tech Twitter System

## Overview

This skill runs Shivang's AI/tech Twitter workflow: regular tweet candidates, fast conversion of discovered insights into posts, and safe posting via X/Twitter only when appropriate.

Default operating mode:
- Draft regularly from current AI/tech/product/startup trends.
- Keep tweets useful, specific, and low-hype.
- Shivang has explicitly switched the recurring AI/tech tweet system to fully auto-post mode. Scheduled AI/tech tweet jobs should self-review and post strong items without asking for manual approval.
- Before every post or reply, apply the `humanizer` skill/checklist: strip AI-isms, preserve Shivang's technical builder voice, avoid polished LinkedIn rhythm, and keep concrete engineering detail.
- If Shivang explicitly says to post a specific insight/tweet now, post it after verifying X auth and final tweet text.
- Never use secrets inline or inspect `~/.xurl`.

## When to Use

Use this skill when Shivang asks to:
- Create daily/regular AI or tech tweets.
- Turn a discovery, observation, article, paper, product launch, or personal insight into a tweet.
- Manage a Twitter/X approval queue.
- Post an approved tweet with `xurl`.
- Adjust cadence, tone, or content pillars for AI/tech posting.

Do not use this skill for:
- Posting sensitive/private information.
- Financial, medical, legal, or safety claims without strong sourcing and disclaimers.
- Engagement bait, plagiarism, impersonation, harassment, or spam.
- Reading or handling X/Twitter credentials.

## Content Strategy

Preferred pillars:
1. Practical AI workflows: what actually helps builders, operators, and founders.
2. AI product insights: UX, distribution, adoption, pricing, trust, workflows.
3. Technical shifts: models, agents, infra, evals, tooling, open source.
4. Founder/operator observations: leverage, speed, taste, compounding, systems.
5. Personal discoveries: things Shivang notices while building, reading, experimenting, or using tools.
6. Recruiter/founder proof-of-work: concise, non-confidential examples from `/Users/shivang/dev/AIConcierge321` that show shipping velocity, production judgment, architecture taste, reliability thinking, and business impact.

Recent engagement lesson:
- Shivang's best recent X posts reached ~1.1k-1.2k views when they attached to an active AI/agent conversation, credited a relevant source, contained concrete mechanisms, and framed a real technical tradeoff.
- Optimize future posts for: source/event + technical takeaway + tradeoff/surprise + simple punchline.
- Strong standalone posts should include at least one concrete technical noun/mechanism: terminal agent, bash/read/write, tool loop, KV cache, context window, memory retrieval, eval harness, trace logs, retry policy, idempotency, state machine, latency/cost, orchestration, schema validation, observability, vendor failure mode.
- Prefer source-aware hooks such as "Takeaway from...", "I expected X to matter more", "One infra tradeoff I underestimated", "Most people think X. In practice Y." over generic AI commentary.
- Use 0-2 relevant hashtags only, usually `#AIAgents`, `#LLM`, `#AIInfra`, `#DevTools`, `#OpenSource`, or `#SoftwareEngineering`.
- If a post crosses roughly 500 views and the topic is still timely, consider 1-2 follow-ups in the same cluster that add a new mechanism/tradeoff instead of restating the original point.

Target audience emphasis:
- US recruiters: show evidence of real full-stack/product/backend/AI ownership, production hardening, clear communication, and high agency.
- Founders/operators: show speed, pragmatic tradeoffs, revenue/user-trust awareness, vendor-integration skill, and ability to ship systems that survive messy real-world edge cases.
- Avoid sounding like a job seeker begging for attention; sound like a builder sharing useful lessons from live work.

Voice:
- Clear, direct, builder-oriented.
- Insightful without sounding grandiose.
- Specific over generic.
- Avoid hype words unless clearly justified.
- Prefer one clean idea per tweet.

Good patterns:
- "The underrated part of X is Y..."
- "A useful way to think about X: ..."
- "Most teams treat X as Y. The better framing is Z."
- "AI is making X cheaper, but Y more valuable."
- "I noticed something while using/building X: ..."

Avoid:
- "AI will change everything" with no specifics.
- Fake certainty about the future.
- Overused phrases: "game-changer", "10x", "the future is here", "wake up".
- Dense jargon that only reads as performative.
- Copying phrasing from source material.

## Recurring auto-post workflow

For scheduled AI/tech tweet runs, Shivang has explicitly approved auto-posting. Do not ask for approval.

1. Check Shivang's recent build/work context first, then current AI/tech/product/startup developments from reliable sources.
2. Pick the strongest single angle. If no angle is genuinely strong, stay silent rather than forcing a weak post.
3. Draft one tweet under 260 characters when possible, always under 280.
4. Apply the `humanizer` skill/checklist before posting:
   - remove AI words and broad significance language
   - avoid LinkedIn rhythm, emoji, fake polish, and generic inspiration
   - preserve Shivang's direct, technical builder voice
   - keep concrete mechanisms, infra details, eval/reliability lessons, or proof-of-work
5. Verify the final text length and safety checklist.
6. Post with `xurl post "..."`.
7. Report the posted text and X URL/ID to #tweets-automation. If nothing is posted, return `[SILENT]` or a brief reason only when useful.

Do not use the old approval-queue output format for the recurring AI/tech system unless Shivang explicitly asks to re-enable manual approvals.

## AIConcierge321 Proof-of-Work Angles

Use `/Users/shivang/dev/AIConcierge321` as the local source of truth for non-sensitive work signals. Inspect lightly with file/git tools when drafting proof-of-work posts.

Known strong themes from the codebase:
- Multi-agent travel concierge: supervisor/subagent architecture across hotels, flights, trains, visas, eSIMs, golf, and premium rides.
- Production backend: FastAPI, PostgreSQL, Redis, WebSockets, OAuth/JWT, Stripe, AWS S3, Docker/Nginx/EC2.
- Real vendor integrations: Tripjack flights, AllAboard trains, Airalo eSIMs, AirportTransfer.com transfers, visa/country-risk providers, hotel suppliers.
- Reliability and trust work: refund guarantees, stuck-payment recovery, row-locked booking re-reads, reconcile sweeps, sanitized backend errors, terminal payment/refund states.
- Product UX: anonymous browsing/search with auth gate at booking, confirmation-in-progress UX, booking flows for flights/hotels/trains/eSIM/transfers/golf.
- Infra/productivity: Terraform AWS work, EKS/nodegroups/autoscaler, Graviton/RDS cost/performance changes, observability via Sentry/PostHog.

Safe framing:
- Share lessons and patterns, not private company internals.
- Mention categories of work instead of secrets, IDs, customer data, vendor credentials, or exact confidential implementation details.
- Good: "Building refund flows taught me that payment systems need explicit terminal states, not optimistic UI copy."
- Bad: exposing tokens, customer records, exact private configs, or unapproved business metrics.

Recruiter/founder positioning:
- Show the judgment behind the work: failure modes considered, user trust protected, complexity simplified, production edge cases handled.
- Prefer "what I learned shipping X" over "look how great I am".
- Strong posts should make a founder think: "this person can own messy product/engineering problems end-to-end."

## User-Discovered Insight Workflow

When Shivang shares an insight/discovery and asks to post it:
1. Extract the core idea in one sentence.
2. Draft 1-3 tweet options depending on ambiguity.
3. If the user gave final wording and says "post this" or equivalent, preserve their voice and make only minor grammar/length fixes.
4. If claims are factual/current, verify with web search unless the user is clearly sharing a personal observation.
5. Before posting, ensure the final text is visible in the conversation and the user's intent to post is explicit.
6. Post with `xurl post "..."` only after X auth is configured and intent is explicit.
7. Return the posted tweet ID/URL if available from `xurl` output.

### Project-launch / not-yet-tested wording

When Shivang asks to post a launch or campaign for a project that is still being tested, do not overclaim completion, adoption, or production readiness. Preserve the excitement but add explicit uncertainty/progress language such as:
- "Local testing is in progress — stay tuned."
- "Testing in progress."
- "This is the direction I’m exploring/building."

For multi-post sequences, apply the caveat across the campaign, not just the first tweet. Prefer "goal", "exploring", "building", and "local testing" over "shipped", "validated", "production-ready", or hard claims unless verified from the repo and the user wants that framing.

Acceptable explicit posting intents include:
- "post this"
- "tweet this"
- "send it"
- "approve 2"
- "post option 1"
- "reply to him" / "reply to them" when a specific X post is already the target and the reply draft is visible in the conversation

If intent is ambiguous, draft and ask for approval instead of posting. However, once Shivang has shared a specific X post, you have drafted a reply, and he says "reply to him" or equivalent, treat that as approval to post the reply rather than merely re-showing the draft.

Reply-length pitfall: X replies may need to be condensed under the character limit. Before calling `xurl reply`, calculate the final body length. If the approved draft is too long, compress it while preserving the core meaning and Shivang's casual builder voice; do not ask for another round unless the compression changes the substance.

## X/Twitter Posting Procedure

Prerequisite: load the `xurl` skill for command details and safety rules.

Also see:
- `references/x-developer-setup-and-policy.md` for X Developer Portal setup, the approved data-use description, and xurl auth/credits pitfalls.
- `references/local-work-summary-cron.md` for the proven weekday end-of-day local-work-summary cron shape, safety guardrails, model pinning, and verification caveats.
- `references/x-tier-quota-recovery.md` for diagnosing and recovering from `HTTP 429: usage limit` fleet outages, the cadence-bomb pattern, and cadence recommendations for each autopost job type.

Verification:
```bash
xurl auth status
xurl whoami
```

Expected auth shape:
- A named app such as `my-app` should be marked as default with `▸`.
- The OAuth2 username under that app should also be marked with `▸`.
- If `default` has no credentials but `my-app` has OAuth2, run `xurl auth default my-app USERNAME` and verify again.

Post:
```bash
xurl post "Final tweet text"
```

Rules:
- Never read, print, summarize, or upload `~/.xurl`.
- Never ask the user to paste tokens or secrets.
- Never use `--verbose` or inline credential flags.
- Never post from a cron job unless Shivang has explicitly changed the mode to auto-post. Shivang has explicitly changed the recurring AI/tech tweet system to auto-post mode; those jobs may post after applying the humanizer checklist and safety checks.
- For approval-queue mode, every post needs a specific approval tied to a specific draft.
- If `xurl search` or other read endpoints fail with `CreditsDepleted`, do not treat auth as broken if `xurl whoami` works. It is an X credits/billing issue; continue with non-API trend/context sources and only test posting with an approved real post.

## Source Priority for Shivang

When drafting for Shivang, use this source priority:
1. His own recent build/work context from `/Users/shivang/dev/AIConcierge321`.
2. Recent session context from `session_search` — what he worked on, studied, watched, debugged, learned, or experimented with.
3. Current AI/tech/product news only as secondary framing.

This means the best recurring posts are usually anchored in:
- recent AWS / infra / load-testing work
- multi-agent architecture and vendor-integration lessons
- reliability, refunds, payments, observability, and trust boundaries
- learning velocity across unfamiliar languages, frameworks, or tools
- videos/articles Shivang recently watched or discussed

Do not default to generic news commentary when there is no strong connection to Shivang's real work or learning.
If a video/article creator is relevant and the exact public handle or URL is visible in session context, an optional tagged draft is fine. Never guess handles.

## Cadence Options

Current default for Shivang:
- Daily must-post approval queue at 12:45 PM IST so the first review lands at the start of the broader Europe + US attention window.
- 45-minute opportunity scans from 12:45 PM IST through 3:45 AM IST, covering Europe/London plus US workday and evening attention.
- Discovery-led posting whenever Shivang shares an insight and explicitly asks to post.

Timing rationale:
- Optimize for Europe/London plus US recruiters and founders without forcing low-quality posts.
- Prefer one strong daily queue plus selective 45-minute scans that can stay silent when there is nothing genuinely fresh.
- Bias toward posts that show real output, judgment, learning speed, and production hardening instead of generic AI hot takes.

Cadence options:
- Light: 1 queue/day, drafts only when there is a strong builder-context angle.
- Standard: daily must-post + selective 45-minute scans during the active window.
- High-frequency: same window, but only if the scans are allowed to return `[SILENT]` when there is no genuine opportunity.
- Discovery-led: post when Shivang shares an insight and explicitly asks to post.
- End-of-office-day reflection: weekdays at 7:30 PM IST, summarize safe local work signals into tweet angles for review; pin recurring Hermes jobs to `openai-codex` / `gpt-5.5` unless Shivang asks otherwise. See `references/local-work-summary-cron.md`.

When changing cadence, update existing Hermes cron jobs rather than creating duplicates unless the user wants separate queues.

## Quality Checklist

Before presenting or posting a tweet:
- [ ] Under 280 characters; ideally under 260 for edit buffer.
- [ ] One clear idea.
- [ ] No private/sensitive info.
- [ ] No unverified factual claim presented as certain.
- [ ] No plagiarism or close paraphrase from source.
- [ ] No spammy CTA or engagement bait.
- [ ] Sounds like a thoughtful builder/operator, not a brand slogan.
- [ ] If posting, user approval is explicit and final text is visible.

## Common Pitfalls

1. Posting from the daily queue without explicit approval. The queue is for review only.
2. Turning every news item into commentary. Prefer implications and patterns over headlines.
3. Over-polishing user discoveries until they lose personality. Preserve Shivang's phrasing when possible.
4. Using broad claims like "AI agents are the future" without a concrete mechanism.
5. Treating X auth as an agent task. The user must configure credentials manually; the agent only checks `xurl auth status`.
6. Leaving recurring cron jobs on an inherited model that later becomes rate-limited or quota-blocked. For important recurring queues/scans, pin the cron job's `model` and `provider` explicitly instead of relying on whatever the interactive session is using at creation time.
7. Assuming `deliver=origin` always maps back to the current chat. Cron jobs run without a live user turn; when there is no origin thread available, Hermes may fall back to the configured home channel. Verify delivery expectations when testing scheduled social workflows.
8. Creating bot-to-bot acknowledgement loops in Discord. When another Hermes bot/profile posts status-only messages like "Done", "Received", "Paused", "Stopped", "[no reply]", or reacts with 👍, do not keep acknowledging the acknowledgement. Only respond when there is a new human instruction, an explicit request for edits/posting, or actionable tweet-approval content.
9. Letting reply/autopost scanners run at `every 5m`. X API tier caps are not designed for that cadence — a single reply scanner at this cadence can exhaust the monthly quota in under 24 hours and silently 429 every other X-facing job in the same profile. Default reply-scan cadence to `every 30m` or longer; treat anything below `every 15m` as a quota bomb unless Shivang explicitly approves it for a short campaign.
10. Treating `last_status: error` on a cron as a transient retry. When `hermes cron list --all` shows a job in `paused` state after 429/quota errors, an unpause alone is not enough — the underlying cadence/credit issue must be fixed first or the job will re-pause within minutes.

## Cron reliability note

For recurring X/Twitter drafting jobs, treat model pinning as part of setup:
- Pin `provider` + `model` on the cron job when creating or updating it.
- If a cron starts failing repeatedly, check whether the pinned model is quota-limited before changing the prompt.
- After changing a cron's model/provider, manually trigger one run and confirm `last_status: ok` before trusting the next scheduled window.

## X API tier-quota failure pattern (autopost fleet)

When multiple X-facing cron jobs (`post`, `reply`, `search`) start failing with `HTTP 429: The usage limit has been reached` inside a narrow window (often 30–60 min), this is **not** a per-job rate limit — it is the X API tier/monthly quota hitting its cap. `xurl` may still answer `whoami` because that endpoint is cheap, but every write and many reads will 429.

What the scheduler does in this state: the scheduler auto-pauses jobs on persistent errors. They will show as `paused` in `hermes cron list --all` with a `next run` timestamp in the past, **and they will not auto-resume** after the cap resets. Each paused job needs an explicit `hermes cron resume <id>` after the underlying issue is fixed.

The high-cadence job is almost always the root cause. An `every 5m` reply scanner can burn a single monthly cap in well under 24 hours. Auditing cadence before resuming is non-negotiable; a sensible starting point is `every 30m` for reply scans and `every 2h` for opportunity scans.

Recovery procedure (do these in order):
1. Diagnose: `hermes cron list --all` — note every `paused` job and its `last_status` error. The first one to fail in the window is usually the rate-limit culprit.
2. Fix credits/tier: top up X API credits (Developer Console → Billing) or upgrade the tier cap (Products → Pro/Basic → Usage). Verify with `xurl post` against an approved draft, or run `xurl search -n 1`.
3. Fix cadence: edit the highest-cadence paused job first. Move from `every 5m` → `every 30m` (or longer) before resuming anything.
4. Resume: `hermes cron resume <job_id>` for each paused job, one at a time. Pause and re-fix if any of them immediately re-429s.
5. Verify: wait for one full cycle of each resumed job and confirm `last_status: ok` in `hermes cron list --all`. Do not declare the fleet healthy until at least one of each cadence has fired cleanly.

Avoid retrying writes during a 429 — each retry consumes a small slice of the remaining window and pushes the recovery window further out.

## Handling cron digests delivered from other profiles

Some cron digests (notably `office-work-summary-for-tweets`) are owned by Shivang's office-laptop/work-agent profile and delivered into shared Discord channels like `#tweets-automation`. When the personal-Hermes bot receives such a digest, it is a **passive data drop**, not a request to draft or post.

- Do not draft tweets from a partial digest. If the message is paginated (e.g. ends with `(1/6)`), acknowledge receipt, wait for the rest, and explicitly note that you are waiting.
- Do not edit or `resume` jobs that belong to another profile. `cronjob` actions from this profile only affect jobs owned by this profile.
- Do surface downstream issues the digest reveals (e.g. a paused autopost fleet) — those are usually owned by this profile and worth flagging.

## Paginated cron responses

If a cron job's output arrives paginated (Discord truncates very long digests into N messages), treat each page as a partial view:
- Do not draft a tweet, post, or reply from a single page.
- Either wait for the full set of pages or note explicitly which sections you have not yet seen.
- A short acknowledgement is fine; a long analysis from incomplete data is not.

## Verification Checklist

- [ ] `xurl` is installed when posting is requested.
- [ ] `xurl auth status` shows a configured default app/account.
- [ ] Tweet text is final and visible.
- [ ] User intent to post is explicit.
- [ ] `xurl post` returns successful JSON.
- [ ] Response includes confirmation and tweet ID/URL when available.
- [ ] Fleet health: `hermes cron list --all` shows the autopost/news jobs in `active` state (not `paused` with stale 429 errors). If any job is paused due to `HTTP 429: usage limit`, follow the recovery procedure in "X API tier-quota failure pattern" before declaring the workflow healthy.
