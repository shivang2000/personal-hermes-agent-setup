import subprocess, sys, json
post = """Big takeaway from @kirat_tw’s agent breakdown: the harness matters less than I expected.

If the model is strong at tool use, a simple terminal agent with bash/read/write can compete surprisingly well.

Complexity should earn its place.

#AIAgents"""
res = subprocess.run(['xurl', 'post', post], text=True, capture_output=True)
if res.returncode != 0:
    print(res.stdout)
    print(res.stderr, file=sys.stderr)
    sys.exit(res.returncode)
try:
    data = json.loads(res.stdout)
    tid = data.get('data', {}).get('id', '')
    print(f"Posted agent sequence 4/5: https://x.com/shivangchheda22/status/{tid}")
except Exception:
    print(res.stdout)
