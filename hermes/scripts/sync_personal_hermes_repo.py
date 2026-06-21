#!/usr/bin/env python3
"""Sanitized hourly sync of Shivang's Hermes setup to GitHub.

Quiet on no-op. Prints a short message only when it commits/pushes changes.
Never copies live .env values, auth.json, logs, sessions, caches, DBs, or binaries.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
HERMES = Path(os.environ.get("HERMES_HOME", HOME / ".hermes")).expanduser()
REPO = HOME / "hermes-github-export"
REMOTE = "https://github.com/shivang2000/personal-hermes-agent-setup.git"
GITHUB_REPO = "shivang2000/personal-hermes-agent-setup"

SECRET_KEY_RE=REDACTED_SET_LOCALLY
    r"(?i)(api[_-]?key|token|secret|password|passwd|credential|auth|bearer|"
    r"private[_-]?key|client[_-]?secret|webhook[_-]?url|discord[_-]?bot[_-]?token)"
)
SECRET_VALUE_PATTERNS=REDACTED_SET_LOCALLY
    ("github_token", re.compile(r"ghp_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]+")),
    ("openai_like", re.compile(r"sk-[A-Za-z0-9_-]{20,}")),
    ("slack_like", re.compile(r"xox[baprs]-[A-Za-z0-9-]+")),
    ("discord_bot", re.compile(r"Bot\s+[A-Za-z0-9._-]{20,}")),
    ("bearer", re.compile(r"Bearer\s+[A-Za-z0-9._-]{20,}")),
]

SKIP_NAMES = {
    ".git", "__pycache__", "node_modules", "venv", ".venv", "dist", "build",
    ".curator_backups", ".manual-backups", ".hub", ".jobs.lock", ".tick.lock",
    ".usage.json.lock", "auth.json", "auth.lock", ".env", ".envrc",
}


def run(cmd: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, check=check, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def redact_text(s: str) -> str:
    lines: list[str] = []
    for line in s.splitlines():
        stripped = line.strip()
        if "=" in stripped and not stripped.startswith("#"):
            key = stripped.split("=", 1)[0].strip()
            if SECRET_KEY_RE.search(key):
                prefix = line[: len(line) - len(line.lstrip())]
                lines.append(f"{prefix}{key}=REDACTED_SET_LOCALLY")
                continue
        match = re.match(
            r"^(\s*)([\w.-]*(?:api[_-]?key|token|secret|password|passwd|credential|auth|"
            r"private[_-]?key|client[_-]?secret|webhook[_-]?url)[\w.-]*)(\s*[:=REDACTED_SET_LOCALLY
            line,
            flags=re.I,
        )
        if match:
            lines.append(f"{match.group(1)}{match.group(2)}{match.group(3)}REDACTED_SET_LOCALLY")
            continue
        for _, pattern in SECRET_VALUE_PATTERNS:
            line = pattern.sub("REDACTED_SECRET", line)
        lines.append(line)
    return "\n".join(lines) + ("\n" if s.endswith("\n") else "")


def clean_worktree_preserve_git(repo: Path) -> None:
    repo.mkdir(parents=True, exist_ok=True)
    for child in repo.iterdir():
        if child.name == ".git":
            continue
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()


def copy_redacted(src: Path, dst: Path) -> None:
    if not src.exists() or not src.is_file():
        return
    try:
        if src.stat().st_size > 5_000_000:
            return
        text = src.read_text(errors="replace")
    except Exception:
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(redact_text(text))


def copy_tree_redacted(src: Path, dst: Path) -> None:
    if not src.exists():
        return
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in SKIP_NAMES and not d.endswith(".lock")]
        rootp = Path(root)
        rel = rootp.relative_to(src)
        for filename in files:
            if filename in SKIP_NAMES or filename.endswith(".lock") or filename.endswith(".pyc"):
                continue
            copy_redacted(rootp / filename, dst / rel / filename)


def export_sanitized() -> None:
    clean_worktree_preserve_git(REPO)

    for filename in [
        "config.yaml", "context_length_cache.yaml", "channel_directory.json",
        "gateway_state.json", "discord_threads.json", "SOUL.md", ".install_method",
    ]:
        copy_redacted(HERMES / filename, REPO / "hermes" / filename)

    for backup in sorted(HERMES.glob("config.yaml.bak*")):
        copy_redacted(backup, REPO / "hermes" / "config-backups" / backup.name)

    for dirname in ["skills", "plugins", "cron", "memories", "scripts", "hooks"]:
        copy_tree_redacted(HERMES / dirname, REPO / "hermes" / dirname)

    env_file = HERMES / ".env"
    if env_file.exists():
        keys: list[str] = []
        for line in env_file.read_text(errors="ignore").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                key = line.split("=", 1)[0].strip()
                if key and re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", key):
                    keys.append(key)
        (REPO / "hermes" / ".env.example").write_text(
            "\n".join(f"{key}=REPLACE_ME" for key in sorted(set(keys))) + ("\n" if keys else "")
        )

    manifest = {
        "updated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source_hermes_home": str(HERMES),
        "github_repo": GITHUB_REPO,
        "included": [
            "redacted config.yaml/backups", "skills", "plugins", "cron jobs/scripts redacted",
            "memories redacted", "hooks/scripts redacted", ".env.example with keys only",
        ],
        "excluded": [
            ".env real values", "auth.json/OAuth tokens", "logs", "sessions/transcripts",
            "caches", "audio/image caches", "node/venv/binaries", "full hermes-agent source checkout", "kanban.db",
        ],
        "security_note": "All copied text files were defensively redacted for token/key/password-like fields. Review before pushing public changes.",
    }
    (REPO / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    (REPO / "README.md").write_text(
        f"""# Shivang Personal Hermes Agent Setup

