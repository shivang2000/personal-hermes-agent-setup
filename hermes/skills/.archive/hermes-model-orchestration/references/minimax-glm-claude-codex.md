# MiniMax M3 → GLM 5.2 → Claude + Codex

This is a worked example of the class-level orchestration pattern. Re-run discovery before applying it because provider catalogs and account entitlements change.

## Intended tiers

```text
MiniMax M3 parent
  ├─ handles lightweight/high-volume work
  ├─ delegate_task → GLM 5.2 for intensive work
  └─ extreme → Codex reference + Claude aggregator, or external coding CLIs
```

## Observed model-ID nuance

Ollama public library pages may show:

```text
minimax-m3:cloud
glm-5.2:cloud
```

A live Hermes account cache may expose bare IDs:

```text
minimax-m3
glm-5.2
```

Run `hermes model --refresh` and use the exact account-visible IDs.

## Recommended routing

### Default three-tier (cost-aware)
- Main: `ollama-cloud/minimax-m3`
- Delegation: `ollama-cloud/glm-5.2`
- Availability fallback 1: `openrouter/z-ai/glm-5.2` for independent quota/provider diversity
- Availability fallback 2: current supported `openai-codex` model
- Extreme MoA: Codex reference, Claude Opus aggregator
- Auxiliary text tasks: MiniMax M3
- Vision: leave on `auto` until explicitly tested

### Single-tier override (user preference 2026-07-11)
When the user has an Ollama Pro plan and explicitly says "use GLM 5.2 for everything":
- Main: `ollama-cloud/glm-5.2` (set via `hermes config set model.default glm-5.2`)
- Delegation: `ollama-cloud/glm-5.2` (set via `hermes config set delegation.model glm-5.2` + `hermes config set delegation.provider ollama-cloud`)
- Fallback: keep existing `openai-codex/gpt-5.6-sol` for outage recovery only
- Auxiliary: leave on `nous/minimax-m3` (cheap tasks don't need GLM's reasoning)
- This collapses the three-tier stack to one tier + fallback. Cost is higher per token but the user has a Pro plan (quota is not the constraint). Respect the user's explicit choice — do NOT re-escalate to MiniMax for "lightweight" work unless they ask.
- Config changes via `hermes config set` (not direct file edit — the `patch` tool refuses to write to `config.yaml` as a security guard)
- Smoke test: `hermes chat -q "Reply with exactly: GLM 5.2 OK" -m ollama-cloud/glm-5.2 --quiet`
- Existing sessions keep the old model until `/reset` or fresh `hermes` launch

## Semantic escalation rules

Delegate to GLM when work needs three or more dependent steps, repository exploration, root-cause debugging, multi-file edits, research synthesis, or large intermediate context.

Escalate to Claude/Codex for security, architecture, major refactors, cross-repository work, adversarial review, high-stakes decisions, or a task unresolved after one serious GLM attempt.

## Deferred activation checklist

- [ ] Provider usage limits have reset.
- [ ] Live picker confirms exact MiniMax and GLM IDs.
- [ ] All intended Ollama keys are healthy in `hermes auth list ollama-cloud`.
- [ ] Main MiniMax one-shot succeeds.
- [ ] GLM one-shot succeeds.
- [ ] Delegated child is verified to use GLM.
- [ ] Auxiliary title/compression route is verified.
- [ ] OpenRouter fallback is tested in an isolated profile.
- [ ] Codex OAuth route is verified.
- [ ] Claude Code and Codex CLI authentication are verified separately.
- [ ] MoA resolves the intended reference and aggregator.
- [ ] Gateway is restarted and checked in a fresh session.
- [ ] Rollback copy exists.

## Safe credential handling

Use the secure prompt instead of placing a key in shell history:

```bash
hermes auth add ollama-cloud --type api-key --label ollama-key-N
```

Use `hermes auth reset ollama-cloud` only after confirming that a stored cooldown is stale. Do not repeatedly clear cooldowns while quota is genuinely exhausted.

## Extreme coding workflow

1. Run Codex or Claude in an explicit repository/worktree with bounded scope.
2. Have the other model review the implementation when the task warrants two perspectives.
3. Independently inspect `git diff` and run the real project verification command.
4. Do not accept an agent's self-report as completion evidence.
