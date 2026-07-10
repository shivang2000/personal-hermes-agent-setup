# Researching Hermes model routing and credentials

Use this reference when auditing current Hermes Agent support for model tiers, fallbacks, auxiliary models, delegation, cron, or credential pooling.

## Source hierarchy

1. Live official docs: `https://hermes-agent.nousresearch.com/docs/`
2. Current repository `main`: `https://github.com/NousResearch/hermes-agent`
3. Generated model catalog: `website/static/api/model-catalog.json`
4. Provider/model live discovery through `hermes model`

Record the repository commit SHA and catalog `updated_at` in time-sensitive reports. Treat model IDs returned by a provider's live `/models` endpoint or Hermes picker as more authoritative than examples in prose docs.

## Capability distinctions to verify explicitly

Do not collapse these into “intelligent routing”:

- `provider_routing`: OpenRouter sub-provider selection for the *same requested model*; not cross-model complexity routing.
- `fallback_providers`: ordered cross-provider/model failover on request/provider errors; not escalation based on task difficulty.
- `auxiliary.<task>`: explicit model slots for named side tasks such as vision, web extraction, compression, approval, title generation, skills hub, MCP, and triage.
- `delegation.provider` / `delegation.model`: one global subagent override. Check `tools/delegate_tool.py`; the tool schema currently states that the model is not selectable per call.
- Cron: per-job model/provider pinning exists in the `cronjob` tool schema. Check `tools/cronjob_tools.py`; do not assume `hermes cron create` exposes equivalent CLI flags—verify `hermes_cli/subcommands/cron.py`.
- Credential pools: same-provider key/token rotation happens before cross-provider fallback.

A truthful three-tier recommendation should state that Hermes has explicit slots and failure routing, but no native semantic “light → intensive → extreme” classifier unless current source adds one.

## High-value source files

- `website/docs/user-guide/features/provider-routing.md`
- `website/docs/user-guide/features/fallback-providers.md`
- `website/docs/user-guide/features/credential-pools.md`
- `website/docs/user-guide/features/delegation.md`
- `website/docs/user-guide/features/cron.md`
- `website/docs/user-guide/configuration.md`
- `website/docs/integrations/providers.md`
- `agent/auxiliary_client.py`
- `agent/credential_pool.py`
- `tools/delegate_tool.py`
- `tools/cronjob_tools.py`
- `hermes_cli/subcommands/cron.py`
- `plugins/model-providers/<provider>/__init__.py`

## Provider-ID quirks

Aggregator IDs and direct-provider IDs differ. For example, an aggregator may expose vendor-prefixed IDs while a first-class provider uses a clean provider-native ID. Cloud model web pages may also display CLI tags such as `:cloud` while the provider's OpenAI-compatible `/models` endpoint returns a normalized ID. Give an example only after checking the live picker/API, and explicitly tell the reader to use the ID shown by `hermes model` for their account.

For Ollama Cloud specifically, verify the current provider profile for:

- provider slug: `ollama-cloud`
- credential env var: `OLLAMA_API_KEY`
- default base URL: `https://ollama.com/v1`

Do not confuse this first-class cloud provider with local Ollama, which is normally configured as a custom OpenAI-compatible endpoint at `http://localhost:11434/v1`.

## Docs/source mismatch rule

When prose documentation and executable schema disagree:

1. Quote or summarize both.
2. Prefer the current executable schema for exact CLI/tool syntax.
3. Label the docs example as stale or shape-inconsistent rather than silently combining forms.
4. Link both URLs/files so the discrepancy is auditable.

This is especially important for rapidly changing cron and delegation APIs.