This repo is a **sanitized, GitHub-ready personal setup export** of Hermes Agent setup files from `{HERMES}`.

## Included

- `hermes/config.yaml` and config backups with secret-like values redacted
- `hermes/skills/` custom and installed skills
- `hermes/plugins/`
- `hermes/cron/` job definitions and scripts with redaction
- `hermes/memories/` with redaction
- `hermes/scripts/` and `hermes/hooks/` with redaction
- `hermes/.env.example` containing environment variable names only
- `manifest.json` describing exactly what was included/excluded

## Not included on purpose

These files can contain live credentials or private runtime data and are **not copied**:

- real `.env` values
- `auth.json` OAuth tokens
- gateway/session logs
- full chat transcripts and request dumps
- caches, binaries, `node_modules`, virtualenvs
- full Hermes source checkout under `~/.hermes/hermes-agent`

## Restore sketch

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
cp -R hermes/skills ~/.hermes/skills
cp hermes/config.yaml ~/.hermes/config.yaml
cp hermes/.env.example ~/.hermes/.env   # then fill real secrets locally
hermes doctor
```

**Security:** This repository is public, so keep real secrets only in local `.env`/`auth.json` files.
"""
    )

    (REPO / ".gitignore").write_text(
        """# Never commit real secrets/runtime state
.env
.env.*
!hermes/.env.example
auth.json
*.token
*.pem
*.key
logs/
sessions/
cache/
*.db
*.lock
.DS_Store
"""
    )


def scan_for_obvious_secrets() -> list[tuple[str, str, int]]:
    findings: list[tuple[str, str, int]] = []
    for path in REPO.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        try:
            text = path.read_text(errors="ignore")
        except Exception:
            continue
        for name, pattern in SECRET_VALUE_PATTERNS:
            for match in pattern.finditer(text):
                findings.append((name, str(path.relative_to(REPO)), text.count("\n", 0, match.start()) + 1))
    return findings


def ensure_git_repo() -> None:
    if not (REPO / ".git").exists():
        run(["git", "init"], cwd=REPO)
    remotes = run(["git", "remote"], cwd=REPO).stdout.split()
    if "origin" in remotes:
        run(["git", "remote", "set-url", "origin", REMOTE], cwd=REPO)
    else:
        run(["git", "remote", "add", "origin", REMOTE], cwd=REPO)
    run(["git", "branch", "-M", "main"], cwd=REPO)


def main() -> int:
    ensure_git_repo()
    export_sanitized()
    findings = scan_for_obvious_secrets()
    if findings:
        print("Refusing to push: obvious secret-like strings remain in sanitized export:")
        for name, path, line in findings[:30]:
            print(f"- {name}: {path}:{line}")
        if len(findings) > 30:
            print(f"... and {len(findings) - 30} more")
        return 2

    run(["git", "add", "-A"], cwd=REPO)
    status = run(["git", "status", "--porcelain"], cwd=REPO).stdout.strip()
    if not status:
        return 0

    timestamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")
    run(["git", "commit", "-m", f"chore: sync Hermes setup ({timestamp})"], cwd=REPO)
    push = run(["git", "push", "-u", "origin", "main"], cwd=REPO)
    changed_files = len(status.splitlines())
    print(f"Synced sanitized Hermes setup to {REMOTE} ({changed_files} changed paths).")
    if push.stdout.strip():
        print(push.stdout.strip().splitlines()[-1])
    return 0


if __name__ == "__main__":
    sys.exit(main())
