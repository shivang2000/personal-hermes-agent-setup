---
name: bot-taREDACTED_SECRET
description: Use when one Hermes bot/profile delegates or requests work from another bot/profile and must decide whether to reply after the other bot reports completion. Treat completion reports as terminal unless they contain an explicit blocker, question, or requested next action.
version: 1.0.0
author: REDACTED_SET_LOCALLY
license: MIT
metadata:
  hermes:
    tags: [multi-agent, bot-collaboration, completion, handoff, silence]
    related_skills: [bot-task-worker-completion, kanban-orchestrator, kanban-worker]
---

# Bot Task Requester Completion Protocol

## Overview

This skill prevents bot-to-bot chatter loops after one bot assigns work to another. When you are the **requesting bot** (the bot that asked another bot/profile to do something), the other bot's completion report is usually the end of the exchange. Do **not** send a courtesy acknowledgement, thanks, or another message just to confirm you saw it.

The default rule is: **a complete handoff requires no reply.** Reply only when there is real work to do next.

## When to Use

Use this skill when:

- You assigned a task to another bot/profile/agent.
- Another bot sends a completion summary, status report, artifact path, PR link, test result, or `kanban_complete`-style handoff.
- You are deciding whether to reply to the worker bot.
- A workflow is creating unnecessary "done" / "thanks" / "acknowledged" / "anything else?" messages.

Do not use this for normal user-facing responses. Humans often need a summary. Bots usually do not.

## Stop Conditions

When a worker bot says the task is done, stop communicating with that bot if all of these are true:

1. The original requested task is complete.
2. The worker gave enough information for downstream use: summary, artifact path/URL/ID, changed files, test results, or key decisions.
3. There is no explicit question.
4. There is no blocker or `review-required` state that needs a decision.
5. No user asked you to relay the result elsewhere.
6. No dependent task requires a new card/message from you.

If those conditions are met, **do not send a reply** to the worker bot. Treat the worker's completion report as terminal.

## When a Reply Is Allowed

Reply to the worker bot only when one of these is true:

- **Blocked:** the worker explicitly asks for a decision, credentials, missing context, or permission. Address the worker bot by exact name/mention at the start of your reply.
- **Invalid completion:** the worker claims completion but omits the required artifact or verifiable result. Address the worker bot by exact name/mention at the start of your correction.
- **Follow-up work:** the user gave a new task that genuinely depends on the completed work. Address the target bot by exact name/mention at the start of the new task.
- **Correction required:** the worker misunderstood scope or produced a wrong/incomplete result. Address the worker bot by exact name/mention at the start of your correction.
- **Coordination required:** another bot/card needs a precise artifact ID, path, URL, or decision that was not provided.

Even then, send the smallest useful message. Avoid social acknowledgements.

## Bot ID / Mention Requirement

When communicating through Discord, Slack, Telegram groups, or any shared channel where bots only wake up when addressed, **start the message with the platform's real mention token / numeric bot user ID whenever it is known**. A plain visible bot name such as `hermes-work-agent` may not create a real Discord mention and may not trigger the receiving bot.

For this Discord setup, use these real mention tokens:

- Office Hermes / `hermes-work-agent`: `<@1516899802913308733>`
- Personal Hermes / this bot: `<@1516782563757133964>`

Use this shape for bot-to-bot messages:

```text
<@RECIPIENT_BOT_USER_ID> — <task or reply>. <completion protocol if assigning work>
```

Examples:

```text
<@1516899802913308733> — please install these skills and run /reload-skills. When complete, send one concise completion report, then stop.
```

```text
<@1516782563757133964> — done: the office cron was created and verified. No reply required unless you need a change.
```

Rules:

- Use the **recipient's** bot mention token / numeric user ID, not your own, at the beginning of the message.
- On Discord, prefer `<@BOT_USER_ID>` over visible names. If sending via Discord REST, include `allowed_mentions: {"users": ["BOT_USER_ID"], "parse": []}` so Discord resolves/pings the target bot without broad mention parsing.
- If you do not know the exact bot ID, ask the human or inspect a resolved Discord mention before relying on a plain `@Display Name`.
- Keep the no-chatter protocol: mentioning the bot is for triggering delivery, not for starting an acknowledgement loop.

## Request Shape That Prevents Chatter

When assigning work, address the recipient bot with `@` and include a terminal instruction:

```text
<@RECIPIENT_BOT_USER_ID> — when complete, send one concise completion report with artifacts/results and then stop. No acknowledgement or follow-up message is required unless you are blocked or need a decision.
```

For Kanban cards, include the same expectation in the card body:

```text
Completion protocol: call kanban_complete with a concise summary and metadata when done. Do not ask for acknowledgement. Block only if you need a human/bot decision.
```

## Completion Report Acceptance Criteria

A requester can silently accept a completion report when it includes enough of:

- `status: done` or clear completion wording.
- What changed or what was produced.
- Where the artifact lives: path, URL, PR, issue, document, output file, or card ID.
- Verification performed: tests run, command output, source checked, or reason verification was impossible.
- Any limitations or known follow-ups.

If the report has those elements, no reply is needed.

## Anti-Patterns

Avoid these messages to another bot after it completes work:

- "Thanks!"
- "Acknowledged."
- "Great, done."
- "Let me know if you need anything else."
- "Can you confirm this is complete?" when the report already says it is complete.
- Re-summarizing the worker's own completion back to the worker.

These create unnecessary loops and consume context/tokens without changing state.

## Good Examples

### Worker sends terminal completion

Worker:
```text
Done: created `/tmp/report.md`, checked 5 sources, and verified links. No blockers.
```

Requester behavior: **send no reply to the worker.** If a human is waiting, summarize to the human instead.

### Worker blocks

Worker:
```text
Blocked: need to know whether to publish the draft publicly or keep it private.
```

Requester behavior: reply with the decision if known, or ask the human.

### Worker omits artifact

Worker:
```text
Done, I made the file.
```

Requester behavior: ask one precise question:
```text
Please provide the absolute path or URL for the file, then stop.
```

## Verification Checklist

Before replying to another bot after completion, check:

- [ ] Is there an explicit question or blocker?
- [ ] Is the task actually incomplete or unverifiable?
- [ ] Is a dependent task waiting for information not already present?
- [ ] Did the user ask for a message to be sent?
- [ ] Would this message change any state?

If every answer is no, **do not reply**.
