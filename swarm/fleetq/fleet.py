#!/usr/bin/env python3
"""Read-only fleet snapshot. Key read from env only; never printed."""
import json, os, sys, urllib.request, time
Q='query { myself { pods { id name desiredStatus costPerHr machine { gpuDisplayName } gpuCount vcpuCount runtime { uptimeInSeconds ports { ip publicPort privatePort type } container { cpuPercent memoryPercent } gpus { gpuUtilPercent memoryUtilPercent } } } } }'
def fetch():
    req=urllib.request.Request('https://api.runpod.io/graphql',data=json.dumps({'query':Q}).encode(),headers={'Authorization':'Bearer '+os.environ['RUNPOD_API_KEY'],'Content-Type':'application/json','User-Agent':'trailboss-fleetq'})
    with urllib.request.urlopen(req,timeout=45) as r: return json.load(r)['data']['myself']['pods']
def summarize(pods):
    rows=[]
    for p in pods:
        r=p.get('runtime') or {}
        c=(r.get('container') or {}).get('cpuPercent') or 0
        g=[x.get('gpuUtilPercent') or 0 for x in (r.get('gpus') or [])]
        ssh=[f"{x['ip']}:{x['publicPort']}" for x in (r.get('ports') or []) if x.get('privatePort')==22 and x.get('type')=='tcp']
        busy=c>30 or any(v>30 for v in g)
        rows.append(dict(id=p['id'],name=p['name'],status=p['desiredStatus'],cost=p['costPerHr'],gpu=(p.get('machine') or {}).get('gpuDisplayName') if p['gpuCount'] else None,vcpu=p['vcpuCount'],cpu=c,gpus=g,ssh=ssh[0] if ssh else None,up=r.get('uptimeInSeconds'),busy=busy))
    return sorted(rows,key=lambda x:x['name'])
if __name__=='__main__':
    rows=summarize(fetch())
    out=os.path.expanduser('~/cs-audit/gemini-hackathon/runpod/fleetq/fleet-now.json')
    json.dump(dict(t=time.strftime('%Y-%m-%dT%H:%M:%S%z'),pods=rows),open(out,'w'),indent=1)
    run=[r for r in rows if r['status']=='RUNNING']
    for r in rows: print(r['id'],r['name'],r['status'],r['cost'],r['gpu'],r['vcpu'],'cpu=%s'%r['cpu'],'gpu=%s'%r['gpus'],r['ssh'],'BUSY' if r['busy'] else 'idle')
    gp=[r for r in run if r['gpu']];cp=[r for r in run if not r['gpu']]
    print('RUNNING',len(run),'busy',sum(r['busy'] for r in run),'| CPU %d/%d GPU %d/%d | $/h %.3f'%(sum(r['busy'] for r in cp),len(cp),sum(r['busy'] for r in gp),len(gp),sum(r['cost'] for r in run)))
