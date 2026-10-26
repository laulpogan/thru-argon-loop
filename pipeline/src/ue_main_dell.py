# THRU UE5 spike: build Sierra creek scene from procedural assets, then render via Movie Render Queue (PIE executor).
import unreal, json, os, math, traceback, glob
ROOT="/home/dellpromax/ue/ws"
RUN=json.load(open(f"{ROOT}/run.json"))
P=json.load(open(f"{ROOT}/src/params.json"))
A=f"{ROOT}/assets"
PL=json.load(open(f"{A}/placements.json"))
AT=unreal.AssetToolsHelpers.get_asset_tools(); EAL=unreal.EditorAssetLibrary; MEL=unreal.MaterialEditingLibrary
def log(*a): unreal.log_warning("THRU: "+" ".join(map(str,a)))
def mark(s): open(f"{ROOT}/ue_stage.txt","a").write(s+"\n")
def sp(o,k,v):
    try: o.set_editor_property(k,v); return True
    except Exception as e: log("setprop fail",k,e); return False
# ---------------- import ----------------
# assetfix-1715 ROOT CAUSE: in-place Interchange reimport (replace_existing=True) of an asset that is already
# loaded trashes the old MaterialInstance/Texture objects; after the next GC (new_level) a deferred
# FMaterialRenderProxy uniform-expression update still points at the freed texture ->
# "Texture not valid! UE-23902! Parameter (NormalTexture)" + SIGSEGV in FUniformExpressionSet::FillUniformBuffer.
# Fix: never replace an existing asset inside a running editor. Import only when the asset is absent;
# changed sources are invalidated OUTSIDE the editor by src/invalidate_imports.py (run by the launcher),
# which moves the stale Content packages to a trash dir so the next session imports them fresh.
MANIFEST=f"{ROOT}/import_manifest.json"
def _man():
    try: return json.load(open(MANIFEST))
    except Exception: return {}
def _sig(f):
    import hashlib; h=hashlib.sha1()
    with open(f,"rb") as fh:
        for ch in iter(lambda: fh.read(1<<20),b""): h.update(ch)
    return h.hexdigest()
def _present(f,dest):
    n=os.path.splitext(os.path.basename(f))[0]
    if f.lower().endswith((".png",".jpg",".jpeg",".tga",".exr")): return EAL.does_asset_exist(f"{dest}/{n}")
    return EAL.does_directory_exist(dest) and len(EAL.list_assets(dest,recursive=True,include_folder=False))>0
def imp(files,dest,src_of=None):
    man=_man(); ts=[]; res={}
    for f in files:
        src=(src_of or {}).get(f,f); n=os.path.splitext(os.path.basename(f))[0]
        if _present(f,dest):
            if src not in man and os.path.exists(src): man[src]={"sig":_sig(src),"dest":dest,"name":n,"adopted":True}
            res[n]=[]; continue
        t=unreal.AssetImportTask(); t.filename=f; t.destination_path=dest; t.automated=True; t.save=True; t.replace_existing=False; ts.append((t,src))
    if ts:
        AT.import_asset_tasks([t for t,_ in ts])
        for t,src in ts:
            n=os.path.splitext(os.path.basename(t.filename))[0]; res[n]=[str(p) for p in t.imported_object_paths]
            man[src]={"sig":_sig(src) if os.path.exists(src) else None,"dest":dest,"name":n,"objects":res[n]}
            log("imported fresh",src,"->",dest,len(res[n]))
    json.dump(man,open(MANIFEST,"w"),indent=1)
    return res
TEX={}
def load_textures():
    pngs=sorted(glob.glob(f"{A}/T_*.png"))
    if RUN.get("reimport",True) or not EAL.does_directory_exist("/Game/T"): imp(pngs,"/Game/T")
    for f in pngs:
        n=os.path.splitext(os.path.basename(f))[0]; t=unreal.load_asset(f"/Game/T/{n}")
        if t is None: log("missing tex",n); continue
        if n.endswith("_N"): t.set_editor_property("compression_settings",unreal.TextureCompressionSettings.TC_NORMALMAP); t.set_editor_property("srgb",False)
        elif n.endswith("_R") or "Mask" in n: t.set_editor_property("srgb",False)
        if "Mask" in n: t.set_editor_property("address_x",unreal.TextureAddress.TA_CLAMP); t.set_editor_property("address_y",unreal.TextureAddress.TA_CLAMP)
        EAL.save_loaded_asset(t); TEX[n]=t
PK=f"{ROOT}/packs"
def load_pack_textures():
    for sset in ["granite-boulders-tors","talus-cobble-wash","pine-needle-duff","granite-slabs-glaciated"]:
        tag=sset.split("-")[0]+sset.split("-")[1][:3]
        for mp in ["albedo","normal","roughness"]:
            src=f"{PK}/tex/{sset}/{mp}.png"; dst=f"/tmp/TP_{tag}_{mp}.png"
            import shutil; shutil.copy(src,dst)
        imp([f"/tmp/TP_{tag}_{mp}.png" for mp in ["albedo","normal","roughness"]],"/Game/TP",{f"/tmp/TP_{tag}_{mp}.png":f"{PK}/tex/{sset}/{mp}.png" for mp in ["albedo","normal","roughness"]})
        for mp in ["albedo","normal","roughness"]:
            n=f"TP_{tag}_{mp}"; t=unreal.load_asset(f"/Game/TP/{n}")
            if t is None: log("missing pack tex",n); continue
            if mp=="normal": sp(t,"compression_settings",unreal.TextureCompressionSettings.TC_NORMALMAP); sp(t,"srgb",False)
            if mp=="roughness": sp(t,"srgb",False)
            EAL.save_loaded_asset(t); TEX[n]=t
    log("pack textures",[k for k in TEX if k.startswith("TP_")])
PACKMESH={}; HIKER={}
def load_packs():
    files=glob.glob(f"{PK}/trees/*.glb")+sorted(glob.glob(f"{PK}/hypergrass/*.glb")+glob.glob(f"{PK}/arnklit/*.glb")+glob.glob(f"{PK}/pvrocks/*.glb")+glob.glob(f"{PK}/shrubs/*.glb")+glob.glob(f"{PK}/evermotion/*.glb"))+glob.glob(f"{PK}/granite/*.glb")+glob.glob(f"{PK}/fern/*.gltf")+glob.glob(f"{PK}/grass/*.gltf")
    for g in files:
        n=os.path.splitext(os.path.basename(g))[0]; dest=f"/Game/Pack/{n}"
        if RUN.get("reimport_packs",False) or not EAL.does_directory_exist(dest): imp([g],dest)
        sms=[unreal.load_asset(p) for p in EAL.list_assets(dest,recursive=True,include_folder=False)]
        sms=[o for o in sms if isinstance(o,unreal.StaticMesh)]; sms.sort(key=lambda o:o.get_name()); PACKMESH[n]=sms
        log("pack",n,len(sms))
    # guard: Interchange glTF material instances with missing textures crash the renderer (UE-23902) -> patch with fallbacks
    nvt=0
    for p in EAL.list_assets("/Game/Pack",recursive=True,include_folder=False):
        o=unreal.load_asset(p)
        if isinstance(o,unreal.Texture2D):
            try:
                if o.get_editor_property("virtual_texture_streaming"):
                    o.set_editor_property("virtual_texture_streaming",False); EAL.save_loaded_asset(o); nvt+=1
            except Exception as e: log("vt",p,e)
    log("disabled VT on pack textures",nvt)
    fb=TEX.get("T_Needle_D")
    for p in EAL.list_assets("/Game/Pack",recursive=True,include_folder=False):
        o=unreal.load_asset(p)
        if isinstance(o,unreal.MaterialInstanceConstant):
            vals=list(o.get_editor_property("texture_parameter_values")); bad=0
            for i,tv in enumerate(vals):
                t=tv.get_editor_property("parameter_value")
                bad_=t is None or not isinstance(t,unreal.Texture)
                if not bad_:
                    try: bad_=(t.blueprint_get_size_x()<=0) if hasattr(t,"blueprint_get_size_x") else False
                    except Exception: bad_=True
                if bad_:
                    tv.set_editor_property("parameter_value",fb); vals[i]=tv; bad+=1
            if bad:
                o.set_editor_property("texture_parameter_values",vals); EAL.save_loaded_asset(o); log("patched MI",p,bad)
    if RUN.get("skip_hiker",False): log("skip_hiker: hiker import skipped"); return
    dest="/Game/Pack/hiker_male"
    if RUN.get("reimport_packs",False) or not EAL.does_directory_exist(dest): imp([f"{PK}/hiker/hiker_male.glb"],dest)
    for p in EAL.list_assets(dest,recursive=True,include_folder=False):
        o=unreal.load_asset(p)
        if isinstance(o,unreal.SkeletalMesh):
            HIKER["mesh"]=o
            try:  # 1629: strip glTF MIs (invalid NormalTexture -> SIGSEGV in FillUniformBuffer)
                _dm=unreal.load_asset("/Engine/EngineMaterials/DefaultMaterial"); _ms=list(o.get_editor_property("materials"))
                for _i,_sm in enumerate(_ms): _sm.set_editor_property("material_interface",_dm); _ms[_i]=_sm
                o.set_editor_property("materials",_ms); log("hiker mats stripped",len(_ms))
            except Exception as _e: log("hiker strip fail",_e)
        if isinstance(o,unreal.AnimSequence):
            HIKER.setdefault("anims",{})[o.get_name()]=o
    log("hiker",HIKER.get("mesh"),list(HIKER.get("anims",{}).keys()))
