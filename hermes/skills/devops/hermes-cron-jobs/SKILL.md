---
name: hermes-cron-jobs
description: Manage Hermes scheduled cron jobs — create, edit prompts, change cadence, pause/resume, debug failures, and find outputs. Use when adding/removing a research source in an existing digest job, updating a job's prompt or selection rules, troubleshooting why a job didn't run or auto-paused, or recovering from a shared API quota that 429'd a whole fleet.
---

# Managing Hermes Cron Jobs

## When to use
- Add or remove a research source in an existing digest job (HN, YC, GitHub, YouTube, engineering blogs, etc.)
- Edit the prompt of a scheduled job (voice, format, selection rules, output sections)
- Change cadence (`every 5m` → `every 30m`) for cost or quota reasons
- Pause/resume jobs, especially after a shared API tier hits 429 and auto-paused the whole fleet
- Debug why a job didn't fire, errored, or paused itself
- Find where job outputs and run logs are stored

## Discovery — find the right job first

Always `cronjob action='list'` first. **Never guess job IDs** — list is the source of truth and returns `id`, `name`, `schedule`, `state`, `paused_at`, `paused_reason`, `last_status`, `last_error`, `last_delivery_error`, `next_run_at`.

**Reading a job's full prompt**: there is **no** `hermes cron show` command (verified — `hermes cron` only has `list/create/add/edit/pause/resume/run/remove/status/tick`). Two paths:
1. **Read the on-disk store**: `~/.hermes/cron/jobs.json`. Job dicts use key **`id`** (not `job_id`).
2. **Round-trip through the tool**: pass the prompt into `cronjob action='update'` (validates JSON, scheduler sees it immediately) and then read back.

The on-disk file is the merge-of-truth. Backups `jobs.json.bak_*` are dated snapshots and may be stale — don't restore from them blindly.

## Editing prompts — the safe path

**Always prefer `cronjob action='update'` with the new `prompt`.** It serializes JSON correctly, the scheduler sees the change immediately, and the on-disk file is updated atomically. Direct file edits to `~/.hermes/cron/jobs.json` also work (the gateway file-watches the file per tick — verified, no service restart needed) but introduce a real pitfall below.

For a typical "add a source" edit: `cronjob list` → grab the current prompt → modify the source list in place → `cronjob update job_id=<id> prompt=<new_prompt>` → verify with `cronjob list` (state=`scheduled`, `next_run_at` in the future).

### Pitfall: literal newline inside a JSON-escaped string (file-edit path)

If you use the `patch` tool to insert text into a `"prompt": "..."` value in a JSON file, **a literal newline in `new_string` is written to the file as a literal newline, breaking JSON**. `python3 -c "import json; json.load(open(path))"` will fail with `Invalid control character at: line N column M`. The `patch` tool's own pre-write lint may or may not catch it (it depends on whether the substituted text is reparsed) — always verify with `json.load` afterward.

