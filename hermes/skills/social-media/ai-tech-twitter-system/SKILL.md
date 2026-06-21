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
- For scheduled queues, do not post automatically; ask for approval.
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

## Regular Approval Queue Workflow

For scheduled runs:
1. Check current AI/tech/product/startup developments from reliable sources.
2. Pick 2-3 candidate angles.
3. Draft 3 tweets under 260 characters each.
4. Add a one-sentence rationale for each.
5. Add one optional thread idea when useful.
6. End with an explicit approval request.
7. Do not post from a scheduled run.

Output format:

```text
Daily AI/tech tweet queue — <date>

1) <tweet candidate>
Why this works: <one sentence>

2) <tweet candidate>
Why this works: <one sentence>

3) <tweet candidate>
Why this works: <one sentence>

Optional thread idea: <short outline or 'None today'>

Approval: Reply with the number you approve, edits you want, or 'skip'. I will only post after explicit approval.
```

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
- Never post from a cron job unless Shivang has explicitly changed the mode to auto-post.
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

## Cron reliability note

For recurring X/Twitter drafting jobs, treat model pinning as part of setup:
- Pin `provider` + `model` on the cron job when creating or updating it.
- If a cron starts failing repeatedly, check whether the pinned model is quota-limited before changing the prompt.
- After changing a cron's model/provider, manually trigger one run and confirm `last_status: ok` before trusting the next scheduled window.

## Verification Checklist

- [ ] `xurl` is installed when posting is requested.
- [ ] `xurl auth status` shows a configured default app/account.
- [ ] Tweet text is final and visible.
- [ ] User intent to post is explicit.
- [ ] `xurl post` returns successful JSON.
- [ ] Response includes confirmation and tweet ID/URL when available.
