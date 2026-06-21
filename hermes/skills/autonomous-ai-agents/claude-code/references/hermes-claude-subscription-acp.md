# Hermes + Claude Pro/Max subscription via Claude Agent SDK ACP

Use this when a user wants Hermes to consume their Claude Pro/Max subscription quota rather than Anthropic API credits.

## Key findings

- Claude Pro/Max does not work through Hermes `provider: anthropic` unless the user also has an `ANTHROPIC_API_KEY` with API billing.
- Claude Code and the Claude Agent SDK can authenticate with subscription OAuth using `CLAUDE_CODE_OAUTH_TOKEN`.
- Generate a long-lived token with:
  ```bash
  claude setup-token
  ```
  The command prints the token; do not ask the user to paste it into chat. Have them add it to their local env file themselves.
- Claude Code auth precedence matters: `ANTHROPIC_API_KEY` can shadow subscription OAuth in non-interactive / print-mode flows. For subscription quota, unset it in the Hermes runtime env unless intentionally using API billing.
- Anthropic docs note that subscription-plan Agent SDK and `claude -p` usage may draw from a separate monthly Agent SDK credit rather than normal interactive Claude limits.
- Anthropic docs also distinguish personal/native use from third-party developers routing other users through Free/Pro/Max credentials. For a user's own local Hermes setup, prefer official Claude Code / Agent SDK tooling rather than scraping or reusing private tokens outside supported paths.

## ACP adapter route

The package `@agentclientprotocol/claude-agent-acp` exposes an ACP agent backed by the official Claude Agent SDK:

```bash
npx -y @agentclientprotocol/claude-agent-acp
```

It responds to ACP `initialize` over stdio and can be used by ACP-compatible clients.

Hermes has an ACP-backed provider path currently named `copilot-acp`. Although named for Copilot, the subprocess ACP client is generic enough to launch a different ACP command via env vars:

```dotenv
CLAUDE_CODE_OAUTH_TOKEN=REDACTED_SET_LOCALLY
HERMES_COPILOT_ACP_COMMAND=npx
HERMES_COPILOT_ACP_ARGS=-y @agentclientprotocol/claude-agent-acp
```

Then configure Hermes to use the ACP provider marker:

```bash
hermes config set model.provider copilot-acp
hermes config set model.base_url acp://copilot
hermes config set model.api_mode chat_completions
hermes config set model.default sonnet
```

For delegated Hermes child agents, set delegation too:

```bash
hermes config set delegation.provider copilot-acp
hermes config set delegation.model sonnet
hermes config set delegation.base_url acp://copilot
```

Restart Hermes after env/config changes.

## Verification checklist

1. `claude auth status --text` shows a Pro/Max/Team/Enterprise login.
2. User has generated and locally stored `CLAUDE_CODE_OAUTH_TOKEN`.
3. `ANTHROPIC_API_KEY` is absent from the Hermes runtime env unless API billing is desired.
4. `npx -y @agentclientprotocol/claude-agent-acp` is available and can initialize as an ACP stdio server.
5. Hermes config points to `provider: copilot-acp` with `base_url: acp://copilot`.

## Pitfalls

- Do not handle or echo the user's OAuth token.
- Do not claim `provider: anthropic` uses Claude Pro/Max; it uses Anthropic API credentials.
- The `copilot-acp` name is misleading here: it is acting as Hermes's generic external ACP subprocess path.
- This is a workaround using existing Hermes ACP plumbing; if Hermes later adds a first-class `claude-agent-acp` provider, prefer that.