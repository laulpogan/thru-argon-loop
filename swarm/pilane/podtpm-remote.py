import json,glob,os,time,datetime
W=300;now=time.time();pi_in=pi_cache=pi_n=0;ov_in=ov_n=0
for f in glob.glob('/root/.pi/agent/sessions/*/*.jsonl'):
    if now-os.path.getmtime(f)>W: continue
    for line in open(f,errors='replace'):
        if '"usage"' not in line: continue
        try: d=json.loads(line)
        except: continue
        ts=d.get('timestamp') or (d.get('message') or {}).get('timestamp')
        try:
            t=ts/1000 if isinstance(ts,(int,float)) else datetime.datetime.fromisoformat(str(ts).replace('Z','+00:00')).timestamp()
        except: continue
        if now-t>W: continue
        u=(d.get('message') or {}).get('usage') or d.get('usage') or {}
        pi_in+=u.get('input',0);pi_cache+=u.get('cacheRead',0);pi_n+=1
try:
    for line in open('/opt/overflow/calls.jsonl'):
        d=json.loads(line);t=datetime.datetime.strptime(d['ts'],'%Y-%m-%dT%H:%M:%S%z').timestamp()
        if now-t<=W and d.get('model')=='gemini-4-argon': ov_in+=((d.get('usage') or {}).get('promptTokenCount') or 0);ov_n+=1
except FileNotFoundError: pass
print(json.dumps({"pi_in":pi_in,"pi_cache":pi_cache,"pi_turns":pi_n,"argon_cli_in":ov_in,"argon_cli_calls":ov_n}))
