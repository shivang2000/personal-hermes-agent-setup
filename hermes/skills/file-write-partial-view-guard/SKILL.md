---
name: file-write-partial-view-guard
description: When a file has been read with offset/limit pagination, NEVER use write_file to "append" — re-read the whole file first. This is the exact failure mode that destroyed data/applications.md in the career-ops job search session on 2026-07-24 (534 lines → 1 line).
---

# CRITICAL: Never write_file a file you have only partially read

## What happened (real example)

Shivang asked for a cold email to pavel@noketa.io. I was working in `/Users/shivang/dev/jobsearch/career-ops/`. The file `data/applications.md` was 534 lines / 124,694 bytes.

1. I called `read_file` on it. Default limit is 500 lines, so I got back **lines 1–406** with a `next_offset: 407` hint and a `truncated_by: bytes` flag. The file is 534 lines, so **128 lines were unseen** and not in my context.
2. I called `write_file` with the *full intended content of the file* (or in my case, what I thought was a single new line) — `write_file` always **overwrites the entire file**.
3. The `write_file` tool issued a warning: *"this file was last read with offset/limit pagination (partial view). Re-read the whole file before overwriting it."*
4. **I ignored the warning.** I overwrote the 534-line file with my single new line. Result: 124,694 bytes → 708 bytes. Application tracker destroyed.
5. Recovery from inside the session failed (git, worktrees, session caches, Time Machine, `find` — all returned nothing). The user has to restore from an external backup.

## The rule

**Before any `write_file` call on a file that exists:**

1. If your last `read_file` on that file used `offset` or `limit` (i.e. returned `truncated_by`, `next_offset`, or `is_binary: false` with pagination metadata) → **STOP.** Re-read with `offset=1` and no `limit` (or a high enough limit to cover the whole file). Verify the read covers the full file.
2. If the file is too big to read in one call (rare, >100K chars / >~2000 lines), use `patch` with `mode='replace'` for targeted edits — `patch` does not require a full re-read and does not overwrite anything except the matched block.
3. If the file was read via a different tool path (`terminal cat`, `read_file` with different params, `cat` in a sub-shell, etc.) — re-read via the canonical `read_file` tool with full-file params before writing.
4. If the file is `.gitignore`'d, user-data, or in any other "unsynced" state, the warning is even MORE important — you cannot recover from git, the user has to restore.

## The `patch` alternative (preferred for any addition)

`patch` with `mode='replace'` does a targeted find-and-replace and does NOT require a full re-read:

```python
patch(
    mode='replace',
    path='/path/to/file.md',
    old_string='<the last line of the existing file as a unique anchor>',
    new_string='<the last line of the existing file>\n<your new line>',
)
```

`patch` is the right tool for **append** (anchor on the last line, replace with last-line-plus-new-line) and for any other single-spot edit. It does not silently nuke the file.

## When `write_file` IS safe to call without re-reading

- The file does not exist yet (write_file will create it from scratch).
- The previous `read_file` returned the full file with no `next_offset` and no `truncated_by` flag.
- The file was *created* in this session by *this* tool and never edited since.
- The user explicitly told you "replace the whole file with X" and you have the full current content in context.

## When the damage is already done

If you overwrite a file by accident:

1. **Stop immediately** and tell the user, do not try to silently "fix" it.
2. Check git: `git log --oneline -- <path>`, `git stash list`, `git reflog`, `git worktree list`. If uncommitted, check `.git/index` recovery options. If gitignored, recovery via git is impossible.
3. Check `~/.config/superpowers/conversation-archive/`, `~/.claude/projects/`, `~/.openclaude/projects/`, `~/.hermes/snapshots/`. These sometimes have the file in a tool_result or message content.
4. Time Machine: `tmutil listbackups`. If "No machine directory found for host" → not configured.
5. If you have the file in your own context window (read successfully, just truncated), tell the user exactly which lines you still have and ask them to source the rest. Do NOT try to reconstruct unseen content from memory — that is fabrication.
6. Update memory and save a skill with the exact failure so the next session doesn't repeat it.

## Why this skill exists

This is a deterministic, structural failure mode. The tool already warns you. The fix is mechanical. But the cost of slipping past the warning is silent data loss. The only way to prevent it is to make the rule load-bearing in your workflow, the same way `verification-before-completion` is load-bearing before claiming "done."
