"""Explicit-placement adapter for the actual world-pack v2 draft schema."""
import math

def export_scene(pl, origin):
    rows=[]
    for it in pl['instances']:
        rows.append((it['asset_id'],it['transform'],it['kind']))
    for aid,transforms in pl['foliage'].items():
        rows.extend((aid,t,'foliage') for t in transforms)
    for it in pl['life']:
        rows.append((it['asset_id'],[*it['anchor_m'],0,it['scale'],0,0,1],it['kind']))
    instances=[]
    for i,(aid,t,kind) in enumerate(rows):
        x,y,z,yaw,s,_,_,sz=t;a=-math.radians(yaw)/2
        instances.append(dict(instance_id=f'fullscene-{i}',asset_id=aid,pos_chunk_m=[x,z,y],rot_quat_xyzw=[0,math.sin(a),0,math.cos(a)],scale_xyz=[s,s*sz,s],height_offset_m=0,biome_evt=None,lod_tier='near',provenance=dict(producer='fullscene-biome-v1',kind=kind)))
    return dict(schema='thru.chunk-placements/v2',region_id='pct-region-0029',chunk_id='chunk_0_0',chunk_origin_region_m=[0,origin,0],world_seed_descriptor=dict(schema='thru.world-seed/v1',generator=1,seed=pl['seed']),explicit_instances=instances,scatter_strata=[])

def import_instances(chunk):
    if chunk['schema']!='thru.chunk-placements/v2':raise ValueError('Expected world-pack v2 explicit placements')
    rows=[]
    for v in chunk['explicit_instances']:
        x,z,y=v['pos_chunk_m'];sx,sz,sy=v['scale_xyz'];qx,qy,qz,qw=v['rot_quat_xyzw']
        if abs(qx)+abs(qz)>1e-6 or abs(sx-sy)>1e-6:raise ValueError('Adapter supports upright yaw, equal horizontal scale only')
        rows.append(dict(asset_id=v['asset_id'],kind=v.get('provenance',{}).get('kind','prop'),transform=[x,y,z+v.get('height_offset_m',0),-math.degrees(2*math.atan2(qy,qw)),sx,0,0,sz/sx]))
    return rows
