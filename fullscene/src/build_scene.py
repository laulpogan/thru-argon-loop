"""Unreal editor entry: import catalog, validate terrain, wire scatter and render."""
import pathlib,sys,hashlib
sys.path.insert(0,"/workspace/fullscene/src")
from worldpack import import_instances
ROOT='/workspace/fullscene'
exec(compile(open(ROOT+'/src/ue_backend.py').read(),ROOT+'/src/ue_backend.py','exec'))
LIB=json.load(open(ROOT+'/library/library.json'));CAT={};PORT=[];LIVE=[]
def import_catalog():
    for ref,info in LIB['files'].items():
        if not info or not ref.endswith(('.glb','.gltf')):continue
        name=info['file'].replace('/','_').rsplit('.',1)[0];dest='/Game/Godot/'+name
        if not EAL.does_directory_exist(dest):imp([ROOT+'/library/'+info['file']],dest)
        objects=[unreal.load_asset(p) for p in EAL.list_assets(dest,recursive=True,include_folder=False)]
        meshes=[v for v in objects if isinstance(v,(unreal.StaticMesh,unreal.SkeletalMesh))]
        anims=[v for v in objects if isinstance(v,unreal.AnimSequence)]
        ids=[v['asset_id'] for v in LIB['rows'] if v['path']==ref]
        for k in ids:CAT[k]={'meshes':meshes,'anims':anims}
        PORT.append(dict(source=ref,asset_ids=ids,meshes=[v.get_path_name() for v in meshes],animations=[v.get_path_name() for v in anims]))
    json.dump(PORT,open(ROOT+'/out/imports.json','w'),indent=2);mark('catalog_imported')
def world_granite():
    m=newmat('M_WorldGranite');p=div(m,wp(m),C(m,180));n=nd(m,unreal.MaterialExpressionVertexNormalWS);ab=nd(m,unreal.MaterialExpressionAbs);cn(n,ab,'');total=add(m,add(m,mask(m,ab,r=True),mask(m,ab,g=True)),mask(m,ab,b=True));weights=div(m,ab,total)
    color=None
    for uv,axis in [(mask(m,p,g=True,b=True),'x'),(mask(m,p,r=True,b=True),'y'),(mask(m,p,r=True,g=True),'z')]:
        t=tex(m,'T_NB_Granite_D',uv);weight=mask(m,weights,r=axis=='x',g=axis=='y',b=axis=='z');v=mul(m,t,weight);color=v if color is None else add(m,color,v)
    prop(m,mul(m,color,C(m,[.84,.85,.83])),unreal.MaterialProperty.MP_BASE_COLOR);prop(m,C(m,.81),unreal.MaterialProperty.MP_ROUGHNESS);return finish(m)
def validate_terrain():
    results=[]
    for tile in PL['tiles']:
        sm=MESH[tile['mesh']][0];b=sm.get_bounds();lo,hi=tile['bounds_m'];expected=[(lo[i]+hi[i])*50 for i in range(3)];expected[1]*=AX['sy'];extent=[(hi[i]-lo[i])*50 for i in range(3)];error=max(abs(v-e) for v,e in zip([b.origin.x,b.origin.y,b.origin.z],expected));error=max(error,max(abs(v-e) for v,e in zip([b.box_extent.x,b.box_extent.y,b.box_extent.z],extent)))
        results.append(dict(tile=tile['mesh'],bounds_error_cm=error))
        if error>1:raise RuntimeError('Terrain import bounds mismatch '+str(results[-1]))
    json.dump(results,open(ROOT+'/out/terrain_validation.json','w'),indent=2);mark('terrain_bounds_pass')
def validate_heights():
    checks=[]
    for p in PL['height_probes']:
        hit=unreal.SystemLibrary.line_trace_single(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(),V3([p[0],p[1],p[2]+10]),V3([p[0],p[1],p[2]-10]),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[],unreal.DrawDebugTrace.NONE,False)
        if hit is None:raise RuntimeError('Terrain height trace missed '+str(p))
        actual=hit.to_tuple()[5].z/100;error=abs(actual-p[2]);checks.append(dict(source_m=p,unreal_z_m=actual,error_m=error))
        if error>.03:raise RuntimeError('Terrain height mismatch '+str(checks[-1]))
    json.dump(checks,open(ROOT+'/out/terrain_heights.json','w'),indent=2);mark('terrain_heights_pass')
