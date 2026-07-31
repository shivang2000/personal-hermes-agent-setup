# MT5 Container Compromise: Detection and Deployment Stop-Gate

Use this runbook when an MT5/noVNC container shows unexpected downloads, miners, unknown shared objects, or unexplained CPU/process activity. A compromised broker terminal is a hard deployment blocker because it handles account credentials and sits on the execution path.

## High-confidence indicators

Treat any of these as confirmed compromise, not a normal MT5/Wine quirk:

- `xmrig` or `xmr_linux_amd64` processes
- `/tmp/xmrig/xmrig-*` running as root
- repeated downloads of shell scripts from unrelated domains
- unknown preload/shared-object files such as `/usr/local/lib/sshdd.so`
- unexpected `node index.js` supervising a miner process
- repeated `Killed` messages paired with re-download/relaunch loops

## Read-only triage first

Capture evidence before changing state:

```bash
docker inspect metatrader5 --format \
  'privileged={{.HostConfig.Privileged}} network={{.HostConfig.NetworkMode}} user={{.Config.User}}'
docker inspect metatrader5 --format \
  'mounts={{range .Mounts}}{{.Source}}->{{.Destination}}(rw={{.RW}}) {{end}}'
docker top metatrader5 -eo pid,ppid,user,etime,args
docker logs --tail 200 metatrader5
sudo ss -lntup | grep -E ':(5900|8001|8080)\b'
ps -ef | grep -E 'xmrig|xmr_linux_amd64|sshdd|check\.sh' | grep -v grep
```

Interpretation:

- `privileged=false`, no host PID mode, miner only in `docker top`: likely container-confined, but writable bind mounts remain untrusted.
- miner/shared-object/process visible on the host: assume host compromise and replace the instance.
- absence of a host process does not make the existing container safe to reuse.

## Immediate containment

Stopping MT5 is disruptive and may require a fresh login, so use the normal side-effect approval gate. Once approved:

```bash
docker stop metatrader5
docker inspect metatrader5 --format \
  'status={{.State.Status}} exit={{.State.ExitCode}} finished={{.State.FinishedAt}}'
sudo ss -lntup | grep -E ':(5900|8001|8080)\b' || echo 'MT5 ports closed'
ps -ef | grep -E 'xmrig|xmr_linux_amd64|sshdd' | grep -v grep \
  || echo 'No host miner process'
```

Do not restart the compromised container to continue deployment. Do not enter funded credentials into it again.

## Recovery standard

Replacement is preferred over cleanup:

1. Preserve only evidence needed for investigation; never copy executables or startup scripts from the container.
2. Replace the EC2 instance or, only when host compromise is confidently excluded, recreate MT5 from a freshly pulled, digest-pinned trusted image.
3. Treat writable MT5 bind mounts and named volumes as untrusted. Build a fresh Wine/MT5 data directory.
4. Review custom mounted startup scripts from the clean local repository.
5. Rotate potentially exposed credentials: MT5 master password, VNC password, mounted API keys, and host secrets.
6. Review cloud audit logs, SSH history, security-group changes, and outbound traffic for the exposure window.
7. Restrict noVNC/VNC/RPyC ports to the operator IP or private network. Never leave 5900, 8001, or 8080 broadly reachable.
8. Replace weak/default VNC passwords such as `botpass`; prefer SSH tunnel or VPN over public noVNC.
9. Re-run the complete readiness gate before adding funded credentials.

## Deployment decision rule

**Any confirmed miner or unknown code execution inside MT5 means BLOCKED.** Passing tests and a successful application image build do not override a compromised runtime target. Resume only after containment, clean replacement/rebuild, credential rotation, port restriction, and clean runtime verification.

The MT5 terminal holds broker authentication and can place orders. A compromise can lead to account theft, unauthorized trading, or prop-firm termination even when the Python bot itself is correct.