import os
# Procedural geometry + tileable textures for THRU UE5 Sierra creek spike. Z-up meters, exported as glb (Y-up).
import numpy as np, trimesh, json, os, sys, math
from PIL import Image
from scipy import ndimage
rng=np.random.default_rng(7)
OUT=sys.argv[1] if len(sys.argv)>1 else "assets"; os.makedirs(OUT,exist_ok=True)
P=json.load(open(os.path.join(os.path.dirname(__file__),"params.json")))["geo"]
P["res"]=257
def to_y_up(m):
    R=np.array([[1,0,0,0],[0,0,1,0],[0,-1,0,0],[0,0,0,1]],float); m.apply_transform(R); return m
def save(name,meshes):
    sc=trimesh.Scene()
    for i,m in enumerate(meshes): sc.add_geometry(to_y_up(m.copy()),geom_name=f"{name}_{i}")
    sc.export(os.path.join(OUT,name+".glb"))
def fbm2(n,octs=6,seed=0,base=4):
    r=np.random.default_rng(seed); acc=np.zeros((n,n))
    amp=1
    for o in range(octs):
        f=base*2**o; g=r.standard_normal((f+1,f+1)); g[-1,:]=g[0,:]; g[:,-1]=g[:,0]
        z=ndimage.zoom(g[:-1,:-1],n/f,order=3,mode='grid-wrap'); acc+=amp*z[:n,:n]; amp*=0.5
    return (acc-acc.min())/(np.ptp(acc)+1e-9)
# ---------- terrain ----------
L,W,N=P["len"],P["wid"],P["res"]
xs=np.linspace(-L/2,L/2,N); ys=np.linspace(-W/2,W/2,N); X,Y=np.meshgrid(xs,ys,indexing='xy')
REALD=os.environ.get("REAL_DIR","/workspace/fullscene/real")
REAL=os.path.exists(f"{REALD}/heightmap_bridge_frame_1009.raw") and os.environ.get("NO_REAL")!="1"
if REAL:
    from scipy.spatial import cKDTree
    from scipy.ndimage import gaussian_filter1d, map_coordinates
    _H=json.load(open(f"{REALD}/heightmap.json"))["variants"]["heightmap_bridge_frame_1009"]
    _u=np.fromfile(f"{REALD}/heightmap_bridge_frame_1009.raw",dtype="<u2").reshape(1009,1009)
    HREAL=_H["min_height_m"]+_u/65535*_H["height_range_m"]-2347.261
    def hreal(x,y): return map_coordinates(HREAL,[np.clip((np.asarray(y)+126)/0.25,0,1008),np.clip((np.asarray(x)+126)/0.25,0,1008)],order=1,mode="nearest")
    _cp=np.array([p["local_m"] for p in json.load(open(f"{REALD}/creek_spline.json"))["resampled_1m_points"]])
    _cp=_cp[(np.abs(_cp[:,0])<200)]
    _cp[:,0]=gaussian_filter1d(_cp[:,0],3,mode="nearest"); _cp[:,1]=gaussian_filter1d(_cp[:,1],3,mode="nearest")
    _wz=gaussian_filter1d(_cp[:,2],8,mode="nearest")
    if _cp[0,0]>_cp[-1,0]: _cp=_cp[::-1]; _wz=_wz[::-1]
    _wz=np.minimum.accumulate(_wz)    # water only ever flows downhill (+x, verified NHD/D8 direction)
    _wz=_wz-np.interp(0,_cp[:,0],_wz)-0.13   # water 1.15 m under the deck at the crossing
    _seg=np.linspace(0,1,len(_cp)); _dense=np.linspace(0,1,len(_cp)*4)
    CP=np.c_[np.interp(_dense,_seg,_cp[:,0]),np.interp(_dense,_seg,_cp[:,1])]; CWZ=np.interp(_dense,_seg,_wz)
    _kd=cKDTree(CP)
    HW_REAL=1.45
    def center(x): return np.interp(x,CP[:,0],CP[:,1])
    def halfw(x): return HW_REAL+0.25*np.sin(np.asarray(x,float)/7.1)
    def zw_real(x): return np.interp(x,CP[:,0],CWZ)
    _dd,_ii=_kd.query(np.c_[X.ravel(),Y.ravel()]); d=_dd.reshape(X.shape); WZG=CWZ[_ii].reshape(X.shape); hw=halfw(X)
    print("REAL terrain on; creek pts",len(CP))
