---
name: ai-tech-twitter-system
description: Use when drafting, approving, scheduling, or posting AI/tech/product insight tweets for Shivang. Covers the full v2 pipeline — daily autopost, breaking-news trigger, quote-tweet amplification, image/screenshot attachment, multi-angle event clusters, reply-engagement scanning, and user-discovered insights. Auto-post mode is on.
version: 2.0.0
author: REDACTED_SET_LOCALLY
license: MIT
metadata:
  hermes:
    tags: [twitter, x, ai, tech, content, approval-queue, social-media]
    related_skills: [xurl, humanizer]
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
- Quote-tweet a high-engagement AI tweet with a new angle.
- Attach screenshots/images to tweets for higher reach.
- Post immediately on a breaking AI event (new model, benchmark, guardrail).
- Reply to high-engagement AI tweets from large accounts for visibility.
- Post multiple angles on the same event for audience testing.
- Analyze a competitor's X/Twitter growth strategy and apply learnings.

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

Growth tactics (studied from high-engagement AI accounts, July 2026 — see `references/twitter-growth-tactics.md` for the full competitive analysis):

1. **Quote-tweet amplification.** When a breaking AI event is happening, don't only post an original take. Find the highest-engagement tweet about it and quote-tweet with a *new angle* — a correction, a cost analysis, a mechanism explanation, a "what this means for builders" framing. This rides the original tweet's reach and puts the post in front of the original author's audience. A 2k-follower account using this tactic regularly gets 5k–67k views per post.

2. **Attach images/screenshots to every high-stakes tweet.** Tweets with benchmark screenshots, terminal output, or source tweet images get 2–5× the reach of pure-text tweets. When posting about a benchmark, model release, or guardrail behavior, attach a screenshot of the relevant data. Use `xurl post --media <path>` to attach images.

3. **Speed on breaking events.** When a major model drops or a benchmark publishes, post within *minutes*, not at the next 45-minute scan window. Add a breaking-news trigger path: if a scan detects a major release/event, post immediately rather than waiting for the next scheduled run.

4. **Multiple angles on the same event.** Instead of one perfect tweet per event, post 3–4 quick takes within the same hour: the news itself, the cost angle, the mechanism/guardrail angle, the "what this means for builders" angle. Each catches a different audience and some will break out. Don't over-polish each one — prioritize speed and a distinct angle over perfection.

5. **Reply in high-visibility reply sections.** Scan for high-engagement tweets from major AI accounts and reply with a useful technical addition (not a generic "great point"). This puts Shivang's handle in front of the big account's audience. A reply scanner at `every 30m` cadence is safe for the API quota.

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
3. Draft one tweet **aiming for ≤260 characters from the first attempt**, never exceed 280. The 260 budget is for edit room after humanizer passes, hashtag adds, and any trim-and-tighten round. Drafting long then trimming 3-4 times wastes turns and tends to lose the mechanism; a tight first draft usually survives the humanizer pass as-is.
4. Apply the `humanizer` skill/checklist before posting:
   - remove AI words and broad significance language
   - avoid LinkedIn rhythm, emoji, fake polish, and generic inspiration
   - preserve Shivang's direct, technical builder voice
   - keep concrete mechanisms, infra details, eval/reliability lessons, or proof-of-work
5. Verify the final text length and safety checklist.
6. Post with `xurl post "..."`.
7. Report the posted text and X URL/ID to #tweets-automation. If nothing is posted, return `[SILENT]` or a brief reason only when useful.

Do not use the old approval-queue output format for the recurring AI/tech system unless Shivang explicitly asks to re-enable manual approvals.

## Quote-Tweet Amplification Workflow

When a breaking AI event is happening (new model release, benchmark, guardrail discovery, major API change), don't only post an original take. Use `xurl quote` to ride the reach of high-engagement tweets about the same event.

Procedure:
1. Search for the event: `xurl search "model name or event" -n 10 --sort public_metrics.impression_count` (or use raw API with `order=recency` for breaking events).
2. Pick the highest-engagement tweet from a larger account (1k+ followers). This maximizes the audience that sees the quote-tweet.
3. Draft a **new angle** — not a restatement. Good quote-tweet angles:
   - Cost analysis: "X is 2x more expensive per task than Y"
   - Correction/warning: "This is confirmed — set this flag to false or X will silently downgrade"
   - Mechanism explanation: "What's actually happening under the hood is..."
   - Builder implication: "What this means for production agents..."
