# Tier 0 — Cloud-only LLM routing (no local inference possible)

Companion to `model-fit-decision-tree.md`. Use this branch when the user **cannot or will not run local models**: insufficient disk free, insufficient RAM, or they explicitly say "no local." More common than the standard tier-1/2/3 framework assumes.

## When to branch here

Signals from the audit (workflow step 1):
- `df -h /System/Volumes/Data` shows <15 GB free **after** subtracting installed Ollama blob size (`du -sh ~/.ollama`).
- `sysctl hw.memsize` shows <16 GB unified memory on macOS.
- User says "no local models," "we don't have storage," "can't run locally," or equivalent.
- User is on a managed/corporate machine where installing local inference is forbidden.

If any of these fire, **don't try to fit a local model in.** Go straight to Tier 0.

## The pattern (as of June 2026)

**Tier 1 — cheap fast cloud for high-volume always-on work:**

| Service | Free tier | Cost after free | Speed | Use for |
|---|---|---|---|---|
| **Groq `llama-3.1-8b-instant`** | 500K tok/day | $0.05/$0.08 per 1M | **840 tok/s** | Cron agents, iMessage, news research, phone agents, tweets, simple chat |
| **OpenRouter `:free`** | ~20 req/min, varies by model | n/a | varies | Free fallback: gpt-oss-120b:free, llama-3.3-70b:free, gemma-4-31b:free, qwen3-coder:free |
| **Google AI Studio** | Generous free RPM (Gemini 2.5 Flash, Gemma 4 31B) | paid if exceeded | varies | Multimodal free tier with Google's models |
| **Ollama free tier (cloud)** | Light usage on `:cloud` models like `minimax-m3:cloud` | n/a | ~50-100 tok/s | Already configured via `~/.hermes/config.yaml` for many users |

**Tier 2 — frontier cloud for demanding agent work:**

| Service | Cost | Use for |
|---|---|---|
| **Ollama Pro $20/mo** (or $200/yr) | 50× free cloud quota | GLM-5.2 max (AA Index 51), qwen3-coder:480b-cloud (1M ctx), kimi-k2.7-code, nemotron-3-ultra |
| **DeepSeek V3.1 / V3.2 API** | $0.18/$0.06 per 1M | Frontier coding (V3.2 hits 74.2% Aider pass@2) |
| **ChatGPT Plus / Cursor Pro / Claude Pro** | $20/mo each | Only worth it if you also use the IDE/agent wrapper |

## The Tier 0 swap trick (Hermes users)

If the user runs Hermes and `~/.hermes/config.yaml` shows:
```yaml
model:
  default: minimax-m3:cloud       # or any :cloud model
  base_url: http://localhost:11434/v1
```

Then they're **already on Ollama Cloud free**. Subscribing to Ollama Pro and changing the model name in `~/.hermes/config.yaml` is the entire Tier 2 setup — no code changes anywhere in their repos. Detect this in workflow step 1 by reading the config file.

## Per-project routing table (deliver as the final response)

Always deliver a table like this so the user knows which model to use in which project:

```
| Project                    | Model                              | Tier | Cost         |
|----------------------------|------------------------------------|------|--------------|
| Hermes cron / iMessage     | groq/llama-3.1-8b-instant          | 1    | $0 (free)    |
| AIConcierge phone agent    | groq/llama-3.1-8b-instant          | 1    | $0           |
| tweets-automation          | groq/llama-3.1-8b-instant          | 1    | $0           |
| trading-bot / tradingview  | groq/llama-3.1-8b-instant          | 1    | $0           |
| termbridge MCP             | ollama-pro/glm-5.2                 | 2    | Pro quota    |
| sentry-fixer-bot triage    | ollama-pro/glm-5.2                 | 2    | Pro quota    |
| paperclip                  | ollama-pro/glm-5.2 or qwen3-coder  | 2    | Pro quota    |
| monorepo refactors         | ollama-pro/qwen3-coder:480b-cloud  | 2    | Pro quota    |
| fallback (quota exceeded)  | minimax-m3:cloud (free)            | F    | $0           |
```

Build the project list from `gh repo list {user} --json name` + `ls /Users/{user}/dev` (Linux/macOS) — don't ask the user for the list.

## Why Tier 0 wins for the right user

- **Cost**: $0 (Groq free) + $20/mo (Ollama Pro) = $240/year. Vs $1,500-4,000/year for closed APIs at similar volume.
- **Speed**: Groq Llama 8B Instant hits 840 tok/s — 8-10× faster than Ollama cloud.
- **Reliability for tool calls**: small models (8B) hallucinate tool schemas less than big models. For Tier 1 (cron/iMessage), 8B > 400B.
- **No disk/RAM pressure**: zero local footprint. Works on a 256 GB MacBook with no free disk.
- **Single config swap**: for Hermes users, Tier 2 swap is one line in `~/.hermes/config.yaml`.

## Anti-patterns to avoid in Tier 0

- **Don't recommend local models "to save money"** when the user just told you they can't run them. Even $0/mo local is more expensive than $0/mo cloud if the cloud route fits.
- **Don't recommend a single closed API** (GPT-5/Claude Opus at $4-7/M) for Tier 1 high-volume work. Groq free + Ollama Pro covers Tier 1 and Tier 2 at flat $20/mo.
- **Don't over-rotate to the newest model.** GLM-5.2 is 1 week old with 90K pulls; GLM-5.1 has 2.3M pulls and 2 months of stability. For production agents, default to the proven previous-gen unless the user explicitly asks for the new release.
- **Don't assume `~/.hermes/config.yaml` is canonical.** Always confirm by reading the file before claiming a swap is one-line. Some users override per-session, per-project, or via environment variables.

## Sources

- Groq free tier limits: https://console.groq.com/docs/rate-limits
- Groq pricing: https://groq.com/pricing
- Ollama pricing: https://ollama.com/pricing
- OpenRouter free models: https://openrouter.ai/api/v1/models
- Artificial Analysis leaderboard (filter `?weights=open`): https://artificialanalysis.ai/leaderboards/models
- Hermes config: `~/.hermes/config.yaml` (always read before recommending a swap)