else:
    def center(x): return P["meander"]*np.sin(x/11.0)+1.2*np.sin(x/4.3+1)
    def halfw(x): return P["halfw"]+0.8*np.sin(x/7.1)
    d=np.abs(Y-center(X)); hw=halfw(X)
n1=fbm2(N,6,1,3); n2=fbm2(N,5,2,12)
bank=np.clip((d-hw)/6.0,0,1)
Z=-P["depth"]*np.clip(1-(d/hw)**2,0,1) + bank**1.4*P["bankh"] + (n1-0.5)*1.6*bank + (n2-0.5)*0.12
Z+=np.clip((np.abs(Y)-W*0.3)/(W*0.2),0,1)**2*6  # rising valley walls
Z+= -X*P["slope"]  # downhill toward -x? flow toward +x lower
if REAL:
    Zr=hreal(X,Y)
    prof=np.where(d<hw, WZG-0.42*np.clip(1-(d/hw)**2,0,1)-0.02, WZG+0.22+(d-hw)*0.32+(n1-0.5)*0.5*np.clip((d-hw)/4,0,1))
    wbl=np.clip((d-hw)/7.0,0,1); wbl=wbl*wbl*(3-2*wbl)
    Z=prof*(1-wbl)+Zr*wbl+(n2-0.5)*0.08
    Z=np.where(d>hw+0.3,np.maximum(Z,WZG+0.18),Z)
# ---- real THRU route (Godot route-hero-after.json), mapped to local frame: origin = bridge centre, +y along bridge, +x along creek
RT=json.load(open(os.path.join(OUT,"route-hero-after.json")))
BC=np.array([3049.5,6249.8]); BAX=np.array([0.865,-0.503]); CAX=np.array([0.503,0.865])
wp=np.array([[p[0],p[2]] for p in RT["waypoints"]])-BC
loc=np.c_[wp@CAX, wp@BAX]
d0=loc[0]-loc[1]; d0/=np.linalg.norm(d0); d1=loc[-1]-loc[-2]; d1/=np.linalg.norm(d1)
ctrl=np.r_[[loc[0]+d0*14,loc[0]+d0*7],loc,[loc[-1]+d1*6,loc[-1]+d1*12]]
def catmull(P_,step=0.4):
    pts=[]; Q=np.r_[[P_[0]],P_,[P_[-1]]]
    for i in range(1,len(Q)-2):
        p0,p1,p2,p3=Q[i-1],Q[i],Q[i+1],Q[i+2]; n=max(2,int(np.linalg.norm(p2-p1)/step))
        for t in np.linspace(0,1,n,endpoint=False):
            t2,t3=t*t,t*t*t; pts.append(0.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t2+(-p0+3*p1-3*p2+p3)*t3))
    pts.append(P_[-1]); return np.array(pts)
TRAIL=catmull(ctrl)
BRIDGE_HALF=6.8
onb=np.abs(TRAIL[:,1])<BRIDGE_HALF+0.3; TRAIL[onb,0]=0.0   # keep the hiker on the deck centreline
TRAIL=TRAIL[np.r_[True,np.linalg.norm(np.diff(TRAIL,axis=0),axis=1)>1e-3]]
def trail_dist(px,py):
    px=np.asarray(px,float); py=np.asarray(py,float); best=np.full(np.broadcast(px,py).shape,1e9)
    for (ax,ay),(bx,by) in zip(TRAIL[:-1],TRAIL[1:]):
        dx,dy=bx-ax,by-ay; t=np.clip(((px-ax)*dx+(py-ay)*dy)/(dx*dx+dy*dy),0,1); best=np.minimum(best,np.hypot(px-ax-t*dx,py-ay-t*dy))
    return best
