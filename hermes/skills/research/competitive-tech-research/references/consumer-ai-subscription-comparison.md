# Consumer AI subscription comparison

Use this reference when comparing consumer plans such as ChatGPT Plus, Claude Pro, Kimi memberships, or similar ~$20 offerings.

## Evidence hierarchy

1. Live official pricing and plan-comparison pages.
2. Official help articles for usage/reset/context limits.
3. Official model/API documentation for model capabilities.
4. Authenticated plan UI when public pricing is hidden.
5. Recent archived official pages only when the live page is blocked; label the archive date.

Never infer consumer-plan access from an API model catalog, API price, or aggregator listing. A model can exist without being included in a particular subscription.

## Required distinctions

For every plan, report these separately:

- Consumer subscription price and billing cadence.
- Models explicitly included at that tier.
- Whether the strongest advertised model is actually included, limited, credit-gated, or reserved for a higher tier.
- Published hard limits: context window, output cap, reset interval, or explicit message quota.
- Dynamic/unpublished limits: quote provider language such as “expanded,” “limits apply,” or “subject to guardrails”; do not turn these into invented message counts.
- Whether chat, desktop, coding CLI, and agent surfaces share one quota.
- Whether API credits are included. Default assumption: consumer subscriptions and pay-as-you-go API billing are separate unless the provider explicitly says otherwise.
- Coding/agent access and whether subscription OAuth can be used by the user’s actual agent stack.

## Workflow

1. Audit the user’s current provider/model configuration before recommending a switch. A plan that already powers their primary agent through OAuth can provide more practical value than a nominally stronger model.
2. Fetch official pricing, help-limit, model-overview, and coding-agent pages in parallel.
3. Build a plan table with: price, confirmed included model, quota wording, coding tools, quota sharing, API inclusion, and integration fit.
4. Build a separate model table with context, output cap, and API price. Label it clearly as API economics, not subscription usage.
5. Rank at least three different notions of “best”: peak model capability, practical daily-driver value, and raw token economics.
6. Make the recommendation conditional on workload and integration, then provide one direct default choice.

## Pitfalls

- **Model existence ≠ plan access.** An aggregator or API catalog proves the endpoint exists, not that a $20 consumer plan includes it.
- **API price ≠ subscription quota.** Do not use $/MTok to imply how much consumer-plan usage the buyer receives.
- **Context-window mismatch.** Product UI, coding CLI, and API may expose different context limits for the same model.
- **Shared quota surprise.** Explicitly verify whether web chat, desktop, and coding-agent usage draw from one allowance.
- **Hidden pricing.** If an exact price or quota is behind login and cannot be verified, say so; do not promote a plausible figure to fact.
- **Archived pages.** Date archived evidence and avoid presenting it as a live page.
- **Peak intelligence is not automatically best value.** Reliability, allowance, tool access, and compatibility with the user’s existing workflow can outweigh a small capability advantage.

## Recommended answer shape

1. One-line verdict.
2. Compact subscription comparison table.
3. “Best by criterion” bullets: peak capability, daily usage, coding/agents, token economics.
4. Integration-specific recommendation based on the audited environment.
5. Caveats on unpublished limits and API/subscription separation.
6. Canonical source links.