# Procedural geometry + tileable textures for THRU UE5 Sierra creek spike. Z-up meters, exported as glb (Y-up).
import numpy as np, trimesh, json, os, sys, math
from PIL import Image
from scipy import ndimage
rng=np.random.default_rng(7)
OUT=sys.argv[1] if len(sys.argv)>1 else "assets"; os.makedirs(OUT,exist_ok=True)
P=json.load(open(os.path.join(os.path.dirname(__file__),"params.json")))["geo"]
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
REALD=os.environ.get("REAL_DIR","/workspace/unreal/real")
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
PKT="/workspace/unreal/packs/tex"
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
# ---------- placements (meters, Z-up, my coords) ----------
from scipy.interpolate import RegularGridInterpolator
ZI=RegularGridInterpolator((ys,xs),Z)
zf=lambda x,y: float(ZI([[np.clip(y,-W/2,W/2),np.clip(x,-L/2,L/2)]])[0])
pl={"meshes":[],"water_z0":-P["depth"]+P["water_h"],"slope":P["slope"],"L":L,"W":W,"deck_z":DECK}
if REAL:
    _xx=np.linspace(-50,50,101); _b,_a=np.polyfit(_xx,zw(_xx),1); pl["water_z0"]=float(_a); pl["slope"]=float(-_b); print("water plane",_a,_b)
def put(mesh,x,y,z,yaw,s=1.0,kind="rock"): pl["meshes"].append({"mesh":mesh,"x":float(x),"y":float(y),"z":float(z),"yaw":float(yaw),"s":float(s),"kind":kind})
put("bridge",0,0,0,0,1.0,"bridge")
r=np.random.default_rng(3)
def clear(x,y,m): return float(trail_dist(x,y))>m and not (abs(x)<1.4 and abs(y)<BL/2+0.5)
for k in range(70):  # in-creek cobbles (procedural, granite PBR)
    x=r.uniform(-40,35); side=r.uniform(-0.9,0.9); y=center(x)+side*halfw(x); b=int(r.choice([2,4,6,7])); s=r.uniform(0.4,1.0)
    if abs(x)<1.2: continue
    put(f"boulder{b}",x,y,zf(x,y)-0.12*s,r.uniform(0,360),s)
for k in range(34):  # bank boulders: THRU hero granite (hero-creek lane generator)
    x=r.uniform(-40,35); sd=r.choice([-1,1]); y=center(x)+sd*(halfw(x)+r.uniform(-0.4,4.0)); s=r.uniform(0.7,1.6)
    if not clear(x,y,1.6): continue
    put("hero_granite_"+"abc"[k%3],x,y,zf(x,y)-0.25*s,r.uniform(0,360),s,"hero_granite")
put("slab",-12,center(-12)-halfw(-12)-3.0,zf(-12,center(-12)-halfw(-12)-3)-0.5,20,0.9)
TREES=["jeffrey_open_LOD0","fir_white_tall_LOD0","fir_red_mature_LOD0"]
n=0
while n<70:
    x=r.uniform(-55,55); y=r.uniform(-W/2+3,W/2-3); dd=abs(y-center(x))
    if dd<halfw(x)+4.5 or not clear(x,y,3.0): continue
    if r.random()>0.3+0.5*np.clip((dd-6)/15,0,1): continue
    put(TREES[int(r.integers(0,3))],x,y,zf(x,y)-0.1,r.uniform(0,360),r.uniform(0.85,1.15),"tree"); n+=1
for k in range(90):  # grass + ferns (Poly Haven CC0) near banks and trail edges
    x=r.uniform(-30,28); sd=r.choice([-1,1]); y=center(x)+sd*(halfw(x)+abs(r.normal(1.2,1.6)))
    if not clear(x,y,0.9): continue
    nm=("polyhaven_fern_02_" if r.random()<0.25 else "polyhaven_grass_medium_01_")+"abcd"[int(r.integers(0,4))]
    put(nm,x,y,zf(x,y)-0.03,r.uniform(0,360),r.uniform(0.8,1.4),"plant")
