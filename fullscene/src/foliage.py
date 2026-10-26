# foliage v2, exec'd inside ue_main.build() after the placement loop (shares ue_main globals: unreal, EAL, AT, MEL, EAS, log, mark, PL, V3, RUN, TEX, nd, cn, prop, C, S, mul, add, sub, div, lerp, sat, mask, wp)
# Rules: (1) import only what does not exist yet, keyed on content hash (fol_prep.py removed stale dirs before launch);
#        (2) never change settings on a texture another material already references (no in-place rebuilds);
#        (3) every asset keeps its own textures: its glTF MI textures are re-bound to a foliage master (two-sided foliage, masked, dithered LOD).
import json as _json, os as _os, math as _math, hashlib as _hashlib
FMAN=_json.load(open(f"{ROOT}/fol_src/manifest.json")); FV="full1"; FROOT="/Game/Fol"
SMES=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
FLOG=[]
def flog(*a): log("FOL",*a); FLOG.append(" ".join(map(str,a)))
def _imp_once(f,dest):
    if EAL.does_directory_exist(dest) and EAL.list_assets(dest,recursive=True,include_folder=False): return False
    t=unreal.AssetImportTask(); t.filename=f; t.destination_path=dest; t.automated=True; t.save=True; t.replace_existing=False
    AT.import_asset_tasks([t]); return True
def _sms(dest):
    o=[unreal.load_asset(p) for p in EAL.list_assets(dest,recursive=True,include_folder=False)]
    return [x for x in o if isinstance(x,unreal.StaticMesh)]
def _nverts(sm):
    try: return SMES.get_number_verts(sm,0)
    except Exception: return 0
# ---------- masters (create once, versioned) ----------
def _create_mat(name):
    p=f"{FROOT}/{name}"
    if EAL.does_asset_exist(p): return unreal.load_asset(p),False
    return AT.create_asset(name,FROOT,unreal.Material,unreal.MaterialFactoryNew()),True
def _tsp(m,name,deftex,stype):
    t=nd(m,unreal.MaterialExpressionTextureSampleParameter2D,parameter_name=name)
    t.set_editor_property("sampler_type",stype); t.set_editor_property("texture",deftex); return t
_ST=unreal.MaterialSamplerType
def _deftex(kind):
    for n,t in TEX.items():
        if kind=="n" and n.endswith("_N"): return t
        if kind=="c" and n.endswith("_D"): return t
        if kind=="l" and n.endswith("_R"): return t
    return None
def _flags(m,masked,foliage):
    sp(m,"two_sided",True); sp(m,"dithered_lod_transition",True)
    sp(m,"used_with_instanced_static_meshes",True)
    if masked: sp(m,"blend_mode",unreal.BlendMode.BLEND_MASKED); sp(m,"opacity_mask_clip_value",0.35)   # mip alpha erosion: 0.5 thins distant needle cards
    if foliage: sp(m,"shading_model",unreal.MaterialShadingModel.MSM_TWO_SIDED_FOLIAGE)
def mask_a(m,t):
    n=nd(m,unreal.MaterialExpressionComponentMask,r=False,g=False,b=False,a=True); MEL.connect_material_expressions(t,"RGBA",n,""); return n