MESH={}
def load_meshes():
    glbs=sorted(glob.glob(f"{A}/*.glb"))
    for g in glbs:
        n=os.path.splitext(os.path.basename(g))[0]; dest=f"/Game/Mesh/{n}"
        if RUN.get("reimport",True) or not EAL.does_directory_exist(dest): imp([g],dest)
        sms=[]
        for p in EAL.list_assets(dest,recursive=True,include_folder=False):
            o=unreal.load_asset(p)
            if isinstance(o,unreal.StaticMesh): sms.append(o)
        sms.sort(key=lambda o:o.get_name()); MESH[n]=sms; log("mesh",n,[o.get_name() for o in sms])
# ---------------- material helpers ----------------
def newmat(name):
    p=f"/Game/M/{name}"
    if EAL.does_asset_exist(p) and name.startswith(("M_Hiker","M_Pack")):  # 1631: no force-delete (SIGSEGV)
        import time as _t; name=f"{name}_{int(_t.time()*1000)%10000000}"
    elif EAL.does_asset_exist(p): EAL.delete_asset(p)
    return AT.create_asset(name,"/Game/M",unreal.Material,unreal.MaterialFactoryNew())
def nd(m,cls,**kw):
    n=MEL.create_material_expression(m,cls,0,0)
    for k,v in kw.items(): n.set_editor_property(k,v)
    return n
def cn(a,b,inp,out=""): MEL.connect_material_expressions(a,out,b,inp)
def prop(m,a,p,out=""): MEL.connect_material_property(a,out,p)
def C(m,v):
    if isinstance(v,(list,tuple)): return nd(m,unreal.MaterialExpressionConstant3Vector,constant=unreal.LinearColor(v[0],v[1],v[2],1))
    return nd(m,unreal.MaterialExpressionConstant,r=float(v))
def S(m,name,v): return nd(m,unreal.MaterialExpressionScalarParameter,parameter_name=name,default_value=float(v))
def V(m,name,v): return nd(m,unreal.MaterialExpressionVectorParameter,parameter_name=name,default_value=unreal.LinearColor(v[0],v[1],v[2],1))
def B(m,cls,a,b,ao="",bo=""):
    n=nd(m,cls); cn(a,n,"A",ao); cn(b,n,"B",bo); return n
def mul(m,a,b,ao="",bo=""): return B(m,unreal.MaterialExpressionMultiply,a,b,ao,bo)
def add(m,a,b,ao="",bo=""): return B(m,unreal.MaterialExpressionAdd,a,b,ao,bo)
def sub(m,a,b,ao="",bo=""): return B(m,unreal.MaterialExpressionSubtract,a,b,ao,bo)
def div(m,a,b,ao="",bo=""): return B(m,unreal.MaterialExpressionDivide,a,b,ao,bo)
def lerp(m,a,b,t,to=""):
    n=nd(m,unreal.MaterialExpressionLinearInterpolate); cn(a,n,"A"); cn(b,n,"B"); cn(t,n,"Alpha",to); return n
def sat(m,a): n=nd(m,unreal.MaterialExpressionSaturate); cn(a,n,""); return n
def mask(m,a,r=False,g=False,b=False):
    n=nd(m,unreal.MaterialExpressionComponentMask,r=r,g=g,b=b,a=False); cn(a,n,""); return n
def tex(m,name,uv,kind="color"):
    t=nd(m,unreal.MaterialExpressionTextureSample,texture=TEX[name])
    t.set_editor_property("sampler_type",{"color":unreal.MaterialSamplerType.SAMPLERTYPE_COLOR,"normal":unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL,"linear":unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR}[kind])
    if uv is not None: cn(uv,t,"UVs")
    return t
def uvmesh(m,tile): return nd(m,unreal.MaterialExpressionTextureCoordinate,u_tiling=tile,v_tiling=tile)
def wp(m): return nd(m,unreal.MaterialExpressionWorldPosition)
def finish(m):
    MEL.layout_material_expressions(m); MEL.recompile_material(m); return m  # no save: thumbnail SIGSEGV fix 1627
AX={"sy":1.0}
def wetness(m,band_m):
    w=wp(m); x=mask(m,w,r=True); z=mask(m,w,b=True)
    zw=sub(m,C(m,PL["water_z0"]*100.0),mul(m,x,C(m,PL["slope"])))
    band=C(m,band_m*100.0)
    return sat(m,div(m,sub(m,add(m,zw,band),z),band))
def mat_granite(name,tile):
    g=P["granite"]; m=newmat(name); uv=uvmesh(m,tile)
    GD="T_PG_D" if "T_PG_D" in TEX else "T_Granite_D"
    d=tex(m,GD,uv); dm=tex(m,"T_Granite_D",uvmesh(m,tile*0.17))
    col=mul(m,mul(m,d,dm),V(m,"Tint",g["tint"])); col=mul(m,col,C(m,0.9 if GD.startswith("T_PG") else 1.6))
    wet=wetness(m,g["wet_band"])
    wetcol=mul(m,col,S(m,"WetDark",g["wet_dark"]))
    prop(m,lerp(m,col,wetcol,wet),unreal.MaterialProperty.MP_BASE_COLOR)
    r=tex(m,"T_PG_R" if "T_PG_R" in TEX else "T_Granite_R",uv,"linear"); rr=mul(m,r,S(m,"Rough",g["rough"]/0.67))
    prop(m,lerp(m,rr,S(m,"WetRough",g["wet_rough"]),wet,),unreal.MaterialProperty.MP_ROUGHNESS)
    n=tex(m,"T_PG_N" if "T_PG_N" in TEX else "T_Granite_N",uv,"normal"); prop(m,lerp(m,n,C(m,[0,0,1]),mul(m,wet,C(m,0.4))),unreal.MaterialProperty.MP_NORMAL)
    return finish(m)
