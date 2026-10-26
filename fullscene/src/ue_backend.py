# THRU UE5 spike: build Sierra creek scene from procedural assets, then render via Movie Render Queue (PIE executor).
import unreal, json, os, math, traceback, glob
ROOT="/workspace/fullscene"
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
    _hb=RUN.get("hiker_basecolor")
    _xt=[]
    if _hb and os.path.exists(_hb):
        import shutil; os.makedirs("/tmp/thru_tex",exist_ok=True); shutil.copy(_hb,"/tmp/thru_tex/T_HikerAlt_D.png"); _xt=["/tmp/thru_tex/T_HikerAlt_D.png"]   # assets/ is root-owned; UE runs as ue
    pngs=sorted(glob.glob(f"{A}/T_*.png"))+_xt
    for f in pngs:
        n=os.path.splitext(os.path.basename(f))[0];path=f"/Game/FullTextures/{n}"
        fresh=not EAL.does_asset_exist(path)
        if fresh:imp([f],"/Game/FullTextures")
        t=unreal.load_asset(path)
        if t is None:raise RuntimeError("Missing terrain texture "+n)
        if fresh:
            if n.endswith("_N"):t.set_editor_property("compression_settings",unreal.TextureCompressionSettings.TC_NORMALMAP);t.set_editor_property("srgb",False)
            elif n.endswith("_R") or "Mask" in n:t.set_editor_property("srgb",False)
            if "Mask" in n:t.set_editor_property("address_x",unreal.TextureAddress.TA_CLAMP);t.set_editor_property("address_y",unreal.TextureAddress.TA_CLAMP)
            EAL.save_loaded_asset(t)
        TEX[n]=t

MESH={}; HIKER={}
MESH={}
def load_meshes():
    glbs=sorted(g for g in glob.glob(f"{A}/*.glb") if os.path.basename(g).startswith("tile_") or os.path.basename(g) in ("bridge.glb","skirt.glb","water.glb","probe.glb"))
    for g in glbs:
        n=os.path.splitext(os.path.basename(g))[0]; dest=f"/Game/FullTerrain/{n}"
        if n in ("backpack","hat") and EAL.does_directory_exist(dest): EAL.delete_directory(dest)   # idempotent gear import (re-import over its glTF MI/textures segfaulted MRQ)
        if not EAL.does_directory_exist(dest): imp([g],dest)
        sms=[]
        for p in EAL.list_assets(dest,recursive=True,include_folder=False):
            o=unreal.load_asset(p)
            if isinstance(o,unreal.StaticMesh): sms.append(o)
        sms.sort(key=lambda o:o.get_name()); MESH[n]=sms; log("mesh",n,[o.get_name() for o in sms])
# ---------------- material helpers ----------------
def newmat(name):
    p=f"/Game/M/{name}"
    if EAL.does_asset_exist(p): return unreal.load_asset(p)
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
    dust=mul(m,tex(m,"T_NB_Duff_D",uvd),V(m,"DustTint",ds["tint"]))
    dust=mul(m,dust,tex(m,"T_Dust_D",div(m,xy,C(m,2300.0))))
    dust=mul(m,dust,C(m,1.5))
    grass=tex(m,"T_NB_Meadow_D",div(m,xy,C(m,200.0)))
    peb=tex(m,"T_NB_Cobbles_D",div(m,xy,C(m,160.0)))
    base=lerp(m,mul(m,dust,C(m,0.9)),grass,mul(m,mask(m,mk,b=True),C(m,0.45))); base=lerp(m,base,mul(m,tex(m,"T_NB_Trail_D",div(m,xy,C(m,180.0))),S(m,"TrailShade",RUN.get("trail_shade",1.0))),mul(m,mask(m,mk,g=True),S(m,"TrailOn",0.0 if RUN.get("trail_off") else 1.0))); base=lerp(m,base,peb,mask(m,mk,r=True))   # trail tread on the sunlit north slope read as a light shaft (bug 14)
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
def lighting():
    L=P["light"]
    sun=EAS.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,1000))
    sc=sun.get_component_by_class(unreal.DirectionalLightComponent)
    sc.set_mobility(unreal.ComponentMobility.MOVABLE); sc.set_intensity(L["sun_lux"]); sc.set_use_temperature(True); sc.set_temperature(L["sun_temp"])
    for k,v in [("atmosphere_sun_light",True),("enable_light_shaft_bloom",not RUN.get("no_shaft_bloom")),("cast_shadows",True)]+([("contact_shadow_length",0.2),("volumetric_scattering_intensity",0.5)] if RUN.get("sun_contact") else []):   # art-director r2: ground grass/tree bases, tame sunbeam
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
def make_seq(name,keys,nframes,constant,fl,fps=24):
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
    EAL.save_loaded_asset(seq); return seq
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
    if seqname!="SeqWalk" or RUN.get("walk_range"):
        a_,b_=RUN.get("walk_range",[23,24]); o.use_custom_playback_range=True; o.custom_start_frame=int(a_); o.custom_end_frame=int(b_); log("walk range",a_,b_)
    cfg.find_or_add_setting_by_class(unreal.MoviePipelineDeferredPassBase)
    cfg.find_or_add_setting_by_class(unreal.MoviePipelineImageSequenceOutput_PNG)
    aa=cfg.find_or_add_setting_by_class(unreal.MoviePipelineAntiAliasingSetting)
    aa.spatial_sample_count=1; aa.temporal_sample_count=temporal; aa.engine_warm_up_count=24; aa.render_warm_up_count=24; aa.use_camera_cut_for_warm_up=False
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