import subprocess, sys, json
post = """Agent infra lesson from @kirat_tw: full conversation history preserves reasoning and cacheability, but it explodes context.

Summarizing helps context length, but can break KV-cache benefits.

A lot of performance hides in these boring tradeoffs.

#LLM #AIInfra"""
res = subprocess.run(['xurl', 'post', post], text=True, capture_output=True)
if res.returncode != 0:
    print(res.stdout)
    print(res.stderr, file=sys.stderr)
    sys.exit(res.returncode)
try:
    data = json.loads(res.stdout)
    tid = data.get('data', {}).get('id', '')
    print(f"Posted agent sequence 5/5: https://x.com/shivangchheda22/status/{tid}")
except Exception:
    print(res.stdout)