def mat_terrain():
    m=newmat("M_Terrain"); ds=P["dust"]
    w=wp(m); xy=mask(m,w,r=True,g=True)
    # mask uv: u=(x/100+L/2)/L, v=(W/2 - sy*y/100)/W
    xm=mask(m,w,r=True); ym=mask(m,w,g=True)
    u=div(m,add(m,div(m,xm,C(m,100)),C(m,PL["L"]/2)),C(m,PL["L"]))
    v=div(m,sub(m,C(m,PL["W"]/2),mul(m,ym,C(m,AX["sy"]/100.0))),C(m,PL["W"]))
    app=nd(m,unreal.MaterialExpressionAppendVector); cn(u,app,"A"); cn(v,app,"B")
    mk=tex(m,"T_TerrainMask",app,"linear")
    uvd=div(m,xy,C(m,250.0)); uvp=div(m,xy,C(m,90.0))
    dust=mul(m,tex(m,"T_Dust_D",uvd),V(m,"DustTint",ds["tint"]))
    dust=mul(m,dust,tex(m,"T_Dust_D",div(m,xy,C(m,2300.0))))
    dust=mul(m,dust,C(m,1.5))
    grass=tex(m,"T_PD_D",div(m,xy,C(m,200.0))) if "T_PD_D" in TEX else mul(m,dust,C(m,[0.85,0.78,0.5]))
    peb=tex(m,"T_PT_D",div(m,xy,C(m,160.0))) if "T_PT_D" in TEX else tex(m,"T_Pebble_D",uvp)
    base=lerp(m,mul(m,dust,C(m,0.9)),grass,mul(m,mask(m,mk,b=True),C(m,0.45))); base=lerp(m,base,(tex(m,"T_DG_D",div(m,xy,C(m,180.0))) if "T_DG_D" in TEX else mul(m,dust,C(m,1.12))),mask(m,mk,g=True)); base=lerp(m,base,peb,mask(m,mk,r=True))
    mac=tex(m,"T_Dust_D",div(m,xy,C(m,7000.0))); mac2=tex(m,"T_Granite_D",div(m,xy,C(m,3100.0)))
    base=mul(m,base,lerp(m,C(m,0.72),C(m,1.22),mask(m,mul(m,mac,mac2),r=True)))   # macro variation, breaks tiling
    wet=wetness(m,0.12); damp=wetness(m,0.9)
    moss=mul(m,base,C(m,[0.55,0.62,0.4]))
    base=lerp(m,base,moss,mul(m,damp,C(m,0.6)))
    prop(m,lerp(m,base,mul(m,base,C(m,0.5)),wet),unreal.MaterialProperty.MP_BASE_COLOR)
    rough=lerp(m,S(m,"DustRough",ds["rough"]),C(m,0.55),mask(m,mk,r=True)); prop(m,lerp(m,rough,C(m,0.12),wet),unreal.MaterialProperty.MP_ROUGHNESS)
    nrm=lerp(m,tex(m,"T_Dust_N",uvd,"normal"),tex(m,"T_Pebble_N",uvp,"normal"),mask(m,mk,r=True)); prop(m,nrm,unreal.MaterialProperty.MP_NORMAL)
    return finish(m)
def mat_water():
    wpar=P["water"]; m=newmat("M_Water")
    m.set_editor_property("blend_mode",unreal.BlendMode.BLEND_TRANSLUCENT)
    m.set_editor_property("translucency_lighting_mode",unreal.TranslucencyLightingMode.TLM_SURFACE_PER_PIXEL_LIGHTING)
    try: m.set_editor_property("refraction_method",unreal.RefractionMode.RM_INDEX_OF_REFRACTION)
    except Exception as e: log("refraction_method",e)
    w=wp(m); xy=mask(m,w,r=True,g=True); t=nd(m,unreal.MaterialExpressionTime)
    sp=S(m,"FlowSpeed",wpar["flow_speed"])
    def panned(scale,speed,offs):
        uv=div(m,xy,C(m,scale)); flow=mul(m,mul(m,t,sp),C(m,[-speed,-offs,0]))
        f2=mask(m,flow,r=True,g=True); return add(m,uv,f2)
    n1=tex(m,"T_Water_N",panned(220.0,1.0,0.05),"normal"); n2=tex(m,"T_Water_N",panned(70.0,2.3,-0.12),"normal")
    nn=lerp(m,n1,n2,C(m,0.5)); nf=lerp(m,C(m,[0,0,1]),nn,S(m,"NormalStrength",wpar["normal_strength"]))
    prop(m,nf,unreal.MaterialProperty.MP_NORMAL)
    fd=nd(m,unreal.MaterialExpressionDepthFade); cn(C(m,1.0),fd,"InOpacity"); cn(C(m,18.0),fd,"FadeDistance")
    fn=tex(m,"T_Water_N",panned(45.0,3.0,0.2),"normal")
    foam=sat(m,mul(m,mul(m,sub(m,C(m,1.0),fd),mask(m,fn,r=True)),C(m,2.2)))
    prop(m,lerp(m,mul(m,V(m,"Tint",wpar["tint"]),C(m,0.08)),C(m,[0.85,0.87,0.86]),foam),unreal.MaterialProperty.MP_BASE_COLOR)
    prop(m,S(m,"Rough",wpar["roughness"]),unreal.MaterialProperty.MP_ROUGHNESS)
    prop(m,C(m,0.5),unreal.MaterialProperty.MP_SPECULAR)
    fr=nd(m,unreal.MaterialExpressionFresnel,exponent=5.0)
    op=add(m,lerp(m,S(m,"Opacity",wpar["opacity"]),C(m,0.95),fr),mul(m,foam,C(m,0.8)))
    df=nd(m,unreal.MaterialExpressionDepthFade); cn(op,df,"InOpacity"); cn(C(m,10.0),df,"FadeDistance")
    prop(m,df,unreal.MaterialProperty.MP_OPACITY)
    prop(m,S(m,"IOR",wpar["ior"]),unreal.MaterialProperty.MP_REFRACTION)
    return finish(m)
def mat_simple(name,texn,tile,rough,foliage=False,tint=None):
    m=newmat(name); c=tex(m,texn,uvmesh(m,tile))
    if tint: c=mul(m,c,C(m,tint))
    prop(m,c,unreal.MaterialProperty.MP_BASE_COLOR); prop(m,C(m,rough),unreal.MaterialProperty.MP_ROUGHNESS)
    if foliage:
        m.set_editor_property("shading_model",unreal.MaterialShadingModel.MSM_TWO_SIDED_FOLIAGE); m.set_editor_property("two_sided",True)
        prop(m,mul(m,c,C(m,[1.6,2.2,0.8])),unreal.MaterialProperty.MP_SUBSURFACE_COLOR)
    return finish(m)
# ---------------- level ----------------
EAS=unreal.get_editor_subsystem(unreal.EditorActorSubsystem); LES=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
def V3(p): return unreal.Vector(p[0]*100.0,p[1]*100.0*AX["sy"],p[2]*100.0)
def look(pos,tgt):
    d=[tgt[i]-pos[i] for i in range(3)]; d[1]*=AX["sy"]
    yaw=math.degrees(math.atan2(d[1],d[0])); pitch=math.degrees(math.atan2(d[2],math.hypot(d[0],d[1])))
    return unreal.Rotator(roll=0.0,pitch=pitch,yaw=yaw)
def spawn_mesh(sm,loc,rot,scale,mat):
    a=EAS.spawn_actor_from_object(sm,loc,rot); a.set_actor_scale3d(unreal.Vector(scale,scale,scale))
    c=a.static_mesh_component
    for i in range(max(1,c.get_num_materials())): c.set_material(i,mat)
    return a