td=trail_dist(X,Y); Z-= 0.10*np.clip(1-td/1.0,0,1)
# keep the bridge abutments as a firm level-ish bank
Z=np.where((np.abs(X)<2.2)&(np.abs(Y-center(X))>halfw(X))&(np.abs(Y-center(X))<halfw(X)+3.5),np.maximum(Z,-P["depth"]+P["water_h"]-X*P["slope"]+0.9),Z)
def grid_mesh(X,Y,Z,uvs):
    n,m=X.shape; v=np.c_[X.ravel(),Y.ravel(),Z.ravel()]
    i=np.arange(n*m).reshape(n,m); a=i[:-1,:-1].ravel();b=i[:-1,1:].ravel();c=i[1:,1:].ravel();dd=i[1:,:-1].ravel()
    f=np.r_[np.c_[a,b,c],np.c_[a,c,dd]]
    me=trimesh.Trimesh(v,f,process=False); me.visual=trimesh.visual.TextureVisuals(uv=uvs); return me
uv=np.c_[X.ravel()/4.0,Y.ravel()/4.0]
save("terrain",[grid_mesh(X,Y,Z,uv)])
# masks for UE material (bed vs dust vs grass) as texture over terrain extent
bed=np.clip(1-(d-hw*0.9)/1.2,0,1); trail=np.clip(1-td/0.9,0,1); trail=np.where(np.abs(Y-center(X))<halfw(X)+0.3,0,trail)
mask=np.dstack([bed,trail,np.clip(bank*1.5-n2*0.5,0,1)])
Image.fromarray((np.flipud(mask)*255).astype(np.uint8)).save(os.path.join(OUT,"T_TerrainMask.png"))
json.dump({"L":L,"W":W},open(os.path.join(OUT,"terrain.json"),"w"))
# ---------- water surface (follows channel, ripple geometry) ----------
wx=np.linspace(-L/2,L/2,600); wv=np.linspace(-1,1,60); WX,WV=np.meshgrid(wx,wv,indexing='xy')
WY=center(WX)+WV*(halfw(WX)*0.97)
WZ=np.full_like(WX,0.0)-P["depth"]+P["water_h"]-WX*P["slope"]
if REAL:
    _m=(np.abs(CP[:,0])<L/2+30)&(np.abs(CP[:,1])<W/2+30); C2=CP[_m]; Z2=CWZ[_m]
    tg=np.gradient(C2,axis=0); tg/=np.linalg.norm(tg,axis=1,keepdims=True); nrm=np.c_[-tg[:,1],tg[:,0]]
    hw2=halfw(C2[:,0])*0.98+0.05
    WX=C2[None,:,0]+wv[:,None]*hw2[None,:]*nrm[None,:,0]; WY=C2[None,:,1]+wv[:,None]*hw2[None,:]*nrm[None,:,1]; WZ=np.repeat(Z2[None,:],len(wv),0)
save("water",[grid_mesh(WX,WY,WZ,np.c_[WX.ravel()/3.0,WY.ravel()/3.0])])
# ---------- boulders ----------
def boulder(seed,sx,sy,sz,sub=4):
    r=np.random.default_rng(seed); m=trimesh.creation.icosphere(sub)
    v=m.vertices.copy(); dirs=v/np.linalg.norm(v,axis=1,keepdims=True)
    disp=np.zeros(len(v))
    for k in range(7):
        a=r.standard_normal(3); a/=np.linalg.norm(a); disp+=0.35/(k+1)*np.sin(dirs@a*(2+3*k)+r.uniform(0,6))
    for k in range(5):  # flat cleaved facets (granite jointing)
        a=r.standard_normal(3); a/=np.linalg.norm(a); t=r.uniform(0.55,0.85); p=dirs@a; disp=np.where(p>t,disp-(p-t)*1.2,disp)
    v=dirs*(1+0.12*disp)[:,None]; v[:,2]=np.where(v[:,2]<-0.3,-0.3-(v[:,2]+0.3)*0.2,v[:,2])
    v*= [sx,sy,sz]; m=trimesh.Trimesh(v,m.faces,process=False)
    # box-ish uv
    n=m.vertex_normals; uvb=np.where(np.abs(n[:,2:3])>0.6,v[:,:2],np.where(np.abs(n[:,0:1])>np.abs(n[:,1:2]),v[:,1:3],v[:,[0,2]]))/1.5
    m.visual=trimesh.visual.TextureVisuals(uv=uvb); return m
for i in range(8):
    s=[(3.5,2.4,1.3),(1.6,1.2,0.9),(0.9,0.7,0.55),(2.5,1.8,0.8),(0.5,0.45,0.35),(5,3.5,1.6),(1.2,1.0,0.8),(0.35,0.3,0.22)][i]
    save(f"boulder{i}",[boulder(100+i,*s)])
