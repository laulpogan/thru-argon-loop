#!/usr/bin/env python3
"""podenv.py POD_ID EXPECTED_NAME [--add-gemini] : re-apply pod env via podEditJob (container restarts). Never prints values."""
import json,os,sys,pathlib,urllib.request
def envfile(p):
    d={}
    for l in pathlib.Path(p).read_text().splitlines():
        l=l.strip().replace('export ','',1)
        if '=' in l and not l.startswith('#'):k,v=l.split('=',1);d[k.strip()]=v.strip().strip('"').strip("'")
    return d
KEY=envfile(os.path.expanduser('~/.config/runpod.env'))['RUNPOD_API_KEY']
def gql(q):
    r=urllib.request.Request("https://api.runpod.io/graphql",json.dumps({"query":q}).encode(),{"content-type":"application/json","Authorization":"Bearer "+KEY,"User-Agent":"fleetq"})
    return json.load(urllib.request.urlopen(r,timeout=60))
pid,name=sys.argv[1],sys.argv[2]
p=gql('query{pod(input:{podId:"%s"}){name imageName containerDiskInGb volumeInGb ports env}}'%pid)["data"]["pod"]
assert p["name"]==name,"name mismatch"
env={k:v.strip() for k,_,v in (e.partition("=") for e in p["env"])}
env["NVIDIA_DRIVER_CAPABILITIES"]="all"
if '--add-gemini' in sys.argv: env["GEMINI_API_KEY"]=envfile(os.path.expanduser('~/.config/gemini/hackathon.env'))["GEMINI_API_KEY"]
env.pop("RUNPOD_API_KEY",None)
e=",".join("{key:%s,value:%s}"%(json.dumps(k),json.dumps(v)) for k,v in env.items())
m='mutation{podEditJob(input:{podId:"%s",imageName:%s,containerDiskInGb:%d,volumeInGb:%d,ports:%s,env:[%s]}){id desiredStatus}}'%(pid,json.dumps(p["imageName"]),p["containerDiskInGb"],p["volumeInGb"],json.dumps(p["ports"]),e)
r=gql(m);print(json.dumps(r.get("data")) if "data" in r and r["data"] else "ERROR "+json.dumps(r.get("errors"))[:300],"env_keys=",sorted(env))
