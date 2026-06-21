# Local Work Summary Cron Pattern

Use this reference for recurring jobs that turn Shivang's recent local work into safe Twitter/X draft angles for review.

## Proven job shape

- Purpose: summarize recent work signals into tweet angles; never auto-post.
- Schedule used: weekdays at 7:30 PM IST (`30 19 * * 1-5`) for end-of-office-day reflection.
- Delivery: current Discord review thread (`origin`) unless Shivang asks for a different channel; for Twitter automation status/review, prefer `#tweets-automation` when selecting a non-origin Discord target.
- Model pin: `openai-codex` / `gpt-5.5` for recurring Hermes cron jobs unless Shivang explicitly requests another model.
- Minimal toolsets: `terminal`, `file`, `session_search` are enough for local-work-signal drafts and reduce cron context/tool overhead.

## Prompt guardrails

The cron prompt should instruct the agent to:

1. Use only safe local work signals: session summaries, git/file metadata, command history, high-level codebase structure, and non-sensitive task names.
2. Avoid secrets, customer data, private payloads, proprietary docs, exact configs, sensitive traces, credentials, or raw internal logs.
3. Produce tweet angles/drafts for review only; do **not** post tweets.
4. Bias toward concrete engineering details and lessons: backend, infra, reliability, payments/refunds, observability, integration edge cases, debugging practice, and implementation tradeoffs.
5. Avoid generic founder/productivity/AI-agent takes unless grounded in Shivang's actual work.

## Verification notes

After creating or updating the cron:

- Manually trigger a run with the cron tool/CLI.
- A consumed trigger plus `next_run` advancing proves the scheduler accepted the run, but not necessarily that the agent completed successfully.
- If cron metadata still reports `last_status: null`, state that limitation clearly instead of claiming a completed successful run.
- Remove any temporary duplicate jobs created while reconciling schedule/model/delivery settings.
