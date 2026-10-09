---
name: discord-bot-loop-hygiene
description: Prevent and recover from bot-to-bot acknowledgement loops in Discord/Hermes gateway workflows.
version: 1.0.0
author: REDACTED_SET_LOCALLY
license: MIT
metadata:
  hermes:
    tags: [discord, gateway, bots, loop-prevention, routing]
    related_skills: [bot-taREDACTED_SECRET, bot-task-worker-completion, hermes-gateway-platforms]
---

# Discord Bot Loop Hygiene

## When to use

Use this skill when working in Discord channels/threads where multiple Hermes bots or other bots can see and respond to each other, especially when:
- A bot reports completion, acknowledgement, or “stopping here”.
- A message is only a bot-to-bot handoff/status ping.
- The user asks to configure or troubleshoot Discord bot routing.
- A gateway setting such as `DISCORD_ALLOW_BOTS` is involved.

## Core rule

Do **not** acknowledge acknowledgements.

If another bot says any of the following, stop responding instead of replying with “received”, “noted”, “understood”, thumbs-up, or similar:
- “Done.”
- “Received.”
- “No further acknowledgements…”
- “Stopping here to avoid a bot-to-bot acknowledgement loop.”
- “Silence.”
- `[no response]`

A final acknowledgement to a stop request is still an acknowledgement and can continue the loop.

## Safe response decision tree

1. **Is there a direct human request in the latest message?**
   - Yes: answer the human request.
   - No: continue.
2. **Is the latest message from a bot and only status/ack/stop-loop text?**
   - Yes: return empty/no response if the platform permits it; otherwise give the shortest possible non-engaging final only if required by runtime constraints.
   - No: continue.
3. **Does the bot message contain actionable output for the human?**
   - Yes: summarize or act only if useful to the human, not to the bot.
   - No: do not respond.

## Configuration guidance

Prefer mention-gated bot handling for shared Discord bot channels:

```bash
DISCORD_ALLOW_BOTS=mentions
```

This allows bot-originated messages only when they explicitly mention the receiving bot, reducing accidental loops.

When recording routing details, use real Discord mention tokens rather than plain bot names if known.

## Practical patterns

Good:
- Human: “Review the report above and draft tweets.” → produce tweet drafts.
- Bot: “Stopping here to avoid a bot-to-bot acknowledgement loop.” → no response.
- Bot: “Done.” after completing a requested job → no response unless the human asked for a summary.

Bad:
- Bot: “No further acknowledgements from me.” → Assistant: “No further acknowledgements from me either.”
- Bot: “Silence.” → Assistant: “Understood.”
- Bot: 👍 → Assistant: 👍

## Verification checklist

Before sending a Discord reply in a bot-rich thread:
- [ ] The latest message contains a human request or useful human-facing artifact.
- [ ] The reply is not merely confirming another bot’s confirmation.
- [ ] Stop/silence requests from bots are honored silently.
- [ ] If changing gateway config, prefer mention-gated bot handling and verify with a safe test that does not create a loop.
