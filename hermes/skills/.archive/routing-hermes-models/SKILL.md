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
2. Back up the live configuration before mutation. Use `hermes config set` for scalar leaves; use `hermes config edit` for lists and mappings unless the installed CLI is proven to parse structured values. Parse the edited YAML and assert its types before restart.
3. Confirm each desired model is available through the intended provider. Distinguish native providers, aggregators, custom endpoints, and Ollama Cloud. Test model entitlement separately from credential validity.
4. Put the high-volume model in `model.provider` + `model.default`.
5. Put the intensive model in `delegation.provider` + `delegation.model`. Hermes subagent models are not selectable per `delegate_task` call; the delegation override applies to all children.
6. Configure extreme reasoning as a named MoA preset: a strong reference model advises and the strongest aggregator acts and emits tools.
7. For extreme coding, invoke Claude Code or Codex CLI in an isolated repo/worktree. Use the relevant `claude-code` or `codex` skill.
8. Add model aliases for manual switching, but prefer delegation or `/moa` over repeated mid-session `/model` changes.
9. Configure credential pools and cross-provider fallback separately.
10. Run `hermes config check`, identify the actual gateway supervisor, restart it, and verify its post-restart PID/status.
11. Run one real task through each tier. Inspect fresh logs for the provider/model that completed each turn; expected response text and exit code 0 are insufficient because fallback may have produced the answer.

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
- Verify the selected provider's auxiliary resolver supports its credential source. In Hermes v0.18.2, `ollama-cloud` worked for the main agent through `auth.json` credential pools, but auxiliary slots configured with `provider: ollama-cloud` did not consume that pool and instead looked for an environment key. If a live auxiliary smoke test reports no key, leave those slots on `provider: auto` (or use another provider with a supported credential surface) rather than copying the main-agent provider blindly.
- Treat credential-pool status as mutable test state. Entitlement 403s and credit 402s can mark otherwise useful credentials failed or exhausted. After a deliberate negative test, remove the bad route, reset only the affected provider marker, and prove a known-good model. Never reset repeatedly to hide a real quota shortage.
- Provider affordability is based on the complete prompt plus declared output allowance, not the visible user message. Lowering `max_tokens` cannot rescue a route whose system/context/tool prompt already exceeds the affordable input budget.

## Verification

Check all of the following before claiming completion:

- Every configured model ID exists on its selected provider and the account is entitled/funded to use it.
- Multiple credentials appear under the correct provider pool.
- A light task's completion log names the main provider/model and has no fallback activation.
- A delegated task's child session reports `platform=subagent` and the intensive provider/model. Use a persistent session when needed so an asynchronous child can return before the parent exits.
- `/moa` logs both the intended reference and aggregator, and the preset itself completes without falling through the main fallback chain.
- Claude/Codex CLI auth works before promising external-agent escalation.
- The fallback route uses independent credentials when outage resilience is required.
- YAML structured fields remain lists/mappings after edits; they were not serialized as quoted JSON strings.

## Common Mistakes

- Using `fallback_providers` as if it detects task difficulty.
- Putting the intensive model on the same exhausted provider and calling it resilient fallback.
- Assuming `delegate_task` accepts a per-call model.
- Switching models repeatedly in one long conversation and losing cache benefits.
- Routing every task to MoA, multiplying latency and model calls.
- Copying stale provider/model names from old examples without checking the live catalog.
- Treating expected response text as proof of the requested route; fallback can return the same text.
- Passing a whole list/mapping to `hermes config set` and failing to notice that it became a quoted string.
- Declaring MoA healthy when its aggregator failed and the normal fallback chain produced the final answer.
- Testing a subscription-only model across a credential pool, poisoning every key's status, and forgetting to reset the test-induced marker.

## Supporting Files

- `references/tiered-routing-notes.md` — condensed Hermes mechanics and the MiniMax/GLM/Claude/Codex design validated in the source session.
- `references/provider-routing-verification.md` — safe config mutation, fallback-aware log proof, credential-pool cleanup after negative tests, credit/context budgeting, and MoA verification.
- `templates/three-tier-config.yaml` — adaptable configuration skeleton for pooled lightweight inference, delegated intensive work, and MoA extreme work.
