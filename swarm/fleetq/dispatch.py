#!/usr/bin/env python3
"""fleetq dispatcher: one process per pod, N slot threads. Each slot PULLS the next job (atomic rename claim) from
the shared queues in priority order, runs it on the pod, pulls out/ back, writes the same receipt format as
overflow/dispatcher.py into the source queue's done/. Loops until 17:45 PT. SSH-dead pod => job requeued, not failed.
No secrets cross SSH; Gemini comes only from the pod's API-injected PID1 env."""
import argparse,datetime,json,os,pathlib,shlex,subprocess,threading,time
H=pathlib.Path.home()/'cs-audit/gemini-hackathon';F=H/'runpod/fleetq'
QUEUES={'gpu':F/'queue-gpu','asset':H/'reset/assetfactory/queue','overflow':H/'overflow/queue'}
STOP='1745'
def stamp():return datetime.datetime.now().astimezone().isoformat()
def log(pod,msg):
    with open(F/'logs'/(pod+'.log'),'a') as f:f.write(time.strftime('%H:%M:%S ')+msg+'\n')
def endpoint(pid):
    p=next(x for x in json.loads((F/'fleet-now.json').read_text())['pods'] if x['id']==pid)
    if p['status']!='RUNNING' or not p['ssh']:raise RuntimeError('pod not running/ssh')
    ip,port=p['ssh'].split(':')
    opts=['-o','BatchMode=yes','-o','ServerAliveInterval=30','-o','ServerAliveCountMax=4','-o','StrictHostKeyChecking=accept-new','-o','UserKnownHostsFile='+str(F/'known_hosts'),'-o','ConnectTimeout=20','-o','ControlMaster=auto','-o','ControlPath=/tmp/fq-%C','-o','ControlPersist=600','-i',str(pathlib.Path.home()/'.ssh/id_ed25519'),'-p',port]
    return p,['ssh',*opts],'root@'+ip
import re
CREEK=re.compile(r'creek|riparian|cobble|water|wash|willow|sycamore|alder|stream|seep|bosque|arroyo',re.I)
DESERT=re.compile(r'desert|sonoran|mojave|anza|socal|yucca|cactus|cholla|joshua|creosote|agave',re.I)
_pc={}
def prio(job):
    # hero-creek assets first, then desert, then submission order
    if job.name not in _pc:
        try:t=(job/'assets.json').read_text()[:200000];_pc[job.name]=0 if CREEK.search(t) else 1 if DESERT.search(t) else 2
        except OSError:_pc[job.name]=2
    return (_pc[job.name],job.name)
def claim(order,gpu,has_godot):
    for name in order:
        q=QUEUES[name];pend=q/'pending'
        if not pend.is_dir():continue
        for job in sorted(pend.iterdir(),key=prio):
            if name=='overflow':
                try:meta=json.loads((job/'job.json').read_text())
                except Exception:continue
                if meta.get('gpu') and not gpu:continue
                try:
                    if not has_godot and 'godot' in (job/'run.sh').read_text(errors='ignore'):continue
                except OSError:continue  # claimed by another slot meanwhile (line keeper fix 14:53)
            act=q/'running'/job.name
            try:job.rename(act);return name,act
            except (FileNotFoundError,OSError):continue
    return None,None
def run_job(pid,slot,gpu,qname,act):
    pod,ssh,host=endpoint(pid);transport=shlex.join(ssh);remote='/opt/overflow/jobs/'+act.name
    receipt=dict(id=act.name,pod=pod['name'],pod_id=pid,started=stamp(),status='failed',dispatcher='fleetq',slot=slot,queue=qname)
    t0=time.monotonic()
    meta=json.loads((act/'job.json').read_text());limit=max(1,min(7200,int(meta.get('timeout',900))))
    r=subprocess.run(ssh+[host,'mkdir -p '+remote+'/out'],timeout=60)
    if r.returncode==255:return 'requeue',None
    subprocess.run(['rsync','-a','--no-links','-e',transport,str(act)+'/',host+':'+remote+'/'],check=True,timeout=900)
    pre=''
    if gpu:pre="sed -i \"s/scene.cycles.device='CPU'/scene.cycles.device=__import__('fleetq_gpu').enable()/\" blender_driver.py 2>/dev/null; "
    cmd='cd '+remote+' && mkdir -p out && '+pre+'timeout --signal=TERM --kill-after=30 '+str(limit)+' env OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 bash run.sh > out/stdout.log 2> out/stderr.log; rc=$?; printf "%s\\n" "$rc" > out/exit-code; exit "$rc"'
    try:receipt['exit_code']=subprocess.run(ssh+[host,cmd],timeout=limit+180).returncode
    except subprocess.TimeoutExpired:receipt['exit_code']=124;receipt['error']='ssh timeout'
    pull=subprocess.run(['rsync','-a','--no-links','-e',transport,host+':'+remote+'/out/',str(act/'out')+'/'],timeout=900)
    receipt['pull_exit']=pull.returncode
    if receipt['exit_code']==255 and pull.returncode!=0:return 'requeue',None
    subprocess.run(['rsync','-a','--no-links','-e',transport,host+':/opt/overflow/calls.jsonl',str(H/'overflow'/('remote-calls-'+pid+'.jsonl'))],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=60)
    receipt['status']='done' if receipt['exit_code']==0 and pull.returncode==0 else 'failed'
    receipt.update(finished=stamp(),elapsed_seconds=round(time.monotonic()-t0,2))
    return 'done',receipt