def scatter_library():
    groups={}
    for it in PL['instances']:groups.setdefault((it['asset_id'],it['kind']),[]).append(it['transform'])
    counts={}
    for (aid,kind),rows in groups.items():
        count=0
        for sm in CAT.get(aid,{}).get('meshes',[]):
            if not isinstance(sm,unreal.StaticMesh):continue
            if aid in ('sierra_pine_snag','snag_red_fir','sierra_fallen_pine','sierra_fallen_pine_low'):
                for j in range(max(1,len(sm.static_materials))):sm.set_material(j,mat_simple('M_SierraDeadwood','T_NB_Jeffrey_D',.85,1))
                EAL.save_loaded_asset(sm)
            if aid in ('sierra_meadow_short','sierra_meadow_tuft','sierra_sedge_clump','sierra_forest_litter'):
                for j in range(max(1,len(sm.static_materials))):sm.set_material(j,mat_simple('M_SierraMeadow','T_NB_Meadow_D',.9,.65))
                EAL.save_loaded_asset(sm)
            if kind=='prop':
                # Plain wood removes any authored trail insignia from the marker.
                for j in range(max(1,len(sm.static_materials))):sm.set_material(j,mat_simple('M_PlainMarker','T_NB_Jeffrey_D',.9,.65))
            if kind=='granite':
                for j in range(max(1,len(sm.static_materials))):sm.set_material(j,MG)
                EAL.save_loaded_asset(sm)
            count+=_place(aid+'_'+sm.get_name(),sm,rows,22000,True)
        counts[aid]=dict(placements=len(rows),mesh_instances=count)
    json.dump(counts,open(ROOT+'/out/scatter_imports.json','w'),indent=2)
def add_life():
    for i,it in enumerate(PL['life']):
        pack=CAT.get(it['asset_id'],{});actors=[]
        for sm in pack.get('meshes',[]):
            a=EAS.spawn_actor_from_object(sm,V3(it['anchor_m']),unreal.Rotator());a.set_actor_scale3d(unreal.Vector(it['scale'],it['scale'],it['scale']));a.set_actor_label('LIFE_%03d_%s'%(i,it['asset_id']));actors.append(a)
            if isinstance(sm,unreal.SkeletalMesh):
                c=a.get_component_by_class(unreal.SkeletalMeshComponent);anims=pack['anims'];an=next((x for x in anims if 'idle' in x.get_name().lower()),anims[0] if anims else None)
                if an:c.set_animation_mode(unreal.AnimationMode.ANIMATION_SINGLE_NODE);c.override_animation_data(an,True,True,0,1)
        LIVE.append((it,actors))
    mark('life_actors '+str(sum(len(v) for _,v in LIVE)))
def animate_life(seq,nframes):
    for it,actors in LIVE:
        p=it['anchor_m'];kind=it['kind'];phase=it['phase'];radius={'butterfly':.35,'insect':.25,'bird':2.5,'critter':.12}[kind]
        for a in actors:
            b=seq.add_possessable(a);t=b.add_track(unreal.MovieScene3DTransformTrack);sec=t.add_section();sec.set_range(0,nframes);ch=sec.get_all_channels()
            for frame in range(0,nframes+1,6):
                t=frame/24;w=t*(2.5 if kind=='butterfly' else .7);d=[radius*(math.sin(w+phase)-math.sin(phase)),radius*(math.cos(w*.7+phase)-math.cos(phase)),0 if kind=='critter' else .13*(math.sin(w*2+phase)-math.sin(phase))];v=V3([p[j]+d[j] for j in range(3)]);vals=[v.x,v.y,v.z,0,5*math.sin(w*5) if kind in ('butterfly','insect') else 0,math.degrees(w)*.2]
                for j,value in enumerate(vals):ch[j].add_key(unreal.FrameNumber(frame),value,0,unreal.MovieSceneTimeUnit.DISPLAY_RATE,unreal.MovieSceneKeyInterpolation.LINEAR)
            # Original Godot animation clips retain flutter/gait; transform track supplies wander/flock paths.
            if isinstance(a,unreal.SkeletalMeshActor):
                pack=CAT[it['asset_id']];an=next((v for v in pack['anims'] if 'move' in v.get_name().lower()),next(iter(pack['anims']),None))
                if an:
                    at=b.add_track(unreal.MovieSceneSkeletalAnimationTrack);s=at.add_section();s.set_range(0,nframes);pr=s.params;pr.animation=an;s.params=pr
    EAL.save_loaded_asset(seq)
