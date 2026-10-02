# Provider credential pools, model entitlements, and fallback probes

Use this reference when one provider account pool contains credentials with different subscription/model entitlements.

## Failure pattern

A credential can be valid for the provider and for one model, yet return HTTP 403 for a subscription-gated model. Hermes may correctly mark that credential exhausted after the 403. This creates two distinct effects:

1. The primary model rotates until it finds an entitled credential.
2. A same-provider fallback model may inherit a pool whose otherwise-valid credentials were marked exhausted by the primary model.

Therefore, `hermes auth list <provider>` showing `auth failed (403)` does not by itself prove the API key is invalid. Read the provider response. Messages such as `this model requires a subscription` indicate model entitlement, not malformed authentication.

## Diagnostic sequence

1. Capture current routing and pool state:

   ```bash
   hermes fallback list
   hermes auth list <provider>
   ```

2. Search `~/.hermes/logs/agent.log` for the exact HTTP response and credential rotation labels.
3. Reset pool cooldown/exhaustion only when evidence shows the stored state came from model-specific entitlement checks rather than truly invalid or quota-exhausted credentials:

   ```bash
   hermes auth reset <provider>
   ```

4. Test models with an explicit provider. When the configured provider differs, `-m provider/model` may be interpreted as a model string; use:

   ```bash
   hermes chat -q 'Reply with exactly: MODEL OK' --provider <provider> -m <model> --quiet
   ```

5. Verify the selected provider/model in `agent.log`; exact output alone is insufficient because a fallback may have produced it.

## Safe fallback test

Force a harmless nonexistent model while keeping the intended provider and configured fallback chain:

```bash
hermes chat -q 'Reply with exactly: FALLBACK OK' \
  --provider <primary-provider> -m definitely-invalid-model --quiet
```

Then verify a log line like:

```text
Fallback activated: definitely-invalid-model → <fallback-model> (<provider>)
```

This proves the fallback path without burning quota or corrupting credentials.

## Configuration pitfalls

- Fallbacks are designed primarily for cross-provider resilience. Same-provider fallback can work for 404/5xx failures while the credential remains usable, but may fail after a 401/403 marks the shared pool exhausted.
- Prefer provider diversity when the fallback must survive subscription, billing, or account-wide failures.
- Generic `hermes config set fallback_providers '<JSON>'` may store the value as a quoted scalar rather than a YAML list on versions whose setter only parses scalar values. Always run `hermes fallback list` immediately after configuration. Use the supported fallback manager where it recognizes credentials; otherwise use a backed-up round-trip YAML edit for the non-secret list and validate it.
- The interactive fallback manager may prompt for a raw provider API key even when `auth.json` has a credential pool. Never paste secrets through agent-controlled terminal input. Stop and use a secure user prompt or a non-secret, backed-up config edit.
- A successful direct model probe can still be misleading if fallback was active. Confirm `agent.conversation_loop: API call #... model=... provider=...` in logs.

## Worked entitlement example

A four-key Ollama Cloud pool had three accounts returning HTTP 403 `this model requires a subscription` for GLM 5.2, while the fourth account successfully served GLM. MiniMax M3 worked on the same provider. Resetting stale exhaustion state allowed Hermes to rotate through the three non-entitled credentials, quarantine them, and settle on the entitled credential. A forced 404 then verified GLM → MiniMax M3 fallback on the surviving credential.

The durable lesson is not the account labels: classify 403s by response body, distinguish model entitlement from invalid auth, and verify both primary and fallback using real provider/model log metadata.