4. Apply the humanizer checklist (same as regular posts).
5. Post with `xurl quote POST_ID "Your take"`.
6. If the original tweet has an image/screenshot, consider also attaching one in the quote tweet for extra reach.

Quota note: Each `xurl quote` is a write endpoint. During breaking events, limit to 1-2 quote tweets per event to avoid burning API quota. The breaking-news scan (see below) should surface the opportunity; the quote-tweet is the action.

xurl quote + media note: `xurl quote POST_ID "text"` supports `--media-id` the same way `xurl post` does. Upload the image first with `xurl media upload`, then pass the returned media ID. If `xurl quote --media-id` fails with a 400, fall back to `xurl post "text" --media-id MEDIA_ID` without the quote reference — some X API tier configurations restrict media on quote tweets but allow it on standalone posts.

Example workflow:
```bash
# Find the highest-engagement tweet about the event
xurl search "Claude Opus 5 benchmark" -n 10

# Quote-tweet with a new angle
xurl quote 1234567890 "Opus 5 is 2x more expensive per task than GPT 5.6 Sol on the Artificial Analysis Index. The benchmark win is real, but the cost/impression ratio matters more for production agent budgets."
```

## Image/Screenshot Attachment Workflow

Tweets with images get 2-5x the reach of pure-text tweets. When posting about a benchmark, model release, terminal output, or guardrail behavior, attach a screenshot.

### When to attach images