# ---------- slab (glacier polished) ----------
sx=np.linspace(-6,6,90); sy=np.linspace(-3,3,50); SX,SY=np.meshgrid(sx,sy)
r=np.hypot(SX/6,SY/3); SZ=0.9*np.clip(1-r**2,0,1)**0.6+0.05*(fbm2(90,4,5)[:50,:90]-0.5)
save("slab",[grid_mesh(SX,SY,SZ,np.c_[SX.ravel()/2,SY.ravel()/2])])
# ---------- conifers (trunk + needle tiers) ----------
def conifer(seed,h):
    r=np.random.default_rng(seed); parts=[]
    tr=trimesh.creation.cone(radius=h*0.022,height=h,sections=12);
    tr.visual=trimesh.visual.TextureVisuals(uv=np.c_[np.arctan2(tr.vertices[:,1],tr.vertices[:,0])/np.pi,tr.vertices[:,2]/1.5])
    fol=[]
    tiers=int(h*1.6)
    for k in range(tiers):
        t=k/tiers; z=h*(0.22+0.78*t); rad=h*0.21*(1-t)**0.9+0.25
        c=trimesh.creation.cone(radius=rad,height=rad*0.9,sections=10)
        vv=c.vertices.copy(); ang=np.arctan2(vv[:,1],vv[:,0]); vv[:,:2]*=(1+0.25*np.sin(ang*r.integers(4,8)+r.uniform(0,6)))[:,None]
        vv[:,2]+=z-rad*0.55+ r.uniform(-0.1,0.1); c=trimesh.Trimesh(vv,c.faces,process=False); fol.append(c)
    fo=trimesh.util.concatenate(fol); fo.visual=trimesh.visual.TextureVisuals(uv=fo.vertices[:,:2]/0.7)
    return [tr,fo]
for i,h in enumerate([18,24,30,14]): save(f"pine{i}",conifer(200+i,h))
# ---------- distant domes (unused) + Sierra skyline ridge ----------
dx=np.linspace(-1,1,120); DX,DY=np.meshgrid(dx,dx); rr=np.hypot(DX,DY)
DZ=np.clip(1-rr**2,0,1)**0.8*(1+0.05*fbm2(120,5,9)-0.025)
save("dome",[grid_mesh(DX*150,DY*110,DZ*120,np.c_[DX.ravel()*20,DY.ravel()*20])])
# ---------- THRU asset-library PBR sets ----------
PKT=os.environ.get("PACK_TEXTURE_DIR","/workspace/fullscene/packs/tex")
_ARG=os.path.exists(f"{PKT}/argon-dgtread/albedo.png")
for sset,tag in ([("argon-granite","PG"),("argon-creekbed","PT"),("pine-needle-duff","PD"),("argon-dgtread","DG"),("argon-bark","BK")] if _ARG else [("granite-boulders-tors","PG"),("talus-cobble-wash","PT"),("pine-needle-duff","PD")]):
    for mp,suf in [("albedo","D"),("normal","N"),("roughness","R")]:
        im=Image.open(f"{PKT}/{sset}/{mp}.png")
        if im.mode in ("I;16","I;16B","I","F"): im=Image.fromarray((np.array(im).astype(np.float32)/(65535.0 if np.array(im).max()>255 else 255.0)*255).astype(np.uint8))
        im=im.convert("RGB")
        if mp=="normal": a=np.array(im); a[...,1]=255-a[...,1]; im=Image.fromarray(a)
        im.save(os.path.join(OUT,f"T_{tag}_{suf}.png"))
# ---------- textures ----------
T=1024
def tex(name,arr): Image.fromarray(np.clip(arr*255,0,255).astype(np.uint8)).save(os.path.join(OUT,name+".png"))
def normal_from_h(h,s):
    gx=(np.roll(h,-1,1)-np.roll(h,1,1))*s; gy=(np.roll(h,-1,0)-np.roll(h,1,0))*s
    n=np.dstack([-gx,-gy,np.ones_like(h)]); n/=np.linalg.norm(n,axis=2,keepdims=True); return n*0.5+0.5