put("ridge",0,0,0,0,1.0,"dome")
put("skirt",0,0,0,0,1.0,"skirt")
_rf=np.random.default_rng(77); n=0
while n<220:  # distant forest on the skirt (hides seams, gives depth)
    x=_rf.uniform(-260,260); y=_rf.uniform(-200,200)
    if abs(x)<L/2+2 and abs(y)<W/2+2: continue
    put(["jeffrey_open_LOD0","fir_white_tall_LOD0","fir_red_mature_LOD0","ponderosa_pine","grand_fir","western_hemlock"][n%6],x,y,float(_SZ([[x,y]])[0])-0.2,_rf.uniform(0,360),_rf.uniform(0.9,1.3),"tree"); n+=1

# ---- seeded rule scatter (PCG-equivalent; seed 1998): density by creek and trail distance, clear trail corridor, wet zone, dusty trail edge
rs=np.random.default_rng(1998)
def dcreek(x,y): return abs(y-center(x))-halfw(x)
HG_TALL=["medium_01","medium_09","tall_03"]; HG_SHORT=["short_01","short_07","sprout_04","patch_short"]; HG_PATCH=["patch_medium"]
n_hg=0
for k in range(9000):
    if n_hg>=1700: break
    x=rs.uniform(-38,34); y=rs.uniform(-18,18); dc=dcreek(x,y); dt=float(trail_dist(x,y))
    if dc<0.15 or dt<0.75 or (abs(x)<1.4 and abs(y)<BL/2+0.5): continue
    p=0.15+0.85*np.exp(-max(dc,0)/5.0)
    if rs.random()>p: continue
    if dt<1.6: nm=HG_SHORT[int(rs.integers(0,len(HG_SHORT)))]; s_=rs.uniform(0.8,1.2)   # dusty trail edge: short, sparse
    elif dc<2.0: nm=(HG_TALL+HG_PATCH)[int(rs.integers(0,4))]; s_=rs.uniform(1.0,1.5)  # lush wet zone
    else: nm=(HG_TALL+HG_SHORT+HG_PATCH)[int(rs.integers(0,8))]; s_=rs.uniform(0.9,1.4)
    put(nm,x,y,zf(x,y)-0.02,rs.uniform(0,360),s_,"plant"); n_hg+=1
for k in range(60):   # bracken (THRU) in the wet zone
    x=rs.uniform(-35,30); sd=rs.choice([-1,1]); y=center(x)+sd*(halfw(x)+rs.uniform(0.3,2.5))
    if not clear(x,y,1.0): continue
    put("bracken_cured",x,y,zf(x,y)-0.03,rs.uniform(0,360),rs.uniform(0.8,1.2),"plant")
for k in range(90):   # needlegrass on the dusty trail edges
    x=rs.uniform(-38,34); y=rs.uniform(-18,18); dt=float(trail_dist(x,y))
    if dt<0.9 or dt>3.0 or dcreek(x,y)<0.5 or (abs(x)<1.4 and abs(y)<BL/2+0.5): continue
    put("needlegrass_cured_large",x,y,zf(x,y)-0.02,rs.uniform(0,360),rs.uniform(0.8,1.2),"plant")
n=0
while n<34:  # chaparral shrubs upslope
    x=rs.uniform(-45,45); y=rs.uniform(-25,25)
    if dcreek(x,y)<6 or not clear(x,y,2.0): continue
    put(["manzanita_shrub","chamise_shrub"][n%2],x,y,zf(x,y)-0.05,rs.uniform(0,360),rs.uniform(0.8,1.2),"plant"); n+=1
AR=["arnklit_boulder1","arnklit_boulder2","arnklit_boulder3","arnklit_boulder4","arnklit_boulder5","arnklit_boulder6","arnklit_rock1","arnklit_rock2","arnklit_rock3","arnklit_rock4","arnklit_pile1","arnklit_pile2"]
for k in range(40):   # Arnklit Cliffs & Rocks (purchased) on the creek banks, partly in the water
    x=rs.uniform(-36,32); sd=rs.choice([-1,1]); y=center(x)+sd*(halfw(x)+rs.uniform(-0.6,2.0))
    if abs(x)<1.6 or float(trail_dist(x,y))<1.2: continue
    put(AR[k%len(AR)],x,y,zf(x,y)-0.15,rs.uniform(0,360),rs.uniform(0.6,1.3),"plant")
