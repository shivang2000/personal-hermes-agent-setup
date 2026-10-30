# Pitfall: literal newline inside a JSON-escaped string when patching jobs.json

## What went wrong (verbatim session trace)

A user asked to add `https://engineering.atspotify.com/` as a new source in the
existing `#tech-news` digest job (`6be19c7edbdb`). I did:

1. `cronjob list` → confirmed 4 jobs, the digest was scheduled, no service
   needed restarting.
2. `python3 -c '...'` on `~/.hermes/cron/jobs.json` to read the full prompt
   (the CLI has no `show` command, only `list/create/add/edit/pause/resume/run/remove/status/tick`).
3. `patch mode=replace` on `jobs.json` to insert the new bullet into the
   `prompt` string. The `new_string` parameter contained a **literal newline**
   between "...infra companies." and "- Big-tech engineering blogs...". The
   patch applied — but the file now has a physical newline inside a JSON string,
   which is not legal JSON.
4. The patch tool's lint reported
   `JSONDecodeError: Invalid control character at (line 98, column 977)`.
5. `python3 json.load` confirmed: `INVALID: Invalid control character at:
   line 98 column 977 (char 9065)`. The file was unparseable — anything that
   re-loaded the scheduler state would have errored.

## What should have happened (cleaner path)

The right tool was `cronjob action='update' job_id=<id> prompt=<new_prompt>`.
That call would have:
- Serialized the prompt as a proper JSON string (escaped `\n` automatically).
- Updated the on-disk `jobs.json` atomically.
- Been visible to the scheduler on the next tick.

I had the tool available the whole time. Reaching for `patch` on a JSON file
when a higher-level `update` action exists is the actual mistake.

## How I recovered (if you do hit the broken state)

The repair: replace the physical newline + leading whitespace inside the broken
string with the two characters `\` + `n` (so the JSON value reads `\\n`, which
parses as a newline escape).

Concrete patch that fixed it:

```
old_string (file content):
  ... infra companies.
  - Big-tech engineering blogs ...

new_string (file content):
  ... infra companies.\\n- Big-tech engineering blogs ...
```

`replace_all=false`, no other context. After the patch the file validated:

```
VALID JSON, jobs: 4
schedule: {'kind': 'cron', 'expr': '55 12,16,20,0 * * *', ...}
state: scheduled
next_run_at: 2026-07-02T12:55:00+05:30
```

**What I did NOT do, and why**: I did not restore from one of the
`jobs.json.bak_*` dated snapshots. Those were from 2026-06-21 (most recent was
`hashtag_policy_20260621_185319`) — older than the live file which had been
updated 2026-07-02. Restoring would have lost newer edits (e.g. any prompt
changes between 06-21 and 07-02). Dated `.bak_*` files are merge-of-trust
snapshots, not transaction logs.

## Verification protocol after any direct jobs.json edit

Run all three:

```
# 1. JSON parses
python3 -c "import json; json.load(open('/Users/shivang/.hermes/cron/jobs.json'))"

# 2. Job count matches expectations
python3 -c "import json; print(len(json.load(open('/Users/shivang/.hermes/cron/jobs.json'))['jobs']))"

# 3. Scheduler still sees the target job
hermes cron list 2>&1 | grep <job_id>   # (or cronjob list via the tool)
```

Step 1 is the only one that catches the newline-in-string bug. Step 3 catches
gateways that cached a broken parse.
