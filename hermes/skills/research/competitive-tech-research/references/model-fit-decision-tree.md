# Tiered Model-Fit Decision Tree

A standard pattern for converting an LLM comparison table into an **actionable routing recommendation** rather than a "the best model is X" single answer. Most users have heterogeneous workloads — coding, chat, agents, reasoning — and a single model is rarely the best at all of them. The tier pattern also matches what people actually pay for: local-first for high-volume, cloud for big-brain.

## The three-tier shape

### Tier 1 — Local-first (run on user's hardware, $0/mo)

**Use for**: high-volume, latency-sensitive, privacy-sensitive, repeat work — coding iteration, chat, drafting, agent loops on smaller repos.

**Selection criteria**:
- Model must fit in user's available RAM/VRAM (quantization adjusted). On M-series Macs, allow ~12-15 GB of unified memory for the model.
- Model must have an Ollama tag, LM Studio format, or llama.cpp GGUF on HF.
- License must allow the user's intended use (Apache 2.0 / MIT is always safe; Llama community license has a 700M MAU cap; Gemma has restrictions on certain uses).

**Recommended picks by hardware** (as of June 2026):
- **8-12 GB available**: Llama 3.2 3B, Phi-4 Mini 3.8B, Gemma 3 4B, Qwen3 8B, **LFM2.5-8B-A1B** (purpose-built for tool-call reliability on consumer hardware — the right pick for Hermes / iMessage / always-on personal-assistant workloads where speed and tool-call correctness beat peak benchmark score)
- **16-24 GB available**: Qwen3 14B, Gemma 3 12B, Ministral 3 8B, Qwen3-Coder 30B-A3B (MoE)
- **24-48 GB available**: Gemma 4 26B-A4B (MoE), gpt-oss-20B (MoE), Qwen3 32B, Gemma 3 27B, Gemma 4 31B
- **64 GB+ available**: Llama 3.3 70B, Qwen3 235B-A22B (MoE)
- **Mac Studio M3 Ultra 192 GB+**: Mistral Medium 3.5 128B, Qwen3 235B-A22B full precision

**Workload-driven overrides** (override the hardware-tier default when the workload demands it):
- **Always-on personal assistant / Hermes / iMessage / cron agent**: prefer LFM2.5-8B-A1B even when you have hardware for a bigger model. Its design goal is "fast, reliable tool calling on consumer hardware" — exactly this workload. Faster + cooler + more battery-friendly than gpt-oss:20b or qwen3:14B for the same task shape.
- **Hard SWE-Bench-style multi-file refactor**: prefer Qwen3-Coder 30B-A3B (the most agentic code model in the Qwen series) or cloud-escalate to qwen3-coder:480b-cloud if it fits the budget.
- **Frontier reasoning / architecture decisions**: don't run locally — escalate to Ollama Pro cloud (GLM-5.2 max, kimi-k2.7-code) or DeepSeek V3.1 API. Local models in the 32B tier can do it, but burn tokens; cloud frontier is faster and cheaper for one-off big jobs.

### Tier 2 — Cloud / API escalation (use when local isn't enough)

**Use for**: tasks that need a bigger brain than fits locally — long multi-file refactors, hard architectural reasoning, frontier coding benchmarks, large-context analysis (1M+ tokens).

**Selection criteria**:
- Cost per 1M tokens must fit the user's monthly budget. Always quote the **blended** price (input + output weighted by typical usage).
- Model must have a hosted endpoint (Ollama cloud, OpenRouter, native provider).
- For OpenRouter `:free` tier, prefer models with stable providers + high uptime.
- For subscription tiers (Ollama Pro $20/mo, Cursor Pro $20/mo, ChatGPT Plus $20/mo), know exactly what models are included and whether the quota is reasonable.

**Recommended picks by budget**:
- **$0/mo (free hosted)**: OpenRouter `:free` aliases of gpt-oss-120b, llama-3.3-70b, qwen3-coder-480b; Google AI Studio Gemma 4 31B; Groq free tier for Llama 3.3 70B at high tok/s.
- **$20/mo subscriptions**: Ollama Pro (GLM-5.2 max, qwen3-coder:480b-a35b, deepseek-v4-flash), ChatGPT Plus (GPT-5.x), Cursor Pro.
- **Pay-per-token**: DeepSeek V3.1 (MIT, $0.18/M, frontier coding), DeepSeek V4 Flash ($0.06/M, fast frontier), Gemini 2.5 Flash (1M ctx).

### Tier 3 — Skip

**What to deliberately NOT use, even if it's "best on benchmarks"**:
- **Closed proprietary models** ($4+/M tokens) when open alternatives hit 90%+ of the quality for 10-20% of the cost. Use DeepSeek V3.1 over Claude Opus for coding; use Gemma 4 31B over GPT-5.5 for general chat.
- **Models that look open-weights but aren't.** Artificial Analysis's `?weights=open` filter surfaces some proprietary models alongside truly open ones — cross-check the HF model card for a weight download link before recommending.
- **Newest flagship (1-week-old) models** for production workloads. Use the proven previous-gen flagship instead (e.g., GLM-5.1 over GLM-5.2 for production agents) — community adoption is the safety signal.

## The decision-tree output shape

End every LLM comparison with a tree like:

```
Do you have a GPU?
├─ NO → Use OpenRouter :free tier
│       ├─ Best quality: gemma-4-31b-it:free or qwen3-coder:free
│       ├─ Best speed: liquid/lfm-2.5-1.2b-instruct:free
│       └─ Best agent: openai/gpt-oss-120b:free
├─ YES, 8GB VRAM → Ollama gemma3:4b or qwen3:8b
├─ YES, 16GB VRAM → Ollama gemma3:12b or qwen3:14b
├─ YES, 24GB VRAM → Ollama gemma4:26b-a4b or gpt-oss-20b or qwen3-coder:30b
├─ YES, 32-48GB VRAM → Ollama gemma4:31b or qwen3:32b
└─ YES, 80GB+ (H100) → Ollama llama3.3:70b or qwen3:235b-a22b
```

Then show a **cost table** for the user's likely volume (e.g. 100M tokens/mo) so they can see the dollar savings of the tiered approach vs flat GPT-5 / Claude Opus usage.

## Why this pattern wins over "just use the best model"

- **Cost**: local is $0, cloud is bounded, closed APIs are uncapped surprise. Tiered usage caps the damage.
- **Latency**: local models on M-series silicon hit 30-100 tok/s; cloud round-trips add 200ms-2s.
- **Privacy**: local for any code that touches credentials, PII, or proprietary logic.
- **Reliability**: local works offline; cloud fails when your network does.
- **Right-sizing**: most "hard reasoning" tasks are actually 80% routine (which local handles) and 20% frontier (which cloud handles). A pure-cloud setup pays frontier prices for routine work.

## Anti-patterns to avoid

- **"Just use Claude/GPT"** — leaves money and privacy on the table.
- **"Just run everything locally"** — undersells the user; they need the frontier brain sometimes.
- **Single-model-for-everything** — doesn't match the heterogeneous workload shape.
- **Recommending newest without stability caveat** — GLM-5.2 (1 week old) vs GLM-5.1 (2.3M pulls, 2 months stable) — the safety signal matters.