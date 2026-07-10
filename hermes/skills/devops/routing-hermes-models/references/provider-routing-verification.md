# Provider Routing Verification and Config Repair

Use this when a Hermes multi-model setup appears to work but provider pools, fallbacks, delegation, or MoA may be masking failures.

## Safe config mutation

1. Back up `~/.hermes/config.yaml` before edits.
2. Use `hermes config set` for scalar leaves only.
3. Do not pass a JSON/YAML list or mapping as one `hermes config set` value without proving the installed CLI parses it. Some releases store the whole value as a quoted string.
4. For lists and mappings, use `hermes config edit` or another supported structured editor path.
5. Parse the resulting YAML and assert types and required leaves before restarting:
   - `fallback_providers` is a list of mappings, not a string.
   - MoA presets and aggregators are mappings.
   - `delegation.provider` and `delegation.model` are scalar strings.
6. Run `hermes config check`, restart only the identified supervised gateway, and verify its new PID/status.

## Prove the route, not merely the response

An exact-response smoke test can succeed through fallback. CLI exit code 0 and expected text do not prove the requested provider served it.

Inspect fresh logs or usage metadata for:

- `turn_context`: requested provider/model.
- `OpenAI client created`: provider/model actually contacted.
- `Fallback activated`: whether success came from another route.
- `API call #`: model/provider that completed the turn.
- Delegated child session: `platform=subagent` plus its provider/model.
- MoA: separate `moa_reference` and `moa_aggregator` entries.

For asynchronous delegation, use a persistent interactive session. A one-shot CLI process can exit before the child result re-enters the parent conversation.

## Credential-pool contamination from negative tests

Provider errors can mutate pooled credential state:

- A model-entitlement HTTP 403 may mark every credential under that provider as authentication-failed even when another model still works.
- A credit-related HTTP 402 may mark the provider credential exhausted for a cooldown period.
- A deliberately unavailable model test can therefore break later requests that would otherwise succeed.

After a deliberate negative test:

1. Fix or remove the unavailable route.
2. Run `hermes auth reset <provider>` to clear only the test-induced status marker.
3. Call a known-good model.
4. Recheck `hermes auth list`.
5. Do not reset repeatedly to conceal a real quota or credit shortage; reroute or top up instead.

## Credit and context budgeting

Aggregator APIs can reject a request before generation based on prompt tokens plus the declared maximum output tokens.

- Lowering `model.max_tokens` helps only if the prompt itself fits the provider's affordable/input limit.
- Hermes sessions can carry large system prompts, context files, and tool schemas. A tiny user prompt may still produce a 30K+ token request.
- If the prompt already exceeds the affordable limit, use fewer toolsets/context, a fresh slimmer profile, a funded account, or a different provider.
- Do not report a model as healthy when it returned 402 and the final answer came from fallback.

## MoA verification

MoA can return a valid-looking final answer after its reference or aggregator fails and the main fallback chain takes over.

Verify all three conditions:

1. Intended references ran.
2. Intended aggregator ran and completed.
3. No `Fallback activated: <preset> → ...` entry produced the final answer.

Also inspect the provider's actual requested token allowance. In some versions, an auxiliary/MoA request may use the model catalog's maximum instead of the smaller preset field, which can trigger preflight credit rejection.

## Auxiliary models

Auxiliary clients can use a different credential resolver from the main agent. Test title generation/compression separately before pinning auxiliaries to the main provider. If auxiliary traffic marks a credential pool unhealthy, isolate it on a provider and credential surface verified for auxiliary use.

## Completion evidence

A robust completion report should include:

- Backup path.
- Parsed routing summary without secrets.
- `hermes config check` result.
- Gateway supervisor and post-restart PID/status.
- Main-model log proof.
- Delegated child provider/model log proof.
- MoA reference and aggregator log proof.
- Honest disclosure of any configured-but-unfunded provider intentionally excluded from active routing.
