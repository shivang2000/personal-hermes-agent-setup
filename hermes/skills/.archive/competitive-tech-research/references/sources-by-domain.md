# Canonical Sources by Domain

Last verified: August 2026. URLs and schemas rot — re-check on every use.

## LLMs / open-weights models

### Leaderboards (use Shape 2 — JS SPA, browser_console scrape)
- **Artificial Analysis** — https://artificialanalysis.ai/leaderboards/models — most comprehensive modern benchmark (MMLU-Pro, GPQA, AIME, BFCL, SWE-Bench, price/speed/latency). Filter via URL: `?weights=open`, `?price=free`, `?reasoning=reasoning`. 220+ models.
- **LMSYS Chatbot Arena** — https://lmarena.ai — human-preference ELO. Best for "which model do users actually prefer."
- **Vellum LLM Leaderboard** — https://www.vellum.ai/llm-leaderboard — clean UX, good per-task tables.
- **OpenRouter rankings** — https://openrouter.ai/rankings — by usage volume, not quality. Useful as adoption signal.

### Free-tier APIs (Shape 1 — JSON)
- **OpenRouter** — `https://openrouter.ai/api/v1/models` — 339 models, 26 are `:free`. Each has `pricing.prompt` and `pricing.completion`. Filter free: `pricing.prompt == "0"`.
- **OpenRouter per-model endpoints** — `https://openrouter.ai/api/v1/models/{id}/endpoints` — quant, provider, uptime, latency.
- **Ollama library** — `https://ollama.com/api/tags` — what's downloadable, file size, quantization tags. (Featured list, not exhaustive — `ollama.com/library` has the full set.)
- **Ollama cloud models** — `https://ollama.com/search?c=cloud` — the subset of models Ollama serves on its cloud (free tier + Pro $20/mo + Max $100/mo). HTML, Shape 2 (browser_console scrape). Crucially includes frontier proprietary models (GLM-5.2 max, MiniMax-M3, Gemini-3-flash-preview) that you cannot pull locally — this is the bridge between "open-weights local" and "use Ollama as your OpenAI-compatible endpoint."
- **Ollama capability filters** (all Shape 2 HTML) — fast capability-driven shortlists:
  - `https://ollama.com/search?c=tools` — only models with native tool-calling. **Use this first when picking an agent-loop model.**
  - `https://ollama.com/search?c=vision` — multimodal models.
  - `https://ollama.com/search?c=thinking` — chain-of-thought reasoning models.
  - `https://ollama.com/search?c=embedding` — embedding models.
- **Ollama registry v2 OCI manifest** — `https://registry.ollama.ai/v2/library/{name}/manifests/{tag}` with Accept headers for `application/vnd.oci.image.manifest.v1+json` + `application/vnd.docker.distribution.manifest.v2+json`. Sum the `layers[].size` fields for exact disk footprint per tag (e.g. `gpt-oss:20b` = 13.79 GB, `qwen3:8b` = 5.23 GB). The `ollama.com/api/show/{tag}` endpoint is POST-gated; the registry is the clean GET path.
- **Ollama pricing** — `https://ollama.com/pricing` — three tiers: Free ($0, light cloud usage, public models), Pro ($20/mo or $200/yr, 50× free cloud usage, "larger more powerful cloud models", 3 concurrent, private model upload), Max ($100/mo, 10 concurrent, 5× Pro usage). Free tier runs Ollama locally forever — Pro/Max are about Ollama-hosted cloud inference.
- **HuggingFace Hub API** — `https://huggingface.co/api/models?search={query}` — every model on the Hub. Use `?filter=open-llm` or sort by `downloads`.

### Per-model benchmark data (Shape 3 — GitHub raw, Shape 4 — HF model card)
- **Aider polyglot (real engineering, 225 cases)** — `https://raw.githubusercontent.com/Aider-AI/aider/main/aider/website/_data/polyglot_leaderboard.yml`. Fields: `model`, `date`, `pass_rate_1`, `pass_rate_2`, `total_cost`, `seconds_per_case`. Gold standard for coding.
- **Aider edit-format** — same path with `edit_leaderboard.yml`. Earlier benchmark, easier tasks.
- **HF model card** — `https://huggingface.co/{org}/{repo}/raw/main/README.md` — labs publish their own benchmark tables.
- **HF LICENSE** — `https://huggingface.co/{org}/{repo}/raw/main/LICENSE` — Apache 2.0 / MIT / proprietary (always check this for commercial use).

### Older / deprecated but still cited
- **HF Open LLM Leaderboard v2** — moved to a Gradio Space, hard to scrape. Most labs still cite it. Use the HF model card numbers instead — they're usually the same set (MMLU, ARC, HellaSwag, TruthfulQA, GSM8K, IFEval).
- **LMSYS older ELO tables** — useful as historical signal only.

