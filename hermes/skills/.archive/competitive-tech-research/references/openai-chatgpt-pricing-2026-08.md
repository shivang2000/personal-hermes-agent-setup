# ChatGPT Pricing — August 2026 Snapshot

**Snapshot date**: August 3, 2026 (Wayback Machine capture)
**Source URL**: `https://chatgpt.com/pricing/` (via `https://web.archive.org/web/20260803154627/https://chatgpt.com/pricing/`)
**Live site**: Cloudflare bot-blocked ("Just a moment..." challenge) — inaccessible via curl, browser_navigate, or UA spoofing

## Plan Tiers (Individual)

| Plan | Price | Tagline | Best Model Included |
|------|-------|---------|---------------------|
| Free | $0 | Intelligence for everyday tasks | Limited GPT-5.5 Instant |
| Go | ~$8/mo | Keep chatting with expanded access | More GPT-5.5 Instant |
| **Plus** | **~$20/mo** | Do more with advanced intelligence | **GPT-5.6 Sol** |
| Pro | From $100/mo | Maximize your productivity | GPT-5.6 Sol Pro (unlimited) |

### Price extraction note
Dollar amounts are NOT in the HTML source. They are rendered client-side from token identifiers (`chatgpt.free`, `chatgpt.go`, `chatgpt.plus`, `chatgpt.pro.5x`) that resolve to currency tables at runtime. The Go plan's currency table was found in the raw HTML: `gbp: 700` (£7.00), `eur-es: 800` (€8.00), `jpy: 140000` — confirming ~$8/mo. The Plus price ($20/mo) is consistent with long-standing published pricing but was not found as an explicit number in the HTML; it may be resolved from a separate currency table not present in this snapshot. Pro's $100/mo appears in a JSON label: `"Consumer > Pro $100"`.

To extract rendered prices: `browser_navigate` to the Wayback URL, then `browser_console` with `document.querySelector('body').innerText` to get the fully-rendered text content.

## Model Access by Plan (from comparison table)

| Model | Free | Go | Plus | Pro |
|-------|------|-----|------|-----|
| GPT-5.5 Instant | Yes | Yes | Expanded | Unlimited* |
| **GPT-5.6 Sol** | No | No | **Yes** | Unlimited* |
| GPT-5.6 Sol Pro | No | No | No | Yes |
| GPT-5.6 Terra | Limited (Work/Codex desktop) | Limited (Work/Codex desktop) | Yes | Unlimited* |
| GPT-5.6 Luna | No | No | Yes | Unlimited* |
| GPT-5 Thinking Mini | Yes | Yes | Expanded | Unlimited* |
| Legacy models | No | No | Yes | Yes |

**GPT-5.6 Sol is real and current** — it is the best reasoning model included in the Plus plan. GPT-5.6 Sol Pro is Pro-only.

## Context Windows (published hard limits)

| Feature | Free | Go | Plus | Pro |
|---------|------|-----|------|-----|
| GPT Instant total context window | 27K | 54K | 54K | 128K |
| GPT Instant input maximum | ~12 pages | ~40 pages | ~40 pages | ~250 pages |
| GPT Reasoning total context window | Varies | 256K | 256K | 400K |
| GPT Reasoning input maximum | Varies | ~320 pages | ~320 pages | ~680 pages |

## Codex / Coding / Agent Access

| Feature | Free | Go | Plus | Pro |
|---------|------|-----|------|-----|
| Codex | Limited | Limited | **Expanded** | Expanded |
| ChatGPT Work | Limited (desktop) | Limited (desktop) | **Desktop, web, mobile** | Desktop, web, mobile |
| Code edits on macOS | Yes | Yes | Yes | Yes |
| Developer mode (beta) | No | No | **Yes** | Yes |

Page text confirms: "Codex is included in your ChatGPT Free, Go, Plus, Pro, Business, or Enterprise plan."

## Usage Limits — Published vs Dynamic

**Published hard limits**: Context windows (54K instant, 256K reasoning for Plus) and input maximums (~40 pages instant, ~320 pages reasoning for Plus).

**Dynamic/unpublished limits**: The page says "Limits apply" for Plus. Messages and interactions = "Unlimited*" (with asterisk noting "subject to abuse guardrails"). OpenAI does not publish exact message caps, hourly rate limits, or Codex task counts for Plus — these are dynamically adjusted based on demand and system capacity. The page uses relative terms ("Expanded" vs "Limited" vs "Unlimited*") rather than specific numbers for most features.

## Other Notable Plus Features

- Memory: Expanded
- Deep research: Expanded
- Image generation: Yes (more complex and accurate)
- Image generation with Thinking: Yes
- Projects, scheduled tasks, custom GPTs: Yes
- Voice: Expanded
- Voice with video: Yes
- Early access to new features: Yes
- Privacy: Content used to train models (opt-out available)
- Response times: Fast
- Interactive tables and charts: Yes
- Apps connecting to internal tools: Yes
- ChatGPT record mode: Yes

## Canonical URLs

- Pricing page: `https://chatgpt.com/pricing/` (redirects from `https://openai.com/chatgpt/pricing/`)
- Plans overview: `https://chatgpt.com/plans/`
- Plus signup: `https://chatgpt.com/explore/plus`
- Codex overview: `https://chatgpt.com/codex`
- Help/billing: `https://help.openai.com/en/articles/7316658-chatgpt-plus-subscription` (Cloudflare-blocked)

## Business & Enterprise plans (for reference)

- Business: Available starting at 2 users, monthly and annual billing options
- Enterprise: Custom pricing, contact sales
- Higher Education: Separate plan
- K-12 Teachers: Separate plan