Always attach an image when the tweet is about:
- Benchmark results (screenshot the benchmark page/chart)
- Terminal output or code (screenshot the terminal)
- Model behavior/guardrails (screenshot the conversation or settings)
- A source tweet (screenshot the tweet as a backup image in case the quote-tweet doesn't render)
- Any "proof" claim — show the evidence

### How to capture and attach

**Option A: Screenshot from browser**
```bash
# If a URL is available, use browser tools to screenshot the page
# Save to /tmp/tweet_screenshot.png

# Upload to X
xurl media upload /tmp/tweet_screenshot.png
# Returns: {"data": {"id": "MEDIA_ID", ...}}

# Post with the media
xurl post "Tweet text" --media-id MEDIA_ID
```

**Option B: Screenshot a terminal/code output**
```bash
# Use the macOS screencapture command for a specific window or region
screencapture -i /tmp/tweet_screenshot.png  # interactive selection

# Or use a script to render text/code to an image
python3 -c "
from PIL import Image, ImageDraw, ImageFont
img = Image.new('RGB', (1200, 400), color=(17, 17, 17))
draw = ImageDraw.Draw(img)
font = ImageFont.truetype('/System/Library/Fonts/Menlo.ttc', 24)
draw.text((20, 20), 'Your code/output here', fill=(255, 255, 255), font=font)
img.save('/tmp/tweet_screenshot.png')
"
```

**Option C: Screenshot a web page via headless browser**
```bash
# Use Chrome headless to capture a page
google-chrome --headless --screenshot=/tmp/tweet_screenshot.png --window-size=1200,600 "https://example.com"
# Or use the browser tool's screenshot capability
```

### Image optimization

Mac screenshots can be very large RGBA PNGs. Before uploading, convert to a smaller RGB JPEG:
```bash
python3 - <<'PY'
from PIL import Image
src = '/tmp/tweet_screenshot.png'
out = '/tmp/tweet_image.jpg'
im = Image.open(src).convert('RGB')
im.thumbnail((1600, 1600))
im.save(out, quality=90, optimize=True)
print(out)
PY
xurl media upload --media-type image/jpeg --category tweet_image /tmp/tweet_image.jpg
```

### Quote-tweet with image

```bash
xurl media upload /tmp/screenshot.png
# Returns MEDIA_ID
xurl quote POST_ID "Your take" --media-id MEDIA_ID
```

## Breaking-News Immediate-Post Trigger

When a major AI event is detected (new model release, benchmark, guardrail discovery, API change), post immediately rather than waiting for the next 45-minute scan window.

### Detection criteria (what counts as "breaking")

A breaking event is:
- A new model release or major version (GPT, Claude, Gemini, Llama, etc.)
- A benchmark result from a credible source (Artificial Analysis, LMSYS, etc.)
- A guardrail/safety behavior discovery (silent fallback, rerouting, etc.)
- A major API change or pricing change from an AI provider
- A significant open-source model release

### Trigger workflow

The breaking-news trigger runs as a cron job at `every 30m` during the active window (12:45 PM IST – 3:45 AM IST). When it detects a breaking event:

1. Search X for recent high-engagement tweets about the event: `xurl search "event keywords" -n 10`
2. Cross-reference with Hacker News / AI news sources for confirmation.
3. If confirmed and no existing tweet from Shivang covers this event:
   a. Post the first take immediately (the news itself + initial analysis) → `xurl post`
   b. If there's a high-engagement tweet to quote, use `xurl quote` instead.
   c. Attach a screenshot if possible (benchmark chart, terminal output, etc.).
4. Schedule 2-3 follow-up angles within the next 30-60 minutes (see Multi-Angle Posting below).
5. Report the posted tweet(s) to #tweets-automation.

### What is NOT breaking news

- Minor product updates, bug fixes, or UX changes
- Opinion pieces or analysis by non-primary sources
- Rumors or unconfirmed leaks
- Generic "AI is changing" trend pieces

When in doubt, defer to the regular 45-minute scan. The breaking-news trigger should fire at most 2-3 times per week.

## Multi-Angle Posting on Same Event

Instead of one perfect tweet per event, post 3-4 quick takes within the same hour. Each one catches a different audience and some will break out.

### Angle templates

When a breaking event happens, draft these angles (pick the strongest 3-4):

1. **The news itself** (fastest, post first): "X just released Y. Initial take: Z."
2. **The cost/pricing angle**: "X costs $N per task. That's 2x more than Y. For production agents running 10k tasks/day, that's $N/day."
3. **The mechanism/guardrail angle**: "Under the hood, X is doing Y. The guardrail behavior means Z for production use."
4. **The builder implication**: "What this means for agent builders: you need to handle X in your retry/fallback logic."
5. **The comparison angle**: "X vs Y on benchmark Z: X wins on A but loses on B. The tradeoff is C."

### Execution

- Post the first angle immediately (breaking-news trigger).
- Schedule follow-up angles 15-30 minutes apart using one-shot cron jobs or the next scan window.
- Each follow-up should add a NEW mechanism/tradeoff, not restate the original point.
- If an earlier tweet in the cluster is gaining traction (500+ views), prioritize follow-ups that add depth to that specific angle.
- Do NOT post all 3-4 at once — spacing them out gives each one its own chance to break out.

### Quota management

Each post + each quote-tweet is a write endpoint hit. During a breaking event, keep total writes to 3-4 per hour. The 45-minute opportunity scans should go [SILENT] during a breaking-event cluster to conserve quota.

## Reply-Engagement Scanner

Scan for high-engagement tweets from major AI accounts and reply with a useful technical addition. This puts Shivang's handle in front of the big account's audience.

### Target accounts

Monitor replies/mentions from accounts in the AI/ML space with 5k+ followers. Priority targets:
- AI lab accounts (Anthropic, OpenAI, Google DeepMind, xAI)
- AI researchers and engineers with large followings
- AI tool builders (Harrison Chase, LangChain, etc.)
- AI news/analysis accounts

### Scanner workflow (cron at `every 30m`)

1. Search for recent high-engagement AI tweets: `xurl search "AI OR LLM OR agent OR Claude OR GPT" -n 20`
2. Filter for tweets with 100+ likes and from accounts with 5k+ followers.
3. For each candidate, check if Shivang has already replied (skip if so).
4. Draft a **useful technical addition** — not a generic "great point":
   - Add a mechanism, tradeoff, or production lesson the original tweet missed
   - Share a relevant data point or benchmark
   - Correct a technical inaccuracy (politely)
   - Ask a sharp technical question that shows depth
5. Apply the humanizer checklist.
6. Post with `xurl reply POST_ID "Reply text"`.
7. Limit to 2-3 replies per scan cycle to conserve API quota.

### Reply quality bar

A reply should make a reader think "this person knows what they're talking about" — not "this person is engagement farming."

Good reply patterns:
- "One thing to add: in production, X also fails when Y. We hit this when..."
- "The benchmark numbers are impressive, but the cost/impression ratio tells a different story..."
- "This matches what we see with [specific mechanism]. The edge case is..."

Bad reply patterns:
- "Great point!" or "Totally agree!"
- Generic restatement of the original tweet
- Link-dropping without context
- "Check out my project" self-promotion

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

### Browser-based automation (FREE — default since July 2026)

X API credits depleted, so the default posting method is now browser-based via Arc browser. X.com is logged in on Arc, and the script `/Users/shivang/.hermes/scripts/x_browser.py` drives it via AppleScript JavaScript execution. This costs $0 — no API credits needed.

Available commands:
```bash
python3 /Users/shivang/.hermes/scripts/x_browser.py check                          # Check login status
python3 /Users/shivang/.hermes/scripts/x_browser.py search "query" 20              # Search tweets
python3 /Users/shivang/.hermes/scripts/x_browser.py post "tweet text"              # Post a tweet
python3 /Users/shivang/.hermes/scripts/x_browser.py quote "URL" "quote text"       # Quote-tweet
python3 /Users/shivang/.hermes/scripts/x_browser.py reply "URL" "reply text"       # Reply to tweet
python3 /Users/shivang/.hermes/scripts/x_browser.py timeline 20                    # Get home timeline
python3 /Users/shivang/.hermes/scripts/x_browser.py profile "@handle" 20           # Get user's tweets
```

Requirements:
- Arc browser must be running with X.com logged in.
- "Allow JavaScript from Apple Events" must be enabled in Arc (Developer menu).
- The script uses `osascript` to execute JavaScript in Arc's active tab.

Limitations:
- Browser automation is slower than API calls (~5-10s per operation vs <1s for API).
- Cannot attach images yet (only text tweets, quote tweets, replies).
- The active tab is shared — don't navigate Arc while a cron job is running.

### xurl API (fallback — requires credits)

The xurl API still works if credits are topped up. Use it as a fallback when Arc is closed or browser automation fails.

Prerequisite: load the `xurl` skill for command details and safety rules.

Also see:
- `references/x-developer-setup-and-policy.md` for X Developer Portal setup, the approved data-use description, and xurl auth/credits pitfalls.
- `references/local-work-summary-cron.md` for the proven weekday end-of-day local-work-summary cron shape, safety guardrails, model pinning, and verification caveats.
- `references/x-tier-quota-recovery.md` for diagnosing and recovering from `HTTP 429: usage limit` fleet outages, the cadence-bomb pattern, and cadence recommendations for each autopost job type.
- `references/x-api-cost-analysis.md` for X API pay-per-use pricing, the session DB cost analysis technique, real cost data from Shivang's fleet, the browser-based $0/month alternative, and cost-safe cadence rules.
- `references/x-api-pricing-and-cost-analysis.md` for X API pay-per-use pricing table, real cost data from Shivang's fleet (session DB analysis technique), monthly projections at various cadences, and the $0/month browser alternative.
- `references/twitter-growth-tactics.md` for competitive analysis of high-engagement AI accounts (quote-tweet amplification, image attachment, breaking-news speed, multi-angle posting, reply engagement) with concrete engagement data and implementation priorities.
- `scripts/x_browser.py` — the browser-based X.com automation script (free alternative to xurl API, drives Arc via AppleScript JS). Copy to `~/.hermes/scripts/x_browser.py` for cron jobs.
- `scripts/x_browser.py` — the browser-based X.com automation script (free alternative to xurl API, drives Arc via AppleScript JS).

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
- Breaking-news trigger at `every 30m` during the same active window — fires immediately on major AI events instead of waiting for the next 45-minute scan.
- Reply-engagement scanner at `every 30m` during the same active window — replies to high-engagement AI tweets from large accounts.
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

1. Posting from the daily queue without explicit approval — **only applies when auto-post mode is OFF**. Shivang has explicitly switched the system to auto-post mode; the daily autopost and opportunity scan jobs post without asking. The approval queue is re-enabled only if Shivang explicitly asks for it.
2. Turning every news item into commentary. Prefer implications and patterns over headlines.
3. Over-polishing user discoveries until they lose personality. Preserve Shivang's phrasing when possible.
4. Using broad claims like "AI agents are the future" without a concrete mechanism.
5. Treating X auth as an agent task. The user must configure credentials manually; the agent only checks `xurl auth status`.
6. Leaving recurring cron jobs on an inherited model that later becomes rate-limited or quota-blocked. For important recurring queues/scans, pin the cron job's `model` and `provider` explicitly instead of relying on whatever the interactive session is using at creation time.
7. Assuming `deliver=origin` always maps back to the current chat. Cron jobs run without a live user turn; when there is no origin thread available, Hermes may fall back to the configured home channel. Verify delivery expectations when testing scheduled social workflows.
8. Creating bot-to-bot acknowledgement loops in Discord. When another Hermes bot/profile posts status-only messages like "Done", "Received", "Paused", "Stopped", "[no reply]", or reacts with 👍, do not keep acknowledging the acknowledgement. Only respond when there is a new human instruction, an explicit request for edits/posting, or actionable tweet-approval content.
9. Letting reply/autopost scanners run at `every 5m`. X API tier caps are not designed for that cadence — a single reply scanner at this cadence can exhaust the monthly quota in under 24 hours and silently 429 every other X-facing job in the same profile. Default reply-scan cadence to `every 30m` or longer; treat anything below `every 15m` as a quota bomb unless Shivang explicitly approves it for a short campaign.
10. Treating `last_status: error` on a cron as a transient retry. When `hermes cron list --all` shows a job in `paused` state after 429/quota errors, an unpause alone is not enough — the underlying cadence/credit issue must be fixed first or the job will re-pause within minutes.
11. Drafting the tweet body long (400+ chars) and trimming down to 280 in 3-4 round-trips. This wastes turns and tends to lose the concrete mechanism with each pass. Aim for ≤260 characters on the first draft — that gives real edit room for humanizer fixes, hashtag addition, and a Shivang-driven tweak without thrashing the message. If the first draft is over 350, you have probably included filler that needs to go, not content that needs to stay.
12. **Auto-mirror noise loops in cron-delivered Discord threads.** Threads opened by a cron job (e.g. `office-work-summary-for-tweets` → #tweets-automation thread 1529126825559588995) auto-mirror every Hermes tool output and assistant turn into the thread. Internal reasoning, tool-result previews, and even `delete_message` cleanup attempts all surface as visible Discord messages to Shivang and any other bots watching the thread. The clean pattern: post the tweet via `xurl post`, send the report via `hermes send --to discord:<channel_id>:<thread_id>` ONCE, then stop touching the thread — no follow-up `fetch_messages` to "verify", no `delete_message` cleanup loops (every delete call itself gets mirrored and creates more noise), no `cronjob` actions, no in-thread clarifications. The single `hermes send` is the only thread message that should land. If you need a "voice calibration" check (e.g. `xurl search from:shivangchheda22 -is:retweet`), run it via terminal — it does not need to be visible in the thread.
13. **Cron `*/N` schedule pitfall.** `*/45 7-22 * * *` does NOT mean "every 45 minutes from 7am to 10pm". In cron, `*/45` in the minute field means "at minute 0 and 45 of every hour" — i.e. two fires per hour, not every-45-minutes. Similarly `*/30` means "at minute 0 and 30" (every 30 min, which is correct but worth confirming). For true every-N-minutes cadence, use the cron schedule string `every Nm` (Hemis shorthand) instead of raw cron `*/N`. The current fleet uses `*/30 7-22` (correct — fires at :00 and :30) and `*/45 7-22` (semi-correct — fires at :00 and :45, which is 15-min then 45-min gap, not uniform 45-min). If uniform spacing matters, switch to `every 45m` with a time-window guard in the prompt instead.

14. **Browser automation shared-tab conflict.** The `scripts/x_browser.py` script drives Arc's *active tab* — if Shivang is actively browsing in Arc while a cron job fires, the cron job will navigate away from whatever Shivang is doing. This is a UX conflict, not a crash. Mitigation: cron jobs should complete quickly (search + post = ~15s) and the window is the active-window hours (12:45 PM – 3:45 AM IST) when Shivang may not be actively browsing. If Shivang reports tab hijacking, consider opening a dedicated Arc space/window for automation or reducing scanner cadence.

16. **X.com compose button selector: `tweetButtonInline` not `tweetButton`.** The X.com compose page (`/compose/post`) uses `data-testid="tweetButtonInline"` for the post button, NOT `data-testid="tweetButton"`. The `tweetButton` selector only appears on reply dialogs and the home timeline inline compose. The `scripts/x_browser.py` script handles this by trying `tweetButtonInline` first, then falling back to `tweetButton`. If a future X.com UI change renames the selector, run this diagnostic in Arc to find the current one:
```bash
osascript -e 'tell application "Arc" to execute active tab of front window javascript "JSON.stringify(Array.from(document.querySelectorAll(\"button[data-testid]\")).map(b => b.getAttribute(\"data-testid\") + \": \" + (b.disabled ? \"disabled\" : \"enabled\"))).filter(s => s.includes(\"tweet\"))"'
```

17. **X.com search returns crypto/spam for generic AI queries.** Searching `x_browser.py search "Claude OR GPT OR LLM"` returns a mix of relevant tweets and crypto scam spam (especially "Moonshot" token listings). To filter: use more specific queries like `"Kimi K3"` (quoted phrase) or `"Claude API"` instead of broad OR queries. The browser search does not support engagement-based sorting (unlike the X API), so results are purely chronological. To find high-engagement tweets, scan the `metrics` array in each result for "N Likes" or "N reposts" and filter programmatically.

18. **`x_browser.py profile` may return empty on first call.** When navigating to a profile page, the JS extraction runs before X.com finishes rendering the React timeline. If `profile` returns `[]`, either: (a) increase the wait time in the script's `arc_navigate` call, or (b) re-run the command after the page has loaded. The `search` and `check` commands are more reliable because they navigate to pages that load faster.

## X API cost management

The X API uses **pay-per-use pricing** — no subscriptions, no tier caps. You buy credits upfront and they deplete per API call. This is fundamentally different from the old tier-based model (which had monthly caps and HTTP 429 errors).

### The #1 cost: search calls

`xurl search` is by far the most expensive operation in the fleet. Each search returns up to 20 posts at **$0.005 per post = $0.10 per search call**. With 3 scanners running every 30-45 minutes during a 15-hour active window, the fleet makes ~265 search calls in 3 days = **~$26.50 in search alone** (97% of total cost).

Posting, by contrast, is cheap: `xurl post` = $0.015/request. Even 34 post calls in 3 days = only $0.51.

### Credits depleted vs HTTP 429

- **`CreditsDepleted` (HTTP 402)**: account balance is $0. `xurl whoami` still works (owned read = $0.001) but `xurl search` and `xurl post` fail. Fix: deposit more credits at Developer Console → Billing.
- **HTTP 429 (usage limit)**: monthly tier cap hit. All X-facing endpoints fail. Fix: upgrade tier or wait for monthly reset. See `references/x-tier-quota-recovery.md`.

### Cost-safe cadence rules

| Job type | Cost-dangerous | Cost-safe | Rationale |
|---|---|---|---|
| Breaking-news trigger | `every 30m` (burns ~$5/day in searches) | `every 2h` | Most scans find nothing; [SILENT] is the common case |
| Opportunity scan | `every 45m` | `every 2h` | Same — most scans go [SILENT] |
| Reply scanner | `every 30m` | `every 2h` | Searches + user lookups per cycle |
| Daily autopost | 1/day | 1/day | Already safe (1 search/day = $0.10) |
| News digest | every <2h | `every 4h` | Uses web search, not X API — minimal X cost |

At `every 2h` for all scanners: **~$40-60/month**. At `every 30m`: **~$140-273/month**.

### When Shivang asks about X API costs

Use the session DB analysis technique in `references/x-api-cost-analysis.md` to calculate actual spend from terminal command history. The key SQL query pattern:

```sql
SELECT m.tool_calls, m.timestamp
FROM messages m
WHERE m.tool_calls LIKE '%xurl%'
AND m.role = 'assistant'
```

Then parse the JSON `tool_calls` to extract `xurl <subcmd>` commands and multiply by the pricing table in `references/x-api-cost-analysis.md`.

### Recommended credit deposit

- **$50**: ~1 month at reduced cadence (every 2h scanners), ~2 weeks at current cadence
- **$100**: ~2 months at reduced cadence, ~1 month at current cadence
- Minimum deposit is $5 but lasts only days with an active fleet

## Cron reliability note

For recurring X/Twitter drafting jobs, treat model pinning as part of setup:
- Pin `provider` + `model` on the cron job when creating or updating it.
- If a cron starts failing repeatedly, check whether the pinned model is quota-limited before changing the prompt.
- After changing a cron's model/provider, manually trigger one run and confirm `last_status: ok` before trusting the next scheduled window.
- If `xurl search` or `xurl post` fails with `credits depleted` (HTTP 402), do NOT treat it as a cadence/rate-limit issue — the account balance is $0. Tell Shivang to deposit credits at Developer Console → Billing. See `references/x-api-cost-analysis.md` for pricing and cost estimation.

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

**Exception: pre-drafted "Safe tweet angles" sections are an explicit auto-post trigger.** When the work-agent digest contains a section labeled "Safe tweet angles in Shivang's technical builder voice" (or similar) listing 3-5 candidate tweets, that is the work-agent's signal that the input is ready for the auto-post pipeline. In that case:
- Verify all N/N pages have arrived before acting.
- Pick the strongest angle by Shivang's audience (recruiters/founders, concrete mechanism, ≤280 chars).
- Apply the humanizer checklist and post via `xurl post` (auto-post mode is on for this system).
- Do not ask Shivang for approval — the pre-drafting IS the approval handoff.
- After posting, send a single concise report to the thread and stop. See Common Pitfall #12 about thread auto-mirror noise.
- Voice calibration: `xurl search "from:shivangchheda22 -is:retweet" -n 50` via terminal to avoid duplicating a recent angle.

## Paginated cron responses

If a cron job's output arrives paginated (Discord truncates very long digests into N messages), treat each page as a partial view:
- Do not draft a tweet, post, or reply from a single page.
- Either wait for the full set of pages or note explicitly which sections you have not yet seen.
- A short acknowledgement is fine; a long analysis from incomplete data is not.

### Finding the rest of a paginated work-agent digest

The work-agent's `office-work-summary-for-tweets` cron is delivered as a Discord message that **mentions** the personal-Hermes bot. The cron body is usually a single message that ends with `(1/6)`, `(1/7)`, etc. — and the remaining pages are siblings in the same thread, not a multi-message split of the same message.

Pattern when the first page lands in your session:
1. Note the `message_id` from the trigger — that is the anchor of the thread, not a single message.
2. `fetch_messages(channel_id, limit=10)` on the originating channel/thread. All paginated pages from the same cron usually appear as consecutive messages from `hermes-work-agent` within seconds of each other.
3. Walk forward in chronological order. The final page is the one that ends with the `To stop or manage this job…` footer and the section-count marker (e.g. `(6/6)`).
4. Only act on the digest once you have seen the stop-footer page. If the footer is missing, you are still missing pages — wait or escalate, do not draft from what you have.

This is a false-alarm trap: the `(1/6)` marker looks like an error or a crash, but it is just the work-agent's normal "I am going to send six messages, this is the first" pattern. Do not reply to the partial page or you will post from incomplete data.

## Verification Checklist

### Browser-based automation (default, $0/month)
- [ ] Arc browser is running and X.com is logged in: `python3 ~/.hermes/scripts/x_browser.py check`
- [ ] "Allow JavaScript from Apple Events" is enabled in Arc (Developer menu).
- [ ] Tweet text is final and under 280 chars.
- [ ] Humanizer checklist applied.
- [ ] `x_browser.py post` returns `"status": "POSTED"`.
- [ ] After posting, verify by running `x_browser.py profile "@shivangchheda22" 3` to confirm the tweet appears.

### xurl API (fallback, requires credits)
- [ ] `xurl` is installed when posting is requested.
- [ ] `xurl auth status` shows a configured default app/account.
- [ ] Tweet text is final and visible.
- [ ] User intent to post is explicit.
- [ ] `xurl post` returns successful JSON.
- [ ] Response includes confirmation and tweet ID/URL when available.
- [ ] Fleet health: `hermes cron list --all` shows the autopost/news jobs in `active` state (not `paused` with stale 429 errors). If any job is paused due to `HTTP 429: usage limit`, follow the recovery procedure in "X API tier-quota failure pattern" before declaring the workflow healthy.
- [ ] If `xurl search` or `xurl post` fails with `credits depleted` (HTTP 402), switch to browser-based automation (`x_browser.py`) or tell Shivang to deposit credits at Developer Console → Billing.