def master_tree(kind,nmap,rsrgb):
    # kind: leaf|bark ; nmap: normal texture is TC_Normalmap ; rsrgb: roughness texture is sRGB
    name=f"M_Fol_{kind}_{'n' if nmap else 'c'}{'s' if rsrgb else 'l'}_{FV}"; m,new=_create_mat(name)
    if not new: return m
    leaf=kind=="leaf"; _flags(m,leaf,leaf)
    uvs=S(m,"UVSet",0.0); u0=nd(m,unreal.MaterialExpressionTextureCoordinate,coordinate_index=0); u1=nd(m,unreal.MaterialExpressionTextureCoordinate,coordinate_index=1); u2=nd(m,unreal.MaterialExpressionTextureCoordinate,coordinate_index=2)
    UV=lerp(m,lerp(m,u0,u1,sat(m,uvs)),u2,sat(m,sub(m,uvs,C(m,1.0))))   # per-asset UV channel (AM283 foliage UVs are not in UV0)
    bc=_tsp(m,"BaseColor",_deftex("c"),_ST.SAMPLERTYPE_COLOR); cn(UV,bc,"UVs")
    col=mul(m,bc,S(m,"Bright",1.0)); colv=mul(m,col,nd(m,unreal.MaterialExpressionVectorParameter,parameter_name="Tint",default_value=unreal.LinearColor(1,1,1,1)))
    # per-instance hue/brightness variation (+-8%)
    pir=nd(m,unreal.MaterialExpressionPerInstanceRandom); var=add(m,C(m,0.92),mul(m,pir,C(m,0.16)))
    colv=mul(m,colv,var); prop(m,colv,unreal.MaterialProperty.MP_BASE_COLOR)
    if leaf:
        um=mask(m,UV,r=True); vm=mask(m,UV,g=True)   # per-asset sprite rect: zero opacity outside [0,ClipU]x[0,ClipV] (THRU jeffrey atlas has opaque bake-dilation junk outside the needle sprite)
        clip=mul(m,sat(m,mul(m,sub(m,S(m,"ClipU",10.0),um),C(m,400.0))),sat(m,mul(m,sub(m,S(m,"ClipV",10.0),vm),C(m,400.0))))
        prop(m,mul(m,mul(m,mask_a(m,bc),S(m,"AlphaGain",1.0)),clip),unreal.MaterialProperty.MP_OPACITY_MASK)   # per-asset gain = clip/vendor alphaCutoff
        prop(m,mul(m,colv,S(m,"Transmission",0.55)),unreal.MaterialProperty.MP_SUBSURFACE_COLOR)
    nt=_tsp(m,"Normal",_deftex("n") if nmap else _deftex("c"),_ST.SAMPLERTYPE_NORMAL if nmap else _ST.SAMPLERTYPE_COLOR); cn(UV,nt,"UVs")
    nv=nt if nmap else sub(m,mul(m,mask(m,nt,r=True,g=True,b=True),C(m,2.0)),C(m,1.0))
    nflip=lerp(m,nv,mul(m,nv,C(m,[1.0,-1.0,1.0])),S(m,"FlipG",0.0))   # glTF normals are +Y (OpenGL); flip only if the texture is not already flipped
    nflat=lerp(m,C(m,[0,0,1]),nflip,S(m,"NormalStrength",1.0)); prop(m,nflat,unreal.MaterialProperty.MP_NORMAL)
    rt=_tsp(m,"ORM",_deftex("c") if rsrgb else (_deftex("l") or _deftex("c")),_ST.SAMPLERTYPE_COLOR if rsrgb else _ST.SAMPLERTYPE_LINEAR_COLOR); cn(UV,rt,"UVs")
    prop(m,mul(m,mask(m,rt,g=True),S(m,"RoughScale",1.0)),unreal.MaterialProperty.MP_ROUGHNESS)
    prop(m,S(m,"Specular",0.35 if leaf else 0.4),unreal.MaterialProperty.MP_SPECULAR)
    MEL.layout_material_expressions(m); MEL.recompile_material(m); EAL.save_loaded_asset(m); flog("master created",name); return m
