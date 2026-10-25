#!/bin/bash
# Build the pod bundle for the moved swarm/council review jobs (Dell, nice 19 / idle IO). Read-only on sources.
H=~/cs-audit/gemini-hackathon; B=/tmp/swarm-bundle; mkdir -p $B/pr $B/row $B/asset
cd $H/swarm
python3 - <<'PY' > $B/todo.tsv
import os
H=os.path.expanduser('~/cs-audit/gemini-hackathon')
C=H+'/council'
models=['gemini-3.1-pro-preview','gemini-3.5-flash','gemini-3.6-flash','gemini-3.7-flash','gemini-3-flash-preview']
jobs=[l.split()[:2] for l in open(H+'/swarm/jobs.tsv') if l.strip()]
def done(p): return os.path.exists(p) and os.path.getsize(p)>0
# swarm (argon/flash) first
for k,i in jobs:
    if not done(f'{H}/swarm/{k}/{i}.md'): print('swarm',k,i,sep='\t')
for m in models:
    for k,i in jobs:
        if k in('pr','row') and not done(f'{C}/{m}/{k}/{i}.md'): print(m,k,i,sep='\t')
PY
cut -f2,3 $B/todo.tsv | sort -u > $B/needed.tsv
grep "^pr" $B/needed.tsv | cut -f2 | xargs -P 4 -I{} sh -c 'f='$B'/pr/{}; [ -s $f.diff ] || { nice -n 19 gh pr view {} -R laulpogan/Thru-2 --json number,title,state,author,body,comments,headRefName,baseRefName,files > $f.json 2>/dev/null; nice -n 19 gh pr diff {} -R laulpogan/Thru-2 > $f.diff 2>/dev/null; }'
python3 - "$B" <<'PY'
import json,os,sys,glob,shutil
B=sys.argv[1]; ids=[l.split()[1] for l in open(B+'/needed.tsv') if l.split()[0] in('row','asset')]
want=set(ids); Q=os.path.expanduser('~/gen3d/work')
with open(B+'/queue-lines.jsonl','w') as out:
    for line in open(Q+'/queue.jsonl',errors='replace'):
        try: i=json.loads(line).get('id')
        except Exception: continue
        if i in want: out.write(line)
for i in want:
    d=B+'/row/'+i; os.makedirs(d,exist_ok=True)
    m=Q+'/done/'+i+'.json'
    if os.path.exists(m): shutil.copy(m,d+'/done-marker.json')
    for src in glob.glob(os.path.expanduser('~/Documents/Codex/*/_trailboss/'+i)):
        for root,_,files in os.walk(src):
            for f in files:
                p=os.path.join(root,f)
                if f.endswith(('.md','.log','.json','.txt','.jsonl','.py','.gd')) and os.path.getsize(p)<300000:
                    rel=os.path.relpath(p,src); dst=os.path.join(d,'trailboss',rel); os.makedirs(os.path.dirname(dst),exist_ok=True); shutil.copy(p,dst)
PY
cp ~/Documents/Codex/thru-refs/PHOTO_GATE.md $B/ 2>/dev/null
cd /tmp && tar -cf - swarm-bundle | nice zstd -q -T2 -9 -o /tmp/swarm-bundle.tar.zst -f && echo BUNDLE_DONE $(date +%T) $(wc -l < $B/todo.tsv) jobs $(du -sh /tmp/swarm-bundle.tar.zst | cut -f1)