for k,(x,sd) in enumerate([(-24,1),(18,-1),(-30,-1),(26,1)]):  # creekside cliffs
    y=center(x)+sd*(halfw(x)+5.5)
    if float(trail_dist(x,y))>3: put(["arnklit_cliff2","arnklit_cliff4"][k%2],x,y,zf(x,y)-0.6,rs.uniform(0,360),1.4,"plant")
for k in range(10):
    x=rs.uniform(-34,30); sd=rs.choice([-1,1]); y=center(x)+sd*(halfw(x)+rs.uniform(0.5,3))
    if clear(x,y,1.3) and abs(x)>2: put(["namaqualand_boulder_02","namaqualand_boulder_03","rock_moss_set_01"][k%3],x,y,zf(x,y)-0.1,rs.uniform(0,360),rs.uniform(0.7,1.2),"plant")
n=0
while n<14:  # Evermotion AM283 riparian trees along the creek
    x=rs.uniform(-45,40); sd=rs.choice([-1,1]); y=center(x)+sd*(halfw(x)+rs.uniform(2.5,7))
    if not clear(x,y,2.5) or abs(x)<4: continue
    put(["riparian_willow_a","riparian_willow_b","riparian_sycamore"][n%3],x,y,zf(x,y)-0.1,rs.uniform(0,360),rs.uniform(0.9,1.1),"tree"); n+=1
n=0; tries=0
while n<46 and tries<5000:  # Evermotion AM283 + THRU conifers upslope
    tries+=1; x=rs.uniform(-60,60); y=rs.uniform(-W/2+3,W/2-3)
    if dcreek(x,y)<9 or not clear(x,y,3.5): continue
    put(["ponderosa_pine","grand_fir","western_hemlock","ponderosa_pine","mature_cedar_14m","coulter_pine_mature"][n%6],x,y,zf(x,y)-0.1,rs.uniform(0,360),rs.uniform(0.85,1.15),"tree"); n+=1
# hiker gear: backpack + hat (procedural)
pk=trimesh.creation.box([0.30,0.40,0.55]); pk.apply_translation([0,0,0]); bed=trimesh.creation.cylinder(radius=0.09,height=0.42,sections=16); bed.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2,[1,0,0])); bed.apply_translation([0,0,-0.33])
for m_ in (pk,bed): m_.visual=trimesh.visual.TextureVisuals(uv=m_.vertices[:,:2])
save("backpack",[trimesh.util.concatenate([pk,bed])])
_PKG="/workspace/unreal/packs/gear/hiker_pack_1990s.glb"
if os.path.exists(_PKG):
    import shutil; shutil.copy(_PKG,os.path.join(OUT,"backpack.glb"))
    for _src,_dst in (("pack_D.png","T_Pack_D.png"),("pack_N.png","T_Pack_N.png")):
        if os.path.exists(f"/workspace/unreal/packs/gear/{_src}"): shutil.copy(f"/workspace/unreal/packs/gear/{_src}",os.path.join(OUT,_dst))
crown=trimesh.creation.cylinder(radius=0.10,height=0.11,sections=24); crown.apply_translation([0,0,0.055]); brim=trimesh.creation.cylinder(radius=0.19,height=0.012,sections=32)
for m_ in (crown,brim): m_.visual=trimesh.visual.TextureVisuals(uv=m_.vertices[:,:2])
save("hat",[trimesh.util.concatenate([crown,brim])])
def cam(name,px,py,pz,tx,ty,tz,fl=35): return {"name":name,"pos":[px,py,max(pz,zf(px,py)+0.35)],"tgt":[tx,ty,tz],"fl":fl}
HIKER_STILL=[0.0,-1.6,DECK]
_cum=np.r_[0,np.cumsum(np.linalg.norm(np.diff(TRAIL,axis=0),axis=1))]; _ib=int(np.argmax(onb)); _it=int(np.argmin(np.abs(_cum-(_cum[_ib]-12))))
TCX,TCY=float(TRAIL[_it,0]),float(TRAIL[_it,1])
shots=[cam("hero_low",9,center(9)+0.6,zw(9)+0.45,-3,center(-3),zw(-3)+1.1,22),
       cam("wet_stones",-3.5,center(-3.5)-1.0,zw(-3.5)+0.75,-8.5,center(-8.5)+0.2,zw(-8.5)-0.05,35),
       cam("trail",TCX,TCY,zf(TCX,TCY)+1.65,0,-3,DECK+0.6,24),
       cam("wide",15,-13,zw(15)+7,-3,1.5,zw(-3)+0.5,20),
       cam("hiker",5.5,-4.6,zw(5.5)+1.5,0,-1.6,DECK+0.95,35)]
