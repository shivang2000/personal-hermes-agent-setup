# Tiered Hermes Routing Notes

## Durable findings

Hermes exposes separate mechanisms that should be composed rather than conflated:

- `model.*`: main agent model used for every ordinary tool loop.
- `delegation.*`: one global provider/model override for all `delegate_task` children. There is no per-call model selector.
- `auxiliary.<task>`: independent models for compression, titles, vision, web extraction, approval, MCP routing, and related side jobs.
- `credential_pool_strategies`: multiple credentials for the same provider. Pools rotate before provider fallback.
- `fallback_providers`: ordered provider:model routes activated by 429/5xx/auth/connection-type failures, not by semantic task difficulty.
- `moa.presets`: reference models advise; the aggregator is the acting Hermes model and emits tools.
- Model aliases and `/model`: explicit session switching; useful, but switching can reset prompt caches.
- Claude Code and Codex CLI: separate autonomous coding processes suited to extreme implementation/review work.

## Validated three-tier pattern

```text
MiniMax M3 on Ollama Cloud
  ├─ direct lightweight work
  ├─ delegate_task → GLM 5.2 on Ollama Cloud
  └─ extreme → Codex reference + Claude aggregator (MoA)
                or Claude Code / Codex CLI for coding
```

At the time this pattern was validated, Ollama Cloud's discovered catalog used the bare IDs `minimax-m3` and `glm-5.2`, with provider `ollama-cloud` and endpoint `https://ollama.com/v1`. OpenRouter/Nous catalogs used namespaced IDs such as `minimax/minimax-m3` and `z-ai/glm-5.2`. Always re-check the live catalog before applying because provider IDs can change.

## Resilience design

If both light and intensive tiers use the same Ollama Cloud credential pool, they share provider/account capacity. That is acceptable for cost-aware semantic routing but not independent outage protection. For availability, point fallback to another credential surface, for example OpenRouter GLM followed by OpenAI Codex OAuth.

```yaml
fallback_providers:
  - provider: openrouter
    model: z-ai/glm-5.2
  - provider: openai-codex
    model: gpt-5.6-sol
```

Fallback is a safety net. The main agent still needs a routing policy or skill telling it when to delegate or invoke MoA.

## Suggested classifier

- **Light:** routine answers, extraction, summaries, small reversible edits, 1–2 commands.
- **Intensive:** dependency depth of 3+, debugging, multi-file work, codebase exploration, research synthesis, tests/builds.
- **Extreme:** high error cost, architecture/security, broad refactors, adversarial review, or failure after one intensive attempt.

## Operational cautions

- Add keys with `hermes auth add <provider>` so the CLI prompts securely; avoid secrets in shell history or config examples.
- `round_robin` spreads traffic but can reduce per-key prompt-cache locality. `fill_first` favors cache locality; `least_used` is useful with concurrent workers.
- Existing sessions do not automatically adopt config changes. Start a new session or restart the gateway.
- Use `/moa <prompt>` for one extreme turn without permanently changing the main model.
- Verify Claude Code and Codex CLI authentication separately from Hermes provider OAuth; they may use different credential stores.
