import subprocess, sys, json
post = """The simplest useful definition of an AI agent:

an LLM inside a loop, with tools + state/context.

observe → decide → call tool → read result → repeat until done.

via @kirat_tw

#AIAgents #AIEngineering"""
res = subprocess.run(['xurl', 'post', post], text=True, capture_output=True)
if res.returncode != 0:
    print(res.stdout)
    print(res.stderr, file=sys.stderr)
    sys.exit(res.returncode)
try:
    data = json.loads(res.stdout)
    tid = data.get('data', {}).get('id', '')
    print(f"Posted agent sequence 2/5: https://x.com/shivangchheda22/status/{tid}")
except Exception:
    print(res.stdout)
