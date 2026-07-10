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

- Main: `ollama-cloud/minimax-m3`
- Delegation: `ollama-cloud/glm-5.2`
- Availability fallback 1: `openrouter/z-ai/glm-5.2` for independent quota/provider diversity
- Availability fallback 2: current supported `openai-codex` model
- Extreme MoA: Codex reference, Claude Opus aggregator
- Auxiliary text tasks: MiniMax M3
- Vision: leave on `auto` until explicitly tested

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
