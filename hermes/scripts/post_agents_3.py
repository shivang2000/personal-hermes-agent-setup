import subprocess, sys, json
post = """A coding agent has two main layers:

1) the agent loop that manages messages + tool calls
2) the terminal UI around it

Once you see that, Claude Code/Codex-style tools feel less mysterious.

via @kirat_tw

#CodingAgents #LLM"""
res = subprocess.run(['xurl', 'post', post], text=True, capture_output=True)
if res.returncode != 0:
    print(res.stdout)
    print(res.stderr, file=sys.stderr)
    sys.exit(res.returncode)
try:
    data = json.loads(res.stdout)
    tid = data.get('data', {}).get('id', '')
    print(f"Posted agent sequence 3/5: https://x.com/shivangchheda22/status/{tid}")
except Exception:
    print(res.stdout)