def build():
    mark("build_start")
    load_textures(); load_meshes()
    # axis detection from probe at my (20,10,5)m
    pb=MESH["probe"][0].get_bounds(); o=pb.origin; log("probe origin",o.x,o.y,o.z)
    if abs(o.x-2000)<200 and abs(abs(o.y)-1000)<200: AX["sy"]=1.0 if o.y>0 else -1.0
    else: AX["swap"]=True; log("WARNING axis mapping unexpected",o)
    log("axis sy",AX["sy"]); json.dump(AX,open(f"{ROOT}/axis.json","w"))
    MG=mat_granite("M_Granite",1.0); MD=mat_granite("M_Dome",0.25); MT=mat_terrain(); MW=mat_water()
    load_packs()
    MWOOD=mat_simple("M_Wood","T_Bark_D",0.6,0.85,tint=[0.42,0.38,0.34])
    MB=mat_simple("M_Bark","T_BK_D" if "T_BK_D" in TEX else "T_Bark_D",1.0,0.85); MF=mat_simple("M_Needle","T_Needle_D",1.0,0.7,True)
    mark("materials_ok")
    if EAL.does_asset_exist("/Game/Maps/Creek"):
        LES.new_level("/Game/Maps/Tmp_"+str(os.getpid())) if False else None
        EAL.delete_asset("/Game/Maps/Creek")
    ok=LES.new_level("/Game/Maps/Creek"); log("new_level",ok)
    if not ok: raise RuntimeError("new_level failed")
    spawn_mesh(MESH["terrain"][0],unreal.Vector(0,0,0),unreal.Rotator(),1.0,MT)
    wa=spawn_mesh(MESH["water"][0],unreal.Vector(0,0,0),unreal.Rotator(),1.0,MW)
    for it in PL["meshes"]:
        loc=V3([it["x"],it["y"],it["z"]]); rot=unreal.Rotator(roll=0.0,pitch=0.0,yaw=it["yaw"])
        if any(it["mesh"].startswith(p_) for p_ in RUN.get("skip_packs",[])): continue
        if it["kind"] in ("tree","plant"):
            for sm in PACKMESH.get(it["mesh"],[]):
                a=EAS.spawn_actor_from_object(sm,loc,rot); a.set_actor_scale3d(unreal.Vector(it["s"],it["s"],it["s"]))
                sk=RUN.get("safe_packs",[])
                if any(it["mesh"].startswith(p_) for p_ in sk):
                    c_=a.static_mesh_component
                    for i_ in range(max(1,c_.get_num_materials())): c_.set_material(i_,MG if ("arnklit" in it["mesh"] or "boulder" in it["mesh"] or "rock" in it["mesh"]) else MF)
            continue
        if it["kind"]=="hero_granite":
            for sm in PACKMESH.get(it["mesh"],[]): spawn_mesh(sm,loc,rot,it["s"],MG)
            continue
        if it["kind"]=="bridge": spawn_mesh(MESH["bridge"][0],loc,rot,1.0,MWOOD); continue
        sms=MESH[it["mesh"]]
        if it["kind"]=="pine":
            spawn_mesh(sms[0],loc,rot,it["s"],MB); spawn_mesh(sms[1] if len(sms)>1 else sms[0],loc,rot,it["s"],MF)
        elif it["kind"]=="skirt":
            spawn_mesh(sms[0],loc,rot,1.0,MT)
        elif it["kind"]=="dome" and RUN.get("hide_dome",False): log("hide_dome: skipped backdrop ridge"); continue
        elif it["kind"]=="dome":
            for sm in sms: spawn_mesh(sm,loc,rot,it["s"],MD)
        else: spawn_mesh(sms[0],loc,rot,it["s"],MG)
    L=P["light"]
    sun=EAS.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,1000))
    sc=sun.get_component_by_class(unreal.DirectionalLightComponent)
    sc.set_mobility(unreal.ComponentMobility.MOVABLE); sc.set_intensity(L["sun_lux"]); sc.set_use_temperature(True); sc.set_temperature(L["sun_temp"])
    for k,v in [("atmosphere_sun_light",True),("enable_light_shaft_bloom",True),("cast_shadows",True)]:
        try: sc.set_editor_property(k,v)
        except Exception as e: log(k,e)
    # sun yaw: base = direction from hero target toward hero camera (backlit), plus offset
    h=PL["shots"][0]; dx=h["pos"][0]-h["tgt"][0]; dy=(h["pos"][1]-h["tgt"][1])*AX["sy"]
    sun.set_actor_rotation(unreal.Rotator(roll=0.0,pitch=L["sun_pitch"],yaw=math.degrees(math.atan2(dy,dx))+L["sun_yaw"]),False)
    EAS.spawn_actor_from_class(unreal.SkyAtmosphere,unreal.Vector(0,0,0))
    sky=EAS.spawn_actor_from_class(unreal.SkyLight,unreal.Vector(0,0,500)); skc=sky.get_component_by_class(unreal.SkyLightComponent)
    skc.set_mobility(unreal.ComponentMobility.MOVABLE); sp(skc,"real_time_capture",True); skc.set_intensity(L["sky_int"])
    fog=EAS.spawn_actor_from_class(unreal.ExponentialHeightFog,unreal.Vector(0,0,0)); fc=fog.get_component_by_class(unreal.ExponentialHeightFogComponent)
    sp(fc,"fog_density",L["fog_density"]); sp(fc,"enable_volumetric_fog",True) or sp(fc,"volumetric_fog",True); sp(fc,"fog_height_falloff",0.25)
    sp(fc,"fog_inscattering_luminance",unreal.LinearColor(*L["fog_inscatter"],1.0)) or sp(fc,"fog_inscattering_color",unreal.LinearColor(*L["fog_inscatter"],1.0))
    try: fc.set_editor_property("volumetric_fog_albedo",unreal.Color(255,int(255*0.85),int(255*0.65),255))
    except Exception as e: log("fogalbedo",e)
    try: EAS.spawn_actor_from_class(unreal.VolumetricCloud,unreal.Vector(0,0,0))
    except Exception as e: log("cloud",e)
    ppv=EAS.spawn_actor_from_class(unreal.PostProcessVolume,unreal.Vector(0,0,0)); ppv.set_editor_property("unbound",True)
    s=ppv.settings
    for k,v in [("override_auto_exposure_bias",True),("auto_exposure_bias",L["exposure_bias"]),("override_bloom_intensity",True),("bloom_intensity",0.6),
                ("override_vignette_intensity",True),("vignette_intensity",0.3),("override_white_temp",True),("white_temp",6200.0)]:
        try: s.set_editor_property(k,v)
        except Exception as e: log("pp",k,e)
    ppv.settings=s
    mark("level_ok")
    make_sequences()
    LES.save_current_level(); EAL.save_directory("/Game",only_if_is_dirty=True,recursive=True)
    mark("saved")
def add_track(seq,cls):
    for fn in ("add_track","add_master_track"):
        if hasattr(seq,fn):
            try: return getattr(seq,fn)(cls)
            except Exception as e: log(fn,e)
def binding_id(seq,b):
    for f in (lambda: seq.get_binding_id(b), lambda: seq.make_binding_id(b,unreal.MovieSceneObjectBindingSpace.LOCAL),
              lambda: unreal.MovieSceneSequenceExtensions.get_portable_binding_id(seq,seq,b)):
        try: return f()
        except Exception as e: log("bid",e)