def master_grass():
    name=f"M_Fol_grass_{FV}"; m,new=_create_mat(name)
    if not new: return m
    _flags(m,False,True)
    bc=_tsp(m,"BaseColor",_deftex("c"),_ST.SAMPLERTYPE_COLOR)
    w=wp(m); x=mask(m,w,r=True); z=mask(m,w,b=True)
    op=nd(m,unreal.MaterialExpressionObjectPositionWS); oz=mask(m,op,b=True)
    hfrac=sat(m,div(m,sub(m,z,oz),S(m,"BladeHeightCm",38.0)))
    shade=lerp(m,S(m,"BaseShade",0.5),C(m,1.0),hfrac)                     # darker at the root, like the Godot ground-cover shader
    # wetness: 1 at the water line, 0 at Band cm above it (water plane z0 - x*slope, from placements)
    zw=sub(m,S(m,"WaterZ0",0.0),mul(m,x,S(m,"Slope",0.0)))
    wet=sat(m,div(m,sub(m,add(m,zw,S(m,"BandCm",180.0)),z),S(m,"BandCm",180.0)))
    lum=nd(m,unreal.MaterialExpressionDotProduct); cn(bc,lum,"A"); cn(C(m,[0.299,0.587,0.114]),lum,"B")
    straw=mul(m,lum,C(m,[1.20,0.99,0.62]))
    cure=mul(m,S(m,"Cure",0.8),sub(m,C(m,1.0),wet))
    pir=nd(m,unreal.MaterialExpressionPerInstanceRandom)
    cure=sat(m,add(m,cure,mul(m,sub(m,pir,C(m,0.5)),C(m,0.35))))
    col=mul(m,mul(m,lerp(m,bc,straw,cure),shade),add(m,C(m,0.88),mul(m,pir,C(m,0.24))))
    prop(m,col,unreal.MaterialProperty.MP_BASE_COLOR); prop(m,mul(m,col,S(m,"Transmission",0.45)),unreal.MaterialProperty.MP_SUBSURFACE_COLOR)
    prop(m,C(m,0.82),unreal.MaterialProperty.MP_ROUGHNESS); prop(m,C(m,0.3),unreal.MaterialProperty.MP_SPECULAR)
    MEL.layout_material_expressions(m); MEL.recompile_material(m); EAL.save_loaded_asset(m); flog("master created",name); return m
def _mic(name,dest,parent):
    p=f"{dest}/{name}"
    if EAL.does_asset_exist(p): return unreal.load_asset(p),False
    mi=AT.create_asset(name,dest,unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew())
    MEL.set_material_instance_parent(mi,parent); return mi,True
def _texp(mi,n):
    try: return MEL.get_material_instance_texture_parameter_value(mi,n)
    except Exception: return None
def _no_nanite(sp_,sm):
    # Nanite simplifies thin, disconnected needle/leaf/blade triangles away (trunks survive, foliage vanishes) and ignores our LODs.
    try:
        ns=sm.get_editor_property("nanite_settings"); was=bool(ns.enabled)
        if was: ns.enabled=False; sm.set_editor_property("nanite_settings",ns); EAL.save_loaded_asset(sm)
        flog("nanite",sp_,"was",was,"now",bool(sm.get_editor_property("nanite_settings").enabled))
    except Exception as e: flog("nanite err",sp_,e)
    try: flog("sections",sp_,[(l,sm.get_num_sections(l),_nverts_l(sm,l)) for l in range(sm.get_num_lods())])
    except Exception as e: flog("sections err",e)
def _nverts_l(sm,l):
    try: return SMES.get_number_verts(sm,l)
    except Exception: return -1
