---
name: hermes-third-party-skills
description: Install and verify third-party/community Hermes skills from taps, GitHub repos, or direct SKILL.md URLs; handle security scanner prompts and blocked verdicts safely.
version: 1.0.0
author: REDACTED_SET_LOCALLY
license: MIT
metadata:
  hermes:
    tags: [hermes, skills, setup, third-party, github, taps]
---

# Hermes Third-Party Skills

Use this when the user wants to install, update, inspect, or troubleshoot community skills for Hermes Agent, especially from a GitHub repository or raw `SKILL.md` URL.

## Core workflow

1. If the request concerns Hermes itself, first consult the `hermes-agent` skill/docs for current CLI syntax.
2. Add the repo as a tap when the user gives a GitHub source repo:

   ```bash
   hermes skills tap add https://github.com/OWNER/REPO
   ```

3. Search to see how Hermes indexes the tap:

   ```bash
   hermes skills search QUERY
   ```

4. If the hub identifier is ambiguous or install does not proceed, inspect or install direct raw `SKILL.md` URLs instead:

   ```bash
   hermes skills inspect https://raw.githubusercontent.com/OWNER/REPO/main/skills/SKILL_NAME/SKILL.md
   hermes skills install --yes https://raw.githubusercontent.com/OWNER/REPO/main/skills/SKILL_NAME/SKILL.md
   ```

5. For multiple repo skills, enumerate the repo's `skills/` directories, then install each direct `SKILL.md` URL. Prefer `--yes` for non-interactive agent runs so installation does not cancel at the confirmation prompt.
6. Use `--force` only when the scanner reports CAUTION/BLOCKED and the user has clearly asked to install that third-party skill set. Never claim `--force` can override DANGEROUS verdicts; Hermes may still refuse installation.
7. Verify by listing installed skills and/or checking the files under the active profile's skills directory:

   ```bash
   hermes skills list
   ```

8. Tell the user to reload or restart so new skills enter the current context:

   ```text
   /reload-skills
   ```

## Pitfalls

- `hermes skills inspect ID` can report “No exact match” even when the search table shows an identifier. When that happens, use the direct raw `SKILL.md` URL path.
- `hermes skills install` is interactive by default. Without `--yes`, it may show the disclaimer and then cancel because no confirmation was supplied.
- Direct URL installs from community sources run the security scanner and may quarantine before install.
- `--force` can override some CAUTION/BLOCKED scanner decisions, but not DANGEROUS decisions.
- Do not edit bundled or hub-installed skills to encode local lessons. If the protected skill is missing a workflow, create or update a local umbrella skill like this one instead.

## Reference notes

- See `references/superpowers-install.md` for a concrete GitHub repo skill-install transcript pattern and blocked-verdict handling.