def add_hiker(seq,hkeys,nframes,constant,play_rate):
    if RUN.get("skip_hiker",False): log("skip_hiker: no hiker/pack/hat"); return
    if "mesh" not in HIKER: log("no hiker mesh"); return
    h=EAS.spawn_actor_from_class(unreal.SkeletalMeshActor,V3(hkeys[0]["pos"]))
    h.skeletal_mesh_component.set_skeletal_mesh_asset(HIKER["mesh"]) if hasattr(h.skeletal_mesh_component,"set_skeletal_mesh_asset") else h.skeletal_mesh_component.set_skeletal_mesh(HIKER["mesh"])
    smc=h.skeletal_mesh_component; nm=smc.get_num_materials()
    names=[str(n) for n in smc.get_material_slot_names()] if hasattr(smc,"get_material_slot_names") else []
    log("hiker slots",nm,names)
    for i in range(nm):
        nmi=(names[i].lower() if i<len(names) else "")
        if "body" in nmi or "skin" in nmi: smc.set_material(i,OUTFIT())
        elif "hair" in nmi: smc.set_material(i,HMAT([0.06,0.045,0.035],i))
        else: smc.set_material(i,HMAT([0.05,0.04,0.035],i))   # eyes etc: never leave a glTF MI on the hiker (its BaseColorTexture is invalid -> MRQ crash)
    b=seq.add_spawnable_from_instance(h)
    ok_=False
    if RUN.get("attach_gear",True):
        try: ok_=add_gear_attached(seq,b,h,nframes)
        except Exception as e: log("attach gear failed",traceback.format_exc()[-600:])
    EAS.destroy_actor(h)
    if not ok_:
        try: add_gear(seq,hkeys,nframes,constant)
        except Exception as e: log("gear failed",e)
    walk=[a for n,a in HIKER.get("anims",{}).items() if "walk" in n.lower()]
    idle=[a for n,a in HIKER.get("anims",{}).items() if n.lower()=="idle" or n.lower().endswith("_idle") and "talk" not in n.lower()]
    segs=PL.get("anim_segments") if (nframes==PL.get("walk_frames") and not constant) else None
    if segs and walk:
        at=b.add_track(unreal.MovieSceneSkeletalAnimationTrack)
        for sg in segs:
            an=walk[0] if sg["anim"]=="walk" or not idle else idle[0]
            asec=at.add_section(); asec.set_range(sg["start"],sg["end"]); pr=asec.params; pr.animation=an
            if sg["anim"]=="walk": set_rate(pr,play_rate)
            asec.params=pr
        log("hiker segments",len(segs),"idle",bool(idle)); walk=None
    if walk:
        at=b.add_track(unreal.MovieSceneSkeletalAnimationTrack); asec=at.add_section(); asec.set_range(0,nframes)
        pr=asec.params; pr.animation=walk[0]; set_rate(pr,play_rate)
        if False:
            ok=False
            for mk in (lambda: unreal.MovieSceneTimeWarpVariant(play_rate), lambda: unreal.MovieSceneTimeWarpVariant(fixed_play_rate=play_rate)):
                try: pr.play_rate=mk(); ok=True; break
                except Exception as e: log("playrate try",e)
            if not ok:
                try:
                    v=pr.play_rate; log("timewarp props",[p for p in dir(v) if not p.startswith("_")][:30])
                except Exception as e: log("tw",e)
        asec.params=pr
        log("hiker anim",walk[0].get_name(),"len",walk[0].get_play_length() if hasattr(walk[0],"get_play_length") else "?")
    tt=b.add_track(unreal.MovieScene3DTransformTrack); ts=tt.add_section(); ts.set_range(0,nframes); ch=ts.get_all_channels()
    interp=unreal.MovieSceneKeyInterpolation.CONSTANT if constant else unreal.MovieSceneKeyInterpolation.LINEAR
    prev=None
    for k in hkeys:
        loc=V3(k["pos"]); yaw=k["yaw"]*AX["sy"]+HIKER_YAW
        if prev is not None:
            while yaw-prev>180: yaw-=360
            while yaw-prev<-180: yaw+=360
        prev=yaw
        for i,v in enumerate([loc.x,loc.y,loc.z,0.0,0.0,yaw]): ch[i].add_key(unreal.FrameNumber(k["f"]),v,0.0,unreal.MovieSceneTimeUnit.DISPLAY_RATE,interp)
_OF=[]
def OUTFIT():
    if _OF: return _OF[0]
    m=newmat("M_HikerOutfit")
    lz=add(m,mask(m,sub(m,wp(m),nd(m,unreal.MaterialExpressionObjectPositionWS)),b=True),C(m,95.0))   # mesh origin sits at the hips (~95 cm), measured in the safety walk
    def band(z0): return sat(m,div(m,sub(m,lz,C(m,z0)),C(m,3.0)))
    boots=C(m,[0.07,0.045,0.03]); pants=C(m,[0.035,0.032,0.03]); belt=C(m,[0.1,0.08,0.06])
    # flannel shirt: red/black check from world-space sin pattern
    w=wp(m); sx=nd(m,unreal.MaterialExpressionSine,period=14.0); cn(mask(m,w,r=True),sx,""); sy=nd(m,unreal.MaterialExpressionSine,period=14.0); cn(mask(m,w,b=True),sy,"")
    chk=sat(m,mul(m,add(m,sx,sy),C(m,2.0))); shirt=lerp(m,C(m,RUN.get("shirt_a",[0.17,0.17,0.13])),C(m,RUN.get("shirt_b",[0.10,0.10,0.08])),mul(m,chk,C(m,0.55)))
    skin=C(m,[0.42,0.26,0.18])
    col=lerp(m,boots,pants,band(16.0)); col=lerp(m,col,belt,band(97.0)); col=lerp(m,col,shirt,band(101.0)); col=lerp(m,col,skin,band(149.0))
    prop(m,col,unreal.MaterialProperty.MP_BASE_COLOR); prop(m,C(m,0.85),unreal.MaterialProperty.MP_ROUGHNESS)
    _OF.append(finish(m)); return _OF[0]
def add_gear(seq,hkeys,nframes,constant):
    MP=HMAT([0.06,0.11,0.06],90)  # dark green pack, distinct from shirt (1628); MH=HMAT([0.55,0.45,0.3],91)
    real_pack="T_Pack_D" in TEX
    for nm,mat,fwd,up,sc,yo in (("backpack",MP,(-0.27 if real_pack else -0.20),(0.82 if real_pack else 1.22),(0.72 if real_pack else 1.0),float(RUN.get("pack_yaw",0.0))),("hat",MH,0.0,1.66,1.0,0.0)):
        if nm not in MESH: log("no gear mesh",nm); continue
        a=EAS.spawn_actor_from_object(MESH[nm][0],V3(hkeys[0]["pos"]),unreal.Rotator())
        for i_ in range(max(1,a.static_mesh_component.get_num_materials())): a.static_mesh_component.set_material(i_,mat)
        a.static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE); a.set_actor_scale3d(unreal.Vector(sc,sc,sc))
        b=seq.add_spawnable_from_instance(a); EAS.destroy_actor(a)
        tt=b.add_track(unreal.MovieScene3DTransformTrack); ts=tt.add_section(); ts.set_range(0,nframes); ch=ts.get_all_channels()
        interp=unreal.MovieSceneKeyInterpolation.CONSTANT if constant else unreal.MovieSceneKeyInterpolation.LINEAR
        prev=None
        for k in hkeys:
            ya=math.radians(k["yaw"]); p=[k["pos"][0]+fwd*math.cos(ya),k["pos"][1]+fwd*math.sin(ya),k["pos"][2]+up]
            loc=V3(p); yaw=k["yaw"]*AX["sy"]
            if prev is not None:
                while yaw-prev>180: yaw-=360
                while yaw-prev<-180: yaw+=360
            prev=yaw
            for i,v in enumerate([loc.x,loc.y,loc.z,0.0,0.0,yaw+yo]): ch[i].add_key(unreal.FrameNumber(k["f"]),v,0.0,unreal.MovieSceneTimeUnit.DISPLAY_RATE,interp)
            for i,v in enumerate([sc,sc,sc]):
                if len(ch)>6+i: ch[6+i].add_key(unreal.FrameNumber(k["f"]),v,0.0,unreal.MovieSceneTimeUnit.DISPLAY_RATE,interp)
    log("gear ok")
