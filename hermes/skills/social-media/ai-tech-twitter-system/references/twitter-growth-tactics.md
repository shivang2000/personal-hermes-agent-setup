# Twitter Growth Tactics — Competitive Analysis

Study of high-engagement AI accounts on X/Twitter, conducted July 2026.

## Case Study: @cheatyyyy (Safzan Pirani)

### Profile
- **Handle:** @cheatyyyy
- **Location:** Hyderabad
- **Bio:** "24, sde @ stealth startup, performative nerd"
- **Website:** safzan.dev (personal site with projects + blog)
- **Joined:** February 2022
- **Stats:** 10.2K posts, 816 following, 2,121 followers
- **Posting rate:** ~8 posts/day average over 3.5 years
- **Verified:** Yes

### Recent engagement data (July 2026)

| Tweet | Views | Likes | Reposts | Replies |
|---|---|---|---|---|
| "Claude Opus 5 BEATS Claude Fable 5 on Artificial Analysis Index!" | 67k | 113 | 7 | 1 |
| "Claude Opus 5 is 2x more expensive per task than GPT 5.6 Sol..." | 58k | 341 | 17 | 27 |
| "Claude Fable 5 rerouting to Claude Opus 5..." (quote tweet w/ video) | 5.4k | 68 | 1 | 2 |
| "Huge leap on CritPt, genuinely impressive" | 6.1k | 42 | 0 | 1 |

### 7 tactics that drive his reach

**1. Quote-tweet amplification**
He screenshots/quotes other people's tweets about AI, adds a new angle or correction, and rides their reach. The "Opus 5 silently fallbacks to 4.8" tweet quote-tweeted @tenderizzation — he added the screenshot + the warning, got 5.4k views on a 2k-follower account. His "Opus 5 is 2x more expensive" was a quote tweet of his OWN earlier post, adding new benchmark data → 58k views.

**2. Speed on breaking AI news**
Every top-performing tweet is from the hour of the event. The moment a new model drops, he's posting within the hour — benchmark results, guardrail behavior, cost comparisons. He's not waiting for a daily queue. He's live-reacting.

**3. Screenshot/visual proof**
Almost every tweet has a "View media" link — screenshots of benchmarks, terminal output, other tweets. Pure text tweets get buried; tweets with images get 2-5x the reach.

**4. Volume + frequency**
8 posts/day. Multiple posts on the same breaking topic (he posted 3-4 tweets about Claude Opus 5 in one hour). Each one a slightly different angle — cost, benchmarks, guardrails, rerouting. He's rapidly iterating angles on the same event.

**5. Self-reinforcing thread clusters**
He posts an initial take → sees it gets traction → posts follow-ups with new data within the same hour. His "Claude Opus 5 BEATS Fable 5" (67k views) was followed by "Opus 5 is 2x more expensive" (58k views, 341 likes) as a follow-up angle.

**6. Personal brand site with real projects**
safzan.dev lists 3 shipped projects: flux-kontext-diff-merge (94 GitHub stars, a ComfyUI node), voicewin (Windows speech-to-text), openports (discovery dashboard for exposed ComfyUI/Ollama instances). Small, focused, real, open-source. Recruiters and founders see these and think "this person ships."

**7. Reply engagement**
He replies to other AI accounts, which puts him in their reply sections and gets him visibility from their followers.

## Implementation priorities for Shivang

### Highest impact (implement first)

1. **Image/screenshot attachment** — Tweets with images get 2-5x reach. Use `xurl media upload` + `--media-id` on every high-stakes post.
2. **Quote-tweet amplification** — Use `xurl quote POST_ID "take"` to ride the reach of high-engagement tweets about breaking events.
3. **Breaking-news trigger** — Post within minutes of a major AI event, not at the next 45-minute scan.

### Medium impact

4. **Multi-angle posting** — Post 3-4 quick takes on the same event, each with a different angle (news, cost, mechanism, builder implication).
5. **Reply-engagement scanner** — Reply with useful technical additions to high-engagement AI tweets from large accounts.

### Long-term investment

6. **Personal site + open-source proof-of-work** — Build a simple site at shivang.dev with 2-3 small open-source tools. Even small projects (a CLI tool, a ComfyUI node, a browser extension) build the same credibility that @cheatyyyy gets from his GitHub.

## Shivang's current baseline (July 2026)

- 53 followers, 375 tweets, recent tweets getting 1-11 impressions
- No images attached to tweets
- No quote-tweets
- No reply engagement with larger accounts
- No breaking-news trigger
- 1 tweet per event at most
- No personal site or public open-source projects

## Expected impact

With all 6 tactics implemented:
- Image attachment alone should 2-5x reach on individual tweets
- Quote-tweet amplification should put posts in front of 10k-100k impression events
- Breaking-news speed should capture early-mover attention
- Multi-angle posting should increase the chance of a breakout tweet
- Reply engagement should build follower growth from larger audiences
- Personal site + open-source should build long-term credibility

Conservative target: 500-2000 followers within 3 months.
Aggressive target: 2000-5000 followers within 6 months if breaking events are caught early.