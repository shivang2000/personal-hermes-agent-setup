# Installing `obra/superpowers` skills into Hermes

Session-derived pattern for installing a GitHub repo that exposes multiple skills under `skills/<name>/SKILL.md`.

## Commands that worked

Add the tap and search:

```bash
hermes skills tap add https://github.com/obra/superpowers
hermes skills search superpowers
```

If `hermes skills inspect superpowers` or `hermes skills install superpowers` says “No exact match” despite showing suggestions, use direct raw URLs:

```bash
hermes skills inspect https://raw.githubusercontent.com/obra/superpowers/main/skills/using-superpowers/SKILL.md
```

Install non-interactively:

```bash
for skill in brainstorming dispatching-parallel-agents executing-plans finishing-a-development-branch receiving-code-review requesting-code-review subagent-driven-development systematic-debugging test-driven-development using-git-worktrees using-superpowers verification-before-completion writing-plans writing-skills; do
  hermes skills install --yes --force "https://raw.githubusercontent.com/obra/superpowers/main/skills/$skill/SKILL.md" || true
done
```

Verify:

```bash
hermes skills list
```

Then tell the user to run:

```text
/reload-skills
```

## Security scanner behavior observed

- SAFE verdicts install with `--yes`.
- CAUTION/BLOCKED verdicts can be installed with `--force` when appropriate.
- DANGEROUS verdicts remain blocked; `--force` does not override them.

For the `obra/superpowers` repo, the scanner blocked these as DANGEROUS in this session:

- `using-superpowers`
- `writing-skills`

Do not report them as installed unless a later verified command shows they installed successfully.

## Reporting pattern

When summarizing, list:

1. Tap added.
2. Skills installed/reinstalled.
3. Skills blocked by scanner, with the reason at a high level.
4. Reload instruction: `/reload-skills` or start a new Hermes session.