LEAFK=("leaf","fir","pinus","needle","cone","cones","spray")
def build_tree(sp_,info):
    dest=f"{FROOT}/{sp_}_{info['hash']}"; new=_imp_once(info["lod0"],dest)
    if info.get("lod1"): _imp_once(info["lod1"],dest+"_lod1")
    s0=_sms(dest); s1=_sms(dest+"_lod1") if info.get("lod1") else []
    if not s0: flog("NO MESH",sp_); return None
    sm=s0[0]
    bad1=[k for k,v in info.get("uv1",{}).items() if v["uv"]<0]
    if bad1 or not info.get("lod1"):
        flog("vendor LOD1 skipped/absent",bad1,sp_); s1=[]
        if sm.get_num_lods()<2:   # generate LOD1 from LOD0 instead (keeps LOD0's valid UV channels)
            try:
                ro=unreal.EditorScriptingMeshReductionOptions(); ro.auto_compute_lod_screen_size=False
                ro.reduction_settings=[unreal.EditorScriptingMeshReductionSettings(percent_triangles=1.0,screen_size=1.0),unreal.EditorScriptingMeshReductionSettings(percent_triangles=0.4,screen_size=0.18)]
                flog("generated LODs",sp_,SMES.set_lods_with_notification(sm,ro,True))
            except Exception as e: flog("lod gen failed",sp_,e)
    if sm.get_num_lods()<2 and s1:
            r=SMES.set_lod_from_static_mesh(sm,1,s1[0],0,True); flog("lod1 set",sp_,r)
    if True:
        try:
            SMES.set_lod_screen_sizes(sm,[1.0,0.22]) if hasattr(SMES,"set_lod_screen_sizes") else None
        except Exception as e: flog("screen sizes",e)
        flog("has set_lod_screen_sizes",hasattr(SMES,"set_lod_screen_sizes"))
        # materials: re-bind the asset's own glTF textures to the foliage masters
        changed=False; sms_=sm.get_editor_property("static_materials")
        for i,stm in enumerate(sms_):
            gmi=stm.get_editor_property("material_interface"); slot=str(stm.get_editor_property("material_slot_name"))
            if gmi is None: flog("slot without material",sp_,slot); continue
            if gmi.get_name()==f"MI_{sp_}_{i}_{FV}": continue
            if gmi.get_name().startswith(f"MI_{sp_}_"):   # bound to an older version of our MI: recover the asset's glTF MI by slot name
                cand=[unreal.load_asset(p) for p in EAL.list_assets(dest,recursive=True,include_folder=False)]
                cand=[c for c in cand if isinstance(c,unreal.MaterialInstanceConstant) and c.get_name()==slot]
                if not cand: flog("glTF MI not found for",slot); continue
                gmi=cand[0]
            pname=gmi.get_editor_property("parent").get_name() if isinstance(gmi,unreal.MaterialInstance) and gmi.get_editor_property("parent") else ""
            part="_".join(slot.split("_")[4:]).lower() if slot.startswith("AM283_") else slot.lower()   # strip "AM283_029_Pinus_ponderosa_" (species name is not a part name)
            leaf=("Mask" in pname) or any(k in part for k in LEAFK)
            bct=_texp(gmi,"BaseColorTexture"); nt=_texp(gmi,"NormalTexture"); rt=_texp(gmi,"MetallicRoughnessTexture")
            if bct is None: flog("NO BASECOLOR",sp_,slot,pname); continue
            nmap=bool(nt) and nt.get_editor_property("compression_settings")==unreal.TextureCompressionSettings.TC_NORMALMAP
            rsrgb=bool(rt) and bool(rt.get_editor_property("srgb"))
            M=master_tree("leaf" if leaf else "bark",nmap,rsrgb)
            mi,_=_mic(f"MI_{sp_}_{i}_{FV}",dest,M)
            MEL.set_material_instance_texture_parameter_value(mi,"BaseColor",bct)
            if nt: MEL.set_material_instance_texture_parameter_value(mi,"Normal",nt)
            else: MEL.set_material_instance_scalar_parameter_value(mi,"NormalStrength",0.0)
            if rt: MEL.set_material_instance_texture_parameter_value(mi,"ORM",rt)
            else: MEL.set_material_instance_scalar_parameter_value(mi,"RoughScale",0.0)
            fg=False
            try: fg=bool(nt.get_editor_property("flip_green_channel")) if nt else False
            except Exception: pass
            MEL.set_material_instance_scalar_parameter_value(mi,"FlipG",0.0 if fg else 1.0)
            if leaf: MEL.set_material_instance_scalar_parameter_value(mi,"NormalStrength",0.6)
            tab=info.get("uv0",{}) if i<len(info.get("uv0",{})) else info.get("uv1",{})
            u_=tab.get(slot,{}).get("uv")
            if u_ is None:   # slot name of a LOD1 section may carry a suffix: match by prefix
                cand=[v for k,v in list(info.get("uv0",{}).items())+list(info.get("uv1",{}).items()) if slot.startswith(k)]
                u_=cand[0]["uv"] if cand else 0
            MEL.set_material_instance_scalar_parameter_value(mi,"UVSet",float(max(u_,0))); flog("uvset",sp_,slot,u_)
            co=([v for k,v in list(info.get("uv0",{}).items())+list(info.get("uv1",{}).items()) if slot.replace("_"," ").lower().startswith(k.replace("_"," ").lower())] or [{"cutoff":0.5}])[0].get("cutoff",0.5)
            if leaf and co<0.35: MEL.set_material_instance_scalar_parameter_value(mi,"AlphaGain",0.35/max(co,0.05)); flog("alphagain",sp_,slot,round(0.35/max(co,0.05),2))
            MEL.update_material_instance(mi); EAL.save_loaded_asset(mi)
            sm.set_material(i,mi); changed=True
            flog("slot",sp_,i,slot,"leaf" if leaf else "bark","parent",pname,"bc",bct.get_name(),"n",nt.get_name() if nt else None,"nmap",nmap,"r",rt.get_name() if rt else None,"rsrgb",rsrgb,"flipG",fg)
        if changed: EAL.save_loaded_asset(sm)
    _no_nanite(sp_,sm)
    # art grade per species (in-place parameter update on our own MIs only): RUN fol_grade {"<sp>_leaf":{"Tint":[r,g,b],"Transmission":x,...}}
    G=RUN.get("fol_grade",{})
    for i in range(len(sm.get_editor_property("static_materials"))):
        mi=sm.get_material(i)
        if not isinstance(mi,unreal.MaterialInstanceConstant) or not mi.get_name().startswith(f"MI_{sp_}_"): continue
        kind="leaf" if "leaf" in mi.get_editor_property("parent").get_name() else "bark"
        if sp_=="jeffrey" and kind=="bark" and "cut" not in str(sm.get_editor_property("static_materials")[i].get_editor_property("material_slot_name")).lower():
            MEL.set_material_instance_texture_parameter_value(mi,"BaseColor",TEX["T_NB_Jeffrey_D"])
            MEL.set_material_instance_scalar_parameter_value(mi,"NormalStrength",0.0)
            MEL.update_material_instance(mi);EAL.save_loaded_asset(mi);flog("NB bark replacement",sp_,i,TEX["T_NB_Jeffrey_D"].get_path_name())
        g=G.get(f"{sp_}_{kind}",{})
        for k,v in g.items():
            if isinstance(v,list): MEL.set_material_instance_vector_parameter_value(mi,k,unreal.LinearColor(v[0],v[1],v[2],1.0))
            else: MEL.set_material_instance_scalar_parameter_value(mi,k,float(v))
        if g: MEL.update_material_instance(mi); EAL.save_loaded_asset(mi); flog("grade",sp_,i,kind,g)
    flog("tree",sp_,"lods",sm.get_num_lods(),"mats",[ (sm.get_material(i).get_name() if sm.get_material(i) else None) for i in range(len(sm.get_editor_property('static_materials')))])
    return sm
