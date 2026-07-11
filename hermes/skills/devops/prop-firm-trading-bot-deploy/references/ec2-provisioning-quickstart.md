# EC2 Provisioning Quickstart — Trading Bot V2

The only reliable deployment path for MT5-based trading bots on Apple Silicon Macs.
MT5 runs natively on x86 Linux — no Wine emulation, no Rosetta, no QEMU.

## Prerequisites

- AWS CLI configured: `aws configure list` shows credentials + region
- SSH key at `~/.ssh/id_ed25519.pub`
- Repo pushed to GitHub (EC2 bootstrap pulls from there)

## One-shot provisioning

```bash
cd ~/dev/advanced-trading-bot/trading-bot-v2

export AWS_REGION=ap-south-1          # Mumbai (closest for India users)
export ACCOUNT_NAME=fundingpips-5k    # used for SSM paths, S3 bucket, tags
export REPO_URL=https://github.com/<user>/trading-bot-v2.git
export GIT_BRANCH=main
export INSTANCE_TYPE=t3.medium        # 2 vCPU, 4 GB — enough for MT5 + bot
export DATA_VOLUME_GB=60              # persists across termination
export KEY_NAME=trading-bot-v2-key

bash scripts/aws-provision.sh
```

## What the provisioner creates

1. **S3 bucket** — nightly backups, versioning + lifecycle
2. **SSM SecureString parameters** — MT5 master password, tokens (you fill in interactively)
3. **IAM role + instance profile** — SSM read + S3 write
4. **Security group** — SSH (22) + noVNC (8080) from your IP only
5. **SSH keypair** — imported from `~/.ssh/id_ed25519.pub`
6. **EBS data volume** — 60 GB gp3, `DeleteOnTermination=false` (survives instance churn)
7. **EC2 instance** — t3.medium, Ubuntu 24.04 LTS, with bootstrap user-data

## Post-provision steps

1. Wait ~5 min for bootstrap (installs Docker, pulls repo, writes .env from SSM)
2. Open noVNC: `http://<ec2-ip>:8080` (password: `botpass`)
3. In MT5: search for "FundingPips Corp (2)" server, log in with funded account credentials
4. Enable AutoTrading (Algo Trading button must be green)
5. Restart bot: `ssh ubuntu@<ip> 'sudo -u bot bash -c "cd /home/bot/trading-bot-v2 && docker compose -f docker-compose.ec2.yml restart trading-bot"'`
6. Verify: `ssh ubuntu@<ip> 'docker logs --tail 20 trading-bot-v2'`

## Cost estimate (ap-south-1, 2026)

| Item | Monthly |
|---|---|
| t3.medium | $35 |
| 60 GB gp3 EBS (data) | $5 |
| 8 GB gp3 EBS (root) | $0.65 |
| Auto-assigned IP | $0 (charged only when stopped >1h) |
| S3 backups (~10GB) | $0.25 |
| CloudWatch metrics | $1 |
| SSM parameters | $0 |
| **Total** | **~$42/mo** |

## Data durability (post-mortem preconditions)

- EBS `DeleteOnTermination=false` — verified by provisioner
- Nightly S3 sync — `scripts/nightly-backup.sh` cron on EC2
- Data volume at `/dev/nvme1n1`, mounted at `/data` by bootstrap
- If instance terminates: data volume survives, re-attach to a new instance

## Teardown

```bash
# Full teardown using the state file
cat /tmp/aws-provision-fundingpips-5k.state
# Then delete resources per AWS_DEPLOYMENT.md §10
```

## Common issues

- **Bootstrap takes >5 min**: check `ssh ubuntu@<ip> 'sudo tail -f /var/log/cloud-init-output.log'`
- **Docker not ready after bootstrap**: `ssh ubuntu@<ip> 'sudo systemctl restart docker'`
- **MT5 not in server list**: search for "FundingPips Corp (2)", add manually, clear MT5 cache if needed
- **Bot can't connect to MT5**: MT5 must be logged in AND AutoTrading enabled before bot starts
- **Public IP changes on stop/start**: auto-assigned IP is ephemeral. Use Elastic IP if you need a fixed IP ($4/mo extra)