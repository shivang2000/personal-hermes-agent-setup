---
name: bot-task-worker-completion
description: Use when a Hermes bot/profile receives a task from another bot/profile and must report completion without starting unnecessary follow-up conversation. Send one complete terminal handoff, then stop unless blocked or explicitly asked for more work.
version: 1.0.0
author: REDACTED_SET_LOCALLY
license: MIT
metadata:
  hermes:
    tags: [multi-agent, bot-collaboration, completion, handoff, silence]
    related_skills: [bot-taREDACTED_SECRET, kanban-worker, kanban-orchestrator]
---

# Bot Task Worker Completion Protocol

## Overview

This skill prevents worker bots from keeping a conversation alive after their assigned work is complete. When you are the **worker bot** (the bot/profile that received a task from another bot/profile), finish the task, send one useful completion report, and then stop. Do not ask for acknowledgement. Do not send follow-up pings. Do not continue messaging unless you are blocked, asked a direct question, or assigned new work.

The default rule is: **one complete handoff, then silence.**

## When to Use

Use this skill when:

- Another Hermes bot/profile/agent gives you a task.
- You are spawned as a worker, subagent, Kanban worker, or specialist profile.
- You need to decide what to say after finishing.
- A bot-to-bot thread is accumulating extra "done?" / "thanks" / "ack" / "anything else?" messages.

Do not use this to withhold important results from a human. If the human is the audience, provide the requested final answer. This skill is specifically for bot-to-bot completion handoffs.

## Bot ID / Mention Requirement

When sending a completion report, blocker, or follow-up through Discord, Slack, Telegram groups, or any shared channel where bots only wake up when addressed, **start the message with the platform's real mention token / numeric bot user ID whenever it is known**. A plain visible bot name such as `hermes-work-agent` may not create a real Discord mention and may not trigger the receiving bot.

For this Discord setup, use these real mention tokens:

- Office Hermes / `hermes-work-agent`: `<@1516899802913308733>`
- Personal Hermes / this bot: `<@1516782563757133964>`

Use this shape:

```text
<@RECIPIENT_BOT_USER_ID> — done: <result>. Artifacts: <paths/URLs/IDs>. Verification: <checks>. No reply required unless you need a change.
```

Examples:

```text
<@1516899802913308733> — done: installed the two completion skills and reloaded skills. Verification: `hermes skills list` shows both enabled. No reply required unless you need a change.
```

```text
<@1516782563757133964> — blocked: I need the target Discord channel ID before creating the cron job.
```

Rules:

- Use the **requesting/recipient** bot's mention token / numeric user ID, not your own, at the beginning of the message.
- On Discord, prefer `<@BOT_USER_ID>` over visible names. If sending via Discord REST, include `allowed_mentions: {"users": ["BOT_USER_ID"], "parse": []}` so Discord resolves/pings the target bot without broad mention parsing.
- If you do not know the exact bot ID, ask the human or inspect a resolved Discord mention before relying on a plain `@Display Name`.
- The mention is only to trigger delivery; it does **not** mean you should ask for acknowledgement.

## Required Completion Behavior

When the assigned task is complete:

1. Send exactly one terminal completion report to the requesting bot or board.
2. If using a shared chat/channel, begin that report with the requesting bot's real mention token / numeric user ID (for Discord, `<@BOT_USER_ID>`) so it is triggered.
3. Include the information needed for downstream use.
4. State blockers or limitations, if any.
5. Stop communicating.

Do **not** append conversational tails such as:

- "Let me know if you need anything else."
- "Waiting for your confirmation."
- "Please acknowledge."
- "I can continue if you want."
- "Thanks."

A good completion report is useful without requiring a reply.

## Completion Report Template

Use a concise structure like this:

```text
<@RECIPIENT_BOT_USER_ID> — done: <one-sentence result>.
Artifacts: <paths / URLs / IDs / PRs / files>.
Verification: <tests/checks/sources run, or why not possible>.
Notes: <limitations or follow-ups, if any>.
No reply required unless you need a change.
```

For Kanban workers, prefer structured completion metadata:

```python
kanban_complete(
    summary="done: <result>; artifacts: <paths/urls>; verification: <checks>",
    metadata={
        "artifacts": ["<path-or-url>"],
        "verification": ["<command-or-check>"],
        "limitations": [],
        "reply_required": False,
    },
)
```

Only use `reply_required: True` when there is a concrete blocker or decision needed.

## When to Block Instead of Complete

Do not fake completion. Block or ask exactly one question if:

- Required credentials, permissions, files, or context are missing.
- The task has mutually exclusive interpretations that would change the outcome.
- You hit an error and no safe alternate path works.
- Human review is required before the work can be considered done.
- The requester explicitly asked for approval before side effects.

For Kanban:

```python
kanban_block(reason="Need decision: <specific choice needed>. No progress can continue safely without it.")
```

For chat:

```text
Blocked: need <specific decision/context>. Once provided, I can complete the task. No other reply needed.
```

## Stop Conditions

After sending a completion report, stop if:

- You delivered the requested artifact/result.
- You included verification or stated why verification was impossible.
- You disclosed limitations.
- You did not ask a direct question.
- No new task was assigned.

If those are true, the next correct action is **silence**, not another message.

## Anti-Loop Rules

- Never ask another bot to acknowledge a completed task.
- Never send a second "still done" message.
- Never restate the same completion because nobody replied.
- Never interpret silence from another bot as a problem. Silence usually means the handoff succeeded.
- If you receive only "thanks" or "ack" from another bot, do not reply.
- If a requester sends a new concrete task, treat it as a new task, not as continuation chatter.

## Good Examples

### Research task

```text
Done: compared 4 queue systems and recommend Redis Streams for the current scale.
Artifacts: `/Users/shivang/research/queue-comparison.md`.
Verification: checked official docs and current pricing pages; links included in the file.
Notes: Kafka may win later above ~100MB/s sustained throughput.
No reply required unless you need a change.
```

### Coding task

```text
Done: added exponential backoff to webhook delivery.
Artifacts: `gateway/webhooks.py`, `tests/test_webhook_backoff.py`.
Verification: `python -m pytest tests/test_webhook_backoff.py -q` passed.
Notes: no schema migration needed.
No reply required unless you need a change.
```

### Blocked task

```text
Blocked: publishing requires the target Discord channel ID. Please provide the channel ID or confirm use of the home channel.
```

## Verification Checklist

Before sending your final handoff, confirm:

- [ ] The requested work is actually done or clearly blocked.
- [ ] The handoff has artifact paths/URLs/IDs when applicable.
- [ ] The handoff has verification or an honest limitation.
- [ ] There is no unnecessary acknowledgement request.
- [ ] The message can stand alone without a follow-up.
- [ ] After sending it, you will stop unless directly asked for more.
