#!/usr/bin/env python3
"""Fetch primary licensed recordings; preserve attribution and source evidence."""
import pathlib,json,urllib.request,subprocess,hashlib,csv,shutil,sys
out=pathlib.Path(sys.argv[1]);godot=pathlib.Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True);(out/'originals').mkdir(exist_ok=True);(out/'evidence').mkdir(exist_ok=True)
assets=[]
def get(url):
 req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 THRU audio provenance'})
 return urllib.request.urlopen(req,timeout=50).read()
def register(src,role,source,license,author,needed,notes):
 name=role+'.wav';dst=out/name
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(src),'-t','60','-ar','48000','-ac','1','-c:a','pcm_s16le',str(dst)],check=True)
 duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(dst)]))
 assets.append(dict(file=name,role=role,source_url=source,license=license,author=author,attribution_needed=needed,origin='Real recording',notes=notes,changes='Decoded to mono PCM 48 kHz, maximum 60 seconds; no generation',duration_s=duration,sha256=hashlib.file_digest(open(dst,'rb'),'sha256').hexdigest()))
for role,slug,num in [('wind','forest-wind-in-the-trees','0904'),('insects','field-cricket','1020'),('gravel','footsteps-on-gravels-2','1117'),('granite','step-shoe-on-stone-staircase','0606'),('wood','walk-on-pontoon','1845')]:
 url=f'https://bigsoundbank.com/{slug}-s{num}.html';html=get(url);(out/'evidence'/f'{num}.html').write_bytes(html)
 if b'CC0' not in html:raise RuntimeError('License evidence missing '+url)
 src=out/'originals'/f'bsb_{num}.mp3'
 if not src.exists():src.write_bytes(get(f'https://bigsoundbank.com/UPLOAD/mp3/{num}.mp3?v=d'))
 register(src,role,url,'CC0-1.0','Joseph SARDIN',False,{'wind':'Recorded forest in Rambouillet, France; conifer species unverified.','insects':'French field cricket; ambience stand-in, not verified Sierra species.','gravel':'Real studio foley; gravel.','granite':'Stone staircase; granite stand-in, stone type unverified.','wood':'Outdoor wooden pontoon, bridge surface proxy.'}[role])
provenance=json.load(open(godot/'provenance.json'))['assets']
for role,key in [('creek','stream01_antoinemax'),('dirt','footstepgrass01')]:
 v=next(a for a in provenance if key in pathlib.Path(a['file']).name);src=godot/pathlib.Path(v['file']).name;shutil.copyfile(src,out/'originals'/src.name)
 register(src,role,v['source_url'],v['license'],v['author'],True,'Reused licensed Godot asset. Grass/duff footstep is dirt proxy.' if role=='dirt' else 'Natural stream field recording, Antoinemax.')
# Sound-level license, not merely observation-level license.
obs=json.loads(get('https://api.inaturalist.org/v1/observations/408572176'))['results'][0];sound=next(s for s in obs['sounds'] if s['id']==2197823)
(out/'evidence'/'inaturalist_408572176.json').write_text(json.dumps(obs,indent=2))
if sound.get('license_code')!='cc0':raise RuntimeError('Bird sound license is not CC0')
src=out/'originals'/'stellers_jay_2197823.m4a';src.write_bytes(get(sound['file_url']))
register(src,'bird','https://www.inaturalist.org/observations/408572176','CC0-1.0',obs['user'].get('name') or obs['user']['login'],False,'Source-identified Steller’s jay, Seattle WA; no independent species validation.')
manifest=dict(schema='thru.audio-manifest/v1',generated_audio=False,assets=assets,source_decisions={'Sonniss':'Primary license checked; multi-GB bundles avoided because direct licensed recordings cover categories.','Freesound':'Login required; skipped without signup.','Pixabay':'Download endpoints returned 403; skipped after two attempts.','Lyria':'Not used; real recordings cover requested roles with stated geographic/surface proxies.'})
(out/'manifest.json').write_text(json.dumps(manifest,indent=2))
with open(out/'LICENSES.csv','w',newline='') as f:
 w=csv.writer(f);w.writerow(['file','source URL','license','author','attribution needed']);w.writerows((v['file'],v['source_url'],v['license'],v['author'],v['attribution_needed']) for v in assets)
(out/'CREDITS.txt').write_text('\n'.join(f"{v['file']}: {v['author']}, {v['source_url']}, {v['license']}; {v['changes']}" for v in assets)+'\n')
print('AUDIO_ASSETS',len(assets))