HIKER_YAW=float(RUN.get("hiker_yaw",-90.0))
def _pick_bone(names,prefs,must,bad=()):
    low=[n.lower() for n in names]
    for pf in prefs:
        for i,n in enumerate(low):
            if n.endswith(pf) and not any(x in n for x in bad): return names[i]
    c=[names[i] for i,n in enumerate(low) if must in n and not any(x in n for x in bad)]
    return c[-1] if c else None
def add_gear_attached(seq,hb,h,nframes):
    smc=h.skeletal_mesh_component
    nb=smc.get_num_bones(); names=[str(smc.get_bone_name(i)) for i in range(nb)]
    log("hiker bones",nb,names)
    spine=RUN.get("pack_bone") or _pick_bone(names,["spine2","spine_03","spine03","upperchest","chest","spine1"],"spine")
    head=RUN.get("hat_bone") or _pick_bone(names,["head"],"head",("end","top","nub"))
    log("gear bones spine",spine,"head",head)
    if not spine or not head: return False
    # temp hiker in canonical frame: origin, yaw=HIKER_YAW (== walk key yaw 0)
    h.set_actor_location_and_rotation(unreal.Vector(0,0,0),unreal.Rotator(roll=0.0,pitch=0.0,yaw=HIKER_YAW),False,False)
    MP=HMAT([0.06,0.11,0.06],90); MH=HMAT([0.36,0.30,0.22],91)
    real_pack="T_Pack_D" in TEX
    for nm,mat,bone,fwd,up,sc,yo in (("backpack",MP,spine,float(RUN.get("pack_fwd",-0.27 if real_pack else -0.20)),float(RUN.get("pack_up",0.82 if real_pack else 1.22)),(0.72 if real_pack else 1.0),float(RUN.get("pack_yaw",180.0))),
                                    ("hat",MH,head,float(RUN.get("hat_fwd",0.0)),float(RUN.get("hat_up",1.66)),1.0,0.0)):
        if nm not in MESH: log("no gear mesh",nm); continue
        bt=smc.get_socket_transform(bone,unreal.RelativeTransformSpace.RTS_WORLD)
        want=unreal.Transform(unreal.Vector(fwd*100.0,0.0,up*100.0),unreal.Rotator(roll=0.0,pitch=0.0,yaw=yo),unreal.Vector(sc,sc,sc))
        rel=unreal.MathLibrary.make_relative_transform(want,bt)
        rl=rel.translation; rr=rel.rotation.rotator(); rs=rel.scale3d
        log("gear",nm,"bone",bone,"boneW",bt.translation,"rel",rl,rr,rs)
        a=EAS.spawn_actor_from_object(MESH[nm][0],unreal.Vector(0,0,0),unreal.Rotator())
        for i_ in range(max(1,a.static_mesh_component.get_num_materials())): a.static_mesh_component.set_material(i_,mat)
        a.static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE)
        gb=seq.add_spawnable_from_instance(a); EAS.destroy_actor(a)
        at=gb.add_track(unreal.MovieScene3DAttachTrack); sec=at.add_section(); sec.set_range(0,nframes)
        sec.set_constraint_binding_id(binding_id(seq,hb)); sec.set_editor_property("attach_socket_name",bone)
        tt=gb.add_track(unreal.MovieScene3DTransformTrack); ts=tt.add_section(); ts.set_range(0,nframes); ch=ts.get_all_channels()
        for i,v in enumerate([rl.x,rl.y,rl.z,rr.roll,rr.pitch,rr.yaw,rs.x,rs.y,rs.z]):
            if i<len(ch): ch[i].add_key(unreal.FrameNumber(0),v,0.0,unreal.MovieSceneTimeUnit.DISPLAY_RATE,unreal.MovieSceneKeyInterpolation.CONSTANT)
    log("gear attached ok"); return True
_HM={}
def HMAT(col,i):
    k=tuple(col)
    if k in _HM: return _HM[k]
    m=newmat(f"M_Hiker{len(_HM)}"); prop(m,C(m,col),unreal.MaterialProperty.MP_BASE_COLOR); prop(m,C(m,0.75),unreal.MaterialProperty.MP_ROUGHNESS)
    _HM[k]=finish(m); return _HM[k]
def set_rate(pr,rate):
    if abs(rate-1.0)<1e-3: return
    for mk in (lambda: unreal.MovieSceneTimeWarpVariant(rate), lambda: unreal.MovieSceneTimeWarpVariant(fixed_play_rate=rate)):
        try: pr.play_rate=mk(); log("play rate set",rate); return
        except Exception as e: log("playrate try",e)
    try:
        v=pr.play_rate; log("timewarp props",[p for p in dir(v) if not p.startswith("_")][:40])
        for m_ in ("set_fixed_play_rate","set"):
            if hasattr(v,m_): getattr(v,m_)(rate); pr.play_rate=v; log("play rate via",m_); return
    except Exception as e: log("tw",e)
def make_seq(name,keys,nframes,constant,fl,fps=24,hiker=None,play_rate=1.0):
    p=f"/Game/Cine/{name}"
    if EAL.does_asset_exist(p): EAL.delete_asset(p)
    seq=AT.create_asset(name,"/Game/Cine",unreal.LevelSequence,unreal.LevelSequenceFactoryNew())
    seq.set_display_rate(unreal.FrameRate(fps,1)); seq.set_playback_start(0); seq.set_playback_end(nframes)
    cam=EAS.spawn_actor_from_class(unreal.CineCameraActor,V3(keys[0][1]),look(keys[0][1],keys[0][2])); cam.set_actor_label("Cam_"+name)
    cc=cam.get_cine_camera_component(); cc.set_editor_property("current_focal_length",float(fl)); cc.set_editor_property("current_aperture",5.6)
    fs=cc.focus_settings; fs.focus_method=unreal.CameraFocusMethod.MANUAL
    d=math.dist(keys[0][1],keys[0][2])*100; fs.manual_focus_distance=d; cc.focus_settings=fs
    b=seq.add_spawnable_from_instance(cam); EAS.destroy_actor(cam)
    cut=add_track(seq,unreal.MovieSceneCameraCutTrack); cs=cut.add_section(); cs.set_range(0,nframes); cs.set_camera_binding_id(binding_id(seq,b))
    tt=b.add_track(unreal.MovieScene3DTransformTrack); ts=tt.add_section(); ts.set_range(0,nframes)
    ch=ts.get_all_channels()
    interp=unreal.MovieSceneKeyInterpolation.CONSTANT if constant else unreal.MovieSceneKeyInterpolation.AUTO
    for f,pos,tgt in keys:
        loc=V3(pos); r=look(pos,tgt); vals=[loc.x,loc.y,loc.z,r.roll,r.pitch,r.yaw]
        for i,v in enumerate(vals): ch[i].add_key(unreal.FrameNumber(f),v,0.0,unreal.MovieSceneTimeUnit.DISPLAY_RATE,interp)
    if hiker: add_hiker(seq,hiker,nframes,constant,play_rate)
    EAL.save_loaded_asset(seq); return seq
HOLD=24
def make_sequences():
    sh=PL["shots"]
    # stills: each shot held HOLD frames (Lumen/TAA settle); last frame of each hold is the still
    hs=PL["hiker_still"]; still_h=[{"f":0,"pos":hs,"yaw":90.0}]
    make_seq("SeqStills",[(i*HOLD,s["pos"],s["tgt"]) for i,s in enumerate(sh)],len(sh)*HOLD,True,sh[0]["fl"],24,still_h,1.0)
    make_seq("SeqWalk",[(k["f"],k["pos"],k["tgt"]) for k in PL["walk"]],PL["walk_frames"],False,24,PL["walk_fps"],PL["hiker_walk"],float(RUN.get("walk_rate",1.375)))
    mark("seq_ok")