# walk: 10 s at 60 fps, 1.25 m/s along trail polyline, reaching the bridge ~3 s in, never through water
def along(sdist):
    seg=np.hypot(*np.diff(TRAIL,axis=0).T); cum=np.r_[0,np.cumsum(seg)]
    i=int(np.clip(np.searchsorted(cum,sdist)-1,0,len(seg)-1)); t=(sdist-cum[i])/seg[i]; p=TRAIL[i]+t*(TRAIL[i+1]-TRAIL[i]); d=(TRAIL[i+1]-TRAIL[i])/seg[i]; return p,d
seg=np.hypot(*np.diff(TRAIL,axis=0).T); s_bridge=float(np.sum(seg[:3]))
TOTAL=float(np.sum(seg)); SPEED=1.15; NF=int(np.clip((TOTAL-1.0)/SPEED,45,60)*60); S0=max(0.0,(TOTAL-SPEED*NF/60)/2); walk=[]; hk=[]
for f in list(range(0,NF,15))+[NF]:
    s_=S0+SPEED*f/60.0; (hx,hy),d=along(s_)
    on_bridge=abs(hx)<0.8 and abs(hy)<BL/2+0.2
    hz=DECK if on_bridge else zf(hx,hy)
    yaw=float(np.degrees(np.arctan2(d[1],d[0])))
    hk.append({"f":f,"pos":[float(hx),float(hy),float(hz)],"yaw":yaw})
    cx,cy=hx-d[0]*3.8+d[1]*1.3, hy-d[1]*3.8-d[0]*1.3; cz=max(hz,zf(cx,cy))+1.6
    walk.append({"f":f,"pos":[float(cx),float(cy),float(cz)],"tgt":[float(hx+d[0]*8),float(hy+d[1]*8),float(hz+0.9)]})
