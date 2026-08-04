# Kimi / Moonshot AI — Pricing, Models & Platform Reference

Last verified: August 4, 2026. All data from live official pages fetched today.

## Canonical URLs

| Resource | URL (English) | URL (Chinese) |
|---|---|---|
| API Platform home | https://platform.kimi.ai/ | https://platform.kimi.com/ |
| Consumer app | https://www.kimi.com/ | https://kimi.com/ |
| Docs (Quickstart) | https://platform.kimi.ai/docs/overview | https://platform.kimi.com/docs/overview |
| Model List | https://platform.kimi.ai/docs/model-list | (sidebar nav) |
| Kimi K3 model page | https://platform.kimi.ai/docs/guides/kimi-k3 | (sidebar nav) |
| K3 Pricing | https://platform.kimi.ai/docs/pricing/kimi-k3 | (sidebar nav) |
| Rate Limits | https://platform.kimi.ai/docs/pricing/recharge-and-rate-limits | (sidebar nav) |
| Blog | https://platform.kimi.ai/blog | — |

**Important**: Direct URL navigation to deep docs pages (e.g. `/docs/pricing/kimi-k3`) redirects to `/docs/overview`. Use sidebar click navigation after landing on the overview page. See SKILL.md pitfall.

## API Pricing (pay-as-you-go, per 1M tokens)

| Model | API ID | Cache Hit | Input (Cache Miss) | Output | Context Window |
|---|---|---|---|---|---|
| Kimi K3 | `kimi-k3` | $0.30 | $3.00 | $15.00 | 1,048,576 (1M) |
| Kimi K2.7 Code | `kimi-k2.7-code` | $0.19 | $0.95 | $4.00 | 256K |
| Kimi K2.7 Code HighSpeed | `kimi-k2.7-code-highspeed` | $0.19 | $0.95 | $4.00 | 256K |
| Kimi K2.6 | `kimi-k2.6` | $0.16 | $0.95 | $4.00 | 256K |
| Kimi K2.5 | `kimi-k2.5` | — | — | — | 256K (sunset Aug 31) |
| Moonshot V1 (8k/32k/128k) | `moonshot-v1-*` | — | — | — | 8K/32K/128K (sunset Aug 31) |

### CNY pricing (Chinese platform, platform.kimi.com)

| Model | Cache Hit (¥) | Input (¥) | Output (¥) |
|---|---|---|---|
| kimi-k3 | ¥2.00 | ¥20.00 | ¥100.00 |
| kimi-k2.7-code | ¥1.30 | ¥6.50 | ¥27.00 |
| kimi-k2.6 | ¥1.10 | ¥6.50 | ¥27.00 |

Prices exclude taxes; tax calculated at checkout based on jurisdiction.

## API Rate Limits (by cumulative recharge tier)

| Tier | Cumulative Recharge | Concurrency | RPM | TPM | TPD |
|---|---|---|---|---|---|
| Tier 0 | $1 | 1 | 3 | 500,000 | 1,500,000 |
| Tier 1 | $10 | 50 | 200 | 2,000,000 | Unlimited |
| Tier 2 | $20 | 100 | 500 | 3,000,000 | Unlimited |
| Tier 3 | $100 | 200 | 5,000 | 3,000,000 | Unlimited |
| Tier 4 | $1,000 | 400 | 5,000 | 4,000,000 | Unlimited |
| Tier 5 | $3,000 | 1,000 | 10,000 | 5,000,000 | Unlimited |

- K3 requires minimum $1 top-up to unlock.
- $5 voucher given when cumulative recharge reaches $5.
- Vouchers do not count toward cumulative recharge total.
- Contact `api-service@moonshot.ai` for higher limits.

## Kimi K3 — Technical Specs