g1=fbm2(T,7,11,4); g2=fbm2(T,4,12,64); sp=rng.random((T,T))
gran=np.dstack([g1*0.10+0.58]*3)*np.array([1.0,0.98,0.95])
gran=np.where((sp<0.05)[...,None],[0.08,0.08,0.09],gran); gran=np.where((sp>0.975)[...,None],[0.85,0.83,0.80],gran)
gran=np.where(((sp>0.94)&(sp<0.96))[...,None],[0.70,0.62,0.55],gran)
gran=ndimage.gaussian_filter(gran,(0.7,0.7,0)); gran*= (0.75+0.35*g2)[...,None]
stain=fbm2(T,5,13,2); gran*= (1-0.25*np.clip(stain-0.55,0,1)*3)[...,None]*np.array([1,0.97,0.92])
tex("T_Granite_D",gran); hg=g1*0.5+g2*0.3+sp*0.06; tex("T_Granite_N",normal_from_h(hg,6)); tex("T_Granite_R",0.55+0.25*g2)
d1=fbm2(T,7,21,8); pe=fbm2(T,3,22,96)
dust=np.dstack([0.62+0.1*d1,0.53+0.09*d1,0.42+0.07*d1])*(0.85+0.2*pe)[...,None]
tex("T_Dust_D",dust); tex("T_Dust_N",normal_from_h(d1*0.3+pe*0.6,4)); tex("T_Dust_R",0.85+0.1*pe)
# pebbles (voronoi)
pts=rng.random((900,2))*T; from scipy.spatial import cKDTree
yy,xx=np.mgrid[0:T,0:T]; q=np.c_[xx.ravel(),yy.ravel()]
tree=cKDTree(np.r_[pts,pts+[T,0],pts-[T,0],pts+[0,T],pts-[0,T],pts+[T,T],pts-[T,T],pts+[T,-T],pts-[T,-T]])
dd,ii=tree.query(q,k=2); ii=ii[:,0]%900; edge=(dd[:,1]-dd[:,0]).reshape(T,T)
cols=np.array([[0.55,0.33,0.18],[0.45,0.43,0.40],[0.62,0.45,0.28],[0.30,0.28,0.26],[0.70,0.64,0.55],[0.50,0.25,0.12]])
pc=cols[rng.integers(0,len(cols),900)]*rng.uniform(0.7,1.1,(900,1))
peb=pc[ii].reshape(T,T,3)*(np.clip(edge/14,0,1)**0.5)[...,None]
tex("T_Pebble_D",peb*(0.9+0.2*g2[...,None])); tex("T_Pebble_N",normal_from_h(np.clip(edge/14,0,1)**0.5,3)); tex("T_Pebble_R",np.full((8,8),0.5))
# water normal: anisotropic ripples
w=np.zeros((T,T)); r2=np.random.default_rng(31)
F=np.fft.fftfreq(T)[:,None],np.fft.fftfreq(T)[None,:]
spec=np.exp(-((F[0]*T/6)**2+(F[1]*T/18)**2))*(r2.standard_normal((T,T))+1j*r2.standard_normal((T,T)))
w=np.real(np.fft.ifft2(spec)); w=(w-w.min())/np.ptp(w)
tex("T_Water_N",normal_from_h(w,9))
bark=fbm2(T,6,41,16); tex("T_Bark_D",np.dstack([0.30+0.1*bark,0.20+0.07*bark,0.15+0.05*bark]))
nd=fbm2(T,5,42,32); tex("T_Needle_D",np.dstack([0.09+0.04*nd,0.16+0.06*nd,0.08+0.03*nd]))

# ---------- probe for axis detection ----------
pr=trimesh.creation.box((1,1,1)); pr.apply_translation([20,10,5]); pr.visual=trimesh.visual.TextureVisuals(uv=np.zeros((len(pr.vertices),2))); save("probe",[pr])
# ---------- bridge (wooden PCT footbridge, crossing at x=0 along y) ----------
zw=(lambda x: zw_real(x)) if REAL else (lambda x: -P["depth"]+P["water_h"]-x*P["slope"])
DECK=zw(0)+1.15; BL=2*BRIDGE_HALF; BW=1.5
def box(c,sz):
    b=trimesh.creation.box(sz); b.apply_translation(c); v=b.vertices; n=b.vertex_normals
    b.visual=trimesh.visual.TextureVisuals(uv=np.where(np.abs(n[:,2:3])>0.5,v[:,:2],np.where(np.abs(n[:,0:1])>0.5,v[:,1:3],v[:,[0,2]]))/0.8); return b
