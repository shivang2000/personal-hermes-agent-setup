#!/usr/bin/env python3
import json
import os
import re
import subprocess
import sys

POSTS = [
    "I’m building `termbridge`: one terminal session shared by an AI agent and a human.\n\nThe agent drives Claude Code through MCP + tmux like a real user. The human watches/intervenes from a browser.\n\nLocal testing is in progress — stay tuned.",
    "A lot of builders moved from Claude Code to Codex-style tools because agent/API economics got messy.\n\nThe missing layer: let agents pilot the logged-in Claude Code terminal directly.\n\nThat’s what `termbridge` is exploring: MCP → tmux → Claude Code TUI.\n\nTesting in progress.",
    "`termbridge` is not a Claude wrapper.\n\nIt is a terminal control plane:\n- tmux session = shared substrate\n- MCP tools = agent hands/eyes\n- xterm.js + WebSocket = human watch UI\n- Docker env = isolated workspace\n- Claude Code login = subscription auth\n\nStay tuned.",
    "The goal for `termbridge` is intentionally real:\n\nan agent pilots a logged-in `claude` TUI through MCP tools, edits a repo, and a human watches live in the browser.\n\nNo API key path. No fake CLI abstraction. Just terminal primitives.\n\nLocal testing is in progress.",
    "One underrated idea:\n\nIf a human can use a terminal tool, an agent should be able to use it too.\n\nNot every product needs a special agent API. Sometimes the right loop is:\n\nread screen → type keys → wait → recover from prompts → continue.\n\nThat is the `termbridge` bet.",
    "Claude Code is already a strong coding interface.\n\nThe problem is when agent orchestrators force everything through API-metered usage.\n\n`termbridge` keeps Claude Code as the interactive CLI, keeps subscription auth, and lets an agent drive the same terminal session.\n\nTesting.",
    "The best coding-agent UX may not be fully autonomous.\n\nI want:\nagent drives the terminal\nhuman watches live\nhuman can take over\nagent resumes after intervention\n\n`termbridge` uses a shared tmux session + browser terminal to make that loop natural.\n\nStay tuned.",
    "MCP usually connects agents to APIs.\n\nBut many developer tools are interactive CLIs, not APIs.\n\n`termbridge` exposes the terminal itself as the MCP surface, so agents can operate tools like Claude Code, auth prompts, permission dialogs, and repo workflows directly.",
    "I think a useful layer for AI coding is terminal-native infra:\n\nshared sessions, human takeover, prompt recognizers, permission handling, subscription-auth CLIs, isolated workspaces.\n\n`termbridge` is my first cut at that stack. Local testing in progress.",
    "How `termbridge` works:\n\n1. start a tmux session\n2. stream it to a browser terminal\n3. expose MCP tools for send/capture/wait\n4. keep Claude auth in a Docker volume\n5. let the agent drive the TUI like a human\n\nInteractive CLIs become agent tools.",
    "If API-based agent workflows made Claude Code too expensive for you, I think the better path is:\n\nkeep Claude Code as the coding engine\nrun it in a real terminal\nlet your agent orchestrator pilot it safely\n\nThat is what I’m testing with `termbridge`.",
    "The hard part is not calling Claude.\n\nIt is making a real terminal usable by both an agent and a human:\n\nscreen sync, idle detection, OAuth URL detection, permission prompts, write locks, Docker isolation, browser takeover.\n\nThis is where agent infra gets real.",
]

m = re.search(r"post_(\d+)\.py$", os.path.basename(__file__))
if not m:
    print(f"Cannot infer post index from filename: {__file__}", file=sys.stderr)
    sys.exit(2)
idx = int(m.group(1))
post = POSTS[idx - 1]
if len(post) > 280:
    print(f"Post {idx} is too long: {len(post)} chars", file=sys.stderr)
    sys.exit(2)

res = subprocess.run(["xurl", "post", post], text=True, capture_output=True)
if res.returncode != 0:
    print(res.stdout)
    print(res.stderr, file=sys.stderr)
    sys.exit(res.returncode)
try:
    data = json.loads(res.stdout)
    tid = data.get("data", {}).get("id", "")
    print(f"Posted termbridge campaign {idx}/12: https://x.com/shivangchheda22/status/{tid}")
except Exception:
    print(res.stdout)
