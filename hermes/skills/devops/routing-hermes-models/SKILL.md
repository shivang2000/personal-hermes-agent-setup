---
name: routing-hermes-models
description: Use when configuring Hermes Agent to split work across cheap, capable, and frontier models; when multiple provider credentials must rotate; or when deciding between main models, delegation, fallback chains, MoA, profiles, and external Claude/Codex agents.
---

# Routing Hermes Models

## Overview

Design model usage along two independent axes:

1. **Task complexity routing** chooses the right intelligence tier.
2. **Failure routing** keeps requests alive when credentials or providers fail.

Never mistake a fallback chain for a complexity classifier. Hermes fallback reacts to errors, not weak answers or hard tasks.

## Architecture

```text
request
  ├─ routine → cheap main model handles directly
  ├─ intensive → delegate_task → pinned capable subagent model
  └─ extreme → one-shot MoA or external Claude/Codex agent

provider request
  ├─ credential pool rotates same-provider keys
  └─ fallback_providers switches provider:model after errors
```

## Workflow

1. Inspect the installed Hermes version, `config.yaml`, provider auth status, live model catalog/cache, and relevant official docs. Model IDs and config shapes change; do not infer them from memory.
2. Confirm each desired model is available through the intended provider. Distinguish native providers, aggregators, custom endpoints, and Ollama Cloud.
3. Put the high-volume model in `model.provider` + `model.default`.
4. Put the intensive model in `delegation.provider` + `delegation.model`. Hermes subagent models are not selectable per `delegate_task` call; the delegation override applies to all children.
5. Configure extreme reasoning as a named MoA preset: a strong reference model advises and the strongest aggregator acts and emits tools.
6. For extreme coding, invoke Claude Code or Codex CLI in an isolated repo/worktree. Use the relevant `claude-code` or `codex` skill.
7. Add model aliases for manual switching, but prefer delegation or `/moa` over repeated mid-session `/model` changes.
8. Configure credential pools and cross-provider fallback separately.
9. Start a new session or restart the gateway, then run one real task through each tier and inspect usage/provider metadata.

## Complexity Contract

| Tier | Observable task shape | Route |
|---|---|---|
| Light | Routine answer, summary, lookup, 1–2 commands, localized edit | Main model |
| Intensive | 3+ dependent steps, debugging, multi-file change, repository exploration, research synthesis, tests/builds | `delegate_task` |
| Extreme | Security/high stakes, architecture, broad refactor, cross-repo work, adversarial review, or one capable-model attempt failed | MoA, Claude Code, or Codex CLI |

Do not escalate because an answer is long. Escalate because error cost, dependency depth, search space, or verification burden is high.

## Reliability Rules

- Credential pools rotate multiple keys for the **same provider** before provider fallback.
- Use `round_robin` to spread traffic, `least_used` to balance concurrent agents, and `fill_first` to preserve prompt-cache locality.
- A fallback on the same provider does not protect against provider-wide quota or outage. Use an independent provider for resilience.
- `provider_routing` controls sub-providers inside OpenRouter; it is not cross-provider Hermes routing.
- Keep API keys in Hermes auth or `.env`, never in skill text or checked-in YAML.
- Key rotation, fallback, and `/model` changes can reset prompt caches. Prefer fresh sessions and stable per-session models.
- Auxiliary jobs such as titles, compression, web extraction, approvals, and skill search should normally use the cheap tier.

## Verification

Check all of the following before claiming completion:

- Every configured model ID exists on its selected provider.
- Multiple credentials appear under the correct provider pool.
- A light task runs on the main model.
- A delegated task reports the intensive provider/model.
- `/moa` runs the intended reference and aggregator.
- Claude/Codex CLI auth works before promising external-agent escalation.
- The fallback route uses independent credentials when outage resilience is required.

## Common Mistakes

- Using `fallback_providers` as if it detects task difficulty.
- Putting the intensive model on the same exhausted provider and calling it resilient fallback.
- Assuming `delegate_task` accepts a per-call model.
- Switching models repeatedly in one long conversation and losing cache benefits.
- Routing every task to MoA, multiplying latency and model calls.
- Copying stale provider/model names from old examples without checking the live catalog.

## Supporting Files

- `references/tiered-routing-notes.md` — condensed Hermes mechanics and the MiniMax/GLM/Claude/Codex design validated in the source session.
- `templates/three-tier-config.yaml` — adaptable configuration skeleton for pooled lightweight inference, delegated intensive work, and MoA extreme work.
