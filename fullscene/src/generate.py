#!/usr/bin/env python3
"""Heightmap + trail -> deterministic biome instances, paths and world-pack placements."""
import os,sys,json,math,hashlib,pathlib
ROOT=pathlib.Path(os.environ.get('FULLSCENE_ROOT','/workspace/fullscene'))
sys.argv=[str(ROOT/'src/terrain.py'),str(ROOT/'assets')]
exec(compile((ROOT/'src/terrain.py').read_text(),str(ROOT/'src/terrain.py'),'exec'))
from scipy.interpolate import RegularGridInterpolator
ZI=RegularGridInterpolator((ys,xs),Z)
def zf(x,y):return float(ZI([[np.clip(y,-W/2,W/2),np.clip(x,-L/2,L/2)]])[0])
def dw(x,y):return abs(y-float(center(x)))-float(halfw(x))
config=json.load(open(ROOT/'config/sierra.json'));seed=int(os.environ.get('SCENE_SEED',config['seed']));r=np.random.default_rng(seed)
library=json.load(open(ROOT/'library/library.json'));ids={v['asset_id'] for v in library['rows'] if v.get('library_file')}
fol={};inst=[];life=[];trees=[];tiles=[];stats={}
# Visibility corridors derive from the bridge/trail cameras, not hand-placed vegetation.
views=[([9,float(center(9))+.8],[-3,float(center(-3))]),([5.5,-4.6],[0,-1.6]),([-8,-17],[0,-3]),([0,-16],[-3,1.5])]
def view_distance(x,y):
 p=np.array([x,y]);best=1e9
 for a,b in views:
  a=np.array(a);v=np.array(b)-a;t=np.clip(np.dot(p-a,v)/np.dot(v,v),0,1);best=min(best,float(np.linalg.norm(p-a-t*v)))
 return best

# Small recentered tiles preserve float precision and make imported bounds a decisive gate.
for j in range(4):
 for i in range(4):
  sl=(slice(j*64,(j+1)*64+1),slice(i*64,(i+1)*64+1));xx,yy,zz=X[sl],Y[sl],Z[sl];cx=float(xx.mean());cy=float(yy.mean());cz=float((zz.min()+zz.max())/2);name=f'tile_{i}_{j}'
  m=grid_mesh(xx-cx,yy-cy,zz-cz,np.c_[xx.ravel()/4,yy.ravel()/4]);save(name,[m]);tiles.append(dict(mesh=name,pos=[cx,cy,cz],bounds_m=m.bounds.tolist()))
# Field gradients and clustering are independent of draw order.
phase=r.uniform(0,math.tau,3)
def fields(x,y):
 gx=(zf(x+.3,y)-zf(x-.3,y))/.6;gy=(zf(x,y+.3)-zf(x,y-.3))/.6
 slope=math.degrees(math.atan(math.hypot(gx,gy)));aspect=math.atan2(-gy,-gx)
 shade=max([math.exp(-((x-t[0])**2+(y-t[1])**2)/40)*.9 for t in trees] or [0])
 cl=.5+.24*math.sin(x*.22+phase[0])*math.cos(y*.24+phase[1])+.2*math.sin(x*.66+y*.37+phase[2])
 return slope,aspect,shade,max(.05,cl)
def add(sp,x,y,z,scale,yaw,kind,sz=1,age='mature'):
 row=[round(x,3),round(y,3),round(z,3),round(yaw,2),round(scale,3),0,0,round(sz,3)]
 if sp in ('jeffrey','red_fir','white_fir') or sp.startswith('hg_'):fol.setdefault(sp,[]).append(row)
 elif kind in ('butterfly','critter','bird','insect'):life.append(dict(asset_id=sp,kind=kind,anchor_m=[x,y,z],scale=scale,phase=float(r.uniform(0,math.tau))))
 else:inst.append(dict(asset_id=sp,kind=kind,transform=row,age=age))