## Agent frameworks / SDKs
- **GitHub awesome lists** — `awesome-llm-agents`, `awesome-agent-frameworks`. Search via `gh search repos "llm agent"` and sort by stars.
- **GitHub topic pages** — `https://github.com/topics/llm-agent`, `https://github.com/topics/agent-framework`.
- **LangChain hub** — `https://api.smith.langchain.com` (gated) / LangChain Hub.
- **Pypi downloads** — `https://pypistats.org/packages/{name}` — best adoption metric.

## MCP servers
- **Official MCP servers** — `https://github.com/modelcontextprotocol/servers` — the canonical reference repo.
- **MCP.so** — community registry, has search.
- **Glama MCP** — `https://glama.ai/mcp/servers` — modern registry with per-server metadata.

## GPU cloud / hardware
- **Lambda Labs** — `https://lambdalabs.com/service/gpu-cloud` — public pricing, no auth.
- **RunPod** — `https://www.runpod.io/gpu-instance/pricing`.
- **Vast.ai** — `https://vast.ai/pricing` — market-rate spot prices.
- **Modal** — `https://modal.com/pricing`.
- **Together.ai** — `https://www.together.ai/pricing` — also inference API.
- **Cloud GPU comparison** — `https://gpulist.com` (community).

## Vector databases
- **ANN-Benchmarks** — `https://ann-benchmarks.com` — recall vs QPS, the canonical comparison.
- **GitHub stars + downloads** — proxy for adoption.

## Coding CLIs / IDE plugins
- **GitHub topic pages** — `https://github.com/topics/cli-coding`, `https://github.com/topics/ai-coding`.
- **Aider polyglot** (already cited) — cross-model coding benchmark.
- **SWE-bench leaderboard** — `https://www.swebench.com` — PR-resolution accuracy, gold standard for coding agents.

## Embedding models
- **MTEB leaderboard** — `https://huggingface.co/spaces/mteb/leaderboard` — Massive Text Embedding Benchmark. 100+ models, 50+ tasks.
- **HF model cards** — same Shape 4 pattern.

## Speech-to-text / TTS
- **HF Open ASR Leaderboard** — `https://huggingface.co/spaces/open-asr-leaderboard/leaderboard`.
- **HF TTS Arena** — `https://huggingface.co/spaces/ArtificialAnalysis/text-to-speech-arena`.

## Anthropic / Claude product line

All Shape 2 (browser_navigate, JS-rendered pages). Help center URLs rot — see the pitfall in SKILL.md about extracting hrefs via browser_console.

### Pricing & plans
- **Claude pricing page** — `https://claude.com/pricing` — all consumer plans (Free, Pro, Max 5x, Max 20x) with feature comparison table. Pro = $20/mo monthly or $17/mo annual ($200 up front). Includes Claude Code, Cowork, Design, Science. Tabbed: Individual / Team & Enterprise / API.
- **Claude product overview** — `https://claude.com/product/overview` — current model lineup (Fable 5, Opus 5, Sonnet 5, Haiku 4.5 as of Aug 2026) with model detail links.

### Model detail pages
- **Claude Opus page** — `https://www.anthropic.com/claude/opus` — Opus 5 announcement, availability, API pricing ($5/M input, $25/M output), benchmarks, customer quotes. States "available on Claude for Pro, Max, Team, and Enterprise users."
- **Claude Platform models overview** — `https://platform.claude.com/docs/en/about-claude/models/overview` — API-level model comparison table (context window, max output, pricing, knowledge cutoff, API IDs for Anthropic/Bedrock/Vertex/Foundry). The authoritative spec table.

### Help center (rate limits, context windows, Claude Code limits)
- **Help center root** — `https://support.claude.com` — search-based; old `support.anthropic.com` URLs redirect here but old article IDs 404.
- **Claude collection** — `https://support.claude.com/en/collections/4078531-claude` — 78 articles organized by category (Get started, Account, Conversation, Features, Personalization, Troubleshooting, Usage and limits). Navigate here first, extract hrefs via browser_console.
- **Usage & length limits** — `https://support.claude.com/en/articles/11647753-how-do-usage-and-length-limits-work` — explains usage limits (dynamic, not published as hard numbers), length limits (context window), automatic context management, shared limits across claude.ai + Claude Code + Desktop.
- **Context window on paid plans** — `https://support.claude.com/en/articles/8606394-how-large-is-the-context-window-on-paid-claude-plans` — Opus 5 & Sonnet 5 = 1M tokens on all paid plans; older Opus/Sonnet = 500K; others = 200K. Pro users need usage credits enabled for 1M Opus in Claude Code.
- **Models, usage, and limits in Claude Code** — `https://support.claude.com/en/articles/14552983-models-usage-and-limits-in-claude-code` — metering (subscription vs API key), model selection via /model, token consumption patterns, context management, five habits to stretch usage.

### Claude Code docs
- **Claude Code overview** — `https://code.claude.com/docs/en/overview` — installation, surfaces (terminal, VS Code, desktop, web, JetBrains), requires Claude subscription or Console account.
- **Claude Code cost management** — `https://code.claude.com/docs/en/costs` — token tracking via /usage and /cost, plan usage breakdown for subscribers, cost reduction strategies. Enterprise average ~$13/dev/active day, $150-250/dev/month.