parts=[]
for k in range(int(BL/0.16)):
    y=-BL/2+0.08+k*0.16; parts.append(box([r.uniform(-0.01,0.01) if (r:=np.random.default_rng(k)) else 0,y,DECK-0.03],[BW,0.145,0.06]))
for sx in (-0.55,0.55): parts.append(box([sx,0,DECK-0.22],[0.18,BL,0.3]))
for sx in (-BW/2,BW/2):
    parts.append(box([sx,0,DECK+0.95],[0.09,BL,0.11])); parts.append(box([sx,0,DECK+0.5],[0.06,BL,0.08]))
    for k in range(7): parts.append(box([sx,-BL/2+0.2+k*(BL-0.4)/6,DECK+0.45],[0.11,0.11,1.0]))
save("bridge",[trimesh.util.concatenate(parts)])

def ridge_mesh(seed,r0,a0,a1,hmax):
    rr=np.random.default_rng(seed); na,nr=420,24
    a=np.linspace(np.radians(a0),np.radians(a1),na)
    crest=np.zeros(na); amp=1.0
    for o in range(7):
        f=2*2**o; ph=rr.uniform(0,6.28,3)
        crest+=amp*(np.abs(np.sin(a*f*3+ph[0]))*0.6+0.4*np.sin(a*f*5.3+ph[1])); amp*=0.5
    crest=(crest-crest.min())/np.ptp(crest); crest=hmax*(0.35+0.65*crest**1.6)
    t=np.linspace(0,1,nr)
    A,T=np.meshgrid(a,t,indexing='xy'); R=r0+T*hmax*1.4; Zr=np.outer(np.sin(np.pi/2*(1-t))**0.7,np.ones(na))*0+ (1-T)**0*0
    Zr=crest[None,:]*(1-T)**1.3-20+ rr.standard_normal(A.shape)*hmax*0.012*(1-T)
    Zr=crest[None,:]*np.clip(1-(T*1.0),0,1)**0.8-25
    X_=R*np.cos(A); Y_=R*np.sin(A)
    return grid_mesh(X_,Y_,Zr,np.c_[A.ravel()*r0/20,Zr.ravel()/20])
save("ridge",[ridge_mesh(11,300,110,255,150),ridge_mesh(12,380,-80,70,185),ridge_mesh(13,470,235,305,210)])

# ---- outer skirt terrain out to 1.2 km so no map edge is ever visible; rises toward the skyline ridges
NS=260; sx=np.linspace(-600,600,NS); SXg,SYg=np.meshgrid(sx,sx,indexing='xy'); rr_=np.hypot(SXg,SYg)
fb=fbm2(NS,6,21,3)
ZS=(fb-0.5)*14+np.clip((rr_-70)/450,0,1)**1.5*70
edge=np.clip(1-np.maximum(np.abs(SXg)/(L/2),np.abs(SYg)/(W/2)),0,1)
ZS=np.where((np.abs(SXg)<L/2-0.5)&(np.abs(SYg)<W/2-0.5),-6.0,ZS)
# blend skirt to hero-terrain edge height near the seam
from scipy.interpolate import RegularGridInterpolator as _RGI
_zi=_RGI((ys,xs),Z,bounds_error=False,fill_value=None)
near=(np.abs(SXg)<L/2+40)&(np.abs(SYg)<W/2+40)&~((np.abs(SXg)<L/2-0.5)&(np.abs(SYg)<W/2-0.5))
ex=np.clip(SXg,-L/2,L/2); ey=np.clip(SYg,-W/2,W/2); ze=_zi(np.c_[ey.ravel(),ex.ravel()]).reshape(ex.shape)
dout=np.maximum(np.abs(SXg)-L/2,np.abs(SYg)-W/2).clip(0); wgt=np.clip(dout/40,0,1)
ZS=np.where(near,ze*(1-wgt)+ZS*wgt-0.05,ZS)
save("skirt",[grid_mesh(SXg,SYg,ZS,np.c_[SXg.ravel()/4,SYg.ravel()/4])])
_SZ=_RGI((sx,sx),ZS.T,bounds_error=False,fill_value=0.0)
