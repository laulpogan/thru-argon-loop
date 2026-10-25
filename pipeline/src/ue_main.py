# THRU UE5 spike: build Sierra creek scene from procedural assets, then render via Movie Render Queue (PIE executor).
import unreal, json, os, math, traceback, glob
ROOT="/workspace/unreal"
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
def imp(files,dest):
    ts=[]
    for f in files:
        t=unreal.AssetImportTask(); t.filename=f; t.destination_path=dest; t.automated=True; t.save=True; t.replace_existing=True; ts.append(t)
    AT.import_asset_tasks(ts)
    return {os.path.splitext(os.path.basename(t.filename))[0]:[str(p) for p in t.imported_object_paths] for t in ts}
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
        imp([f"/tmp/TP_{tag}_{mp}.png" for mp in ["albedo","normal","roughness"]],"/Game/TP")
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
    dest="/Game/Pack/hiker_male"
    if RUN.get("reimport_packs",False) or not EAL.does_directory_exist(dest): imp([f"{PK}/hiker/hiker_male.glb"],dest)
    for p in EAL.list_assets(dest,recursive=True,include_folder=False):
        o=unreal.load_asset(p)
        if isinstance(o,unreal.SkeletalMesh): HIKER["mesh"]=o
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
    if EAL.does_asset_exist(p): EAL.delete_asset(p)
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
    MEL.layout_material_expressions(m); MEL.recompile_material(m); EAL.save_loaded_asset(m); return m
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
    base=lerp(m,mul(m,dust,C(m,0.9)),grass,mask(m,mk,b=True)); base=lerp(m,base,(tex(m,"T_DG_D",div(m,xy,C(m,180.0))) if "T_DG_D" in TEX else mul(m,dust,C(m,1.12))),mask(m,mk,g=True)); base=lerp(m,base,peb,mask(m,mk,r=True))
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
def mat_simple(name,texn,tile,rough,foliage=False):
    m=newmat(name); c=tex(m,texn,uvmesh(m,tile)); prop(m,c,unreal.MaterialProperty.MP_BASE_COLOR); prop(m,C(m,rough),unreal.MaterialProperty.MP_ROUGHNESS)
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
    MWOOD=mat_simple("M_Wood","T_Bark_D",0.6,0.75)
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
    b=seq.add_spawnable_from_instance(h); EAS.destroy_actor(h)
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
    lz=mask(m,sub(m,wp(m),nd(m,unreal.MaterialExpressionObjectPositionWS)),b=True)
    def band(z0): return sat(m,div(m,sub(m,lz,C(m,z0)),C(m,3.0)))
    boots=C(m,[0.07,0.045,0.03]); pants=C(m,[0.36,0.31,0.21]); belt=C(m,[0.1,0.08,0.06])
    # flannel shirt: red/black check from world-space sin pattern
    w=wp(m); sx=nd(m,unreal.MaterialExpressionSine,period=14.0); cn(mask(m,w,r=True),sx,""); sy=nd(m,unreal.MaterialExpressionSine,period=14.0); cn(mask(m,w,b=True),sy,"")
    chk=sat(m,mul(m,add(m,sx,sy),C(m,2.0))); shirt=lerp(m,C(m,[0.32,0.05,0.04]),C(m,[0.05,0.03,0.03]),mul(m,chk,C(m,0.55)))
    skin=C(m,[0.42,0.26,0.18])
    col=lerp(m,boots,pants,band(16.0)); col=lerp(m,col,belt,band(97.0)); col=lerp(m,col,shirt,band(101.0)); col=lerp(m,col,skin,band(149.0))
    prop(m,col,unreal.MaterialProperty.MP_BASE_COLOR); prop(m,C(m,0.85),unreal.MaterialProperty.MP_ROUGHNESS)
    _OF.append(finish(m)); return _OF[0]
def add_gear(seq,hkeys,nframes,constant):
    MP=HMAT([0.12,0.2,0.14],90); MH=HMAT([0.55,0.45,0.3],91)
    for nm,mat,fwd,up in (("backpack",MP,-0.20,1.22),("hat",MH,0.0,1.66)):
        if nm not in MESH: log("no gear mesh",nm); continue
        a=EAS.spawn_actor_from_object(MESH[nm][0],V3(hkeys[0]["pos"]),unreal.Rotator())
        a.static_mesh_component.set_material(0,mat); a.static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE)
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
            for i,v in enumerate([loc.x,loc.y,loc.z,0.0,0.0,yaw]): ch[i].add_key(unreal.FrameNumber(k["f"]),v,0.0,unreal.MovieSceneTimeUnit.DISPLAY_RATE,interp)
    log("gear ok")
HIKER_YAW=float(RUN.get("hiker_yaw",-90.0))
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
try:
    if RUN.get("build",True): build()
    else: LES.load_level("/Game/Maps/Creek"); AX.update(json.load(open(f"{ROOT}/axis.json")))
    out=RUN["out"]
    if RUN.get("stills",True): QUEUE.append(("SeqStills",out+"/stills",RUN.get("res",[1920,1080]),RUN.get("temporal",8),CV))
    if RUN.get("walk",False): QUEUE.append(("SeqWalk",out+"/walk",RUN.get("walk_res",[1920,1080]),RUN.get("walk_temporal",4),CV))
    nxt()
except Exception:
    open(f"{ROOT}/ue_error.txt","w").write(traceback.format_exc()); mark("ERROR"); unreal.SystemLibrary.quit_editor()