## OpenAI / ChatGPT product line

**Cloudflare bot-blocked** — `openai.com`, `chatgpt.com`, and `help.openai.com` all return "Just a moment..." Cloudflare challenge to curl and browser_navigate. Use the Wayback Machine fallback: `https://web.archive.org/web/2026/https://chatgpt.com/pricing/` then `browser_console` with `document.querySelector('body').innerText` to extract rendered content. See `bot-blocked-web-fetch` skill for the full technique. Full pricing snapshot stored at `references/openai-chatgpt-pricing-2026-08.md`.

### Pricing & plans (Shape 2 — JS-rendered, Cloudflare-blocked)
- **ChatGPT pricing page** — `https://chatgpt.com/pricing/` — all individual plans (Free, Go ~$8, Plus ~$20, Pro from $100) + Business + Enterprise. JS-rendered comparison table with model access, context windows, Codex, features. Prices are rendered client-side from token identifiers (`chatgpt.plus`, `chatgpt.go`, etc.) — NOT in raw HTML. Must use `browser_console` to extract rendered text.
- **Plans overview** — `https://chatgpt.com/plans/` — redirects to pricing page.
- **Plus signup** — `https://chatgpt.com/explore/plus`
- **Codex overview** — `https://chatgpt.com/codex`

### Help center (Cloudflare-blocked, Wayback may not have snapshots)
- **ChatGPT Plus subscription** — `https://help.openai.com/en/articles/7316658-chatgpt-plus-subscription` — blocked as of Aug 2026.
- **Usage limits** — `https://help.openai.com/en/articles/10262009-what-are-the-limits-of-chatgpt-plus` — blocked as of Aug 2026.

### Current model lineup (as of Aug 2026 snapshot)
- GPT-5.5 Instant — base model, available on Free+
- GPT-5.6 Sol — reasoning model, Plus+ (the best model included in Plus)
- GPT-5.6 Sol Pro — advanced reasoning, Pro only
- GPT-5.6 Terra — available on Plus+ (limited on Free/Go via Work/Codex desktop)
- GPT-5.6 Luna — available on Plus+
- GPT-5 Thinking Mini — lightweight reasoning, available on Free+

## Kimi / Moonshot AI product line

**Platform dual-language**: `platform.kimi.ai` (English, USD pricing) and `platform.kimi.com` (Chinese, CNY pricing). Consumer app at `kimi.com`. Docs are SPAs — direct deep-link URLs redirect to `/docs/overview`; use sidebar click navigation. Full pricing/model reference at `references/kimi-moonshot-pricing-2026-08.md`.

### API Platform (Shape 2 — JS SPA, use sidebar navigation)
- **Platform home** — `https://platform.kimi.ai/` — model lineup with USD API pricing in the page snapshot. Chinese version at `https://platform.kimi.com/` shows CNY pricing.
- **Docs overview** — `https://platform.kimi.ai/docs/overview` — entry point; navigate via sidebar from here.
- **Model List** — sidebar: Get Started → Model List. All current + deprecated models with context windows.
- **Kimi K3 model page** — sidebar: Get Started → Kimi K3. Full specs, architecture, limits, code examples.
- **K3 Pricing** — sidebar: Pricing → Kimi K3. Token pricing table.
- **Rate Limits** — sidebar: Pricing → Recharge and Rate Limits. 6-tier recharge table (Tier 0 $1 → Tier 5 $3,000).
- **Blog** — `https://platform.kimi.ai/blog` — blog index (Next.js, server-rendered post links). Posts at `/blog/posts/{slug}`.
- **API base URL**: `https://api.moonshot.ai/v1` (OpenAI-compatible). API key env var: `MOONSHOT_API_KEY`.

### Consumer app (login-gated pricing)
- **Consumer app** — `https://www.kimi.com/` — SPA, requires login for subscription pricing. JS bundles at `statics.moonshot.cn/kimi-web-seo/assets/` contain subscription tier logic (Shape 6 technique — see SKILL.md). Membership levels: FREE, BASIC (INTERMEDIATE), higher. Monthly + annual billing, USD + CNY. Exact prices not extractable without auth.
- **Kimi Business** — `https://platform.kimi.ai/kimi-business` — redirects to login.

### Current model lineup (as of Aug 2026)
- **kimi-k3** — flagship, 2.8T params, 1M context, vision, always-on reasoning (`reasoning_effort`: low/high/max). Open-source (weights by July 27, 2026). $3/$15 per MTok input/output.
- **kimi-k2.7-code** / **kimi-k2.7-code-highspeed** — coding model, 256K context. HighSpeed: ~180 tok/s output. $0.95/$4.00 per MTok.
- **kimi-k2.6** — general-purpose, 256K context, vision+text, thinking/non-thinking modes. $0.95/$4.00 per MTok.
- **kimi-k2.5** — being sunset (Aug 31, 2026).
- **moonshot-v1-*** — legacy, being sunset (Aug 31, 2026).
- Deprecated: kimi-k2 series (May 2026), kimi-latest (Jan 2026), kimi-thinking-preview (Nov 2025).