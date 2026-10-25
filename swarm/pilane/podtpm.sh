#!/bin/bash
# Dell: Argon input tokens/min (5-min window) across ALL RUNNING pods (pi sessions + argon CLI logs) + Dell calls.jsonl.
H=~/cs-audit/gemini-hackathon
python3 - <<'PY' > /tmp/podtpm-pods.txt
import json,urllib.request,os
k=[l.split("=",1)[1].strip().strip('"') for l in open(os.path.expanduser("~/.config/runpod.env")) if l.startswith(("RUNPOD_API_KEY","export RUNPOD_API_KEY"))][0]
q='{"query":"{ myself { pods { name desiredStatus runtime { ports { ip isIpPublic privatePort publicPort } } } } }"}'
r=json.load(urllib.request.urlopen(urllib.request.Request("https://api.runpod.io/graphql",q.encode(),{"Content-Type":"application/json","Authorization":"Bearer "+k}),timeout=30))
for p in r["data"]["myself"]["pods"]:
    s=[x for x in ((p.get("runtime") or {}).get("ports") or []) if x["privatePort"]==22 and x["isIpPublic"]]
    if p["desiredStatus"]=="RUNNING" and s: print(p["name"],s[0]["ip"],s[0]["publicPort"])
PY
T=0; PI=0; CLI=0; N=0
while read NAME IP PORT; do
  R=$(timeout 25 ssh -o BatchMode=yes -o ConnectTimeout=8 -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile=$H/overflow/known_hosts -p $PORT root@$IP "python3 - " < /tmp/podtpm-remote.py 2>/dev/null) || continue
  echo "$NAME $R"; N=$((N+1))
done < /tmp/podtpm-pods.txt > /tmp/podtpm-rows.txt
python3 - "$N" <<'PY'
import json,sys,subprocess,os
rows=[l.split(" ",1) for l in open("/tmp/podtpm-rows.txt") if "{" in l]
pi=sum(json.loads(r[1])["pi_in"]+json.loads(r[1])["pi_cache"] for r in rows)
cli=sum(json.loads(r[1])["argon_cli_in"] for r in rows)
dell=subprocess.run(["python3",os.path.expanduser("~/cs-audit/gemini-hackathon/tpm.py")],capture_output=True,text=True).stdout
d=0
for l in dell.splitlines():
    if l.startswith("gemini-4-argon"): d=int(l.split()[1])
print(f"pods_reached={len(rows)} pi_in_tok_per_min={pi//5} pod_argon_cli_in_per_min={cli//5} dell_argon_in_per_min={d} TOTAL_ARGON_IN_PER_MIN={pi//5+cli//5+d}")
PY