for rule in config['strata']:
 names=rule.get('assets',[rule.get('asset_id')]);names=[a for a in names if a in ids or a in ('jeffrey','red_fir','white_fir') or a.startswith('hg_')]
 if not names:raise RuntimeError('No source meshes for '+rule['id'])
 n=0;attempts=0
 while n<rule['count'] and attempts<rule['count']*120:
  attempts+=1;x=float(r.uniform(-L/2+.5,L/2-.5));y=float(r.uniform(-W/2+.5,W/2-.5));z=zf(x,y);water=dw(x,y);trail=float(trail_dist(x,y));slope,aspect,shade,cl=fields(x,y)
  # Bridge is the sole authored structure; its safety envelope applies to every layer.
  if abs(x)<1.4 and abs(y)<BRIDGE_HALF+.4:continue
  values=[(config['elevation_origin_m']+z,rule['height_m']),(slope,rule['slope_deg']),(water,rule['water_m']),(trail,rule['trail_m']),(shade,rule['shade'])]
  if any(not lo<=v<=hi for v,(lo,hi) in values):continue
  probability=(1-rule['cluster'])+rule['cluster']*cl
  probability*=max(.1,1+rule['aspect_bias']*math.cos(aspect))
  if r.random()>probability:continue
  if rule['id'] in ('jeffrey','red_fir','white_fir'):
   if view_distance(x,y)<5.0:continue
   if any((x-t[0])**2+(y-t[1])**2<3.7**2 for t in trees):continue
   # All cameras derive from paths. A trunk-free trail corridor also protects the walk.
   trees.append((x,y))
  if rule['id']=='granite' and view_distance(x,y)<2.8:continue
  if rule['id'] in ('butterfly','critter') and any((x-v['transform'][0])**2+(y-v['transform'][1])**2<3.5**2 for v in inst if v['kind']=='granite'):continue
  sp=names[int(r.integers(len(names)))];scale=float(r.uniform(*rule['scale']));scale*=.65 if rule['id']=='granite' else 1;age='mature';sz=1
  if rule.get('age_mix') and r.random()<rule['age_mix']['sapling']:scale*=float(r.uniform(.18,.34));age='sapling'
  if rule['id']=='grass':sz=float(r.uniform(.55,.9));z-=.04
  if rule['id']=='granite':z-=scale*.18
  if rule['id']=='butterfly':z+=float(r.uniform(.35,1.05))
  if rule['id']=='bird':z+=float(r.uniform(5,12))
  if rule['id']=='insect':z+=float(r.uniform(.3,1.4))
  add(sp,x,y,z,scale,float(r.uniform(0,360)),rule['id'],sz,age);n+=1
 stats[rule['id']]=dict(accepted=n,requested=rule['count'],attempts=attempts)
# Outer forest grows on the same heightmap/skirt producer; deterministic, no art-directed rows.
for _ in range(650):
 x=float(r.uniform(-270,270));y=float(r.uniform(-210,210))
 if abs(x)<L/2 and abs(y)<W/2:continue
 sp=['jeffrey','red_fir','white_fir'][int(r.integers(3))];add(sp,x,y,float(_SZ([[x,y]])[0])-.15,float(r.uniform(.7,1.15)),float(r.uniform(0,360)),'tree')
# A modest procedural camp on a terrace: no logos or new hand-authored coordinates.
prop_ids=[a for a in ids if any(t in a.lower() for t in ['trail_marker','tent_dome','campfire_ring','fallen_log'])][:4]
for a in prop_ids:
 for _ in range(1000):
  x=float(r.uniform(-30,30));y=float(r.uniform(-25,25))
  if 3<dw(x,y)<18 and 3<float(trail_dist(x,y))<7 and fields(x,y)[0]<15:
   add(a,x,y,zf(x,y),1,float(r.uniform(0,360)),'prop');break
# Cameras are derived from the bridge, spline and generated life anchors.
def cam(name,pos,tgt,fl):
 pos=list(map(float,pos));pos[2]=max(pos[2],zf(pos[0],pos[1])+.35)
 return dict(name=name,pos=pos,tgt=list(map(float,tgt)),fl=fl)