# ---------------- render ----------------
EXE=None
def render(seqname,outdir,res,temporal,cvars):
    global EXE
    sub=unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem); q=sub.get_queue(); q.delete_all_jobs()
    job=q.allocate_new_job(unreal.MoviePipelineExecutorJob)
    job.map=unreal.SoftObjectPath("/Game/Maps/Creek.Creek"); job.sequence=unreal.SoftObjectPath(f"/Game/Cine/{seqname}.{seqname}"); job.job_name=seqname
    cfg=job.get_configuration()
    o=cfg.find_or_add_setting_by_class(unreal.MoviePipelineOutputSetting); o.output_directory=unreal.DirectoryPath(outdir)
    o.output_resolution=unreal.IntPoint(res[0],res[1]); o.file_name_format="{sequence_name}.{frame_number}"; o.override_existing_output=True
    if seqname=="SeqWalk" and RUN.get("walk_range"):
        a_,b_=RUN["walk_range"]; o.use_custom_playback_range=True; o.custom_start_frame=int(a_); o.custom_end_frame=int(b_); log("walk range",a_,b_)
    cfg.find_or_add_setting_by_class(unreal.MoviePipelineDeferredPassBase)
    cfg.find_or_add_setting_by_class(unreal.MoviePipelineImageSequenceOutput_PNG)
    aa=cfg.find_or_add_setting_by_class(unreal.MoviePipelineAntiAliasingSetting)
    aa.spatial_sample_count=1; aa.temporal_sample_count=temporal; aa.engine_warm_up_count=48; aa.render_warm_up_count=48; aa.use_camera_cut_for_warm_up=False
    cv=cfg.find_or_add_setting_by_class(unreal.MoviePipelineConsoleVariableSetting)
    for k,v in cvars.items():
        try: cv.add_or_update_console_variable(k,float(v))
        except Exception as e:
            try: m=cv.get_editor_property("console_variables"); m[k]=float(v); cv.set_editor_property("console_variables",m)
            except Exception as e2: log("cvar",k,e,e2)
    EXE=sub.render_queue_with_executor(unreal.MoviePipelinePIEExecutor)
    def done(exe,ok):
        mark(f"render_done {seqname} ok={ok}"); nxt()
    EXE.on_executor_finished_delegate.add_callable(done)
QUEUE=[]
def nxt():
    if QUEUE:
        a=QUEUE.pop(0); mark("render_start "+a[0]); render(*a)
    else:
        mark("ALL_DONE"); unreal.SystemLibrary.quit_editor()
CV={"r.Lumen.TranslucencyReflections.FrontLayer.Enable":1,"r.Lumen.Reflections.ScreenTraces":1,"r.LumenScene.Radiosity.ProbeSpacing":2,
    "r.Lumen.ScreenProbeGather.ScreenTraces.HZBTraversal.FullResDepth":1,"r.Shadow.Virtual.SMRT.RayCountDirectional":16,"r.VolumetricFog.GridPixelSize":4,
    "r.Lumen.Reflections.DownsampleFactor":1,"r.Lumen.TraceMeshSDFs":1,"r.MotionBlurQuality":0,"r.DepthOfFieldQuality":4,"r.Tonemapper.Sharpen":0.6}
CV.update(RUN.get("cvars",{}))
NOCOL=("grass","medium_0","patch_","short_0","tall_0","sprout","bracken","needlegrass","fern","water","chamise","manzanita","shrub")
def playtest_setup():  # live-1715: walkable first-person playtest (no C++/BP graph: input handled by a Python tick)
    nc=0; cx=0; seen=set()
    for a_ in EAS.get_all_level_actors():
        if not isinstance(a_,unreal.StaticMeshActor): continue
        c_=a_.static_mesh_component; sm=c_.static_mesh
        nm=(a_.get_actor_label()+" "+(sm.get_name() if sm else "")).lower()
        if any(k in nm for k in NOCOL): c_.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION); nc+=1; continue
        c_.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS); c_.set_collision_profile_name("BlockAll")
        if sm and sm.get_path_name() not in seen:
            seen.add(sm.get_path_name())
            try:
                bs=sm.get_editor_property("body_setup")
                if bs: bs.set_editor_property("collision_trace_flag",unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE); cx+=1
            except Exception as e: log("bodysetup",sm.get_name(),e)
    log("collision: complex-as-simple meshes",cx,"nocollision actors",nc)
    def mkbp(name,parent):
        pth=f"/Game/Play/{name}"
        if EAL.does_asset_exist(pth): return unreal.load_asset(pth)
        f=unreal.BlueprintFactory(); f.set_editor_property("parent_class",parent)
        return AT.create_asset(name,"/Game/Play",unreal.Blueprint,f)
    bw=mkbp("BP_Walker",unreal.Character); unreal.BlueprintEditorLibrary.compile_blueprint(bw)
    wc=unreal.BlueprintEditorLibrary.generated_class(bw); cdo=unreal.get_default_object(wc)
    cdo.set_editor_property("base_eye_height",float(RUN.get("eye_above_center",87.0)))  # capsule half-height 88 -> eye ~1.75 m
    cm=cdo.get_editor_property("character_movement")
    for k_,v_ in (("max_walk_speed",float(RUN.get("walk_speed",320.0))),("jump_z_velocity",420.0),("max_step_height",50.0),("air_control",0.3)):
        try: cm.set_editor_property(k_,v_)
        except Exception as e: log("cm",k_,e)
    try: cm.set_walkable_floor_angle(55.0)
    except Exception as e: log("floor angle",e)
    gm=mkbp("GM_Walk",unreal.GameModeBase); unreal.BlueprintEditorLibrary.compile_blueprint(gm)
    unreal.get_default_object(unreal.BlueprintEditorLibrary.generated_class(gm)).set_editor_property("default_pawn_class",wc)
    EAL.save_loaded_asset(bw); EAL.save_loaded_asset(gm)
    ws=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_world_settings()
    ws.set_editor_property("default_game_mode",unreal.BlueprintEditorLibrary.generated_class(gm))
    LES.save_current_level(); log("playtest setup saved"); mark("playtest_setup")
def _key(n):
    k=unreal.Key(); k.set_editor_property("key_name",n); return k
PT={"n":0,"keys":{}}
def playtest_tick(dt):
    PT["n"]+=1
    try:
        w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
        if w is None:
            try: w=unreal.EditorLevelLibrary.get_game_world()
            except Exception: w=None
        if w is None:
            if PT["n"]%300==0: log("pt: no game world")
            return
        pc=unreal.GameplayStatics.get_player_controller(w,0); ch=unreal.GameplayStatics.get_player_character(w,0)
        if pc is None or ch is None:
            if PT["n"]%300==0: log("pt: pc",pc,"ch",ch,"pawn",pc.get_controlled_pawn() if pc else None)
            return
        if not PT["keys"]: PT["keys"]={n:_key(n) for n in ("W","A","S","D","SpaceBar","LeftShift","Up","Down","Left","Right")}
        K=PT["keys"]; down=lambda n: pc.is_input_key_down(K[n])
        if PT["n"]%15==0: PT["inject"]=os.path.exists(f"{ROOT}/live_inject_w")
        fw=(1.0 if (down("W") or down("Up") or PT.get("inject")) else 0.0)-(1.0 if (down("S") or down("Down")) else 0.0)
        rt=(1.0 if (down("D") or down("Right")) else 0.0)-(1.0 if (down("A") or down("Left")) else 0.0)
        cr=pc.get_control_rotation(); yaw=math.radians(cr.yaw)
        f=unreal.Vector(math.cos(yaw),math.sin(yaw),0.0); r=unreal.Vector(-math.sin(yaw),math.cos(yaw),0.0)
        cm=ch.get_editor_property("character_movement"); base=float(RUN.get("walk_speed",320.0))
        cm.set_editor_property("max_walk_speed",base*(2.0 if down("LeftShift") else 1.0))
        if fw: ch.add_movement_input(f,fw)
        if rt: ch.add_movement_input(r,rt)
        if down("SpaceBar"): ch.jump()
        md=pc.get_input_mouse_delta(); dx,dy=(md[0],md[1]) if isinstance(md,(tuple,list)) else (md.x,md.y)
        sens=float(RUN.get("mouse_sens",1.0))
        if dx: pc.add_yaw_input(dx*sens)
        if dy: pc.add_pitch_input(-dy*sens)
        if PT["n"]%300==0: log("pt",PT["n"],ch.get_actor_location(),cr.yaw,"fw",fw,"md",dx,dy)
    except Exception as e:
        PT["err"]=PT.get("err",0)+1
        if PT["err"]<5 or PT["err"]%300==0: log("playtest tick err",traceback.format_exc()[-400:])
