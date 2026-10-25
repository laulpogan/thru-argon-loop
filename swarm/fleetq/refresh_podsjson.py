#!/usr/bin/env python3
"""Refresh ONE pod's runtime in runpod/pods.json from the live API (atomic replace). Usage: refresh_podsjson.py POD_ID"""
import json,os,sys,pathlib,urllib.request
F=pathlib.Path.home()/'cs-audit/gemini-hackathon/runpod'
def envfile(p):
    d={}
    for l in pathlib.Path(p).read_text().splitlines():
        l=l.strip().replace('export ','',1)
        if '=' in l and not l.startswith('#'):k,v=l.split('=',1);d[k.strip()]=v.strip().strip('"').strip("'")
    return d
KEY=envfile(os.path.expanduser('~/.config/runpod.env'))['RUNPOD_API_KEY']
q='query{pod(input:{podId:"%s"}){runtime{uptimeInSeconds ports{ip isIpPublic privatePort publicPort type}}}}'%sys.argv[1]
r=urllib.request.Request("https://api.runpod.io/graphql",json.dumps({"query":q}).encode(),{"content-type":"application/json","Authorization":"Bearer "+KEY,"User-Agent":"fleetq"})
rt=json.load(urllib.request.urlopen(r,timeout=60))['data']['pod']['runtime']
d=json.loads((F/'pods.json').read_text())
for p in d['pods']:
    if p['id']==sys.argv[1]:p['runtime']=rt;print('updated',p['name'],[x for x in rt['ports'] if x['privatePort']==22])
t=F/'pods.json.fleetq-tmp';t.write_text(json.dumps(d,indent=2));t.replace(F/'pods.json')