# ---- Playtest dense route (Godot, 60 fps, 1.4 m/s, 4 s bridge pause) -> local frame; intro + outro to reach ~50 s
DP=os.path.join(OUT,"path-hero-after-dense.json")
if os.path.exists(DP):
    DR=json.load(open(DP))["frames"]
    def g2l(p): r_=np.array([p[0]-BC[0],p[2]-BC[1]]); return float(r_@CAX), float(r_@BAX)
    INTRO=360; OUTRO=300; walk=[]; hk=[]; pauses=[]
    body=[g2l(f["body"]) for f in DR]
    def ground(x,y): return DECK if (abs(x)<0.9 and abs(y)<BRIDGE_HALF+0.2) else zf(x,y)
    yaw=None; still=0
    for i,f in enumerate(DR):
        x,y=body[i]; j=min(i+6,len(DR)-1); dx,dy=body[j][0]-x,body[j][1]-y
        if math.hypot(dx,dy)>0.02: yaw=math.degrees(math.atan2(dy,dx))
        elif yaw is None: yaw=0.0
        sp=math.hypot(body[min(i+1,len(DR)-1)][0]-x,body[min(i+1,len(DR)-1)][1]-y)*60
        pauses.append(sp<0.15)
        hz=ground(x,y); F=INTRO+i
        if i%6==0 or i==len(DR)-1:
            hk.append({"f":F,"pos":[x,y,hz],"yaw":yaw})
            cx,cy=g2l(f["cam"]); tx,ty=g2l(f["target"])
            cz=max(hz+(f["cam"][1]-f["body"][1]),zf(cx,cy)+0.4); tz=hz+(f["target"][1]-f["body"][1])
            walk.append({"f":F,"pos":[cx,cy,cz],"tgt":[tx,ty,tz]})
    # intro: crane from wide establishing view down to the first follow-cam pose, hiker idle at route start
    w0=shots[3]; first=walk[0]
    hk.insert(0,{"f":0,"pos":hk[0]["pos"],"yaw":hk[0]["yaw"]})
    walk.insert(0,{"f":0,"pos":w0["pos"],"tgt":w0["tgt"]}); walk.insert(1,{"f":INTRO//2,"pos":[(w0["pos"][k]+first["pos"][k])/2+(1.5 if k==2 else 0) for k in range(3)],"tgt":first["tgt"]})
    END=INTRO+len(DR); last=walk[-1]; lh=hk[-1]
    hk.append({"f":END+OUTRO,"pos":lh["pos"],"yaw":lh["yaw"]})
    walk.append({"f":END+OUTRO,"pos":[last["pos"][0]-2,last["pos"][1]-2,last["pos"][2]+3.5],"tgt":last["tgt"]})
    # animation segments: idle in intro, walk, idle in pauses, idle in outro
    segs=[]; cur=None; st=0
    states=["idle"]*INTRO+["idle" if p else "walk" for p in pauses]+["idle"]*OUTRO
    for i,sname in enumerate(states+["end"]):
        if sname!=cur:
            if cur is not None: segs.append({"anim":cur,"start":st,"end":i})
            cur=sname; st=i
    segs=[sg for sg in segs if sg["end"]-sg["start"]>=10 or sg["anim"]=="walk"]
    pl["anim_segments"]=segs; NF=END+OUTRO; SPEED=1.4
    print("dense route",len(DR),"frames; total",NF,"segments",[(sg["anim"],sg["start"],sg["end"]) for sg in segs])
# path hygiene (Trailboss 15:49): no fern / procedural faceted boulders / broadleaf trees crowding the walk path or cameras
_wc=np.array([w["pos"][:2] for w in walk]) if walk else np.zeros((0,2))
def _near_path(x,y,r):
    dd=float(trail_dist(x,y)); dc=np.min(np.hypot(_wc[:,0]-x,_wc[:,1]-y)) if len(_wc) else 1e9
    return dd<r or dc<r
def _segd(px,py,a,b):
    a=np.array(a[:2]); b=np.array(b[:2]); d=b-a; t=np.clip(((px-a[0])*d[0]+(py-a[1])*d[1])/(d@d+1e-9),0,1); return float(np.hypot(px-a[0]-t*d[0],py-a[1]-t*d[1])), t
def _near_cams(x,y):   # nothing may block a still camera: clear 2.5 m around the first 70% of each camera->target line
    for sh in shots:
        dd,t=_segd(x,y,sh["pos"],sh["tgt"])
        if dd<2.5 and t<0.7: return True
    return False
_keep=[]
for it in pl["meshes"]:
    m_=it["mesh"]; x_,y_=it["x"],it["y"]
    if m_.startswith("polyhaven_fern"): continue   # "broadleaf houseplants" (critic): removed
    if m_.startswith("hero_granite"):   # faceted, crumpled look in UE: swap for Poly Haven (CC0) Namaqualand boulders
        it=dict(it); it["mesh"]=["namaqualand_boulder_02","namaqualand_boulder_03"][int(abs(x_*7.3+y_*3.1))%2]; it["kind"]="plant"
    if m_ in ("jeffrey_open_LOD0","fir_white_tall_LOD0","fir_red_mature_LOD0") and _near_path(x_,y_,45.0):
        it=dict(it); it["mesh"]=["fir_white_tall_LOD0","fir_red_mature_LOD0"][int(abs(x_*5.7+y_*2.3))%2]
    if it["kind"]=="rock" and m_.startswith("boulder") and _near_path(x_,y_,4.0): continue
    if m_.startswith("riparian_") and _near_path(x_,y_,6.0): continue
    if it["mesh"].startswith("arnklit_") and _near_path(x_,y_,8.0): it=dict(it); it["mesh"]=["namaqualand_boulder_02","namaqualand_boulder_03"][int(abs(x_*3.3+y_))%2]
    if it["kind"]!="bridge" and _near_cams(x_,y_): continue
    _keep.append(it)
print("path hygiene removed",len(pl["meshes"])-len(_keep)); pl["meshes"]=_keep
pl["shots"]=shots; pl["walk"]=walk; pl["hiker_walk"]=hk; pl["hiker_still"]=HIKER_STILL; pl["walk_speed"]=SPEED; pl["walk_fps"]=60; pl["walk_frames"]=NF; pl["trail"]=TRAIL.tolist()
json.dump(pl,open(os.path.join(OUT,"placements.json"),"w"),indent=0)
print("GEN_OK",len(pl["meshes"]))