**Fix**: the file must contain the two characters `\` + `n` (which JSON parses as a newline escape) at the position where you want a line break inside a string. To repair a broken file: `patch` the literal newline back to `\\n` in the parameter, so the file gets the two characters `\n`. Do **not** restore from a dated `.bak_*` — those are older merged states and will lose subsequent edits.

**Cleanest alternative**: skip the file edit entirely. Use `cronjob action='update' job_id=<id> prompt=<new_prompt>` and let the tool serialize. The new_prompt value is just a Python string passed through the tool's parameters — embedded `\n` is fine.

## Pausing, resuming, and force-running

- **Pause**: `cronjob action='pause' job_id=<id>`. State changes to `paused`; `next_run_at` freezes.
- **Resume**: `cronjob action='resume' job_id=<id>`. **One at a time** if multiple jobs were auto-paused together (shared quota 429). Bulk-resuming a paused fleet before fixing the cause just lets them re-burn quota and re-pause.
- **Force-run now**: `cronjob action='run' job_id=<id>`. Use this to verify a prompt change works before the next scheduled tick — much faster than waiting hours.
- **Edit cadence**: `cronjob action='update' job_id=<id> schedule="every 30m"` or `"55 12,16,20,0 * * *"`. Both cron-expression and relative forms are accepted.

## Where outputs and logs live

- Per-run stdout/agent output: `~/.hermes/cron/output/<job_id>/<timestamp>.txt` (one file per run)
- Full per-run request dumps (prompt, model, context, tool calls): `~/.hermes/sessions/request_dump_cron_<job_id>_<timestamp>_*.json`
- Scheduler state: `~/.hermes/cron/jobs.json` + `ticker_heartbeat` + `ticker_last_success`
- Lock files (ignore unless debugging scheduler contention): `~/.hermes/cron/.jobs.lock`, `~/.hermes/cron/.tick.lock`

## Quota and auto-pause behavior (X API and similar shared tiers)

Some cron fleets share a single API tier — e.g. multiple X/Twitter jobs on one quota. An aggressive cadence on one job (the classic trap: an `every 5m` reply scanner) can burn the monthly cap in well under 24h and silently 429 every other job in the fleet. The scheduler auto-pauses all of them on 429.

**Symptoms in `cronjob list`**:
- `state: paused`, `last_status: error`
- `last_delivery_error: HTTP 429: The usage limit has been reached`
- Multiple jobs paused at the same timestamp

**Recovery sequence**: (1) lower cadence on the offending job via `cronjob update` schedule, (2) top up credits / quota on the upstream API, (3) `cronjob resume <id>` for each paused job **one at a time**, (4) verify with `cronjob list` that each is `state: scheduled` with a future `next_run_at`.

**Safe default cadences for X/Twitter fleets**: reply scanner `every 30m`, opportunity scan `every 45m`–`2h`, news digest `every 4h`, daily queue `1/day`.

## Model pinning

For Shivang's personal-Hermes profile, recurring cron jobs should be pinned to **`openai-codex/gpt-5.5`** unless he explicitly requests a different model — set this in `cronjob create` / `cronjob update` via the `model` parameter. Tier-1 always-on jobs (crons, iMessage replies, news digests, tweets, trading bots) belong on the cheap/fast tier; reserve Tier-2 top-intelligence models for one-off multi-step agent work, not scheduled automations.

## Common workflows

### Add a new research source to a digest job
1. `cronjob list` → identify the digest job, copy its current `prompt` (or read `~/.hermes/cron/jobs.json`)
2. Edit the prompt: add the new source in the appropriate bullet section, keep the existing bullet style, follow any source-grouping convention (e.g. AI labs / big-tech engineering blogs / GitHub / YouTube)
3. `cronjob update job_id=<id> prompt=<new_prompt>` — pass the full new prompt as a single string
4. `cronjob list` to confirm `state: scheduled`, `next_run_at` in the future
5. Optional: `cronjob run job_id=<id>` to dry-run now, then check `~/.hermes/cron/output/<job_id>/` for the result

### Edit cadence without changing prompt
`cronjob update job_id=<id> schedule="every 30m"` (or cron expression). No prompt change needed.

### Recover a fleet from 429 auto-pause
1. Identify the offending job (the one with the highest frequency / most calls per period)
2. Lower its cadence via `cronjob update schedule="..."`
3. Top up the upstream API credits/limit
4. `hermes cron resume <job_id>` **for each paused job, one at a time**, in order from least-frequent to most-frequent (so a job that 429'd last cycle doesn't immediately re-burn quota)
5. `cronjob list` to confirm the whole fleet is back to `scheduled`

## Verification before claiming done
- `cronjob list` shows the job `state: scheduled` (not `paused`) and a future `next_run_at`
- If you changed the prompt: `cronjob run <id>` produces a delivery and the output file exists in `~/.hermes/cron/output/<job_id>/`
- If you wrote to `jobs.json` directly: `python3 -c "import json; json.load(open('~/.hermes/cron/jobs.json'))"` parses cleanly
- If the change was substantive: skim the run output for format/voice regressions before assuming the next scheduled tick will look the same

## Reference files
- `references/jobs-json-edit-pitfall.md` — verbatim session trace of a literal-newline JSON corruption and the in-place fix; the dated `.bak_*` files are merge-of-trust snapshots, not transaction logs.