def particles():
    records=[]
    specs=[('Pollen','HangingParticulates',None,.08,[v['anchor_m'] for v in PL['life'] if v['kind']=='butterfly'][::4],True),('TrailDust','BlowingParticles',None,.025,[[k['pos'][0],k['pos'][1],k['pos'][2]-1.5] for k in PL['walk'][::12]],True),('Fireflies','HangingParticulates',None,.04,[v['anchor_m'] for v in PL['life'] if v['kind']=='insect'][::8],RUN.get('dusk',False))]
    for kind,aid in [('butterfly','sierra_alpine_butterfly'),('bird','free_stellers_jay'),('insect','oregon_bumblebee')]:
        mesh=CAT[aid]['meshes'][0]
        if isinstance(mesh,unreal.SkeletalMesh):
            component=next(a.get_component_by_class(unreal.SkeletalMeshComponent) for it,actors in LIVE if it['asset_id']==aid for a in actors if isinstance(a,unreal.SkeletalMeshActor))
            mesh_key=hashlib.sha256((mesh.get_path_name()+str(next(v['scale'] for v in PL['life'] if v['asset_id']==aid))).encode()).hexdigest()[:12]
            mesh=unreal.FullsceneNiagaraLibrary.bake_fauna(component,'/Game/FullsceneVFX/SM_'+kind+'_'+mesh_key)
        if mesh is None:raise RuntimeError('Niagara fauna bake failed '+kind)
        specs.append((kind,'BlowingParticles',mesh,.15,[v['anchor_m'] for v in PL['life'] if v['kind']==kind][::8],True))
    for i,(kind,template,mesh,scale,anchors,enabled) in enumerate(specs):
        key=hashlib.sha256(json.dumps([PL['seed']+i,template,mesh.get_path_name() if mesh else None,scale]).encode()).hexdigest()[:12]
        path='/Game/FullsceneVFX/NS_'+kind+'_'+key;emitter='/Niagara/DefaultAssets/Templates/Emitters/'+template
        asset=unreal.FullsceneNiagaraLibrary.make_ambient(path,emitter,mesh,PL['seed']+i,1/scale if mesh else 1)
        if asset is None:raise RuntimeError('Niagara authoring failed '+kind)
        EAL.save_loaded_asset(asset)
        if not enabled:continue
        for p in anchors:
            a=EAS.spawn_actor_from_class(unreal.NiagaraActor,V3(p));a.set_actor_label('NIAGARA_'+kind);c=a.get_component_by_class(unreal.NiagaraComponent);c.set_asset(asset);a.set_actor_scale3d(unreal.Vector(scale,scale,scale));c.activate(True)
            records.append(dict(kind=kind,system=asset.get_path_name(),emitter=emitter,mesh=mesh.get_path_name() if mesh else None,anchor_m=p,active=c.is_active()))
    json.dump(records,open(ROOT+'/out/niagara.json','w'),indent=2);mark('niagara_actors '+str(len(records)))
def emitters():
    manifest=json.load(open(ROOT+'/audio/manifest.json'));ambient={v['role']:v for v in manifest['assets'] if v['role'] in ('creek','wind','insects','bird')}
    sounds={}
    for role,v in ambient.items():
        dest='/Game/Audio/'+role
        if not EAL.does_directory_exist(dest):imp([ROOT+'/audio/'+v['file']],dest)
        sounds[role]=next((unreal.load_asset(p) for p in EAL.list_assets(dest,recursive=True,include_folder=False) if isinstance(unreal.load_asset(p),unreal.SoundWave)),None)
        if sounds[role]:sp(sounds[role],'looping',role!='bird');EAL.save_loaded_asset(sounds[role])
    rows=[]
    for role,sound in sounds.items():
        if not sound:raise RuntimeError('Sound failed '+role)
        anchors=([s['anchor_m'] for s in PL['life'] if s['kind']=='butterfly'][::5] if role=='creek' else [s['anchor_m'] for s in PL['life'] if s['kind']==('bird' if role in ('bird','wind') else 'insect')][::7])
        for p in anchors:
            a=EAS.spawn_actor_from_class(unreal.AmbientSound,V3(p));a.set_actor_label('FIELD_'+role);c=a.audio_component;c.set_sound(sound);c.set_volume_multiplier({'creek':.4,'wind':.16,'bird':.25,'insects':.07}[role]);sp(c,'auto_activate',True);sp(c,'override_attenuation',True)
            settings=c.attenuation_overrides;sp(settings,'attenuate',True);sp(settings,'spatialize',True);sp(settings,'attenuation_shape_extents',unreal.Vector(300,0,0));sp(settings,'falloff_distance',4000 if role=='wind' else 1800);c.attenuation_overrides=settings;rows.append(dict(role=role,pos_m=p,sound=sound.get_path_name()))
    json.dump(rows,open(ROOT+'/out/emitters.json','w'),indent=2);mark('ambient_emitters '+str(len(rows)))
