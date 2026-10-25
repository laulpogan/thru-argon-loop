#!/usr/bin/env python3
"""fleetq monitor: refresh fleet-now.json every 60 s (dispatchers read endpoints from it); every 5 min append
busy/total/cost to FLEET.md (measurements table) and BOTTLENECKS.md. Read-only on the API."""
import json,os,pathlib,time,subprocess,sys
H=pathlib.Path.home()/'cs-audit/gemini-hackathon';F=H/'runpod/fleetq'
sys.path.insert(0,str(F));import fleet
def q(p):return {s:len(list((p/s).iterdir())) if (p/s).is_dir() else 0 for s in ('pending','running','done')}
last=0
while time.strftime('%H%M')<'1800':
    try:
        rows=fleet.summarize(fleet.fetch());t=F/'fleet-now.tmp'
        t.write_text(json.dumps(dict(t=time.strftime('%Y-%m-%dT%H:%M:%S%z'),pods=rows),indent=1));t.replace(F/'fleet-now.json')
        if time.time()-last>=290:
            last=time.time();run=[r for r in rows if r['status']=='RUNNING'];g=[r for r in run if r['gpu']];c=[r for r in run if not r['gpu']]
            b=sum(r['busy'] for r in run);pct=100*b/max(1,len(run))
            ov=q(H/'overflow/queue');af=q(H/'reset/assetfactory/queue');gq=q(F/'queue-gpu')
            line='| %s | %d/%d (%.0f%%) | %d/%d | %d/%d | $%.2f | overflow p%d r%d d%d; asset p%d r%d; gpu p%d r%d |'%(time.strftime('%H:%M'),b,len(run),pct,sum(r['busy'] for r in c),len(c),sum(r['busy'] for r in g),len(g),sum(r['cost'] for r in run),ov['pending'],ov['running'],ov['done'],af['pending'],af['running'],gq['pending'],gq['running'])
            idle=', '.join(r['name'].replace('thru-cpu-overflow-','cpu-') for r in run if not r['busy'])
            with open(F/'measurements.md','a') as f:f.write(line+'\n')
            with open(F/'idle-latest.txt','w') as f:f.write(time.strftime('%H:%M ')+idle+'\n')
            with open(H/'BOTTLENECKS.md','a') as f:f.write('\nFleet operator %s PT: busy %d/%d pods (%.0f%%; CPU %d/%d, GPU %d/%d), $%.2f/hr. Idle: %s\n'%(time.strftime('%H:%M'),b,len(run),pct,sum(r['busy'] for r in c),len(c),sum(r['busy'] for r in g),len(g),sum(r['cost'] for r in run),idle or '-'))
            fm=H/'runpod/FLEET.md'
            if fm.exists():
                s=fm.read_text();A,B='<!-- FLEETQ-MEASUREMENTS -->','<!-- /FLEETQ-MEASUREMENTS -->'
                if A in s and B in s:
                    pre,_,rest=s.partition(A);_,_,post=rest.partition(B)
                    body='\n| time PT | busy/total | CPU busy | GPU busy | $/hr | queues |\n|---|---|---|---|---|---|\n'+(F/'measurements.md').read_text()+'\nIdle at last measure: '+idle+'\n'
                    t=fm.with_suffix('.fleetq-tmp');t.write_text(pre+A+body+B+post);t.replace(fm)
    except Exception as e:open(F/'logs/monitor.log','a').write(time.strftime('%H:%M:%S ')+type(e).__name__+' '+str(e)[:200]+'\n')
    time.sleep(60)