def slot_loop(pid,slot,gpu,order,has_godot,name):
    while time.strftime('%H%M')<STOP:
        try:qname,act=claim(order,gpu,has_godot)
        except OSError:time.sleep(2);continue
        if not act:time.sleep(10);continue
        log(name,f'slot{slot} CLAIM {qname}/{act.name}')
        try:status,receipt=run_job(pid,slot,gpu,qname,act)
        except Exception as e:status,receipt='requeue',None;log(name,f'slot{slot} ERROR {type(e).__name__}: {str(e)[:200]}')
        q=QUEUES[qname]
        if status=='requeue':
            try:act.rename(q/'pending'/act.name);log(name,f'slot{slot} REQUEUE {act.name}')
            except OSError:pass
            time.sleep(30);continue
        (act/'receipt.json').write_text(json.dumps(receipt,indent=2));act.rename(q/'done'/act.name)
        log(name,f"slot{slot} {receipt['status']} {act.name} rc={receipt.get('exit_code')} {receipt.get('elapsed_seconds')}s")
def bootstrap(pid,name):
    pod,ssh,host=endpoint(pid);transport=shlex.join(ssh)
    subprocess.run(ssh+[host,'mkdir -p /opt/fleetq /opt/overflow/jobs'],check=True,timeout=60)
    for src,dst in [(F/'pod-bootstrap.sh','pod-bootstrap.sh'),(F/'fleetq_gpu.py','fleetq_gpu.py'),(H/'overflow/argon-pod.py','argon')]:
        subprocess.run(['rsync','-a','-e',transport,str(src),host+':/opt/fleetq/'+dst],check=True,timeout=120)
    r=subprocess.run(ssh+[host,'bash /opt/fleetq/pod-bootstrap.sh > /opt/fleetq/bootstrap.log 2>&1; rc=$?; tail -1 /opt/fleetq/bootstrap.log; exit $rc'],capture_output=True,text=True,timeout=1200)
    log(name,'BOOTSTRAP rc=%d %s'%(r.returncode,r.stdout.strip()[-300:]));return (r.returncode==0 and r.stdout.strip().startswith('v4')),r.stdout
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('pod_id');a.add_argument('--slots',type=int,default=4);a.add_argument('--queues',default='asset,overflow');a=a.parse_args()
    (F/'logs').mkdir(exist_ok=True)
    p=next(x for x in json.loads((F/'fleet-now.json').read_text())['pods'] if x['id']==a.pod_id);name=p['name'];gpu=bool(p['gpu'])
    for attempt in range(20):
        try:ok,info=bootstrap(a.pod_id,name)
        except Exception as e:ok,info=False,str(e)
        if ok:break
        log(name,'bootstrap not ready; retry in 60s');time.sleep(60)
    else:raise SystemExit('bootstrap failed')
    if 'gemini_env=0' in info:log(name,'NO GEMINI ENV: Argon jobs excluded; gpu queue only');order=['gpu'] if gpu else []
    else:order=(['gpu'] if gpu else [])+a.queues.split(',')
    if not order:raise SystemExit('nothing runnable')
    has_godot='godot=none' not in info
    ts=[threading.Thread(target=slot_loop,args=(a.pod_id,i,gpu,order,has_godot,name),daemon=True) for i in range(1,a.slots+1)]
    for t in ts:t.start();time.sleep(2)
    log(name,f'STARTED slots={a.slots} gpu={gpu} order={order}')
    for t in ts:t.join()