def build_grass(sp_,info,texinfo):
    dest=f"{FROOT}/{sp_}_{info['hash']}"; new=_imp_once(info["lod0"],dest); _imp_once(info["lod1"],dest+"_lod1")
    tdest=f"{FROOT}/hg_albedo_{texinfo['hash']}"; _imp_once(texinfo["file"],tdest)
    tx=[unreal.load_asset(p) for p in EAL.list_assets(tdest,recursive=True,include_folder=False)]; tx=[t for t in tx if isinstance(t,unreal.Texture2D)]
    s0=_sms(dest); s1=_sms(dest+"_lod1")
    if not s0 or not tx: flog("NO GRASS MESH/TEX",sp_,len(s0),len(tx)); return None
    sm=s0[0]; mi,mnew=_mic(f"MI_{sp_}_{FV}",dest,master_grass())
    if mnew:
        MEL.set_material_instance_texture_parameter_value(mi,"BaseColor",tx[0]); MEL.update_material_instance(mi); EAL.save_loaded_asset(mi)
    if new or sm.get_num_lods()<2:
        if s1: flog("grass lod1",sp_,SMES.set_lod_from_static_mesh(sm,1,s1[0],0,True))
        for i in range(max(1,len(sm.get_editor_property("static_materials")))): sm.set_material(i,mi)
        EAL.save_loaded_asset(sm)
    # scene-dependent wetness params: in-place scalar update on our own MI (no texture/asset replacement)
    for k,v in (("WaterZ0",PL["water_z0"]*100.0),("Slope",PL["slope"])):
        try:
            if abs(MEL.get_material_instance_scalar_parameter_value(mi,k)-v)>1e-4: MEL.set_material_instance_scalar_parameter_value(mi,k,v); MEL.update_material_instance(mi); EAL.save_loaded_asset(mi)
        except Exception as e: flog("scalar",k,e)
    _no_nanite(sp_,sm)
    flog("grass",sp_,"lods",sm.get_num_lods(),"verts",_nverts(sm))
    return sm