def interactive():  # live-1708: open Creek, PlayerStart at the bridge approach, PIE in a new window, never quit
    LES.load_level("/Game/Maps/Creek"); AX.update(json.load(open(f"{ROOT}/axis.json"))); mark("interactive_level")
    if RUN.get("playtest",True):
        try: playtest_setup()
        except Exception: log("playtest setup failed",traceback.format_exc()[-800:])
        PT["h"]=unreal.register_slate_post_tick_callback(playtest_tick)
    f0=int(RUN.get("live_frame",1650)); k=min(PL["walk"],key=lambda k_:abs(k_["f"]-f0))
    loc=V3(k["pos"]); rot=look(k["pos"],k["tgt"]); log("live start",k["f"],loc,rot)
    for a_ in EAS.get_all_level_actors():
        if isinstance(a_,unreal.PlayerStart): EAS.destroy_actor(a_)
    ps=EAS.spawn_actor_from_class(unreal.PlayerStart,loc,unreal.Rotator(roll=0.0,pitch=0.0,yaw=rot.yaw))
    try: unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(loc,rot)
    except Exception as e: log("vpcam",e)
    _C=getattr(unreal,"LevelEditorPlaySettings",None)
    st=None
    try: st=unreal.get_default_object(_C) if _C else None
    except Exception as e: log("pie settings",e)
    if st is None:
        class _N:
            def set_editor_property(self,*a): raise RuntimeError("no LevelEditorPlaySettings in python")
        st=_N()
    for k_,v_ in (("new_window_width",1920),("new_window_height",1080),("center_new_window",False),("new_window_position",unreal.IntPoint(0,0))):
        try: st.set_editor_property(k_,v_)
        except Exception as e: log("pie set",k_,e)
    for en in ("LastExecutedPlayModeType","PlayModeType"):
        E_=getattr(unreal,en,None)
        if E_ is None: continue
        for mv in ("PLAY_MODE_IN_EDITOR_FLOATING","PLAY_MODE_IN_EDITOR_FLOATING_WINDOW","PLAYMODE_IN_EDITOR_FLOATING"):
            if hasattr(E_,mv):
                try: st.set_editor_property("last_executed_play_mode_type",getattr(E_,mv)); log("pie mode",en,mv)
                except Exception as e: log("pie mode fail",e)
    log("pie enum candidates",[n for n in dir(unreal) if "PlayMode" in n])
    T={"n":0}
    def tick(dt):
        T["n"]+=1
        if T["n"]==int(RUN.get("live_ticks",120)):
            try: unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play(); mark("pie_requested"); log("PIE requested")
            except Exception as e: log("pie fail",e); mark("pie_fail")
            unreal.unregister_slate_post_tick_callback(H["h"])
    H={"h":unreal.register_slate_post_tick_callback(tick)}
try:
    if RUN.get("interactive",False): interactive(); raise SystemExit
    if RUN.get("build",True): build()
    else: LES.load_level("/Game/Maps/Creek"); AX.update(json.load(open(f"{ROOT}/axis.json")))
    for _pf in RUN.get("place_order",[]):
        _pp=f"{ROOT}/place/{_pf}.py"
        if not os.path.exists(_pp): log("place missing",_pf); continue
        try:
            _g={"__name__":"thru_place_"+_pf}; exec(open(_pp).read(),_g)
            if "place" in _g: _g["place"]()
            mark("place_ok "+_pf)
        except Exception:
            mark("place_fail "+_pf); log("place fail",_pf,traceback.format_exc()[-800:])
    if RUN.get("sanitize_mi",True):  # scene2-1652: targeted texture-param guard; swap only broken MIs
        _MF=unreal.load_asset("/Game/M/M_Needle"); _MG=unreal.load_asset("/Game/M/M_Granite")
        _DN=unreal.load_asset("/Engine/EngineMaterials/DefaultNormal"); _DT=unreal.load_asset("/Engine/EngineResources/DefaultTexture") or unreal.load_asset("/Engine/EngineMaterials/DefaultDiffuse")
        _blanket=RUN.get("sanitize_mode","targeted")=="blanket"; _seen={}; _n=0; _fx=0; _sw=0
        def _okt(t):
            if t is None or not isinstance(t,unreal.Texture): return False
            try:
                if isinstance(t,unreal.Texture2D) and t.blueprint_get_size_x()<=0: return False
            except Exception: return False
            return True
        def _fixmi(m):
            # returns True if usable after fix, False -> swap
            if isinstance(m,unreal.Material): return True
            if not isinstance(m,unreal.MaterialInstance): return False
            if m.get_editor_property("parent") is None: return False
            try: names=list(MEL.get_texture_parameter_names(m))
            except Exception as e: log("texnames fail",m.get_name(),e); return False
            ch=[]
            for nm in names:
                try: t=MEL.get_material_instance_texture_parameter_value(m,nm)
                except Exception: t=None
                if not _okt(t):
                    d=_DN if "normal" in str(nm).lower() else _DT
                    if d is None: return False
                    try: MEL.set_material_instance_texture_parameter_value(m,nm,d); ch.append(str(nm))
                    except Exception as e: log("settex fail",m.get_name(),nm,e); return False
            if ch:
                try: MEL.update_material_instance(m)
                except Exception: pass
                EAL.save_loaded_asset(m); log("fixed MI",m.get_path_name(),ch)
            return True
        for _a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
            for _c in _a.get_components_by_class(unreal.MeshComponent):
                for _i in range(_c.get_num_materials()):
                    _m=_c.get_material(_i)
                    if isinstance(_m,unreal.Material) and _m.get_path_name().startswith("/Game/M/"): continue
                    _n+=1
                    k=_m.get_path_name() if _m else "None"
                    if k not in _seen: _seen[k]=(not _blanket) and _m is not None and _fixmi(_m)
                    if not _seen[k]:
                        _r=_MG if any(q in _a.get_actor_label().lower() for q in ("rock","boulder","arnklit","cliff","pile")) else _MF
                        if _r: _c.set_material(_i,_r); _sw+=1
        log("sanitize slots",_n,"unique",len(_seen),"swapped_slots",_sw,"bad",[k for k,v in _seen.items() if not v][:40])
        mark(f"sanitized slots={_n} swapped={_sw}")
    out=RUN["out"]
    if RUN.get("stills",True): QUEUE.append(("SeqStills",out+"/stills",RUN.get("res",[1920,1080]),RUN.get("temporal",8),CV))
    if RUN.get("walk",False): QUEUE.append(("SeqWalk",out+"/walk",RUN.get("walk_res",[1920,1080]),RUN.get("walk_temporal",4),CV))
    nxt()
except SystemExit: log("interactive mode: editor stays open")
except Exception:
    open(f"{ROOT}/ue_error.txt","w").write(traceback.format_exc()); mark("ERROR"); unreal.SystemLibrary.quit_editor()
