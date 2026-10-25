#!/usr/bin/env python3
"""pilane queue bridge (Dell, light): pod lanes write job dirs to /work/lanes/<lane>/jobs-out/<name>/ (run.sh + inputs; run.sh writes results to ./out/;
a file named GPU marks a GPU job). pilane/sync.sh pulls them to reset/<lane>/pod/jobs-out/. This submits each new one to the shared fleet queue
(CPU: overflow/submit.sh; GPU: runpod/fleetq/queue-gpu/pending/ with job.json gpu=true), and when done copies out/ back to
reset/<lane>/job-results/<name>/ and pushes it to the pod's /work/lanes/<lane>/job-results/<name>/."""
import json,os,pathlib,shutil,subprocess,time,uuid,datetime
H=pathlib.Path.home()/'cs-audit/gemini-hackathon'; P=H/'pilane'; ST=P/'bridge-state.json'
state=json.loads(ST.read_text()) if ST.exists() else {}
GQ=H/'runpod/fleetq/queue-gpu'
def lanes():
    m={}
    for l in (P/'lanes.tsv').read_text().split('\n'):
        f=l.split()
        if len(f)==4: m[f[0]]=f
    return m
def log(s):
    with open(P/'bridge.log','a') as f: f.write(time.strftime('%H:%M:%S ')+s+'\n')
while time.strftime('%H%M')<'1800':
    L=lanes()
    for lane in L:
        jo=H/'reset'/lane/'pod/jobs-out'
        if not jo.is_dir(): continue
        for j in sorted(jo.iterdir()):
            key=lane+'/'+j.name
            if key in state or not (j/'run.sh').is_file() or not (j/'READY').exists(): continue
            stage=pathlib.Path('/tmp/pilane-stage')/lane/j.name
            if stage.exists(): shutil.rmtree(stage)
            shutil.copytree(j,stage,ignore=shutil.ignore_patterns('out','READY'))
            try:
                if (j/'GPU').exists():
                    jid=datetime.datetime.now().strftime('%H%M%S')+'-'+uuid.uuid4().hex[:10]
                    tmp=GQ/('.submit-'+jid); shutil.copytree(stage,tmp)
                    (tmp/'job.json').write_text(json.dumps(dict(id=jid,gpu=True,lane=lane,source=str(stage),timeout=1800)))
                    tmp.rename(GQ/'pending'/jid); state[key]={'q':'gpu','id':jid}
                else:
                    jid=subprocess.run([str(H/'overflow/submit.sh'),str(stage),'--timeout','1800'],capture_output=True,text=True,check=True).stdout.strip().split()[-1]
                    state[key]={'q':'overflow','id':jid}
                log('submitted %s -> %s'%(key,state[key]))
            except Exception as e:
                state[key]={'err':str(e)[:300]}; log('submit FAIL %s %s'%(key,e))
    for key,v in state.items():
        if 'id' not in v or v.get('back'): continue
        base=GQ if v['q']=='gpu' else H/'overflow/queue'
        for st in ('done','failed'):
            d=base/st/v['id']
            if d.is_dir():
                lane,name=key.split('/',1); dst=H/'reset'/lane/'job-results'/name
                if dst.exists(): shutil.rmtree(dst)
                shutil.copytree(d,dst,ignore=shutil.ignore_patterns('game','*.zst','*.tar'))
                (dst/'STATUS').write_text(st+'\n')
                f=L.get(lane)
                if f:
                    e='ssh -o BatchMode=yes -o ConnectTimeout=15 -o UserKnownHostsFile=%s -p %s'%(H/'overflow/known_hosts',f[3])
                    subprocess.run(['nice','rsync','-az','--max-size=300m','-e',e,str(dst)+'/','root@%s:/work/lanes/%s/job-results/%s/'%(f[2],lane,name)],capture_output=True)
                v['back']=st; log('returned %s (%s)'%(key,st)); break
    ST.write_text(json.dumps(state,indent=1))
    time.sleep(60)