shots=[cam('hero_low',[9,float(center(9))+.8,float(zw(9))+.9],[-3,float(center(-3)),DECK+.25],24),cam('hiker',[5.5,-4.6,DECK+1.5],[0,-1.6,DECK+1.1],35),cam('trail',[-8,-17,zf(-8,-17)+1.7],[0,-3,DECK+.7],26),cam('wide',[0,-16,max(zf(0,-16),DECK)+9],[-3,1.5,DECK],24)]
for name,kind in [('butterflies','butterfly'),('critters','critter')]:
 candidates=[v for v in life if v['kind']==kind]
 if not candidates:raise RuntimeError('No '+kind+' habitat accepted; inspect rule statistics: '+str(stats))
 v=min(candidates,key=lambda v:np.linalg.norm(np.array(v['anchor_m'][:2])-np.array([5,-5])));p=np.array(v['anchor_m']);offset=np.array([.6,-1.05,.4]) if kind=='butterfly' else np.array([1.1,-1.6,.55]);shots.append(cam(name,p+offset,p+[0,0,.08],45))
# First person walk follows the trail at 1.1 m/s; sampled every 6 frames, 18 seconds.
seg=np.linalg.norm(np.diff(TRAIL,axis=0),axis=1);cum=np.r_[0,np.cumsum(seg)];bridge_index=int(np.argmin(np.linalg.norm(TRAIL,axis=1)));start=max(0,float(cum[bridge_index])-11)
def point(s):
 i=int(np.clip(np.searchsorted(cum,s)-1,0,len(seg)-1));t=float(np.clip((s-cum[i])/seg[i],0,1));return TRAIL[i]*(1-t)+TRAIL[i+1]*t
walk=[];steps=[]
for f in range(0,433,6):
 s=min(start+f/24*1.1,float(cum[-1])-.1);p=point(s);ahead=point(min(s+3,float(cum[-1])-.01));on=abs(p[0])<.8 and abs(p[1])<BRIDGE_HALF+.2;z=DECK if on else zf(*p)
 walk.append(dict(f=f,pos=[float(p[0]),float(p[1]),z+1.67],tgt=[float(ahead[0]),float(ahead[1]),z+1.5]))
 if f%12==0:steps.append(dict(time=f/24,surface='wood' if on else 'gravel' if dw(*p)<4 else 'dirt',pos_m=[float(p[0]),float(p[1]),z]))
height_probes=[[float(X[j,i]),float(Y[j,i]),float(Z[j,i])] for j,i in [(84,94),(110,145),(143,117),(166,146),(122,190)]]
pl=dict(height_probes=height_probes,meshes=[dict(mesh='bridge',x=0,y=0,z=0,yaw=0,s=1,kind='bridge'),dict(mesh='skirt',x=0,y=0,z=0,yaw=0,s=1,kind='skirt')],tiles=tiles,instances=inst,foliage=fol,life=life,shots=shots,walk=walk,walk_frames=432,walk_fps=24,hiker_still=[0,-1.6,DECK],hiker_walk=[],water_z0=float(zw(0)),slope=P['slope'],L=L,W=W,deck_z=DECK,seed=seed,statistics=stats,steps=steps,trail_m=TRAIL.tolist())
json.dump(pl,open(ROOT/'assets/placements.json','w'))
# Explicit world-pack v2 export includes every procedural layer.
from worldpack import export_scene,import_instances
wp=export_scene(pl,config['elevation_origin_m'])
assert len(import_instances(wp))==len(inst)+sum(map(len,fol.values()))+len(life)
json.dump(wp,open(ROOT/'out/worldpack-placements.json','w'));json.dump(dict(seed=seed,statistics=stats,tiles=len(tiles),foliage={k:len(v) for k,v in fol.items()},instances=len(inst),life=len(life),placement_sha256=hashlib.sha256(json.dumps(pl,sort_keys=True).encode()).hexdigest()),open(ROOT/'out/generation.json','w'),indent=2)
print('GENERATED',seed,stats)