def main():
    global MG
    chunk=json.load(open(ROOT+'/out/worldpack-placements.json'))
    if chunk['world_seed_descriptor']['seed']!=PL['seed']:raise RuntimeError('Stale world-pack seed')
    rows=import_instances(chunk);PL['instances']=[];PL['foliage']={};life_rows=[]
    for row in rows:
        if row['kind']=='foliage':PL['foliage'].setdefault(row['asset_id'],[]).append(row['transform'])
        elif row['kind'] in ('butterfly','bird','insect','critter'):life_rows.append(row)
        else:PL['instances'].append(row)
    if len(life_rows)!=len(PL['life']):raise RuntimeError('World-pack life count mismatch')
    for metadata,row in zip(PL['life'],life_rows):
        if (metadata['asset_id'],metadata['kind'])!=(row['asset_id'],row['kind']):raise RuntimeError('World-pack life identity mismatch')
        metadata['anchor_m']=row['transform'][:3];metadata['scale']=row['transform'][4]
    mark('worldpack_consumed '+str(len(rows)))
    load_textures();load_meshes();pb=MESH['probe'][0].get_bounds().origin
    if abs(pb.x-2000)>1 or abs(abs(pb.y)-1000)>1 or abs(pb.z-500)>1:raise RuntimeError('Axis probe failed')
    AX['sy']=1 if pb.y>0 else -1;validate_terrain();import_catalog();MG=world_granite();MT=mat_terrain();MW=mat_water();wood=mat_simple('M_BridgeWood','T_Bark_D',.6,.86,tint=[.42,.38,.34]);EAL.delete_asset('/Game/Maps/Creek') if EAL.does_asset_exist('/Game/Maps/Creek') else None
    if not LES.new_level('/Game/Maps/Creek'):raise RuntimeError('Could not create scene map')
    for tile in PL['tiles']:
        a=spawn_mesh(MESH[tile['mesh']][0],V3(tile['pos']),unreal.Rotator(),1,MT)
        a.static_mesh_component.set_collision_profile_name('BlockAll')
    validate_heights()
    for name,material in [('water',MW),('bridge',wood),('skirt',MT)]:spawn_mesh(MESH[name][0],V3([0,0,0]),unreal.Rotator(),1,material)
    hiker=CAT.get('assets__people__quaternius__hiker_female.glb',{});hm=hiker.get('meshes',[])
    if hm:
        a=EAS.spawn_actor_from_object(hm[0],V3(PL['hiker_still']),unreal.Rotator(yaw=90));a.set_actor_label('Hiker_Godot')
        if isinstance(a,unreal.SkeletalMeshActor):
            idle=next((v for v in hiker['anims'] if v.get_name()=='idle'),None)
            if idle is None:raise RuntimeError('Hiker idle animation missing')
            c=a.get_component_by_class(unreal.SkeletalMeshComponent);c.set_animation_mode(unreal.AnimationMode.ANIMATION_SINGLE_NODE);c.override_animation_data(idle,True,True,0,1)
    exec(compile(open(ROOT+'/src/foliage.py').read(),ROOT+'/src/foliage.py','exec'),globals());scatter_library();add_life();particles();emitters();lighting()
    for s in PL['shots']:
        seq=make_seq('Seq_'+s['name'],[(0,s['pos'],s['tgt'])],24,True,s['fl']);animate_life(seq,24)
    seq=make_seq('SeqWalk',[(k['f'],k['pos'],k['tgt']) for k in PL['walk']],432,False,24);animate_life(seq,432)
    if not LES.save_current_level():raise RuntimeError('Scene map save failed')
    EAL.save_directory('/Game',only_if_is_dirty=True,recursive=True);mark('SCENE_SAVED')
    for name in RUN.get('shots',[]):QUEUE.append(('Seq_'+name,RUN['out']+'/'+name,RUN.get('res',[1280,720]),RUN.get('temporal',4),CV))
    if RUN.get('walk'):QUEUE.append(('SeqWalk',RUN['out']+'/walk',RUN.get('walk_res',[1280,720]),1,CV))
    nxt()
try:main()
except Exception:
    err=traceback.format_exc();log(err);open(ROOT+'/ue_error.txt','w').write(err);unreal.SystemLibrary.quit_editor()