# ---------- foliage types + instances ----------
def _ftype(sp_,sm,cull,shadow=True):
    safe="FT_"+_hashlib.sha256(sp_.encode()).hexdigest()[:16]+"_"+FV
    p=f"{FROOT}/FT/{safe}"
    if EAL.does_asset_exist(p): ft=unreal.load_asset(p)
    else:
        fac=getattr(unreal,"FoliageType_InstancedStaticMeshFactory",None)
        ft=AT.create_asset(safe,f"{FROOT}/FT",unreal.FoliageType_InstancedStaticMesh,fac() if fac else None)
    if ft is None:raise RuntimeError("Foliage type creation failed "+sp_)
    sp(ft,"mesh",sm)
    try: ft.set_editor_property("cull_distance",unreal.Int32Interval(min=int(cull*0.8),max=int(cull)))
    except Exception as e: flog("cull",e)
    sp(ft,"cast_shadow",shadow); EAL.save_loaded_asset(ft); return ft
def _xf(r):
    x,y,z,yaw,s,tx,ty=r[:7]; sz=r[7] if len(r)>7 else 1.0   # optional z/xy ratio (non-uniform scale)
    return unreal.Transform(location=V3([x,y,z]),rotation=unreal.Rotator(roll=tx,pitch=ty,yaw=yaw),scale=unreal.Vector(s,s,s*sz))
MODE={"api":None}
def _place(sp_,sm,rows,cull,shadow):
    xs=[_xf(r) for r in rows]
    if MODE["api"] in (None,"ifa"):
        try:
            ft=_ftype(sp_,sm,cull,shadow)
            unreal.InstancedFoliageActor.add_instances(unreal.EditorLevelLibrary.get_editor_world(),ft,xs)
            MODE["api"]="ifa"; return len(xs)
        except Exception as e: flog("IFA add_instances failed -> HISM actor",e); MODE["api"]="hism"
    a=EAS.spawn_actor_from_class(unreal.Actor,unreal.Vector(0,0,0)); a.set_actor_label(f"FOL_{sp_}")
    sds=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem); hs=sds.k2_gather_subobject_data_for_instance(a)
    pr=unreal.AddNewSubobjectParams(parent_handle=hs[0],new_class=unreal.HierarchicalInstancedStaticMeshComponent,blueprint_context=None)
    h,fail=sds.add_new_subobject(pr)
    comp=unreal.SubobjectDataBlueprintFunctionLibrary.get_object(unreal.SubobjectDataBlueprintFunctionLibrary.get_data(h))
    comp.set_static_mesh(sm); comp.set_editor_property("instance_end_cull_distance",int(cull)); comp.set_editor_property("instance_start_cull_distance",int(cull*0.8))
    comp.set_cast_shadow(shadow); comp.add_instances(xs,False,True)
    return len(xs)
def build_foliage():
    mark("foliage_start"); FO=PL.get("foliage",{}); n_tot={}
    for sp_,info in FMAN["trees"].items():
        if sp_ not in FO: continue
        sm=build_tree(sp_,info)
        if sm: n_tot[sp_]=_place(sp_,sm,FO[sp_],60000,True)
    for sp_,info in FMAN["grass"].items():
        if sp_ not in FO: continue
        sm=build_grass(sp_,info,FMAN["tex"]["hg_albedo"])
        if sm: n_tot[sp_]=_place(sp_,sm,FO[sp_],RUN.get("grass_cull",6000),True)
    flog("placed",n_tot,"api",MODE["api"]); open(f"{RUN['out']}/foliage_log.txt","w").write("\n".join(FLOG)); mark("foliage_ok")
build_foliage()
