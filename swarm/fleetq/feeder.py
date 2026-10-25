#!/usr/bin/env python3
"""fleetq feeder: keeps reset/assetfactory/queue/pending topped up from MANIFEST.csv using the lane's own
controller.submit (same staging, state and receipts), hero-creek then desert then P0/P1/P2 first.
Takes controller.lock non-blocking per submit; if the lane controller holds it, skips that cycle. Stops at 17:30."""
import fcntl,json,pathlib,re,sys,time
H=pathlib.Path.home()/'cs-audit/gemini-hackathon';AF=H/'reset/assetfactory';sys.path.insert(0,str(AF))
import controller as C
LOW=int(sys.argv[1]) if len(sys.argv)>1 else 16;BATCH=2;CHUNK=12
CREEK=re.compile(r'creek|riparian|cobble|water|wash|willow|sycamore|alder|stream|seep|bosque|arroyo|meadow',re.I)
DESERT=re.compile(r'desert|sonoran|mojave|anza|socal|yucca|cactus|cholla|joshua|creosote|agave',re.I)
def score(r):
    t=' '.join([r.get('id',''),r.get('biome',''),r.get('real-world reference','')])
    return (0 if CREEK.search(t) else 1 if DESERT.search(t) else 2,{'P0':0,'P1':1}.get(r.get('priority'),2))
def log(m):open(H/'runpod/fleetq/logs/feeder.log','a').write(time.strftime('%H:%M:%S ')+m+'\n')
while time.strftime('%H%M')<'1730':
    pend=len(list((AF/'queue/pending').iterdir()))
    if pend<LOW:
        try:
            with open(AF/'controller.lock','w') as lock:
                fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
                state=json.loads(C.STATE.read_text()) if C.STATE.exists() else {'jobs':{},'started':C.stamp()}
                rows=C.readrows();known={i for j in state['jobs'].values() for i in j['ids']}
                todo=sorted([r for r in rows if r['id'] not in known and r['status'] in ('planned','planned-rebuild')],key=score)
                orig=C.save_rows;C.save_rows=lambda _r:orig(rows)
                try:n=C.submit(todo,state,BATCH,CHUNK)
                finally:C.save_rows=orig
                log(f'pending={pend} submitted {n} assets ({(n+BATCH-1)//BATCH} jobs); remaining={len(todo)-n}; first={[r["id"] for r in todo[:3]]}')
        except BlockingIOError:log('controller.lock held by lane controller; skip')
        except Exception as e:log(f'ERROR {type(e).__name__}: {str(e)[:300]}')
    time.sleep(30)
