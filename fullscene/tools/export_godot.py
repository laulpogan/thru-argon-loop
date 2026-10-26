#!/usr/bin/env python3
"""Read a pinned Godot branch without mutating its checkout. Copy assets by path only."""
import argparse, hashlib, json, pathlib, re, shutil, subprocess
p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--text',required=True);p.add_argument('--output',required=True);a=p.parse_args()
src=pathlib.Path(a.source);text=pathlib.Path(a.text);out=pathlib.Path(a.output);out.mkdir(parents=True,exist_ok=True)
revision=subprocess.check_output(['git','-C',str(src),'rev-parse','fleet/thru'],text=True).strip()
def show(path):return subprocess.check_output(['git','-C',str(src),'show',revision+':godot/'+path])
models=json.loads((text/'assets/biomes/manifest.json').read_text())['models'];roster=json.loads((text/'assets/wildlife/regional_roster.json').read_text())
rows=[]
for k,v in models.items():
 if 'path' in v:rows.append(dict(asset_id=k,type='plant/rock',path=v['path'],source='assets/biomes/manifest.json',rules={q:v[q] for q in ['latitude_deg','elevation_m','reference_height_m'] if q in v}))
for group in ['entries','supplemental_entries','companion_entries','ambient_insects']:
 for v in roster[group]:rows.append(dict(asset_id=v['id'],type='ambient insect' if group=='ambient_insects' else 'wildlife',path=v['path'],source='assets/wildlife/regional_roster.json',rules={q:v[q] for q in ['region','habitat','habitats','vegetation_forms','min_raw_height_m','max_raw_height_m'] if q in v}))
refs={}
for f in text.rglob('*'):
 if f.is_file():
  for ref in re.findall(r'res://[^\s"\'<>\)]+?\.(?:glb|gltf|obj|fbx|ogg|wav|mp3|tscn)',f.read_text(errors='replace')):refs.setdefault(ref,set()).add(str(f.relative_to(text)))
known={r['path'] for r in rows}
for ref,callers in sorted(refs.items()):
 if ref not in known:rows.append(dict(asset_id=ref[6:].replace('/','__'),type='scene' if ref.endswith('.tscn') else 'audio' if ref.endswith(('.ogg','.wav','.mp3')) else 'mesh/prop',path=ref,source='; '.join(sorted(callers)[:4]),rules={}))
common=subprocess.check_output(['git','-C',str(src),'rev-parse','--git-common-dir'],text=True).strip()
common=pathlib.Path(common) if pathlib.Path(common).is_absolute() else src/common
files={};missing=[]
for row in rows:
 ref=row['path'];rel=ref[6:];row['callers']=sorted(refs.get(ref,[]));row['eligible']=not ('evermotion' in rel.lower());row['library_file']=None
 if not row['eligible'] or ref.endswith('.tscn'):continue
 if ref not in files:
  try:b=show(rel)
  except subprocess.CalledProcessError:missing.append(ref);files[ref]=None;continue
  name=hashlib.sha256(ref.encode()).hexdigest()[:12]+'_'+pathlib.Path(rel).name;dst=out/name
  if b.startswith(b'version https://git-lfs'):
   oid=re.search(rb'oid sha256:(\w+)',b).group(1).decode()
   obj=common/'lfs/objects'/oid[:2]/oid[2:4]/oid
   if not obj.exists():missing.append(ref);files[ref]=None;continue
   shutil.copyfile(obj,dst)
  else:dst.write_bytes(b)
  files[ref]=dict(file=name,sha256=hashlib.file_digest(open(dst,'rb'),'sha256').hexdigest(),bytes=dst.stat().st_size)
 if files[ref]:row['library_file']=files[ref]['file']
# glTF has external buffers/textures. Preserve its complete sibling directory by path;
# never inspect vendor mesh/image bytes or rewrite the glTF payload.
for ref,info in files.items():
 if not info or not ref.endswith('.gltf'):continue
 rel=pathlib.PurePosixPath(ref[6:]);folder=hashlib.sha256(str(rel.parent).encode()).hexdigest()[:12]
 paths=subprocess.check_output(['git','-C',str(src),'ls-tree','-r','--name-only',revision,'--','godot/'+str(rel.parent)],text=True).splitlines()
 for source_path in paths:
  target=out/folder/pathlib.PurePosixPath(source_path).relative_to('godot/'+str(rel.parent));target.parent.mkdir(parents=True,exist_ok=True)
  b=show(source_path[6:])
  if b.startswith(b'version https://git-lfs'):
   oid=re.search(rb'oid sha256:(\w+)',b).group(1).decode();obj=common/'lfs/objects'/oid[:2]/oid[2:4]/oid
   if not obj.exists():raise FileNotFoundError(source_path)
   shutil.copyfile(obj,target)
  else:target.write_bytes(b)
 info['file']=folder+'/'+rel.name
for row in rows:
 if row['path'] in files and files[row['path']]:row['library_file']=files[row['path']]['file']
manifest=dict(schema='thru.fullscene-library/v1',source_commit=revision,rows=rows,files=files,missing=missing)
(out/'library.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(dict(rows=len(rows),files=sum(v is not None for v in files.values()),MB=round(sum(v['bytes'] for v in files.values() if v)/1e6),missing=len(missing))))
