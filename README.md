# Shivang Hermes Backup / Setup

This repo is a **sanitized, GitHub-ready backup** of Hermes Agent setup files from `/Users/shivang/.hermes`.

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

These files can contain live credentials or private runtime data and were **not copied**:

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

**Security:** review before making this repo public. Prefer a private GitHub repo.