- **Parameters**: 2.8 trillion (world's first open-source model in the 3T class)
- **Architecture**: Kimi Delta Attention (KDA) + Attention Residuals (AttnRes), Stable LatentMoE (16/896 experts activated)
- **Context**: 1,048,576 tokens (1M)
- **Vision**: Native visual understanding (images + video via base64 or `ms://<file-id>`; no public image URLs)
- **Reasoning**: Always-on thinking mode; `reasoning_effort` field: `low` / `high` / `max` (default `max`)
- **`max_completion_tokens`**: default 131,072; max 1,048,576
- **Fixed params**: `temperature=1.0`, `top_p=0.95`, `n=1`, `presence_penalty=0`, `frequency_penalty=0` — omit from requests
- **Caching**: Automatic prefix caching (requires previous prompt >256 tokens for cache hit)
- **Tool calls**: `tool_choice` constraints, dynamic tool loading, JSON mode, structured output (`response_format` / JSON Schema), Partial Mode
- **Official tools via "Formula" system**: Web Search, Rethink, Random-Choice, Memory, Excel, Code-Runner, Quick JS, Date, Fetch, Convert, Base 64
- **Web search**: Currently being updated, not recommended for production (as of Aug 2026)
- **Open source**: Full model weights to be released by July 27, 2026
- **API base URL**: `https://api.moonshot.ai/v1` (OpenAI-compatible)

### Coding/agent features
- Long-horizon coding: sustained engineering tasks, large codebase understanding, terminal tool coordination
- Visual reasoning + coding: screenshots, game dev, frontend, CAD
- Integrations documented: Kimi Code CLI, OpenClaw, Claude Code, OpenCode, Hermes Agent, Codex
- Consumer app features: Plugins, Scheduled Tasks, Swarm, Slides, Deep Research, Websites, Docs, Sheets, Design, Kimi Work, Kimi Code, Kimi Claw

## Consumer Subscription (kimi.com) — Structure Only

**Consumer pricing requires login — exact $/month prices NOT verified from official sources.**

Tier structure extracted from SPA JS bundles (`subscription-*.js`, `check-*.js`):

| Membership Level | Features gated |
|---|---|
| FREE | Base access |
| BASIC (INTERMEDIATE) | Agent Swarm, Dream Memory, Self-Growth |
| INTERMEDIATE+ | Kimi Claw, Goal plans, Kimi Code Highspeed |

- Supports **monthly and annual** billing cycles
- Supports both **USD and CNY** currencies
- 7-day free trial plans available
- "Invite to Earn — Up to 1-year K3 Credits" referral program visible on consumer app
- The ~$20/month figure is plausible given the tier structure but UNCONFIRMED without login

## "Fable" Investigation

No mention of "Fable" found across any official Kimi/Moonshot page, docs, model list, pricing pages, K3 model page, blog listing, or consumer app. "Fable" does not appear to be a current Kimi/Moonshot product, model, or feature as of August 2026.

**Note**: "Fable" IS an Anthropic/Claude model name (Claude Fable 5) — see `references/sources-by-domain.md` under Anthropic. Possible confusion with that.

## Deprecated Models

- `kimi-k2-*` series (0905-preview, 0711-preview, turbo-preview, thinking, thinking-turbo): discontinued May 25, 2026
- `kimi-latest`: discontinued January 28, 2026
- `kimi-thinking-preview`: discontinued November 11, 2025
- `kimi-k2.5` + `moonshot-v1-*`: sunset August 31, 2026 (no longer available to new users)

## Extraction techniques used

1. **API pricing**: Direct `browser_navigate` to platform.kimi.ai homepage (English) — pricing table in page snapshot. Chinese CNY pricing from platform.kimi.com homepage.
2. **Rate limits**: `browser_navigate` to platform root → click Pricing nav → click "Recharge and Rate Limits" sidebar link (direct URL redirected to overview).
3. **K3 specs**: Sidebar navigation to "Kimi K3" model page → `browser_console` with `document.querySelector('main').innerText` to extract full rendered content.
4. **Consumer subscription structure**: Shape 6 — `curl` the kimi.com landing page, grep for `modulepreload` JS bundle URLs, fetch `subscription-*.js` and `check-*.js`, grep for plan/membership logic.
5. **"Fable" search**: `browser_console` text search across all loaded docs pages; visual scan of all snapshots and blog listings.